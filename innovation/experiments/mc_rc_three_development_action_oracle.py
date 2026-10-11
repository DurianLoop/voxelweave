"""CPU-only target-assisted action-space diagnostic on three fixed MC-RC developers."""
from __future__ import annotations

import csv
import json
import math
import os
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import nibabel as nib
import numpy as np
import pydicom
import torch
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_runtime import reconstruct, sha
from remind_native_t2_ixi_pair import MODELS, prepared

OUT = ROOT / "experiments/mc_rc_three_development_action_oracle"
PLAN = ROOT / "MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_PLAN_2026-10-02.md"
HEADERS = ROOT / "literature/source_cache/mc_rc_004_006_native_headers_2026-10-02"
LABELS = ROOT / "experiments/mc_rc_004_006_native_label_gate"
BASES = ("pipeline_pchip", "raw_pchip")
FIXED = (0., .25, .5, .75, 1.)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def freeze():
    ledger = read(HEADERS / "attempt_01.json")
    labels = read(LABELS / "resource_followup_attempt_01.json")
    proof = read(LABELS / "independent_raw_geometry_grid_verification.json")
    if proof["errors"] or proof["header_result_sha256"] != sha(HEADERS / "attempt_01.json") or proof["resource_followup_result_sha256"] != sha(LABELS / "resource_followup_attempt_01.json"):
        raise ValueError("Source independent verification differs")
    by_uid = {r["series_uid"]: r for r in labels["series"]}
    cases = []
    for patient in ("VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"):
        eligible = [r for r in ledger["series"] if r["source"]["PatientID"] == patient and by_uid[r["source"]["SeriesInstanceUID"]]["header_and_label_grid_preflight_passed"]]
        row = sorted(eligible, key=lambda r: (r["source"]["StudyDate"], r["source"]["SeriesInstanceUID"]))[0]
        cases.append({"patient": patient, "header": row, "label": by_uid[row["source"]["SeriesInstanceUID"]], "role": "development"})
    cls, checkpoint, expected = MODELS["hat"]
    if sha(checkpoint) != expected:
        raise ValueError("Frozen IXI HAT checkpoint differs")
    sources = [PLAN, Path(__file__), HEADERS / "attempt_01.json", LABELS / "resource_followup_attempt_01.json", LABELS / "independent_raw_geometry_grid_verification.json", checkpoint,
               ROOT / "experiments/vs_seg_full_volume_runtime.py", ROOT / "experiments/remind_native_t2_ixi_pair.py", ROOT / "experiments/vs_seg_task_cpu_support.py",
               ROOT.parent / "baseline/ixi_hat_2p5d/train.py", ROOT.parent / "baseline/ixi_hat_2p5d/model.py", ROOT.parent / "pre/ixi_diffusion/common.py"]
    sources += [ROOT / c["header"]["transfer"]["file"] for c in cases]
    sources += [ROOT / c["label"]["label_file"] for c in cases]
    contract = {"cases": cases, "created_utc": datetime.now(timezone.utc).isoformat(), "primary_action": ["pipeline_pchip", "hat"], "secondary_action": ["raw_pchip", "hat"], "tile_size": 32,
                "checkpoint_sha256": expected, "independent_confirmation": False, "scientific_goal_complete": False,
                "files": [{"path": p.relative_to(ROOT.parent).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(set(sources))]}
    write(OUT / "run_contract.json", contract)
    return cases, cls, checkpoint


def decode(case):
    row, label = case["header"], case["label"]
    hdr = read(HEADERS / row["header_file"])
    by_member = {r["zip_member"]: r for r in hdr["records"]}
    path = ROOT / row["transfer"]["file"]
    if sha(path) != row["transfer"]["sha256"] or sha(ROOT / label["label_file"]) != label["label_sha256"]:
        raise ValueError("Frozen MR/label source hash differs")
    planes = []
    with zipfile.ZipFile(path) as archive:
        for member in row["summary"]["ordered_zip_members"]:
            with archive.open(member) as stream:
                ds = pydicom.dcmread(stream)
            prior = by_member[member]
            if str(ds.SOPInstanceUID) != prior["sop_uid"] or str(ds.PatientID) != case["patient"] or str(ds.SeriesInstanceUID) != row["source"]["SeriesInstanceUID"] or str(ds.StudyInstanceUID) != row["source"]["StudyInstanceUID"] or str(ds.PhotometricInterpretation) != "MONOCHROME2":
                raise ValueError("Decoded MR identity/order/photometric mismatch")
            plane = ds.pixel_array.astype(np.float32) * float(ds.get("RescaleSlope", 1)) + float(ds.get("RescaleIntercept", 0))
            planes.append(plane)
    volume = np.stack(planes, axis=-1)
    img = nib.load(ROOT / label["label_file"])
    lab = np.asarray(img.dataobj) != 0
    transform = np.array(label["grid"]["dicom_rcz_from_label_xyz"], dtype=int)
    permutation = np.argmax(abs(transform[:3, :3]), axis=1)
    native_label = np.transpose(lab, permutation)
    for axis, other in enumerate(permutation):
        if transform[axis, other] < 0:
            native_label = np.flip(native_label, axis=axis)
    if volume.shape != native_label.shape or volume.shape != (row["summary"]["rows"], row["summary"]["columns"], row["summary"]["planes"]) or not np.isfinite(volume).all() or int(native_label.sum()) != label["label_foreground_voxels"]:
        raise ValueError("Decoded MR/label shape, finite or index transformation gate failed")
    return volume, native_label


def metric_rows(rows, region):
    present = [r[region] for r in rows if r[region]["pixels"]]
    pixels = sum(r["pixels"] for r in present)
    return {"nonempty_targets": len(present), "pixels": pixels,
            "target_equal_nmse": float(np.mean([r["sse"] / r["pixels"] for r in present])) if present else None,
            "pixel_weighted_nmse": sum(r["sse"] for r in present) / pixels if pixels else None}


def plane_error(z, pred, ref, support, lesion):
    squared = (pred - ref) ** 2
    return {"z": z, **{name: {"pixels": int(mask.sum()), "sse": float(squared[mask].sum())} for name, mask in (("support", support), ("lesion", lesion))}}


def analyse(case, native, lesion_mask, candidate, prep, writer):
    last = (native.shape[-1] - 1) // 4 * 4
    targets = [z for z in range(1, last) if z % 4]
    span = prep[2] - prep[1]
    supports = {}
    for z in targets:
        left, right = native[:, :, z - z % 4], native[:, :, z - z % 4 + 4]
        supports[z] = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
        if not supports[z].any():
            raise ValueError("Empty frozen observed-only support")
    actions = []
    for base_name in BASES:
        base = reconstruct(base_name, native, prep, {})
        total_m, total_d = 0., 0.
        for z in targets:
            delta = (candidate[:, :, z].astype(float) - base[:, :, z]) / span
            residual = (native[:, :, z].astype(float) - base[:, :, z]) / span
            total_m += float((delta * residual)[supports[z]].sum())
            total_d += float((delta * delta)[supports[z]].sum())
        volume_alpha = float(np.clip(total_m / total_d, 0, 1)) if total_d else 0.
        strategies = {f"fixed_{a:g}": [] for a in FIXED} | {"volume_oracle": [], "slice_oracle": [], "tile_32_oracle": []}
        largest_identity_error = 0.
        for z in targets:
            support, lesion = supports[z], supports[z] & lesion_mask[:, :, z]
            b, y, r = base[:, :, z].astype(float) / span, native[:, :, z].astype(float) / span, candidate[:, :, z].astype(float) / span
            delta, residual = r - b, y - b
            alpha_map = np.zeros_like(b)
            for row in range(0, b.shape[0], 32):
                for col in range(0, b.shape[1], 32):
                    block = np.s_[row:row + 32, col:col + 32]
                    mask = support[block]
                    count = int(mask.sum())
                    if not count:
                        continue
                    d = float((delta[block] ** 2)[mask].sum())
                    m = float((delta[block] * residual[block])[mask].sum())
                    alpha = float(np.clip(m / d, 0, 1)) if d else 0.
                    before = float((residual[block] ** 2)[mask].sum())
                    after = float(((b[block] + alpha * delta[block] - y[block]) ** 2)[mask].sum())
                    formula = 2 * alpha * m - alpha * alpha * d
                    mismatch = abs(before - after - formula)
                    if mismatch > 1e-8 or before - after < -1e-8:
                        raise ValueError("Tile gain identity violated")
                    largest_identity_error = max(largest_identity_error, mismatch)
                    alpha_map[block] = alpha
                    writer.writerow({"patient": case["patient"], "base": base_name, "z": z, "row": row, "col": col, "support_pixels": count, "d": d, "m": m, "alpha": alpha, "base_sse": before, "oracle_sse": after, "oracle_gain": before - after})
            sm, sd = float((delta * residual)[support].sum()), float((delta * delta)[support].sum())
            slice_alpha = float(np.clip(sm / sd, 0, 1)) if sd else 0.
            predictions = {f"fixed_{a:g}": b + a * delta for a in FIXED}
            predictions |= {"volume_oracle": b + volume_alpha * delta, "slice_oracle": b + slice_alpha * delta, "tile_32_oracle": b + alpha_map * delta}
            for name, pred in predictions.items():
                strategies[name].append(plane_error(z, pred, y, support, lesion))
        summaries = {name: {region: metric_rows(rows, region) for region in ("support", "lesion")} for name, rows in strategies.items()}
        limits = {key: min(summaries["fixed_0"]["lesion"][key], summaries["fixed_1"]["lesion"][key]) if summaries["fixed_0"]["lesion"][key] is not None else None for key in ("target_equal_nmse", "pixel_weighted_nmse")}
        guard = {key: value is not None and summaries["tile_32_oracle"]["lesion"][key] <= value for key, value in limits.items()}
        best = min(summaries["fixed_0"]["support"]["target_equal_nmse"], summaries["fixed_1"]["support"]["target_equal_nmse"])
        gain_db = 10 * math.log10(best / summaries["tile_32_oracle"]["support"]["target_equal_nmse"])
        actions.append({"base": base_name, "candidate": "hat", "support_gain_db_vs_better_fixed": gain_db, "lesion_guard": guard,
                        "development_gate_passed": gain_db >= .1 and all(guard.values()), "volume_oracle_alpha": volume_alpha,
                        "largest_gain_identity_error": largest_identity_error, "summaries": summaries, "per_plane_errors": strategies})
    return {"patient": case["patient"], "series_uid": case["header"]["source"]["SeriesInstanceUID"], "targets": targets,
            "observation_indices": list(range(0, native.shape[-1], 4)), "shape_rcz": list(native.shape),
            "normalization_observed_min": prep[1], "normalization_observed_max": prep[2], "actions": actions,
            "task_fidelity_evaluated": False, "independent_confirmation": False}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resource_gate()
    OUT.mkdir(parents=True, exist_ok=False)
    cases, cls, checkpoint = freeze()
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    def deny_cuda(*args, **kwargs):
        raise RuntimeError("CUDA initialization prohibited by development contract")
    torch.cuda._lazy_init = deny_cuda
    model = cls(checkpoint, device="cpu")
    result = {"started_utc": datetime.now(timezone.utc).isoformat(), "complete": False, "run_contract_sha256": sha(OUT / "run_contract.json"), "patients_expected": 3, "patients": [], "failures": [], "gpu_used": False, "publication_claim_confirmed": False}
    write(OUT / "attempt_01.json", result)
    for case in cases:
        started = time.perf_counter()
        try:
            resource_gate()
            native, labels = decode(case)
            prep = prepared(native[:, :, ::4])
            if prep[2] <= prep[1]:
                raise ValueError("Invalid observed-only normalization")
            hat = reconstruct("hat", native, prep, {"hat": model})
            if torch.cuda.is_initialized():
                raise ValueError("Unexpected CUDA initialization")
            output = OUT / (case["patient"] + "_hat.npz")
            np.savez_compressed(output, image_rcz=hat, affine_rcz_ras=np.array(case["header"]["summary"]["affine_rcz_ras"]))
            tile_path = OUT / (case["patient"] + "_tiles.csv")
            with tile_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["patient", "base", "z", "row", "col", "support_pixels", "d", "m", "alpha", "base_sse", "oracle_sse", "oracle_gain"])
                writer.writeheader()
                analysis = analyse(case, native, labels, hat, prep, writer)
            analysis.update(hat_file=output.relative_to(ROOT).as_posix(), hat_sha256=sha(output), tiles_file=tile_path.relative_to(ROOT).as_posix(), tiles_sha256=sha(tile_path), seconds=time.perf_counter() - started)
            result["patients"].append(analysis)
            print(json.dumps({"patient": case["patient"], "seconds": analysis["seconds"], "actions": [{k: a[k] for k in ("base", "support_gain_db_vs_better_fixed", "lesion_guard", "development_gate_passed")} for a in analysis["actions"]]}), flush=True)
            del native, labels, hat
        except Exception as exc:
            result["failures"].append({"patient": case["patient"], "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
            print(json.dumps(result["failures"][-1]), flush=True)
        write(OUT / "attempt_01.json", result)
    result.update(complete=len(result["patients"]) == 3 and not result["failures"], finished_utc=datetime.now(timezone.utc).isoformat(), cuda_initialized=torch.cuda.is_initialized())
    result["primary_fixed_action_development_gate_passed"] = result["complete"] and all(next(a for a in p["actions"] if a["base"] == "pipeline_pchip")["development_gate_passed"] for p in result["patients"])
    write(OUT / "attempt_01.json", result)
    print(json.dumps({"complete": result["complete"], "primary_fixed_action_development_gate_passed": result["primary_fixed_action_development_gate_passed"], "failures": result["failures"]}), flush=True)
    return int(not result["complete"])


if __name__ == "__main__":
    raise SystemExit(main())
