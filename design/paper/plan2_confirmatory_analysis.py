"""Plan-2 confirmation/falsification analyses for PC-v1-FROZEN.

Reads existing immutable per-case outputs and writes all derived artifacts under
design/paper/plan2_outputs.  The examination is the resampling unit.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "design" / "rasinet" / "outputs"
OUT = HERE / "plan2_outputs"
sys.path.insert(0, str(ROOT / "design"))
sys.path.insert(0, str(ROOT / "baseline"))
from rasinet.icassp_statistics import ranking_metrics  # noqa: E402
from rasinet.committee_reliability import risk_coverage_summary  # noqa: E402

METHODS = ("frozen_baseline", "physical_consistency")
METRICS = ("normalized_aurc", "case_spearman", "case_kendall", "rrr_25", "rrr_50", "rrr_75")
SEED = 20260812


def profile_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for (method, scale, target), group in frame.groupby(["method", "scale", "target_model"], sort=True):
        values = ranking_metrics(group.common_error.to_numpy(), group.triage_score.to_numpy())
        records.append({"method": method, "scale": int(scale), "target_model": target, "n": len(group), **values})
    return pd.DataFrame(records)


def aggregate_delta(frame: pd.DataFrame) -> dict[str, float]:
    prof = profile_metrics(frame)
    means = prof.groupby("method")[list(METRICS)].mean()
    return {metric: float(means.loc["physical_consistency", metric] - means.loc["frozen_baseline", metric]) for metric in METRICS}


def load_ningxia() -> pd.DataFrame:
    path = SOURCE / "nested_optimization" / "all_finalist_outer_predictions.csv"
    frame = pd.read_csv(path)
    frame = frame[frame.method.isin(METHODS)].copy()
    assert len(frame) == 396 and frame.case.nunique() == 22
    return frame


def load_fastmri() -> pd.DataFrame:
    physical = pd.read_csv(SOURCE / "nested_optimization" / "cross_scale_consistency_per_case.csv")
    physical = physical[
        physical.dataset.eq("fastmri")
        & physical.target_model.isin(["i3net", "hat", "swinir"])
    ][["scale", "case", "target_model", "common_error", "consistency"]].copy()
    physical["method"] = "physical_consistency"
    physical = physical.rename(columns={"consistency": "triage_score"})

    baseline = pd.read_csv(SOURCE / "multiscale" / "per_case_scores.csv")
    baseline = baseline[
        baseline.dataset.eq("fastmri")
        & baseline.target.isin(["i3net", "hat", "swinir"])
        & baseline.method.eq("target_median")
    ][["scale", "case_id", "target", "case_score"]].copy()
    baseline.columns = ["scale", "case", "target_model", "triage_score"]
    # Use one audited common-support error label for both scores.  The older
    # multiscale table used a slightly different target-derived error support.
    baseline = baseline.merge(
        physical[["scale", "case", "target_model", "common_error"]],
        on=["scale", "case", "target_model"], how="inner"
    )
    baseline["method"] = "frozen_baseline"
    frame = pd.concat([baseline, physical], ignore_index=True)
    assert len(frame) == 432 and frame.case.nunique() == 24
    return frame


def leave_one_out(frame: pd.DataFrame) -> pd.DataFrame:
    full = aggregate_delta(frame)
    records = []
    for case in sorted(frame.case.unique()):
        values = aggregate_delta(frame[frame.case.ne(case)])
        case_rows = frame[frame.case.eq(case)]
        pc = case_rows[case_rows.method.eq("physical_consistency")]
        base = case_rows[case_rows.method.eq("frozen_baseline")]
        records.append({
            "case": case,
            **{f"delta_{metric}": values[metric] for metric in METRICS},
            "influence_on_delta_nAURC": values["normalized_aurc"] - full["normalized_aurc"],
            "mean_error": float(pc.common_error.mean()),
            "mean_pc_rank": float(pc.groupby(["scale", "target_model"]).triage_score.rank(pct=True).mean()),
            "mean_pc_score": float(pc.triage_score.mean()),
            "mean_baseline_score": float(base.triage_score.mean()),
        })
    return pd.DataFrame(records)


def cluster_resample(frame: pd.DataFrame, samples: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    cases = np.asarray(sorted(frame.case.unique()))
    by_case = {case: frame[frame.case.eq(case)] for case in cases}
    records = []
    for replicate in range(samples):
        selected = rng.choice(cases, size=len(cases), replace=True)
        parts = []
        for draw, case in enumerate(selected):
            part = by_case[case].copy()
            part["case"] = f"draw_{draw:03d}"
            parts.append(part)
        values = aggregate_delta(pd.concat(parts, ignore_index=True))
        records.append({"replicate": replicate, **{f"delta_{k}": v for k, v in values.items()}})
    return pd.DataFrame(records)


def clustered_permutation(frame: pd.DataFrame, samples: int = 2000) -> dict[str, float]:
    rng = np.random.default_rng(SEED + 1)
    cases = np.asarray(sorted(frame.case.unique()))
    observed = aggregate_delta(frame)
    null = {metric: [] for metric in ("normalized_aurc", "case_spearman", "case_kendall")}
    wide = frame.pivot(index=["case", "scale", "target_model", "common_error"], columns="method", values="triage_score").reset_index()
    # The two scores have unrelated physical units.  Exchangeability is valid
    # only after converting each to its within-profile ordering; all evaluated
    # metrics are invariant to this monotone rank transform.
    for method in METHODS:
        wide[method] = wide.groupby(["scale", "target_model"])[method].rank(method="average")
    for _ in range(samples):
        swap_cases = set(cases[rng.random(len(cases)) < 0.5])
        perm = wide.copy()
        mask = perm.case.isin(swap_cases)
        left = perm.loc[mask, "frozen_baseline"].copy()
        perm.loc[mask, "frozen_baseline"] = perm.loc[mask, "physical_consistency"].to_numpy()
        perm.loc[mask, "physical_consistency"] = left.to_numpy()
        long = perm.melt(
            id_vars=["case", "scale", "target_model", "common_error"],
            value_vars=list(METHODS), var_name="method", value_name="triage_score"
        )
        values = aggregate_delta(long)
        for metric in null:
            null[metric].append(values[metric])
    result = {}
    for metric, values in null.items():
        array = np.asarray(values)
        obs = observed[metric]
        result[f"observed_delta_{metric}"] = obs
        result[f"two_sided_p_{metric}"] = float((1 + np.sum(np.abs(array) >= abs(obs))) / (len(array) + 1))
    return result


def risk_curves(frame: pd.DataFrame, dataset: str) -> pd.DataFrame:
    records = []
    for (method, scale, target), group in frame.groupby(["method", "scale", "target_model"]):
        risk = risk_coverage_summary(group.common_error, group.triage_score)
        mean_error = float(group.common_error.mean())
        for coverage, value in zip(risk["coverage"], risk["risk"]):
            records.append({"dataset": dataset, "method": method, "scale": scale, "target_model": target,
                            "coverage": coverage, "risk": value, "relative_risk": value / mean_error})
    return pd.DataFrame(records)


def plot_forest(profile: pd.DataFrame, path: Path, title: str) -> None:
    pivot = profile.pivot(index=["scale", "target_model"], columns="method", values="normalized_aurc")
    delta = (pivot.physical_consistency - pivot.frozen_baseline).sort_values()
    labels = [f"x{s} {t}" for s, t in delta.index]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    colors = ["#176B87" if value < 0 else "#C44536" for value in delta]
    ax.barh(np.arange(len(delta)), delta, color=colors)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_yticks(np.arange(len(delta)), labels)
    ax.set_xlabel("Delta nAURC (PC-v1 minus frozen baseline; lower is better)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_risk(curves: pd.DataFrame, path: Path, title: str) -> None:
    summary = curves.groupby(["method", "coverage"], as_index=False).relative_risk.mean()
    fig, ax = plt.subplots(figsize=(6.4, 4.5))
    styles = {"frozen_baseline": ("#C44536", "Frozen committee"), "physical_consistency": ("#176B87", "PC-v1-FROZEN")}
    for method, group in summary.groupby("method"):
        color, label = styles[method]
        ax.plot(group.coverage, group.relative_risk, label=label, color=color, linewidth=2)
    ax.axhline(1, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("Coverage retained")
    ax.set_ylabel("Retained MAE / full-cohort MAE")
    ax.set_title(title)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def summarize_dataset(name: str, frame: pd.DataFrame) -> dict[str, object]:
    profile = profile_metrics(frame)
    profile.to_csv(OUT / f"{name}_per_profile.csv", index=False)
    loo = leave_one_out(frame)
    loo.to_csv(OUT / f"{name}_leave_one_case_out.csv", index=False)
    bootstrap = cluster_resample(frame)
    bootstrap.to_csv(OUT / f"{name}_cluster_bootstrap.csv", index=False)
    permutation = clustered_permutation(frame)
    curves = risk_curves(frame, name)
    curves.to_csv(OUT / f"{name}_risk_curves.csv", index=False)
    plot_forest(profile, OUT / f"{name}_forest.png", f"{name}: profile heterogeneity")
    plot_risk(curves, OUT / f"{name}_risk_coverage.png", f"{name}: mean risk-coverage behavior")

    full = aggregate_delta(frame)
    n_col = bootstrap.delta_normalized_aurc.to_numpy()
    profile_wide = profile.pivot(index=["scale", "target_model"], columns="method", values="normalized_aurc")
    profile_delta = profile_wide.physical_consistency - profile_wide.frozen_baseline
    return {
        "dataset": name,
        "cases": int(frame.case.nunique()),
        "profiles": int(len(profile_delta)),
        "aggregate_delta": full,
        "cluster_bootstrap_delta_nAURC_95ci": [float(np.quantile(n_col, 0.025)), float(np.quantile(n_col, 0.975))],
        "loo_direction_preserved": int((loo.delta_normalized_aurc < 0).sum()),
        "loo_total": int(len(loo)),
        "loo_delta_nAURC_range": [float(loo.delta_normalized_aurc.min()), float(loo.delta_normalized_aurc.max())],
        "profiles_favoring_pc": int((profile_delta < 0).sum()),
        "profile_delta_nAURC_range": [float(profile_delta.min()), float(profile_delta.max())],
        "permutation": permutation,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summaries = [summarize_dataset("ningxia", load_ningxia()), summarize_dataset("fastmri", load_fastmri())]
    (OUT / "confirmatory_summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
