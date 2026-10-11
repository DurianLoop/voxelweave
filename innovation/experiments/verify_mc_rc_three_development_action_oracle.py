"""Independent raw decoding, Hermite PCHIP and vectorized line projections."""
from __future__ import annotations

import csv
import json
import math
import os
import sys
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
from skimage.transform import resize
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_runtime import sha
from remind_native_t2_ixi_pair import MODELS

OUT = ROOT / "experiments/mc_rc_three_development_action_oracle"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def raw_source(case):
    row = case["header"]
    datasets = []
    with zipfile.ZipFile(ROOT / row["transfer"]["file"]) as archive:
        for member in archive.infolist():
            if member.filename.lower().endswith(".dcm") and not member.is_dir():
                with archive.open(member) as stream:
                    datasets.append(pydicom.dcmread(stream))
    iop = np.asarray(datasets[0].ImageOrientationPatient, dtype=float)
    normal = np.cross(iop[:3], iop[3:])
    datasets.sort(key=lambda d: float(np.asarray(d.ImagePositionPatient, dtype=float) @ normal))
    expected = read(ROOT / "literature/source_cache/mc_rc_004_006_native_headers_2026-10-02" / row["header_file"])
    by_member = {r["zip_member"]: r["sop_uid"] for r in expected["records"]}
    if [str(d.SOPInstanceUID) for d in datasets] != [by_member[m] for m in row["summary"]["ordered_zip_members"]]:
        raise ValueError("Independent raw SOP sort differs")
    volume = np.stack([d.pixel_array.astype(np.float32) * float(d.get("RescaleSlope", 1)) + float(d.get("RescaleIntercept", 0)) for d in datasets], axis=2)
    img = nib.load(ROOT / case["label"]["label_file"])
    transform = np.linalg.solve(np.array(row["summary"]["affine_rcz_ras"]), img.affine)
    orientation = nib.orientations.io_orientation(transform)
    label = nib.orientations.apply_orientation(np.asarray(img.dataobj) != 0, orientation)
    if volume.shape != label.shape or not np.isfinite(volume).all():
        raise ValueError("Independent raw volume/label coordinate gate failed")
    return volume, label


def harmonic(a, b):
    out = np.zeros_like(a)
    valid = a * b > 0
    np.divide(2 * a * b, a + b, out=out, where=valid)
    return out


def hermite_plane(anchors, i, t):
    if i < 1 or i + 2 >= len(anchors):
        return (1 - t) * anchors[i] + t * anchors[i + 1]
    previous, left, right, following = (np.asarray(anchors[j], dtype=float) for j in (i - 1, i, i + 1, i + 2))
    m0 = harmonic(left - previous, right - left)
    m1 = harmonic(right - left, following - right)
    return ((2 * t ** 3 - 3 * t ** 2 + 1) * left + (t ** 3 - 2 * t ** 2 + t) * m0
            + (-2 * t ** 3 + 3 * t ** 2) * right + (t ** 3 - t ** 2) * m1)


