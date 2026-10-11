"""CPU-only frozen VS-SEG high-resolution T2 cross-pathology model audit."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import shutil
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
import pydicom
import torch
from scipy.interpolate import PchipInterpolator
from skimage.draw import polygon
from skimage.transform import resize

from remind_native_t2_ixi_pair import MODELS, predict, prepared


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "VS_SEG_THIN3D_MODEL_CONFIRMATION_PROTOCOL_2026-10-01.md"
NONPIXEL = ROOT / "literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json"
MAPPING = ROOT / "literature/source_cache/vs_seg_official_inventory_2026-10-01/mapping.csv"
FIRST_SOURCE = ROOT / "data/vs_seg_001_header_pilot"
PREFLIGHT = ROOT / "experiments/vs_seg_001_model_preflight.json"
DATA = ROOT / "data/vs_seg_thin3d_model_confirmation"
OUT = ROOT / "experiments/vs_seg_thin3d_model_confirmation"
BASE = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?"
MIN_FREE = 15_000_000_000
METHODS = ("raw_linear", "pipeline_linear", "raw_pchip", "pipeline_pchip", "hat", "swinir")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mapped_rt_uids() -> dict[str, str]:
    with MAPPING.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    return {row["Descriptive Directory Name"].split("/")[0]:
            row["Classic Directory Name"].split("/")[-1]
            for row in rows if row["Modality"] == "T2 RTSTRUCT"}


def download_or_cached(patient: str, kind: str, uid: str, cap: int,
                       first_expected_hash: str | None = None) -> tuple[Path, dict]:
    if patient == "VS-SEG-001":
        path = FIRST_SOURCE / f"{kind}.zip"
    else:
        path = DATA / f"{patient}_{kind}.zip"
    if not path.exists():
        if shutil.disk_usage(DATA).free < MIN_FREE:
            raise OSError("15 GB free-space floor reached")
        url = BASE + urllib.parse.urlencode({"SeriesInstanceUID": uid})
        req = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=120) as response:
            raw = response.read(cap + 1)
            if response.status != 200 or len(raw) > cap:
                raise ValueError("Unexpected TCIA response size/status")
        path.write_bytes(raw)
    if path.stat().st_size > cap:
        raise ValueError("Cached ZIP exceeds cap")
    digest = sha256(path)
    if first_expected_hash and digest != first_expected_hash:
        raise ValueError("Preflight source ZIP hash changed")
    return path, {"url": BASE + urllib.parse.urlencode({"SeriesInstanceUID": uid}),
                  "series_uid": uid, "path": path.relative_to(ROOT).as_posix(),
                  "bytes": path.stat().st_size, "sha256": digest}


def read_series(path: Path, patient: str, series_uid: str, kind: str) -> list:
    objects = []
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if member.is_dir() or member.filename == "LICENSE":
                continue
            parts = Path(member.filename).parts
            if (not member.filename.lower().endswith(".dcm") or ".." in parts or
                    member.filename.startswith(("/", "\\")) or any(":" in p for p in parts)):
                raise ValueError("Unsafe or non-DICOM ZIP member")
            if member.file_size > (2_000_000 if kind == "rtstruct" else 10_000_000):
                raise ValueError("Unexpected DICOM member size")
            ds = pydicom.dcmread(io.BytesIO(archive.read(member)))
            if str(ds.get("PatientID", "")) != patient or str(ds.get("SeriesInstanceUID", "")) != series_uid:
                raise ValueError("DICOM patient or series UID differs")
            objects.append(ds)
    if not objects or len({str(x.SOPInstanceUID) for x in objects}) != len(objects):
        raise ValueError("Empty/duplicate DICOM series")
    return objects


def volume_and_mask(images: list, structures: list) -> tuple[np.ndarray, np.ndarray, dict]:
    if len(structures) != 1:
        raise ValueError("T2 RTSTRUCT series not unique")
    orientation = np.asarray(images[0].ImageOrientationPatient, dtype=np.float64)
    col_dir, row_dir = orientation[:3], orientation[3:]
    normal = np.cross(col_dir, row_dir)
    images.sort(key=lambda ds: float(np.dot(normal, np.asarray(ds.ImagePositionPatient, dtype=np.float64))))
    if any(str(ds.get("MRAcquisitionType", "")) != "3D" or
           not np.allclose(ds.ImageOrientationPatient, orientation, rtol=0, atol=1e-5) or
           str(ds.get("FrameOfReferenceUID", "")) != str(images[0].FrameOfReferenceUID) or
           not 1.0 <= float(ds.SliceThickness) <= 1.5 or
           str(ds.PhotometricInterpretation) != "MONOCHROME2" for ds in images):
        raise ValueError("T2 acquisition/geometry gate failed")
    positions = np.array([np.dot(normal, np.asarray(ds.ImagePositionPatient, dtype=np.float64))
                          for ds in images])
    steps = np.diff(positions)
    if len(steps) < 7 or not np.allclose(steps, steps[0], rtol=0, atol=1e-4) or not 1.0 <= steps[0] <= 1.5:
        raise ValueError("Native T2 plane spacing gate failed")
    if str(structures[0].get("FrameOfReferenceUID", "")) != str(images[0].FrameOfReferenceUID):
        raise ValueError("T2 RTSTRUCT frame differs")
    volume = np.stack([ds.pixel_array.astype(np.float32) for ds in images], axis=-1)
    if not np.isfinite(volume).all():
        raise ValueError("Nonfinite T2 pixels")
    by_uid = {str(ds.SOPInstanceUID): (i, ds) for i, ds in enumerate(images)}
    names = {int(x.ROINumber): str(x.ROIName) for x in structures[0].StructureSetROISequence}
    tv = [x for x in structures[0].ROIContourSequence if names[int(x.ReferencedROINumber)] == "TV"]
    if len(tv) != 1:
        raise ValueError("Missing or ambiguous TV contour")
    mask = np.zeros(volume.shape, dtype=bool)
    per_slice = defaultdict(int)
    for contour in tv[0].ContourSequence:
        if str(contour.ContourGeometricType) != "CLOSED_PLANAR" or len(contour.get("ContourImageSequence", [])) != 1:
            raise ValueError("TV contour not a single referenced closed plane")
        ref = str(contour.ContourImageSequence[0].ReferencedSOPInstanceUID)
        if ref not in by_uid:
            raise ValueError("TV references a different T2 series")
        z, ds = by_uid[ref]
        origin = np.asarray(ds.ImagePositionPatient, dtype=np.float64)
        points = np.asarray(contour.ContourData, dtype=np.float64).reshape(-1, 3)
        delta = points - origin
        if (len(points) != int(contour.NumberOfContourPoints) or
                float(np.max(np.abs(delta @ normal))) > 1e-3):
            raise ValueError("TV contour point/plane mismatch")
        rr = delta @ row_dir / float(ds.PixelSpacing[0])
        cc = delta @ col_dir / float(ds.PixelSpacing[1])
        if rr.min() < -.5 or cc.min() < -.5 or rr.max() > int(ds.Rows) - .5 or cc.max() > int(ds.Columns) - .5:
            raise ValueError("TV contour outside T2 FOV")
        r, c = polygon(rr, cc, shape=volume.shape[:2])
        mask[r, c, z] = True
        per_slice[z] += 1
    if mask.sum() == 0:
        raise ValueError("Rasterized TV is empty")
    return volume, mask, {"shape": list(volume.shape), "slice_thickness": float(images[0].SliceThickness),
                          "spacing": float(steps[0]), "pixel_spacing": [float(x) for x in images[0].PixelSpacing],
                          "tumor_voxels": int(mask.sum()), "tumor_slices": len(per_slice),
                          "multi_contour_slices": sum(x > 1 for x in per_slice.values()),
                          "sequence": "TSE" if "tse3d" in str(images[0].SeriesDescription).lower() else "CISS"}


def roi_metrics(output: np.ndarray, target: np.ndarray, roi: np.ndarray, span: float) -> dict:
    error = (output - target)[roi].astype(np.float64)
    return {"pixels": int(roi.sum()), "normalized_mse": float(np.mean(error ** 2) / span ** 2),
            "mae": float(np.mean(np.abs(error)))}


def score_case(info: dict, rt_uid: str, hat: object, swinir: object,
               first_hashes: dict[str, str]) -> dict:
    patient = info["patient"]
    t2_path, t2_source = download_or_cached(patient, "t2", info["series_uid"], 35_000_000,
                                             first_hashes.get("t2") if patient == "VS-SEG-001" else None)
    rt_path, rt_source = download_or_cached(patient, "rtstruct", rt_uid, 5_000_000,
                                            first_hashes.get("rtstruct") if patient == "VS-SEG-001" else None)
    images = read_series(t2_path, patient, info["series_uid"], "t2")
    if len(images) != info["image_count"]:
        raise ValueError("NBIA T2 object count differs")
    structures = read_series(rt_path, patient, rt_uid, "rtstruct")
    volume, label, geometry = volume_and_mask(images, structures)
    anchors = volume[:, :, ::4]
    prep = prepared(anchors)
    planes, lo, hi = prep
    span = float(hi - lo)
    if not np.isfinite(span) or span <= 0:
        raise ValueError("Invalid observed-anchor range")
    eligible, supports = {"1": [], "3": []}, {}
    for residue in (1, 3):
        for z in range(residue, volume.shape[2] - 4, 4):
            i = z // 4
            left, right = anchors[:, :, i], anchors[:, :, i + 1]
            support = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                       (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
            supports[z] = support
            if i >= 1 and i + 2 < anchors.shape[2] and int((label[:, :, z] & support).sum()) >= 64:
                eligible[str(residue)].append(z)
    targets = {}
    for residue in (1, 3):
        choices = eligible[str(residue)]
        if len(choices) < 3:
            raise ValueError(f"Insufficient residue-{residue} tumor targets")
        selected = [choices[(len(choices) - 1) // 3], choices[2 * (len(choices) - 1) // 3]]
        if len(set(selected)) != 2:
            raise ValueError("Target selection duplicated a slice")
        targets[str(residue)] = selected
    rows = []
    for residue in (1, 3):
        for z in targets[str(residue)]:
            i = z // 4
            rel = (z - 4 * i) / 4
            left, right = anchors[:, :, i], anchors[:, :, i + 1]
            raw_linear = ((1 - rel) * left + rel * right).astype(np.float32)
            coarse = ((1 - rel) * planes[i] + rel * planes[i + 1]).astype(np.float32)
            pipeline_linear = (resize(np.clip(coarse, 0, 1), volume.shape[:2],
                                      preserve_range=True, anti_aliasing=True) * span + lo).astype(np.float32)
            idx = np.arange(i - 1, i + 3)
            raw_pchip = PchipInterpolator(4 * idx, np.moveaxis(anchors[:, :, idx], -1, 0), axis=0)(z)
            coarse_pchip = PchipInterpolator(4 * idx, np.stack([planes[j] for j in idx]), axis=0)(z)
            pipeline_pchip = (resize(np.clip(coarse_pchip, 0, 1), volume.shape[:2],
                                     preserve_range=True, anti_aliasing=True) * span + lo).astype(np.float32)
            outputs = {"raw_linear": raw_linear, "pipeline_linear": pipeline_linear,
                       "raw_pchip": raw_pchip, "pipeline_pchip": pipeline_pchip,
                       "hat": predict(hat, prep, i, rel, volume.shape[:2]),
                       "swinir": predict(swinir, prep, i, rel, volume.shape[:2])}
            row = {"z": z, "residue": residue}
            for roi_name, roi in (("tumor", label[:, :, z] & supports[z]),
                                  ("support", supports[z])):
                for method, output in outputs.items():
                    if not np.isfinite(output).all():
                        raise ValueError(f"Nonfinite {method} output")
                    for key, value in roi_metrics(output, volume[:, :, z], roi, span).items():
                        row[f"{roi_name}_{method}_{key}"] = value
            rows.append(row)
    if len(rows) != 4:
        raise ValueError("Incomplete four-target case")
    if patient == "VS-SEG-001":
        frozen = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        previous = {row["z"]: row for row in frozen["rows"]}
        for row in rows:
            if row["z"] not in previous:
                raise ValueError("First-case target differs from model preflight")
            for roi in ("tumor", "support"):
                for method in ("hat", "swinir", "pipeline_linear", "pipeline_pchip"):
                    field = f"{roi}_{method}_normalized_mse"
                    if abs(row[field] - previous[row["z"]][roi][method]["normalized_mse"]) > 1e-10:
                        raise ValueError(f"First-case model preflight differs: {field}")
    patient_row = {"patient": patient, "sequence": geometry["sequence"]}
    for roi in ("tumor", "support"):
        for method in METHODS:
            for metric in ("normalized_mse", "mae"):
                field = f"{roi}_{method}_{metric}"
                patient_row[field] = float(np.mean([r[field] for r in rows]))
    for model in ("hat", "swinir"):
        for baseline in ("pipeline_pchip", "raw_pchip", "pipeline_linear", "raw_linear"):
            for roi in ("tumor", "support"):
                patient_row[f"{roi}_{model}_minus_{baseline}"] = (
                    patient_row[f"{roi}_{model}_normalized_mse"] -
                    patient_row[f"{roi}_{baseline}_normalized_mse"])
    return {"patient": patient, "complete": True, "source": {"t2": t2_source, "rtstruct": rt_source},
            "geometry": geometry, "observed_span": span, "eligible": eligible,
            "targets": targets, "rows": rows, "patient_row": patient_row}


def interval(values: np.ndarray, draws: np.ndarray) -> dict:
    means = values[draws].mean(axis=1)
    return {"mean": float(values.mean()),
            "ci95": [float(x) for x in np.percentile(means, [2.5, 97.5])],
            "positive_patients": int((values > 0).sum())}


def wilson_lower(k: int, n: int) -> float:
    z = 1.959963984540054
    p = k / n
    return (p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1 + z*z/n)


def main() -> None:
    source = json.loads(NONPIXEL.read_text(encoding="utf-8"))
    if source["mapped_patients"] != 242 or source["nbia_t2_patients"] != 241 or len(source["t2_series"]) != 241:
        raise ValueError("Frozen source denominator differs")
    rt_uids = mapped_rt_uids()
    first = json.loads((ROOT / "literature/source_cache/vs_seg_001_two_series_headers_2026-10-01/index.json")
                       .read_text(encoding="utf-8"))
    first_hashes = {x["name"]: x["sha256"] for x in first}
    if set(first_hashes) != {"t2", "rtstruct"}:
        raise ValueError("First-case source contract differs")
    for name in ("hat", "swinir"):
        if sha256(MODELS[name][1]) != MODELS[name][2]:
            raise ValueError("Frozen checkpoint changed")
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    contract = {"protocol_sha256": sha256(PROTOCOL), "nonpixel_sha256": sha256(NONPIXEL),
                "mapping_sha256": sha256(MAPPING), "script_sha256": sha256(Path(__file__)),
                "preflight_sha256": sha256(PREFLIGHT),
                "checkpoint_sha256": {name: MODELS[name][2] for name in ("hat", "swinir")},
                "source_mapped": 242, "attempted": 241, "gpu_used": False}
    contract_path = OUT / "run_contract.json"
    if contract_path.exists():
        if json.loads(contract_path.read_text(encoding="utf-8")) != contract:
            raise ValueError("Existing run contract differs")
    else:
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    case_dir = OUT / "cases"
    case_dir.mkdir(exist_ok=True)
    completed, failures = [], []
    for number, info in enumerate(source["t2_series"], 1):
        patient = info["patient"]
        case_path = case_dir / f"{patient}.json"
        if case_path.exists():
            result = json.loads(case_path.read_text(encoding="utf-8"))
            if result.get("contract_sha256") != sha256(contract_path):
                raise ValueError(f"Existing case contract differs: {patient}")
        else:
            try:
                result = score_case(info, rt_uids[patient], hat, swinir, first_hashes)
            except Exception as exc:
                result = {"patient": patient, "complete": False,
                          "failure_type": type(exc).__name__, "failure_reason": str(exc)[:200]}
            result["contract_sha256"] = sha256(contract_path)
            case_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        if result["complete"]:
            completed.append(result)
        else:
            failures.append({"patient": patient, "reason": result["failure_reason"]})
        print(f"VS-SEG CPU {number}/241 {patient} complete={result['complete']}", flush=True)
        if patient == "VS-SEG-001" and not result["complete"]:
            raise RuntimeError("First-case source/model preflight did not reproduce")
    patients = [x["patient_row"] for x in completed]
    targets = [{"patient": x["patient"], **row} for x in completed for row in x["rows"]]
    csv_write(OUT / "per_patient.csv", patients)
    csv_write(OUT / "per_target.csv", targets)
    summary = {"source_mapped": 242, "attempted": 241, "completed": len(patients),
               "failures": failures, "complete_cohort": True, "no_gpu": True,
               "contract_sha256": sha256(contract_path), "bootstrap_seed": 20261006,
               "bootstrap_draws": 5000, "sequences": dict(Counter(p["sequence"] for p in patients))}
    if patients:
        draws = np.random.default_rng(20261006).integers(0, len(patients), (5000, len(patients)))
        fields = [f"{roi}_{model}_minus_{baseline}"
                  for roi in ("tumor", "support") for model in ("hat", "swinir")
                  for baseline in ("pipeline_pchip", "raw_pchip", "pipeline_linear", "raw_linear")]
        summary["differences"] = {field: interval(np.array([p[field] for p in patients]), draws)
                                  for field in fields}
        signs = sum(p["tumor_hat_minus_pipeline_pchip"] > 0 and
                    p["support_hat_minus_pipeline_pchip"] < 0 for p in patients)
        summary["hat_pipeline_pchip_discordance"] = {
            "patients": signs, "fraction": signs / len(patients),
            "wilson_95_lower": wilson_lower(signs, len(patients))}
        tumor_ci = summary["differences"]["tumor_hat_minus_pipeline_pchip"]["ci95"]
        full_ci = summary["differences"]["support_hat_minus_pipeline_pchip"]["ci95"]
        summary["primary_gate_pass"] = bool(len(patients) >= 100 and tumor_ci[0] > 0 and
                                            full_ci[1] < 0 and wilson_lower(signs, len(patients)) > .20)
        summary["sequence_sensitivity"] = {
            seq: {"patients": len(group),
                  "mean_tumor_hat_minus_pipeline_pchip": float(np.mean([
                      p["tumor_hat_minus_pipeline_pchip"] for p in group])),
                  "mean_support_hat_minus_pipeline_pchip": float(np.mean([
                      p["support_hat_minus_pipeline_pchip"] for p in group]))}
            for seq in ("CISS", "TSE") for group in [[p for p in patients if p["sequence"] == seq]]}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("failures", "differences")}, indent=2))


if __name__ == "__main__":
    main()
