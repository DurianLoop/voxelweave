"""C5-E008: linear-interpolation family check for acquired-anchor bipartition."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve()
UP = HERE.parents[1]
PAPER = HERE.parents[3]
OUT = UP / "outputs"
RNG = np.random.default_rng(20260813)


def rho(a, b):
    if len(a) < 4 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(stats.spearmanr(a, b).statistic)


def cluster_ci(frame, y, reps=5000):
    frame = frame.reset_index(drop=True)
    clusters = frame.patient_cluster.unique()
    vals = []
    groups = [frame.index[frame.patient_cluster.eq(cluster)].to_numpy() for cluster in clusters]
    score = frame.score.to_numpy()
    endpoint = frame[y].to_numpy()
    for _ in range(reps):
        chosen = RNG.integers(0, len(groups), len(groups))
        indices = np.concatenate([groups[j] for j in chosen])
        value = rho(score[indices], endpoint[indices])
        if np.isfinite(value):
            vals.append(value)
    return [float(x) for x in np.quantile(vals, [0.025, 0.975])]


def interpolate(volume, left, right, z):
    w = (z - left) / (right - left)
    return (1.0 - w) * volume[:, :, left] + w * volume[:, :, right]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    saved = OUT / "analytical_acquired_anchor_bipartition_per_case.csv"
    if args.summary_only:
        frame = pd.read_csv(saved)
        write_summary(frame)
        return
    manifest = pd.read_csv(UP / "DATA_MANIFEST.csv")
    manifest = manifest[(manifest.factor.eq(4)) & manifest.architecture.isin(["hat", "swinir"])]
    rows = []
    for record in manifest.itertuples():
        gt = nib.load(record.ground_truth_file).get_fdata(dtype=np.float32)
        base = nib.load(record.source_file).get_fdata(dtype=np.float32)
        scores, errors = [], []
        depth = min(gt.shape[2], base.shape[2])
        for z in range(2, depth - 2, 4):
            left_a = (z // 8) * 8
            right_a = left_a + 8
            left_b = ((z - 4) // 8) * 8 + 4
            right_b = left_b + 8
            if min(left_a, left_b) < 0 or max(right_a, right_b) >= depth:
                continue
            pred_a = interpolate(gt, left_a, right_a, z)
            pred_b = interpolate(gt, left_b, right_b, z)
            base_z = base[:, :, z]
            threshold = 0.01 * max(float(np.max(np.abs(base_z))), 1e-6)
            mask = np.abs(base_z) > threshold
            if not np.any(mask):
                continue
            scores.append(float(np.abs(pred_a - pred_b)[mask].mean()))
            errors.append(float(np.abs(base_z - gt[:, :, z])[mask].mean()))
        if scores:
            rows.append({
                "dataset": record.dataset,
                "case": record.case_id,
                "patient_cluster": record.patient_cluster,
                "model": record.architecture,
                "planes": len(scores),
                "score": float(np.median(scores)),
                "x4_error": float(np.median(errors)),
            })
        print("C5-E008", record.dataset, record.architecture, record.case_id, flush=True)

    frame = pd.DataFrame(rows)
    benefit = pd.read_csv(PAPER / "plan4_outputs" / "adaptive_acquisition_per_case.csv")
    benefit = benefit.rename(columns={"target_model": "model"})[
        ["dataset", "case", "model", "benefit_x4_to_x2"]
    ]
    frame = frame.merge(benefit, on=["dataset", "case", "model"], how="left")
    frame.to_csv(saved, index=False)
    write_summary(frame)


def write_summary(frame):

    summary = []
    for dataset, group in frame.groupby("dataset"):
        record = {
            "dataset": dataset,
            "cases": int(group.case.nunique()),
            "patient_clusters": int(group.patient_cluster.nunique()),
            "models": int(group.model.nunique()),
            "planes": int(group.planes.sum()),
            "rho_score_vs_x4_error": rho(group.score, group.x4_error),
            "rho_score_vs_x4_error_cluster_95ci": cluster_ci(group, "x4_error"),
        }
        available = group[group.benefit_x4_to_x2.notna()]
        if len(available) == len(group):
            record["rho_score_vs_benefit"] = rho(available.score, available.benefit_x4_to_x2)
            record["rho_score_vs_benefit_cluster_95ci"] = cluster_ci(available, "benefit_x4_to_x2")
        else:
            record["rho_score_vs_benefit"] = "NOT RUN: no stored IXI x2 benefit"
        summary.append(record)
    payload = {
        "experiment": "C5-E008",
        "status": "EXPLORATORY / registered before execution",
        "estimator": "linear interpolation on two already-acquired disjoint x8 sub-lattices",
        "rows": summary,
    }
    (OUT / "analytical_acquired_anchor_bipartition_summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
