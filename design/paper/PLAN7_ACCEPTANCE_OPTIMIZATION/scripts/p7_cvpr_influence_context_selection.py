"""P7-CV-E01: target-free influence-aware context selection at fixed overlap count."""

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
CONTEXTS = ("(-2, 1)", "(-2, 3)", "(-1, 2)", "(-3, 2)")
BOOTSTRAPS = 5000
SEED = 20260813


def rho(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return np.nan
    return float(stats.spearmanr(a[ok], b[ok]).statistic)


def aggregate_rule(group, rule, fixed_context=None):
    selected = []
    for _, plane in group.groupby("z", sort=False):
        plane = plane[plane.context.isin(CONTEXTS)]
        if rule == "minimum_influence":
            row = plane.sort_values(["neural_influence_cosine", "context"], kind="stable").iloc[0]
            value = row.disagreement_mae
        elif rule == "maximum_raw_diversity":
            row = plane.sort_values(["disagreement_mae", "context"], ascending=[False, True], kind="stable").iloc[0]
            value = row.disagreement_mae
        elif rule == "mean_random_expectation":
            # Expected score under uniform random choice, without random Monte Carlo noise.
            row = None
            value = float(plane.disagreement_mae.mean())
        elif rule == "fixed_context":
            row = plane[plane.context.eq(fixed_context)].iloc[0]
            value = row.disagreement_mae
        else:
            raise ValueError(rule)
        selected.append((value, None if row is None else row.context))
    return float(np.median([q[0] for q in selected])), "|".join(str(q[1]) for q in selected)


def build_scores(raw, fixed_by_model):
    records = []
    for (dataset, case, cluster, model), group in raw.groupby(["dataset", "case", "patient_cluster", "model"], sort=False):
        rec = {"dataset": dataset, "case": case, "patient_cluster": cluster, "model": model}
        for rule in ("minimum_influence", "maximum_raw_diversity", "mean_random_expectation"):
            rec[rule], rec[f"{rule}_contexts"] = aggregate_rule(group, rule)
        rec["fixed_context"], rec["fixed_contexts"] = aggregate_rule(group, "fixed_context", fixed_by_model[model])
        records.append(rec)
    return pd.DataFrame(records)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(RAW)
    raw = raw[(raw.overlap_count == 1) & raw.context.isin(CONTEXTS)].copy()
    split = pd.read_csv(PC)[["dataset", "case", "split"]].drop_duplicates()
    raw = raw.merge(split, on=["dataset", "case"], how="left")
    raw["split"] = raw.split.fillna("transfer")

    # Development-only target use freezes one fixed-context comparator per architecture.
    dev = raw[(raw.dataset == "fastmri") & (raw.split == "development")]
    fixed_by_model = {}
    dev_table = []
    outcome = pd.read_csv(ANCHOR).groupby(["dataset", "case", "patient_cluster", "model"], as_index=False).agg(x4_error=("x4_error", "first"))
    for model, group in dev.groupby("model"):
        candidates = []
        for context in CONTEXTS:
            scores = group[group.context.eq(context)].groupby("case").disagreement_mae.median()
            y = outcome[(outcome.dataset == "fastmri") & (outcome.model == model)].set_index("case").x4_error
            idx = scores.index.intersection(y.index)
            candidates.append((context, rho(scores.loc[idx], y.loc[idx])))
        candidates.sort(key=lambda q: (-np.nan_to_num(q[1], nan=-999), q[0]))
        fixed_by_model[model] = candidates[0][0]
        for context, value in candidates:
            dev_table.append({"model": model, "context": context, "development_spearman": value, "selected": context == fixed_by_model[model]})

    scores = build_scores(raw, fixed_by_model).merge(outcome, on=["dataset", "case", "patient_cluster", "model"])
    anchor_features = pd.read_csv(ANCHOR).groupby(["dataset", "case", "model"], as_index=False).agg(anchor_cv=("anchor_cv", "first"), adjacent_mae=("adjacent_mae", "first"))
    pc_features = pd.read_csv(PC).groupby(["dataset", "case", "model"], as_index=False).agg(output_pc=("score", "first"), split=("split", "first"))
    scores = scores.merge(anchor_features, on=["dataset", "case", "model"]).merge(pc_features, on=["dataset", "case", "model"], suffixes=("", "_pc"))
    scores["evaluation_partition"] = np.where((scores.dataset == "fastmri") & (scores.split == "development"), "development", np.where((scores.dataset == "fastmri") & (scores.split == "confirmation"), "confirmation", "transfer"))
    scores.to_csv(OUT / "p7_cvpr_influence_context_selection_per_case.csv", index=False)
    pd.DataFrame(dev_table).to_csv(OUT / "p7_cvpr_fixed_context_development_freeze.csv", index=False)

    methods = ["minimum_influence", "fixed_context", "mean_random_expectation", "maximum_raw_diversity", "anchor_cv", "adjacent_mae", "output_pc"]
    summaries = []
    deltas = []
    rng = np.random.default_rng(SEED)
    for (dataset, partition, model), group in scores.groupby(["dataset", "evaluation_partition", "model"], sort=False):
        clusters = group.patient_cluster.astype(str).unique()
        by = {c: group[group.patient_cluster.astype(str).eq(c)] for c in clusters}
        observed = {m: rho(group[m], group.x4_error) for m in methods}
        boot = {m: [] for m in methods}
        for _ in range(BOOTSTRAPS):
            sample = pd.concat([by[c] for c in rng.choice(clusters, len(clusters), replace=True)], ignore_index=True)
            for method in methods:
                boot[method].append(rho(sample[method], sample.x4_error))
        for method in methods:
            arr = np.asarray(boot[method], float)
            summaries.append({
                "dataset": dataset,
                "partition": partition,
                "model": model,
                "cases": int(group.case.nunique()),
                "patient_clusters": int(len(clusters)),
                "method": method,
                "spearman_x4_error": observed[method],
                "cluster_ci_low": float(np.nanquantile(arr, 0.025)),
                "cluster_ci_high": float(np.nanquantile(arr, 0.975)),
            })
        for comparator in methods[1:]:
            arr = np.asarray(boot["minimum_influence"], float) - np.asarray(boot[comparator], float)
            deltas.append({
                "dataset": dataset,
                "partition": partition,
                "model": model,
                "comparator": comparator,
                "rho_delta_minimum_influence_minus_comparator": observed["minimum_influence"] - observed[comparator],
                "cluster_ci_low": float(np.nanquantile(arr, 0.025)),
                "cluster_ci_high": float(np.nanquantile(arr, 0.975)),
            })
    summary = pd.DataFrame(summaries)
    delta = pd.DataFrame(deltas)
    summary.to_csv(OUT / "p7_cvpr_influence_context_selection_summary.csv", index=False)
    delta.to_csv(OUT / "p7_cvpr_influence_context_selection_deltas.csv", index=False)
    payload = {
        "experiment": "P7-CV-E01",
        "status": "COMPLETE",
        "selection": "minimum neural influence among four contexts with overlap_count=1; tie broken lexicographically",
        "target_access_for_selection": False,
        "fixed_comparator_freeze": fixed_by_model,
        "development": "12 fastMRI development cases only for choosing the fixed-context comparator",
        "locked_evaluation": "12 fastMRI confirmation cases plus IXI and NingXia transfer cohorts",
        "capability_boundary": "neural influence is identically zero for zero-overlap pairs and cannot rank them under the Plan6 definition",
        "deployment_cost_boundary": "requires finite-difference responses for candidate contexts; practicality gate evaluated separately",
        "outputs": [
            "p7_cvpr_influence_context_selection_per_case.csv",
            "p7_cvpr_fixed_context_development_freeze.csv",
            "p7_cvpr_influence_context_selection_summary.csv",
            "p7_cvpr_influence_context_selection_deltas.csv",
        ],
    }
    (OUT / "p7_cvpr_influence_context_selection.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("FROZEN FIXED CONTEXT", fixed_by_model)
    print(summary.to_string(index=False))
    print("\nPAIRED DELTAS\n", delta.to_string(index=False))


if __name__ == "__main__":
    main()
