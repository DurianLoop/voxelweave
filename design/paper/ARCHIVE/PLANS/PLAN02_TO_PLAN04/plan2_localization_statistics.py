"""Clustered uncertainty and failure-boundary analysis for held-out localization."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "plan2_outputs" / "localization"


def spearman(a, b) -> float:
    return float(stats.spearmanr(a, b).statistic)


def analyze(label: str, directory: Path, samples: int = 5000) -> dict[str, object]:
    frame = pd.read_csv(directory / "per_plane.csv")
    case = pd.read_csv(directory / "case_pair_summary.csv")
    cases = np.asarray(sorted(frame.case.unique()))
    rng = np.random.default_rng(20260816)
    estimates = []
    for _ in range(samples):
        picked = rng.choice(cases, len(cases), replace=True)
        plane_parts, case_parts = [], []
        for draw, name in enumerate(picked):
            p = frame[frame.case.eq(name)].copy(); p["case"] = f"draw_{draw}"; plane_parts.append(p)
            c = case[case.case.eq(name)].copy(); c["case"] = f"draw_{draw}"; case_parts.append(c)
        pf, cf = pd.concat(plane_parts), pd.concat(case_parts)
        estimates.append({
            "median_pixel_spearman": float(pf.pixel_spearman.median()),
            "slice_spearman": spearman(pf.mean_inconsistency, pf.mean_error),
            "case_pair_spearman": spearman(cf.inconsistency, cf.error),
            "top10_capture": float(pf.top10_error_capture.median()),
        })
    boot = pd.DataFrame(estimates)
    boot.to_csv(directory / "cluster_bootstrap.csv", index=False)
    boundaries = frame.copy()
    boundaries["error_pct"] = boundaries.groupby(["target_model", "pair"]).mean_error.rank(pct=True)
    boundaries["inconsistency_pct"] = boundaries.groupby(["target_model", "pair"]).mean_inconsistency.rank(pct=True)
    stable_wrong = boundaries[(boundaries.error_pct >= .75) & (boundaries.inconsistency_pct <= .25)].copy()
    stable_wrong.to_csv(directory / "consistent_but_wrong_planes.csv", index=False)
    summary = {
        "dataset_split": label,
        "cluster_bootstrap_samples": samples,
        "median_pixel_spearman_95ci": [float(boot.median_pixel_spearman.quantile(.025)), float(boot.median_pixel_spearman.quantile(.975))],
        "slice_spearman_95ci": [float(boot.slice_spearman.quantile(.025)), float(boot.slice_spearman.quantile(.975))],
        "case_pair_spearman_95ci": [float(boot.case_pair_spearman.quantile(.025)), float(boot.case_pair_spearman.quantile(.975))],
        "top10_capture_95ci": [float(boot.top10_capture.quantile(.025)), float(boot.top10_capture.quantile(.975))],
        "consistent_but_wrong_planes": len(stable_wrong),
        "total_planes": len(frame),
    }
    (directory / "statistical_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main(samples: int = 5000) -> None:
    summaries = [
        analyze("fastmri-heldout16", OUT / "confirmation", samples),
        analyze("ningxia-oof22", OUT / "ningxia_confirmation", samples),
    ]
    (OUT / "cross_dataset_statistical_summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
