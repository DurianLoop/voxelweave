"""Post-result, target-assisted array-only action-space diagnostic on seen case 001."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/vs_seg_001_full_volume_cpu_preflight"
OUT = ROOT / "experiments/vs_seg_001_local_action_oracle"
PLAN = ROOT / "VS_SEG_001_LOCAL_ACTION_ORACLE_PLAN_2026-10-02.md"
BASES = ("raw_pchip", "pipeline_pchip")
SIZES = (16, 32, 64)
FIXED = (0., .25, .5, .75, 1.)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def freeze_inputs():
    preflight_path, proof_path = SOURCE / "attempt_01.json", SOURCE / "independent_saved_output_verification.json"
    previous, proof = read(preflight_path), read(proof_path)
    if not previous["complete"] or previous["patient"] != "VS-SEG-001" or previous["author_split"] != "training" or previous["independent_confirmation"]:
        raise ValueError("Only the previously seen development case is allowed")
    if proof["errors"] or proof["preflight_sha256"] != sha(preflight_path) or proof["independent_confirmation"]:
        raise ValueError("Existing independent saved-array proof differs")
    records = {r["condition"]: r for r in previous["conditions"]}
    paths = {}
    for name in ("native", "hat", *BASES):
        item = records[name]
        path = ROOT / item["reconstruction_file"]
        if sha(path) != item["reconstruction_sha256"]:
            raise ValueError("Existing saved volume differs: " + name)
        paths[name] = path
    mask = ROOT / "experiments/vs_seg_original_mask_cpu_development/VS-SEG-001_masks_attempt_03.npz"
    if sha(mask) != previous["original_label_sha256"]:
        raise ValueError("Existing development label differs")
    entries = [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size}
               for p in (PLAN, Path(__file__), preflight_path, proof_path, mask, *paths.values())]
    return previous, paths, mask, {"patient": "VS-SEG-001", "author_split": "training", "independent_confirmation": False,
        "fixed_actions": [[b, "hat"] for b in BASES], "fixed_patch_sizes": list(SIZES), "primary_development_patch_size": 32,
        "files": entries, "created_utc": datetime.now(timezone.utc).isoformat()}


def optimal_alpha(m, d):
    return min(1., max(0., m / d)) if d > 0 else 0.


def metrics_of_planes(rows, region):
    usable = [r[region] for r in rows if r[region]["pixels"] > 0]
    pixels = sum(r["pixels"] for r in usable)
    return {"nonempty_targets": len(usable), "pixels": pixels,
            "target_equal_nmse": float(np.mean([r["sse"] / r["pixels"] for r in usable])) if usable else None,
            "pixel_weighted_nmse": sum(r["sse"] for r in usable) / pixels if pixels else None}


def error_row(z, prediction, target, support, lesion):
    squared = (prediction - target) ** 2
    return {"z": z, **{name: {"pixels": int(mask.sum()), "sse": float(squared[mask].sum())}
                      for name, mask in (("support", support), ("lesion", lesion))}}


def run(previous, paths, mask_file, tile_writer):
    volumes = {}
    affine = None
    for name, path in paths.items():
        with np.load(path) as bundle:
            volume = bundle["image_rcz"]
            other_affine = bundle["affine_rcz_ras"]
        if volume.shape != (384, 384, 80) or volume.dtype != np.float32:
            raise ValueError("Saved development array shape or dtype differs")
        if affine is None:
            affine = other_affine
        elif not np.array_equal(affine, other_affine):
            raise ValueError("Saved reconstruction coordinate grid differs")
        volumes[name] = volume
    with np.load(mask_file) as bundle:
        label = bundle["original_mask_rcz"].astype(bool)
    native, candidate = volumes["native"], volumes["hat"]
    observed, targets = previous["observation_indices"], previous["internal_targets"]
    if observed != list(range(0, 80, 4)) or targets != [z for z in range(1, 76) if z % 4] or label.shape != native.shape:
        raise ValueError("Saved observation, targets, or label grid differs")
    span = float(native[:, :, observed].max()) - float(native[:, :, observed].min())
    if span != previous["observed_max"] - previous["observed_min"] or span <= 0:
        raise ValueError("Observed-only normalization differs")
    supports = {}
    for z in targets:
        left, right = native[:, :, z-z%4], native[:, :, z-z%4+4]
        supports[z] = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
    source_metrics = {}
    source_rows = {r["condition"]: r for r in previous["conditions"]}
    for name, volume in volumes.items():
        if name != "native":
            if not np.array_equal(volume[:, :, observed], native[:, :, observed]) or not np.array_equal(volume[:, :, 77:], np.repeat(native[:, :, 76, None], 3, axis=2)):
                raise ValueError("Saved observations or common tail changed: " + name)
        rows = [error_row(z, volume[:, :, z].astype(float) / span, native[:, :, z].astype(float) / span,
                          supports[z], supports[z] & label[:, :, z]) for z in targets]
        summary = {r: metrics_of_planes(rows, r) for r in ("support", "lesion")}
        for region in ("support", "lesion"):
            for field in ("target_equal_nmse", "pixel_weighted_nmse"):
                expected = source_rows[name]["image_metrics"][region][field]
                if abs(summary[region][field] - expected) > 1e-9:
                    raise ValueError("Independent array score differs from saved endpoint")
        source_metrics[name] = summary
    actions = []
    for base_name in BASES:
        base = volumes[base_name]
        total_m, total_d = 0., 0.
        for z in targets:
            b = base[:, :, z].astype(float) / span
            delta = candidate[:, :, z].astype(float) / span - b
            residual = native[:, :, z].astype(float) / span - b
            total_m += float((delta * residual)[supports[z]].sum())
            total_d += float((delta * delta)[supports[z]].sum())
        volume_alpha = optimal_alpha(total_m, total_d)
        names = [f"fixed_{a:g}" for a in FIXED] + ["volume_oracle", "slice_oracle"] + [f"tile_{s}_oracle" for s in SIZES] + ["pixel_oracle"]
        by_strategy = {name: [] for name in names}
        alpha_counts = {str(size): {"valid_tiles": 0, "empty_support_tiles": 0, "zero": 0, "one": 0, "interior": 0,
                                  "positive_candidate_gain": 0, "zero_delta_tiles": 0} for size in SIZES}
        largest_identity_residual = 0.
        for z in targets:
            support, lesion = supports[z], supports[z] & label[:, :, z]
            b = base[:, :, z].astype(float) / span
            r = candidate[:, :, z].astype(float) / span
            y = native[:, :, z].astype(float) / span
            delta, residual = r-b, y-b
            predictions = {f"fixed_{a:g}": b+a*delta for a in FIXED}
            predictions["volume_oracle"] = b + volume_alpha * delta
            slice_alpha = optimal_alpha(float((delta * residual)[support].sum()), float((delta * delta)[support].sum()))
            predictions["slice_oracle"] = b + slice_alpha * delta
            pixel_alpha = np.zeros_like(b)
            np.divide(residual, delta, out=pixel_alpha, where=delta != 0)
            predictions["pixel_oracle"] = b + np.clip(pixel_alpha, 0, 1) * delta
            for size in SIZES:
                alpha_map = np.zeros_like(b)
                counts = alpha_counts[str(size)]
                for row in range(0, 384, size):
                    for col in range(0, 384, size):
                        region = np.s_[row:row+size, col:col+size]
                        mask = support[region]
                        count = int(mask.sum())
                        if not count:
                            counts["empty_support_tiles"] += 1
                            continue
                        d = float((delta[region]**2)[mask].sum())
                        m = float((delta[region]*residual[region])[mask].sum())
                        alpha = optimal_alpha(m, d)
                        before = float((residual[region]**2)[mask].sum())
                        after = float(((b[region] + alpha*delta[region] - y[region])**2)[mask].sum())
                        gain, formula = before-after, 2*alpha*m-alpha*alpha*d
                        discrepancy = abs(gain-formula)
                        if discrepancy > 1e-9 or gain < -1e-9:
                            raise ValueError("Local quadratic gain identity or support guard failed")
                        largest_identity_residual = max(largest_identity_residual, discrepancy)
                        alpha_map[region] = alpha
                        counts["valid_tiles"] += 1
                        counts["zero" if alpha == 0 else "one" if alpha == 1 else "interior"] += 1
                        counts["positive_candidate_gain"] += int(2*m-d > 0)
                        counts["zero_delta_tiles"] += int(d == 0)
                        tile_writer.writerow({"action_base": base_name, "size": size, "z": z, "row": row, "col": col,
                            "support_pixels": count, "d": d, "m": m, "alpha": alpha, "base_sse": before, "oracle_sse": after,
                            "oracle_gain": gain, "formula_gain": formula, "candidate_gain": 2*m-d})
                predictions[f"tile_{size}_oracle"] = b + alpha_map * delta
            for name, image in predictions.items():
                by_strategy[name].append(error_row(z, image, y, support, lesion))
        strategies = {name: {"image_metrics": {reg: metrics_of_planes(rows, reg) for reg in ("support", "lesion")},
                             "per_plane_errors": rows, "uses_hidden_target": not name.startswith("fixed_")}
                      for name, rows in by_strategy.items()}
        better_support = min(source_metrics[base_name]["support"]["target_equal_nmse"], source_metrics["hat"]["support"]["target_equal_nmse"])
        local = strategies["tile_32_oracle"]["image_metrics"]
        gain_db = 10 * math.log10(better_support / local["support"]["target_equal_nmse"])
        lesion_limits = {key: min(source_metrics[base_name]["lesion"][key], source_metrics["hat"]["lesion"][key])
                         for key in ("target_equal_nmse", "pixel_weighted_nmse")}
        guard = {key: local["lesion"][key] <= value for key, value in lesion_limits.items()}
        actions.append({"base": base_name, "candidate": "hat", "volume_oracle_alpha": volume_alpha,
            "support_nmse_gain_db_vs_better_fixed_output": gain_db, "primary_patch_size": 32,
            "lesion_endpointwise_best_fixed_limits": lesion_limits, "lesion_guard": guard,
            "single_seen_case_headroom_gate_passed": gain_db >= .1 and all(guard.values()),
            "alpha_counts": alpha_counts, "largest_gain_identity_residual": largest_identity_residual, "strategies": strategies})
    return {"source_metrics": source_metrics, "actions": actions, "targets": targets, "normalization_observed_span": span,
        "only_internal_missing_planes_evaluated": True, "observed_and_tail_conventions_checked": True,
        "strategy_precision": "float64 calculation from saved float32 arrays; no new task inference",
        "task_fidelity_evaluated": False, "patient_inferential_statistics_computed": False, "publication_claim_confirmed": False}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    result = {"attempt": attempt, "created_utc": datetime.now(timezone.utc).isoformat(), "complete": False,
              "patient": "VS-SEG-001", "independent_confirmation": False, "gpu_used": False}
    start = time.perf_counter()
    try:
        previous, paths, mask, contract = freeze_inputs()
        contract_path = OUT / f"run_contract_attempt_{attempt:02d}.json"
        write(contract_path, contract)
        result["run_contract_sha256"] = sha(contract_path)
        tile_path = OUT / f"tile_stats_attempt_{attempt:02d}.csv"
        fields = ("action_base", "size", "z", "row", "col", "support_pixels", "d", "m", "alpha", "base_sse", "oracle_sse", "oracle_gain", "formula_gain", "candidate_gain")
        with tile_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            result["analysis"] = run(previous, paths, mask, writer)
        result.update(complete=True, tile_stats_file=tile_path.relative_to(ROOT).as_posix(), tile_stats_sha256=sha(tile_path))
    except Exception as exc:
        result.update(error=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
    result["elapsed_seconds"] = time.perf_counter()-start
    write(OUT / f"attempt_{attempt:02d}.json", result)
    print(json.dumps({"complete": result["complete"], "error": result.get("error"), "elapsed_seconds": result["elapsed_seconds"],
        "actions": [{k: action[k] for k in ("base", "support_nmse_gain_db_vs_better_fixed_output", "lesion_guard", "single_seen_case_headroom_gate_passed")}
                    for action in result.get("analysis", {}).get("actions", [])]}))
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
