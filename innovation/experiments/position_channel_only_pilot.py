"""Frozen, CPU-only position-channel diagnostic on two public sources."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import time
import zipfile
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import pydicom
import torch
from skimage.transform import resize

import msvalid_ixi_weights_secondary as ms
import remind_native_t2_ixi_pair as rem


ROOT = Path(__file__).resolve().parents[2]
INNOVATION = ROOT / "innovation"
PLAN = INNOVATION / "POSITION_CHANNEL_ONLY_PILOT_PLAN_2026-10-01.md"
OUT = INNOVATION / "experiments/position_channel_only_pilot"
SOURCES = (
    ("msvalid", ("P1", "P2", "P3")),
    ("remind", ("ReMIND-003", "ReMIND-007", "ReMIND-009")),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def original_rows(source: str) -> dict[tuple[str, int], dict]:
    path = (INNOVATION / "experiments" /
            ("msvalid_ixi_weights_secondary" if source == "msvalid"
             else "remind_native_t2_ixi_pair") / "per_target.csv")
    with path.open(newline="", encoding="utf-8") as stream:
        return {(row["patient"], int(row["z"])): row for row in csv.DictReader(stream)}


def load_ms(patient: dict) -> np.ndarray:
    path = ms.DATA / f"{patient['patient']}.nii.gz"
    hashes = {p["patient"]: p["sha256"] for p in
              json.loads(ms.SOURCE_MANIFEST.read_text(encoding="utf-8"))["records"]}
    if sha256(path) != hashes[patient["patient"]]:
        raise ValueError("MSValid source hash changed")
    volume = nib.load(str(path)).get_fdata(dtype=np.float32)
    if tuple(volume.shape) != tuple(patient["shape"]):
        raise ValueError("MSValid shape changed")
    return volume


def load_rem(patient: dict) -> np.ndarray:
    path = INNOVATION / patient["path"]
    if sha256(path) != patient["zip_sha256"]:
        raise ValueError("ReMIND source hash changed")
    depth = patient["depth"]
    selected = set(range(0, depth, 2))
    selected.update(z for positions in patient["targets"].values() for z in positions)
    volume = np.zeros((*patient["shape"], depth), dtype=np.float32)
    with zipfile.ZipFile(path) as archive:
        for z in sorted(selected):
            with archive.open(patient["ordered_files"][z]) as stream:
                ds = pydicom.dcmread(stream)
            plane = ds.pixel_array.astype(np.float32)
            if tuple(plane.shape) != tuple(patient["shape"]):
                raise ValueError(f"ReMIND pixel shape changed z{z}")
            volume[:, :, z] = (plane * float(ds.get("RescaleSlope", 1)) +
                               float(ds.get("RescaleIntercept", 0)))
    return volume


def predict_map_only(model: object, prep: tuple, index: int,
                     rel0: float, rel2: float, shape: tuple[int, int]) -> np.ndarray:
    planes, lo, hi = prep
    left, right = planes[index], planes[index + 1]
    coarse = ((1 - rel0) * left + rel0 * right).astype(np.float32)
    base = np.stack([left, right, coarse, np.full((256, 256), rel0, np.float32)])
    changed = base.copy()
    changed[3, :, :] = rel2
    if not np.array_equal(base[:3], changed[:3]) or np.array_equal(base[3], changed[3]):
        raise AssertionError("position-only channel intervention failed")
    residual = model._predict_residual(changed)
    generated = np.clip(coarse + residual, 0, 1)
    return (resize(generated, shape, preserve_range=True, anti_aliasing=True)
            * (hi - lo) + lo).astype(np.float32)


def score_patient(source: str, patient: dict, volume: np.ndarray, hat: object,
                  swinir: object, frozen: dict) -> tuple[list[dict], dict]:
    if not np.isfinite(volume).all():
        raise ValueError("nonfinite source pixels")
    prep = {}
    for phase in (0, 2):
        indices = list(range(phase, volume.shape[2], 4))
        anchors = np.ascontiguousarray(volume[:, :, indices])
        prep[phase] = (indices, anchors, ms.prepared(anchors))
    rows = []
    for residue in (1, 3):
        targets = (patient["eligible_targets"][f"residue_{residue}"] if source == "msvalid"
                   else patient["targets"][str(residue)])
        for z in targets:
            i0, i2 = z // 4, (z - 2) // 4
            rel0 = (z - prep[0][0][i0]) / 4
            rel2 = (z - prep[2][0][i2]) / 4
            left, right = prep[0][1][:, :, i0], prep[0][1][:, :, i0 + 1]
            mask = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                    (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
            if not mask.any():
                raise ValueError(f"empty support z{z}")
            shape = volume.shape[:2]
            a = ms.predict(hat, prep[0][2], i0, rel0, shape)
            b0 = ms.predict(swinir, prep[0][2], i0, rel0, shape)
            bmap = predict_map_only(swinir, prep[0][2], i0, rel0, rel2, shape)
            b2 = ms.predict(swinir, prep[2][2], i2, rel2, shape)
            y = volume[:, :, z]
            shared = ms.metrics(a, b0, y, mask)
            position = ms.metrics(a, bmap, y, mask)
            disjoint = ms.metrics(a, b2, y, mask)
            old = frozen[(patient["patient"], z)]
            for key, actual in (("shared_observable", shared["observable"]),
                                ("disjoint_observable", disjoint["observable"]),
                                ("shared_a_mae", shared["a_mae"])):
                if abs(float(old[key]) - actual) > 1e-5:
                    raise ValueError(f"frozen-result mismatch {patient['patient']} z{z} {key}")
            if int(old["support_pixels"]) != int(mask.sum()):
                raise ValueError(f"frozen support mismatch {patient['patient']} z{z}")
            delta_full = disjoint["observable"] - shared["observable"]
            delta_map = position["observable"] - shared["observable"]
            rows.append({"source": source, "patient": patient["patient"], "z": z,
                         "residue": residue, "rel0": rel0, "rel2": rel2,
                         "support_pixels": int(mask.sum()),
                         "shared_o": shared["observable"], "map_only_o": position["observable"],
                         "disjoint_o": disjoint["observable"],
                         "delta_map_o": delta_map, "delta_full_o": delta_full,
                         "absolute_delta_ratio": (abs(delta_map) / abs(delta_full)
                                                  if delta_full != 0 else None),
                         "shared_b_mae": shared["b_mae"], "map_only_b_mae": position["b_mae"],
                         "disjoint_b_mae": disjoint["b_mae"]})
    if not rows or any(not any(r["residue"] == residue for r in rows) for residue in (1, 3)):
        raise ValueError("missing target residue")
    by_residue = {residue: [r for r in rows if r["residue"] == residue]
                  for residue in (1, 3)}
    fields = ("shared_o", "map_only_o", "disjoint_o", "delta_map_o", "delta_full_o",
              "shared_b_mae", "map_only_b_mae", "disjoint_b_mae")
    result = {key: float(np.mean([np.mean([r[key] for r in by_residue[residue]])
                                   for residue in (1, 3)])) for key in fields}
    result.update({"source": source, "patient": patient["patient"], "targets": len(rows)})
    return rows, result


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    for name, (_, path, expected) in ms.MODELS.items():
        if sha256(path) != expected or rem.MODELS[name][2] != expected:
            raise ValueError(f"{name} checkpoint mismatch")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = ms.MODELS["hat"][0](ms.MODELS["hat"][1], device="cpu")
    swinir = ms.MODELS["swinir"][0](ms.MODELS["swinir"][1], device="cpu")
    ms_records = json.loads(ms.QUALIFIED.read_text(encoding="utf-8"))["patients"]
    rem_records = json.loads(rem.QUALIFIED.read_text(encoding="utf-8"))["records"]
    selected = {"msvalid": ms_records[:3],
                "remind": [p for p in rem_records if p["eligible"]][:3]}
    for source, names in SOURCES:
        if tuple(p["patient"] for p in selected[source]) != names:
            raise ValueError(f"frozen {source} selection changed")
    OUT.mkdir(parents=True)
    targets, patients, failures = [], [], []
    started = time.perf_counter()
    for source, _ in SOURCES:
        frozen = original_rows(source)
        for patient in selected[source]:
            name = patient["patient"]
            try:
                volume = load_ms(patient) if source == "msvalid" else load_rem(patient)
                rows, result = score_patient(source, patient, volume, hat, swinir, frozen)
                targets.extend(rows)
                patients.append(result)
                print(f"{source} {name} targets={len(rows)} elapsed={time.perf_counter()-started:.1f}s", flush=True)
            except Exception as error:
                failures.append({"source": source, "patient": name,
                                 "error": f"{type(error).__name__}: {error}"})
                print(f"{source} {name} FAIL {error}", flush=True)
    write_csv(OUT / "per_target.csv", targets)
    write_csv(OUT / "per_patient.csv", patients)
    summary = {"plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
               "checkpoint_sha256": {name: spec[2] for name, spec in ms.MODELS.items()},
               "patients_expected": 6, "patients_scored": len(patients),
               "targets_scored": len(targets), "failures": failures,
               "elapsed_seconds": time.perf_counter() - started, "sources": {}}
    for source, _ in SOURCES:
        group = [p for p in patients if p["source"] == source]
        summary["sources"][source] = {
            "patients_scored": len(group), "targets_scored": sum(p["targets"] for p in group),
            **{f"mean_{key}": float(np.mean([p[key] for p in group])) if group else None
               for key in ("shared_o", "map_only_o", "disjoint_o", "delta_map_o",
                           "delta_full_o", "shared_b_mae", "map_only_b_mae", "disjoint_b_mae")}}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