def block_sum(array):
    h, w = array.shape
    padded = np.pad(array, ((0, -h % 32), (0, -w % 32)))
    return padded.reshape((padded.shape[0] // 32, 32, padded.shape[1] // 32, 32)).transpose(0, 2, 1, 3).sum(axis=(2, 3))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resource_gate()
    result, contract = read(OUT / "attempt_01.json"), read(OUT / "run_contract.json")
    if not result["complete"] or len(result["patients"]) != 3:
        raise ValueError("Cannot verify an incomplete fixed-three development experiment")
    errors, checked = [], []
    for file in contract["files"]:
        if sha(ROOT.parent / file["path"]) != file["sha256"]:
            errors.append("Frozen input/code/weight differs " + file["path"])
    if sha(OUT / "run_contract.json") != result["run_contract_sha256"]:
        errors.append("Development run contract differs")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    def deny_cuda(*args, **kwargs):
        raise RuntimeError("CUDA initialization prohibited")
    torch.cuda._lazy_init = deny_cuda
    cls, checkpoint, expected_weight = MODELS["hat"]
    if sha(checkpoint) != expected_weight:
        raise ValueError("Frozen IXI HAT weight differs")
    model = cls(checkpoint, device="cpu")
    total_tiles, total_targets, direct_forwards = 0, 0, 0
    by_patient = {p["patient"]: p for p in result["patients"]}
    for case in contract["cases"]:
        resource_gate()
        patient = case["patient"]
        saved = by_patient[patient]
        native, label = raw_source(case)
        if sha(ROOT / saved["hat_file"]) != saved["hat_sha256"] or sha(ROOT / saved["tiles_file"]) != saved["tiles_sha256"]:
            errors.append("Saved HAT/tile file hash differs " + patient)
        with np.load(ROOT / saved["hat_file"]) as bundle:
            hat = bundle["image_rcz"]
            if not np.array_equal(bundle["affine_rcz_ras"], case["header"]["summary"]["affine_rcz_ras"]):
                errors.append("Saved HAT affine differs " + patient)
        observation = list(range(0, native.shape[2], 4))
        last = observation[-1]
        targets = [z for z in range(1, last) if z % 4]
        total_targets += len(targets)
        if targets != saved["targets"] or observation != saved["observation_indices"] or not np.array_equal(native[:, :, observation], hat[:, :, observation]) or not np.array_equal(hat[:, :, last + 1:], np.repeat(native[:, :, last, None], native.shape[2] - last - 1, axis=2)):
            errors.append("Observed/target/tail convention differs " + patient)
        observed = native[:, :, observation]
        lo, hi = float(observed.min()), float(observed.max())
        span = hi - lo
        normalized = ((observed - lo) / (span + 1e-8)).astype(np.float32)
        low_planes = [resize(normalized[:, :, i], (256, 256), preserve_range=True, anti_aliasing=True).astype(np.float32) for i in range(len(observation))]
        raw_planes = [observed[:, :, i] for i in range(len(observation))]
        if lo != saved["normalization_observed_min"] or hi != saved["normalization_observed_max"]:
            errors.append("Independent normalization differs " + patient)
        direct_checks = []
        for z in [targets[0], targets[len(targets) // 2], targets[-1]]:
            i, t = z // 4, (z % 4) / 4
            coarse = ((1 - t) * low_planes[i] + t * low_planes[i + 1]).astype(np.float32)
            cond = np.stack([low_planes[i], low_planes[i + 1], coarse, np.full((256, 256), t, np.float32)])
            with torch.no_grad():
                # Direct network call bypasses both predict() and _predict_residual().
                residual = model.model(torch.from_numpy(cond).float()[None]).float().clamp(-1, 1)[0, 0].numpy()
            reproduced = (resize(np.clip(coarse + residual, 0, 1), native.shape[:2], preserve_range=True, anti_aliasing=True) * span + lo).astype(np.float32)
            bitwise = np.array_equal(reproduced, hat[:, :, z])
            direct_checks.append({"z": z, "bitwise_equal": bitwise, "max_abs_difference": float(abs(reproduced - hat[:, :, z]).max())})
            direct_forwards += 1
            if not bitwise:
                errors.append("Direct HAT sample differs " + patient + " " + str(z))
        with (ROOT / saved["tiles_file"]).open(encoding="utf-8", newline="") as f:
            tile_rows = {(r["base"], int(r["z"]), int(r["row"]), int(r["col"])): r for r in csv.DictReader(f)}
        for action in saved["actions"]:
            base_name = action["base"]
            projections = []
            tm, td = 0., 0.
            for z in targets:
                i, t = z // 4, (z % 4) / 4
                if base_name == "raw_pchip":
                    b = hermite_plane(raw_planes, i, t).astype(np.float32)
                else:
                    b = (resize(np.clip(hermite_plane(low_planes, i, t), 0, 1), native.shape[:2], preserve_range=True, anti_aliasing=True) * span + lo).astype(np.float32)
                y, b, h = native[:, :, z].astype(float) / span, b.astype(float) / span, hat[:, :, z].astype(float) / span
                left, right = native[:, :, observation[i]], native[:, :, observation[i + 1]]
                support = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
                lesion = support & label[:, :, z]
                delta, e = h - b, y - b
                d = block_sum(delta * delta * support)
                m = block_sum(delta * e * support)
                before = block_sum(e * e * support)
                counts = block_sum(support.astype(int))
                alpha = np.divide(m, d, out=np.zeros_like(m), where=d != 0).clip(0, 1)
                tm, td = tm + float(m.sum()), td + float(d.sum())
                for rr, cc in np.argwhere(counts > 0):
                    row = tile_rows[(base_name, z, int(rr * 32), int(cc * 32))]
                    total_tiles += 1
                    formula = before[rr, cc] - 2 * alpha[rr, cc] * m[rr, cc] + alpha[rr, cc] ** 2 * d[rr, cc]
                    observed_fields = {"d": d[rr, cc], "m": m[rr, cc], "alpha": alpha[rr, cc], "base_sse": before[rr, cc], "oracle_sse": formula}
                    if any(not np.isclose(float(row[k]), v, rtol=1e-7, atol=1e-8) for k, v in observed_fields.items()) or int(row["support_pixels"]) != counts[rr, cc]:
                        errors.append("Independent tile projection differs " + patient + " " + str((base_name, z, rr, cc)))
                alpha_map = np.repeat(np.repeat(alpha, 32, axis=0), 32, axis=1)[:b.shape[0], :b.shape[1]]
                slice_alpha = float(np.clip(m.sum() / d.sum(), 0, 1)) if d.sum() else 0.
                projections.append((z, b, y, delta, support, lesion, alpha_map, slice_alpha))
            va = float(np.clip(tm / td, 0, 1)) if td else 0.
            if not math.isclose(va, action["volume_oracle_alpha"], rel_tol=1e-7, abs_tol=1e-9):
                errors.append("Independent volume oracle alpha differs " + patient + " " + base_name)
            for name, per_plane in action["per_plane_errors"].items():
                for prior, (z, b, y, delta, support, lesion, alpha_map, slice_alpha) in zip(per_plane, projections):
                    alpha = float(name.removeprefix("fixed_")) if name.startswith("fixed_") else va if name == "volume_oracle" else slice_alpha if name == "slice_oracle" else alpha_map
                    square = (b + alpha * delta - y) ** 2
                    for region, mask in (("support", support), ("lesion", lesion)):
                        if prior["z"] != z or prior[region]["pixels"] != int(mask.sum()) or not np.isclose(prior[region]["sse"], float(square[mask].sum()), rtol=1e-7, atol=1e-8):
                            errors.append("Independent full-plane metric differs " + patient + " " + str((base_name, name, z, region)))
                for region in ("support", "lesion"):
                    usable = [r[region] for r in per_plane if r[region]["pixels"]]
                    mean = float(np.mean([r["sse"] / r["pixels"] for r in usable])) if usable else None
                    n = sum(r["pixels"] for r in usable)
                    weighted = sum(r["sse"] for r in usable) / n if n else None
                    summary = action["summaries"][name][region]
                    if mean != summary["target_equal_nmse"] or weighted != summary["pixel_weighted_nmse"]:
                        errors.append("Saved aggregation differs " + patient + " " + str((base_name, name, region)))
            verified = action["summaries"]
            best = min(verified["fixed_0"]["support"]["target_equal_nmse"], verified["fixed_1"]["support"]["target_equal_nmse"])
            gain = 10 * math.log10(best / verified["tile_32_oracle"]["support"]["target_equal_nmse"])
            guard = {}
            for field in ("target_equal_nmse", "pixel_weighted_nmse"):
                left, right = verified["fixed_0"]["lesion"][field], verified["fixed_1"]["lesion"][field]
                guard[field] = left is not None and verified["tile_32_oracle"]["lesion"][field] <= min(left, right)
            if not math.isclose(gain, action["support_gain_db_vs_better_fixed"], abs_tol=1e-12) or guard != action["lesion_guard"] or (gain >= .1 and all(guard.values())) != action["development_gate_passed"]:
                errors.append("Independent gain/lesion-guard/development gate differs " + patient + " " + base_name)
        checked.append({"patient": patient, "targets": len(targets), "direct_HAT_forward_checks": direct_checks, "independent_confirmation": False})
        del native, label, hat
    if torch.cuda.is_initialized():
        errors.append("Unexpected CUDA initialization")
    primary = all(next(a for a in p["actions"] if a["base"] == "pipeline_pchip")["development_gate_passed"] for p in result["patients"])
    if primary != result["primary_fixed_action_development_gate_passed"]:
        errors.append("Fixed-three development conclusion differs")
    proof = {"created_utc": datetime.now(timezone.utc).isoformat(), "verification_script_sha256": sha(__file__),
             "result_sha256": sha(OUT / "attempt_01.json"), "run_contract_sha256": sha(OUT / "run_contract.json"),
             "scope": "all development targets/tiles/plane metrics independently recomputed; HAT first/middle/last planes directly forward checked, not all HAT planes regenerated",
             "patients": checked, "targets": total_targets, "tiles": total_tiles, "direct_HAT_forward_planes": direct_forwards,
             "full_HAT_output_regenerated": False, "primary_fixed_action_development_gate_passed": primary,
             "errors": errors, "gpu_used": False, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False}
    (OUT / "independent_numerical_and_forward_verification.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: proof[k] for k in ("targets", "tiles", "direct_HAT_forward_planes", "primary_fixed_action_development_gate_passed", "errors")}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
