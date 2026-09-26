"""P11-E01: same-model x4->x2 retrospective benefit prediction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


HERE = Path(__file__).resolve()
P11 = HERE.parents[1]
PAPER = P11.parent
ROOT = PAPER.parents[1]
OUT = P11 / "outputs"
SEED = 20260827
BUDGETS = (0.10, 0.20, 0.30, 0.50)

FIDELITY = {
    "development": ROOT / "design/rasinet/outputs/nested_optimization/common_fidelity_per_case_development.csv",
    "ningxia": ROOT / "design/rasinet/outputs/nested_optimization/common_fidelity_per_case_ningxia.csv",
}
PAIR_FEATURES = {
    "development": ROOT / "design/rasinet/outputs/nested_optimization/pair_features_per_case_development.csv",
    "ningxia": ROOT / "design/rasinet/outputs/nested_optimization/pair_features_per_case_ningxia.csv",
}
ANCHOR = ROOT / "design/paper/CVPR/archive/CVPR_UPGRADE/outputs/plan6_anchor_cv_explanation_per_case.csv"
REGISTRY = ROOT / "design/rasinet/model_bank_registry.csv"
PAIR_SCORE = "intensity_mean__target_0.01"


def rho(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    keep = np.isfinite(a) & np.isfinite(b)
    if keep.sum() < 4 or np.std(a[keep]) == 0 or np.std(b[keep]) == 0:
        return float("nan")
    return float(stats.spearmanr(a[keep], b[keep]).statistic)


def tau(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    keep = np.isfinite(a) & np.isfinite(b)
    if keep.sum() < 4:
        return float("nan")
    return float(stats.kendalltau(a[keep], b[keep]).statistic)


def selected(values, scores, budget: float) -> float:
    values = np.asarray(values, dtype=float)
    scores = np.asarray(scores, dtype=float)
    k = max(1, int(np.ceil(len(values) * budget)))
    return float(np.mean(values[np.argsort(scores)[::-1][:k]]))


def bootstrap_group(g: pd.DataFrame, score: str, samples: int, rng: np.random.Generator) -> dict:
    cluster_values = g.patient_cluster.astype(str).to_numpy()
    clusters = np.unique(cluster_values)
    by = [np.flatnonzero(cluster_values == cluster) for cluster in clusters]
    score_values = g[score].to_numpy(float)
    benefits = g.benefit.to_numpy(float)
    observed = rho(score_values, benefits)
    reps = []
    for _ in range(samples):
        draw = rng.integers(0, len(clusters), len(clusters))
        idx = np.concatenate([by[i] for i in draw])
        value = rho(score_values[idx], benefits[idx])
        if np.isfinite(value):
            reps.append(value)
    lo, hi = np.percentile(reps, [2.5, 97.5]) if reps else (np.nan, np.nan)
    return {"spearman": observed, "ci_low": float(lo), "ci_high": float(hi), "bootstrap_valid": len(reps)}


def budget_rows(g: pd.DataFrame, score: str, samples: int, rng: np.random.Generator) -> list[dict]:
    cluster_values = g.patient_cluster.astype(str).to_numpy()
    clusters = np.unique(cluster_values)
    by = [np.flatnonzero(cluster_values == cluster) for cluster in clusters]
    benefits = g.benefit.to_numpy(float)
    score_values = g[score].to_numpy(float)
    rows = []
    for budget in BUDGETS:
        point = selected(benefits, score_values, budget)
        random_expected = float(benefits.mean())
        oracle = selected(benefits, benefits, budget)
        reps = []
        for _ in range(samples):
            draw = rng.integers(0, len(clusters), len(clusters))
            idx = np.concatenate([by[i] for i in draw])
            reps.append(selected(benefits[idx], score_values[idx], budget) - float(benefits[idx].mean()))
        denom = oracle - random_expected
        rows.append(
            {
                "budget": budget,
                "selected_benefit": point,
                "random_expected": random_expected,
                "gain_above_random": point - random_expected,
                "gain_ci_low": float(np.percentile(reps, 2.5)),
                "gain_ci_high": float(np.percentile(reps, 97.5)),
                "oracle_benefit": oracle,
                "oracle_normalized_gain": (point - random_expected) / denom if denom > 0 else np.nan,
            }
        )
    return rows


def load_analysis_table(datasets: list[str], models: list[str] | None, max_cases: int | None) -> pd.DataFrame:
    fidelity = pd.concat([pd.read_csv(path) for path in FIDELITY.values()], ignore_index=True)
    fidelity = fidelity[fidelity.dataset.isin(datasets) & fidelity.scale.isin([2, 4])].copy()
    if models:
        fidelity = fidelity[fidelity.model.isin(models)]
    x2 = fidelity[fidelity.scale.eq(2)].rename(columns={"mae": "mae_x2"})
    x4 = fidelity[fidelity.scale.eq(4)].rename(columns={"mae": "mae_x4"})
    keys = ["dataset", "fold", "case", "model", "support"]
    table = x4[keys + ["mae_x4"]].merge(x2[keys + ["mae_x2"]], on=keys, how="inner", validate="one_to_one")
    table["benefit"] = table.mae_x4 - table.mae_x2

    anchor = pd.read_csv(ANCHOR)
    anchor = (
        anchor[anchor.dataset.isin(datasets)]
        .groupby(["dataset", "case", "patient_cluster"], as_index=False)
        .agg(anchor_cv=("anchor_cv", "first"), adjacent_mae=("adjacent_mae", "first"))
    )
    table = table.merge(anchor, on=["dataset", "case"], how="left", validate="many_to_one")

    registry = pd.read_csv(REGISTRY)
    bank = set(registry.loc[registry.candidate_bank_member.astype(bool), "model"].astype(str))
    pair = pd.concat([pd.read_csv(path) for path in PAIR_FEATURES.values()], ignore_index=True)
    pair = pair[pair.dataset.isin(datasets) & pair.scale.eq(4) & pair.member.isin(bank)].copy()
    pair_score = (
        pair.groupby(["dataset", "fold", "case", "target_model"], as_index=False)[PAIR_SCORE]
        .median()
        .rename(columns={"target_model": "model", PAIR_SCORE: "bank_median_disagreement"})
    )
    table = table.merge(pair_score, on=["dataset", "fold", "case", "model"], how="left", validate="one_to_one")
    if max_cases:
        keep = []
        for dataset, g in table.groupby("dataset"):
            keep.extend(sorted(g.case.unique())[:max_cases])
        table = table[table.case.isin(keep)].copy()
    table["eligible_benefit"] = np.isfinite(table[["mae_x2", "mae_x4", "benefit"]]).all(axis=1)
    return table


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", choices=("fastmri", "ningxia"), default=["fastmri", "ningxia"])
    parser.add_argument("--models", nargs="+", default=None)
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--suffix", default="")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.suffix}" if args.suffix else ""
    table = load_analysis_table(args.datasets, args.models, args.max_cases)
    table.to_csv(OUT / f"p11_same_model_benefit_per_case{suffix}.csv", index=False)
    scores = ("anchor_cv", "adjacent_mae", "bank_median_disagreement")
    corr_rows, allocation_rows = [], []
    rng = np.random.default_rng(args.seed)
    eligible = table[table.eligible_benefit].copy()
    for (dataset, model), base in eligible.groupby(["dataset", "model"]):
        for score in scores:
            g = base[np.isfinite(base[score])].copy()
            if len(g) < 4:
                continue
            boot = bootstrap_group(g, score, args.bootstrap, rng)
            corr_rows.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "cases": int(g.case.nunique()),
                    "patient_clusters": int(g.patient_cluster.nunique()),
                    "score": score,
                    "kendall": tau(g[score], g.benefit),
                    **boot,
                }
            )
            for row in budget_rows(g, score, args.bootstrap, rng):
                allocation_rows.append({"dataset": dataset, "model": model, "score": score, **row})
    corr = pd.DataFrame(corr_rows)
    allocations = pd.DataFrame(allocation_rows)
    corr.to_csv(OUT / f"p11_same_model_benefit_correlations{suffix}.csv", index=False)
    allocations.to_csv(OUT / f"p11_same_model_benefit_budgets{suffix}.csv", index=False)
    direction = (
        corr.groupby(["dataset", "score"], as_index=False)
        .agg(models=("model", "nunique"), positive_models=("spearman", lambda s: int((s > 0).sum())), median_spearman=("spearman", "median"))
    )
    direction.to_csv(OUT / f"p11_same_model_benefit_direction_summary{suffix}.csv", index=False)
    payload = {
        "experiment": "P11-E01 same-model x4-to-x2 benefit prediction",
        "status": "PILOT" if args.max_cases else "FROZEN ANALYSIS",
        "seed": args.seed,
        "bootstrap": args.bootstrap,
        "datasets": args.datasets,
        "eligible_rows": int(len(eligible)),
        "eligible_models": sorted(eligible.model.unique()),
        "benefit_definition": "same-model common-support MAE_x4 minus MAE_x2",
        "scores": list(scores),
        "direction_summary": direction.to_dict(orient="records"),
        "retrospective_only": True,
    }
    (OUT / f"p11_same_model_benefit_summary{suffix}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(direction.to_string(index=False))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
