"""Independent blocked least-squares/interval projection of saved development arrays."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/vs_seg_001_local_action_oracle"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def blocks(array, size):
    n = array.shape[0] // size
    return array.reshape(n, size, n, size).transpose(0, 2, 1, 3).reshape(n*n, size*size)


def unblocks(array, size):
    n = math.isqrt(array.shape[0])
    return array.reshape(n, n, size, size).transpose(0, 2, 1, 3).reshape(n*size, n*size)


def projection(m, d):
    raw = np.zeros_like(np.asarray(m, dtype=float))
    np.divide(m, d, out=raw, where=np.asarray(d) > 0)
    return np.clip(raw, 0., 1.)


def main():
    errors = []
    result_path = OUT / "attempt_01.json"
    result = read(result_path)
    contract_path = OUT / "run_contract_attempt_01.json"
    contract = read(contract_path)
    if not result["complete"] or result["run_contract_sha256"] != sha(contract_path) or result["independent_confirmation"]:
        raise ValueError("Development result is incomplete or contract differs")
    for item in contract["files"]:
        path = ROOT / item["path"]
        if path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
            errors.append("Frozen development input differs: " + item["path"])
    if sha(ROOT / result["tile_stats_file"]) != result["tile_stats_sha256"]:
        errors.append("Saved tile table differs")
    if errors:
        raise ValueError("; ".join(errors))
    previous = read(ROOT / "experiments/vs_seg_001_full_volume_cpu_preflight/attempt_01.json")
    sources = {r["condition"]: r for r in previous["conditions"]}
    arrays = {}
    for name in ("native", "hat", "raw_pchip", "pipeline_pchip"):
        path = ROOT / sources[name]["reconstruction_file"]
        with np.load(path) as bundle:
            arrays[name] = bundle["image_rcz"]
    with np.load(ROOT / "experiments/vs_seg_original_mask_cpu_development/VS-SEG-001_masks_attempt_03.npz") as bundle:
        label = bundle["original_mask_rcz"].astype(bool)
    with (ROOT / result["tile_stats_file"]).open(newline="", encoding="utf-8") as stream:
        csv_rows = {}
        for row in csv.DictReader(stream):
            key = (row["action_base"], int(row["size"]), int(row["z"]), int(row["row"]), int(row["col"]))
            if key in csv_rows:
                raise ValueError("Duplicate saved tile row")
            csv_rows[key] = row
    native = arrays["native"]
    anchors = np.arange(0, native.shape[-1], 4)
    span = float(np.ptp(native[:, :, anchors]))
    indices = [i for i in range(native.shape[-1]) if i % 4 and i < anchors[-1]]
    if indices != result["analysis"]["targets"] or span != result["analysis"]["normalization_observed_span"]:
        errors.append("Target indices or normalization differ")
    supports = {}
    for z in indices:
        bracket = native[:, :, [z - z % 4, z - z % 4 + 4]]
        thresholds = np.maximum(np.max(abs(bracket), axis=(0, 1)), 1e-6) * .01
        supports[z] = np.any(abs(bracket) > thresholds[None, None, :], axis=2)
    checked_tile_keys = set()
    checked_endpoints = 0
    max_tile_difference, max_summary_difference = 0., 0.
    for action in result["analysis"]["actions"]:
        base_name = action["base"]
        measurements = {strategy: {"support": [], "lesion": []} for strategy in action["strategies"]}
        whole_m, whole_d = 0., 0.
        for z in indices:
            diff = (arrays["hat"][:, :, z].astype(float) - arrays[base_name][:, :, z].astype(float)) / span
            residual = (native[:, :, z].astype(float) - arrays[base_name][:, :, z].astype(float)) / span
            whole_m += np.dot(diff[supports[z]], residual[supports[z]])
            whole_d += np.dot(diff[supports[z]], diff[supports[z]])
        whole_alpha = float(projection(whole_m, whole_d))
        if abs(whole_alpha - action["volume_oracle_alpha"]) > 1e-10:
            errors.append("Whole-volume projection coefficient differs")
        for z in indices:
            b = arrays[base_name][:, :, z].astype(float) / span
            r = arrays["hat"][:, :, z].astype(float) / span
            y = native[:, :, z].astype(float) / span
            diff, residual = r-b, y-b
            support = supports[z]
            scalar = float(projection(np.dot(diff[support], residual[support]), np.dot(diff[support], diff[support])))
            images = {f"fixed_{a:g}": (1-a)*b+a*r for a in (0., .25, .5, .75, 1.)}
            images["volume_oracle"] = (1-whole_alpha)*b+whole_alpha*r
            images["slice_oracle"] = (1-scalar)*b+scalar*r
            images["pixel_oracle"] = np.minimum(np.maximum(y, np.minimum(b, r)), np.maximum(b, r))
            for size in (16, 32, 64):
                db, eb, sb = blocks(diff, size), blocks(residual, size), blocks(support, size)
                d = np.einsum("ij,ij,ij->i", db, db, sb)
                m = np.einsum("ij,ij,ij->i", db, eb, sb)
                alpha = projection(m, d)
                image = b + unblocks(alpha[:, None]*db, size)
                images[f"tile_{size}_oracle"] = image
                before = np.einsum("ij,ij,ij->i", eb, eb, sb)
                after = np.einsum("ij,ij,ij->i", eb-alpha[:, None]*db, eb-alpha[:, None]*db, sb)
                gradient = 2*(alpha*d-m)
                interior = (alpha > 0) & (alpha < 1)
                if np.any(abs(gradient[interior]) > 1e-8) or np.any(gradient[alpha == 0] < -1e-8) or np.any(gradient[alpha == 1] > 1e-8):
                    errors.append("Tile boundary/interior least-squares optimality failed")
                if np.any(after > before+1e-8) or np.any(after > (before-2*m+d)+1e-8):
                    errors.append("Tile oracle is worse than a fixed endpoint on its own objective")
                n = 384 // size
                counts = sb.sum(axis=1)
                for index in np.flatnonzero(counts):
                    row, col = index // n * size, index % n * size
                    key = (base_name, size, z, int(row), int(col))
                    saved = csv_rows[key]
                    checked_tile_keys.add(key)
                    if int(saved["support_pixels"]) != counts[index]:
                        errors.append("Tile support count differs")
                    computed = {"d": d[index], "m": m[index], "alpha": alpha[index], "base_sse": before[index],
                                "oracle_sse": after[index], "oracle_gain": before[index]-after[index],
                                "formula_gain": 2*alpha[index]*m[index]-alpha[index]**2*d[index], "candidate_gain": 2*m[index]-d[index]}
                    largest = max(abs(float(saved[name])-value) for name, value in computed.items())
                    max_tile_difference = max(max_tile_difference, largest)
                    if largest > 1e-8:
                        errors.append("Independently blocked tile differs")
            for strategy, image in images.items():
                squared = (image-y)**2
                for region, mask in (("support", support), ("lesion", support & label[:, :, z])):
                    measurements[strategy][region].append((int(mask.sum()), float(squared[mask].sum())))
        summaries = {}
        for strategy, regions in measurements.items():
            summaries[strategy] = {}
            for region, rows in regions.items():
                nonempty = [(n, total) for n, total in rows if n]
                count = sum(n for n, _ in rows)
                summary = {"target_equal_nmse": sum(total/n for n, total in nonempty)/len(nonempty),
                           "pixel_weighted_nmse": sum(total for _, total in rows)/count}
                summaries[strategy][region] = summary
                saved = action["strategies"][strategy]["image_metrics"][region]
                if saved["pixels"] != count or saved["nonempty_targets"] != len(nonempty):
                    errors.append("Strategy domain count differs")
                for name, value in summary.items():
                    discrepancy = abs(saved[name]-value)
                    max_summary_difference = max(max_summary_difference, discrepancy)
                    if discrepancy > 1e-10:
                        errors.append("Strategy endpoint differs")
                    checked_endpoints += 1
        primary = summaries["tile_32_oracle"]
        better = min(summaries["fixed_0"]["support"]["target_equal_nmse"], summaries["fixed_1"]["support"]["target_equal_nmse"])
        gain_db = 10*math.log10(better/primary["support"]["target_equal_nmse"])
        guards = {name: primary["lesion"][name] <= min(summaries["fixed_0"]["lesion"][name], summaries["fixed_1"]["lesion"][name])
                  for name in ("target_equal_nmse", "pixel_weighted_nmse")}
        if abs(gain_db-action["support_nmse_gain_db_vs_better_fixed_output"]) > 1e-8 or guards != action["lesion_guard"] or (gain_db >= .1 and all(guards.values())) != action["single_seen_case_headroom_gate_passed"]:
            errors.append("Primary development gate differs")
    if checked_tile_keys != set(csv_rows):
        errors.append("Tile coverage/uniqueness differs")
    proof = {"script_sha256": sha(Path(__file__)), "result_sha256": sha(result_path), "run_contract_sha256": sha(contract_path),
             "complete": not errors, "errors": errors, "checked_tiles": len(checked_tile_keys), "checked_strategy_endpoints": checked_endpoints,
             "max_tile_float64_difference": max_tile_difference, "max_summary_difference": max_summary_difference,
             "independent_method": "Batched tile least-squares and boundary derivatives; pixel interval projection; separately aggregated domain SSE",
             "new_model_inference": False, "gpu_used": False, "scientific_independent_confirmation": False}
    (OUT / "independent_verification.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(proof, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
