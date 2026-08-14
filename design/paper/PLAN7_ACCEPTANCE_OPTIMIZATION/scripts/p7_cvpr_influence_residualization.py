"""P7-CV-E04: target-free shared-influence residualization.

The correction is frozen before outcome inspection from the paired covariance model:
if the observable independent-error fraction is approximately (1-I), disagreement
magnitude scales as sqrt(1-I), hence corrected disagreement is d/sqrt(1-I).
No exponent, weight, or cohort-specific transform is fitted.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy import stats


HERE = Path(__file__).resolve()
P7 = HERE.parents[1]
PAPER = P7.parent
CV = PAPER / "CVPR" / "CVPR_UPGRADE"
RAW = CV / "outputs" / "plan6_neural_shared_influence_confirm3_per_case_config.csv"
ANCHOR = CV / "outputs" / "plan6_anchor_cv_explanation_per_case.csv"
PC = CV / "outputs" / "orthogonal_two_component_per_case.csv"
OUT = P7 / "outputs"
BOOTSTRAPS = 5000
SEED = 20260813


def rho(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return np.nan
    return float(stats.spearmanr(a[ok], b[ok]).statistic)


def partial_rho(x, y, controls):
    frame = pd.DataFrame({"x": x, "y": y}).join(pd.DataFrame(controls).reset_index(drop=True))
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()
    if len(frame) < 8:
        return np.nan
    ranked = frame.rank(method="average")
    design = np.column_stack([np.ones(len(ranked)), ranked.iloc[:, 2:].to_numpy(float)])
    rx = ranked.x.to_numpy() - design @ np.linalg.lstsq(design, ranked.x.to_numpy(), rcond=None)[0]
    ry = ranked.y.to_numpy() - design @ np.linalg.lstsq(design, ranked.y.to_numpy(), rcond=None)[0]
    return float(np.corrcoef(rx, ry)[0, 1]) if np.std(rx) and np.std(ry) else np.nan


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(RAW)
    raw = raw[raw.context.ne("(-2, 2)")].copy()  # self-pair has d=0 and I=1 by construction
    raw["influence_clipped"] = raw.neural_influence_cosine.clip(0.0, 0.95)
    raw["corrected_disagreement"] = raw.disagreement_mae / np.sqrt(1.0 - raw.influence_clipped)

    case = raw.groupby(["dataset", "case", "patient_cluster", "model"], as_index=False).agg(
        residualized=("corrected_disagreement", "median"),
        raw_disagreement=("disagreement_mae", "median"),
        x4_error=("paired_error_mae", "median"),
        mean_influence=("neural_influence_cosine", "mean"),
    )
    anchor = pd.read_csv(ANCHOR).groupby(["dataset", "case", "patient_cluster", "model"], as_index=False).agg(
        adjacent_mae=("adjacent_mae", "first"), anchor_cv=("anchor_cv", "first")
    )
    pc = pd.read_csv(PC).groupby(["dataset", "case", "model"], as_index=False).agg(
        output_pc=("score", "first"), split=("split", "first")
    )
    case = case.merge(anchor, on=["dataset", "case", "patient_cluster", "model"]).merge(pc, on=["dataset", "case", "model"])
    case["partition"] = np.where(
        (case.dataset == "fastmri") & (case.split == "development"), "development",
        np.where((case.dataset == "fastmri") & (case.split == "confirmation"), "confirmation", "transfer"),
    )
    case.to_csv(OUT / "p7_cvpr_influence_residualization_per_case.csv", index=False)

    methods = ["residualized", "raw_disagreement", "adjacent_mae", "output_pc", "anchor_cv"]
    rows = []; deltas = []; rng = np.random.default_rng(SEED)
    for (dataset, partition, model), group in case.groupby(["dataset", "partition", "model"], sort=False):
        clusters = group.patient_cluster.astype(str).unique()
        by = {c: group[group.patient_cluster.astype(str).eq(c)] for c in clusters}
        observed = {m: rho(group[m], group.x4_error) for m in methods}
        boots = {m: [] for m in methods}
        for _ in range(BOOTSTRAPS):
            b = pd.concat([by[c] for c in rng.choice(clusters, len(clusters), replace=True)], ignore_index=True)
            for m in methods:
                boots[m].append(rho(b[m], b.x4_error))
        for m in methods:
            a = np.asarray(boots[m], float)
            rows.append({
                "dataset": dataset, "partition": partition, "model": model,
                "cases": int(group.case.nunique()), "patient_clusters": int(len(clusters)), "method": m,
                "spearman_x4_error": observed[m], "cluster_ci_low": float(np.nanquantile(a, .025)),
                "cluster_ci_high": float(np.nanquantile(a, .975)),
                "partial_rho_beyond_adjacent": partial_rho(group[m], group.x4_error, group[["adjacent_mae"]]),
            })
        for comparator in methods[1:]:
            a = np.asarray(boots["residualized"], float) - np.asarray(boots[comparator], float)
            deltas.append({
                "dataset": dataset, "partition": partition, "model": model, "comparator": comparator,
                "rho_delta_residualized_minus_comparator": observed["residualized"] - observed[comparator],
                "cluster_ci_low": float(np.nanquantile(a, .025)), "cluster_ci_high": float(np.nanquantile(a, .975)),
            })
    summary = pd.DataFrame(rows); delta = pd.DataFrame(deltas)
    summary.to_csv(OUT / "p7_cvpr_influence_residualization_summary.csv", index=False)
    delta.to_csv(OUT / "p7_cvpr_influence_residualization_deltas.csv", index=False)

    locked = delta[delta.partition.ne("development")]
    beats_raw = locked[locked.comparator.eq("raw_disagreement")]
    beats_trivial = locked[locked.comparator.isin(["adjacent_mae", "output_pc"])]
    passed = bool((beats_raw.rho_delta_residualized_minus_comparator > 0).all() and
                  (beats_trivial.groupby(["dataset", "model"]).rho_delta_residualized_minus_comparator.max() > 0).all())
    payload = {
        "experiment": "P7-CV-E04", "status": "COMPLETE", "method_id": "INFLUENCE_RESIDUAL_V1",
        "frozen_formula": "median_context[d / sqrt(1 - clip(I, 0, 0.95))]",
        "fit_parameters": 0, "dense_target_at_score_time": False,
        "gate": "positive locked improvement over raw disagreement and over at least one of adjacent MAE/output PC in every dataset-model stratum",
        "gate_passed": passed,
        "outputs": ["p7_cvpr_influence_residualization_per_case.csv", "p7_cvpr_influence_residualization_summary.csv", "p7_cvpr_influence_residualization_deltas.csv"],
    }
    (OUT / "p7_cvpr_influence_residualization.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2)); print(summary.to_string(index=False)); print(delta.to_string(index=False))


if __name__ == "__main__":
    main()
