"""First-case CPU pixel replay of raw and model-pipeline linear interpolation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from skimage.transform import resize

from msd_task01_source import DATA, ROOT, load_exact_pair, official_index, region_masks


SCAN = "BRATS_001"
ARCHIVE_DIR = ROOT / "experiments/msd_task01_analytic_context_control/cases"
OUT = ROOT / "experiments/msd_pipeline_linear_preflight_brats001.json"


def mse(a: np.ndarray, y: np.ndarray, roi: np.ndarray) -> float:
    error = (a - y)[roi].astype(np.float64)
    return float(np.mean(error * error))


def score_scan(scan: str) -> dict:
    for kind in ("imagesTr", "labelsTr"):
        if not (DATA / kind / f"{scan}.nii.gz").is_file():
            raise FileNotFoundError("Pilot refuses to download missing source bytes")
    indexed, entries = official_index()
    t2, label, sources = load_exact_pair(scan, indexed, entries)
    archived = json.loads((ARCHIVE_DIR / f"{scan}.json").read_text(encoding="utf-8"))
    signature = lambda items: [(x["member"], x["compressed_sha256"]) for x in items]
    if signature(sources) != signature(archived["source_files"]):
        raise ValueError("Compressed source hashes differ from archived case")
    phase0 = t2[:, :, ::4]
    lo, hi = float(phase0.min()), float(phase0.max())
    if hi <= lo:
        raise ValueError("Constant phase-0 anchor range")
    output = []
    for row in archived["rows"]:
        z = row["z"]
        left_idx, right_idx = (z // 4) * 4, (z // 4 + 1) * 4
        weight = (z - left_idx) / 4
        left = t2[:, :, left_idx].astype(np.float64)
        right = t2[:, :, right_idx].astype(np.float64)
        raw = (1 - weight) * left + weight * right
        normalized = [(plane.astype(np.float32) - lo) / (hi - lo + 1e-8)
                      for plane in (left, right)]
        resized = [resize(plane.astype(np.float32), (256, 256), preserve_range=True,
                          anti_aliasing=True).astype(np.float32)
                   for plane in normalized]
        coarse = ((1 - weight) * resized[0] + weight * resized[1]).astype(np.float32)
        pipeline = (resize(np.clip(coarse, 0, 1), (240, 240), preserve_range=True,
                           anti_aliasing=True) * (hi - lo) + lo).astype(np.float32)
        support, lesion, local = region_masks(t2, label, z)
        y = t2[:, :, z]
        values = {"z": z, "residue": row["residue"]}
        for name, roi in (("lesion", lesion), ("local_control", local)):
            if int(roi.sum()) != row[name]["pixels"]:
                raise ValueError(f"Frozen ROI differs at z{z} {name}")
            values[f"{name}_pixels"] = int(roi.sum())
            values[f"{name}_raw_linear_mse"] = mse(raw, y, roi)
            values[f"{name}_pipeline_linear_mse"] = mse(pipeline, y, roi)
            if abs(values[f"{name}_raw_linear_mse"] - row[name]["shared"]["b_mse"]) > 1e-6:
                raise ValueError(f"Raw linear replay differs at z{z} {name}")
        values["full_support_pixels"] = int(support.sum())
        values["full_support_raw_linear_mse"] = mse(raw, y, support)
        values["full_support_pipeline_linear_mse"] = mse(pipeline, y, support)
        output.append(values)
    result = {"scan": scan, "complete_targets": len(output),
              "source_sha256": [x["compressed_sha256"] for x in sources],
              "phase0_min_max": [lo, hi], "rows": output,
              "patient_mean": {name: float(np.mean([row[name] for row in output]))
                               for name in ("lesion_raw_linear_mse", "lesion_pipeline_linear_mse",
                                            "local_control_raw_linear_mse",
                                            "local_control_pipeline_linear_mse")},
              "interpretation": "one-case post-result software preflight only"}
    return result


def main() -> None:
    result = score_scan(SCAN)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["patient_mean"], indent=2))


if __name__ == "__main__":
    main()
