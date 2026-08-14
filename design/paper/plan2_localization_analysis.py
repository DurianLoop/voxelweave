"""EXPLORATORY localization audit of physical inconsistency maps."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan2_outputs" / "localization"
sys.path.insert(0, str(ROOT / "design"))
from rasinet.cross_scale_physical import matches, planes  # noqa: E402
from rasinet.optimization_protocol import case_names, gt_path, prediction_path, profile_sources  # noqa: E402

SCALES = (2, 4, 6)
TARGETS = ("i3net", "hat", "swinir")


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 3 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    return float(stats.spearmanr(a, b).statistic)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("derivation", "confirmation"), default="derivation")
    args = parser.parse_args()
    output = OUT / args.split
    output.mkdir(parents=True, exist_ok=True)
    sources = {s: profile_sources("fastmri", s) for s in SCALES}
    all_cases = sorted(set.intersection(*[set(case_names(sources[s]["i3net"], None)) for s in SCALES]))
    cases = all_cases[:8] if args.split == "derivation" else all_cases[8:]
    records = []
    for case in cases:
        for target in TARGETS:
            imgs = {s: nib.load(str(prediction_path(sources[s][target], None, case))) for s in SCALES}
            pred = {s: imgs[s].get_fdata(dtype=np.float32) for s in SCALES}
            gt = {s: nib.load(str(gt_path(sources[s]["i3net"], None, case))).get_fdata(dtype=np.float32) for s in SCALES}
            for a, b in ((2, 4), (2, 6), (4, 6)):
                for za, zb, distance, _ in matches(planes(imgs[a], a), planes(imgs[b], b)):
                    pa, pb = pred[a][:, :, za], pred[b][:, :, zb]
                    ea, eb = np.abs(pa - gt[a][:, :, za]), np.abs(pb - gt[b][:, :, zb])
                    inc = np.abs(pa - pb)
                    threshold = 0.01 * max(float(np.max(np.abs(pa))), float(np.max(np.abs(pb))), 1e-6)
                    mask = (np.abs(pa) > threshold) | (np.abs(pb) > threshold)
                    avg_error = 0.5 * (ea + eb)
                    records.append({
                        "case": case, "target_model": target, "pair": f"{a}-{b}", "za": za, "zb": zb,
                        "plane_distance_mm": distance, "pixel_spearman": corr(inc[mask], avg_error[mask]),
                        "mean_inconsistency": float(np.mean(inc[mask])), "mean_error": float(np.mean(avg_error[mask])),
                        "top10_error_capture": float(np.mean(avg_error[mask][inc[mask] >= np.quantile(inc[mask], 0.9)]) / max(np.mean(avg_error[mask]), 1e-12)),
                    })
        print(f"completed {case}", flush=True)
    frame = pd.DataFrame(records)
    frame.to_csv(output / "per_plane.csv", index=False)
    case_level = frame.groupby(["case", "target_model", "pair"], as_index=False).agg(
        inconsistency=("mean_inconsistency", "median"), error=("mean_error", "median"),
        pixel_spearman=("pixel_spearman", "median"), top10_error_capture=("top10_error_capture", "median")
    )
    case_level.to_csv(output / "case_pair_summary.csv", index=False)
    summary = {
        "split": args.split, "cases": len(cases), "planes": len(frame),
        "median_pixel_spearman": float(frame.pixel_spearman.median()),
        "pixel_spearman_iqr": [float(frame.pixel_spearman.quantile(.25)), float(frame.pixel_spearman.quantile(.75))],
        "median_top10_error_capture_ratio": float(frame.top10_error_capture.median()),
        "slice_level_spearman": corr(frame.mean_inconsistency.to_numpy(), frame.mean_error.to_numpy()),
        "case_pair_level_spearman": corr(case_level.inconsistency.to_numpy(), case_level.error.to_numpy()),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
