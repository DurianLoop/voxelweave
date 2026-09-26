"""Small derived analyses and scientific figures for plan2."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "plan2_outputs"
FIG = OUT / "figures"


def risk_summary(dataset: str) -> dict[str, object]:
    frame = pd.read_csv(OUT / f"{dataset}_risk_curves.csv")
    mean = frame.groupby(["method", "coverage"], as_index=False).relative_risk.mean()
    wide = mean.pivot(index="coverage", columns="method", values="relative_risk")
    wide["delta_pc_minus_baseline"] = wide.physical_consistency - wide.frozen_baseline
    wide.to_csv(OUT / f"{dataset}_mean_risk_curve_difference.csv")
    delta = wide.delta_pc_minus_baseline
    signs = np.sign(delta.to_numpy())
    crossings = int(np.sum(signs[1:] * signs[:-1] < 0))
    return {
        "coverage_points_pc_better": int((delta < 0).sum()),
        "coverage_points_total": len(delta),
        "crossings": crossings,
        "best_delta": float(delta.min()),
        "worst_delta": float(delta.max()),
        "delta_at_nearest_25": float(delta.iloc[np.argmin(np.abs(delta.index - .25))]),
        "delta_at_nearest_50": float(delta.iloc[np.argmin(np.abs(delta.index - .50))]),
        "delta_at_nearest_75": float(delta.iloc[np.argmin(np.abs(delta.index - .75))]),
    }


def intensity_driver() -> dict[str, float]:
    frame = pd.read_csv(OUT / "context_controls" / "per_case.csv")
    frame = frame[~frame.scale.astype(str).str.startswith("pair_")]
    raw = frame[frame.variant.eq("raw")][["case", "scale", "target_model", "score", "common_error"]].rename(columns={"score": "raw_pc"})
    norm = frame[frame.variant.eq("pooled_dynamic_range")][["case", "scale", "target_model", "score", "range_normalized_error"]].rename(columns={"score": "normalized_pc"})
    merged = raw.merge(norm, on=["case", "scale", "target_model"])
    merged["inferred_dynamic_range"] = merged.raw_pc / merged.normalized_pc.clip(lower=1e-12)
    merged.to_csv(OUT / "intensity_driver_per_profile_case.csv", index=False)
    return {
        "rho_dynamic_range_vs_raw_error": float(stats.spearmanr(merged.inferred_dynamic_range, merged.common_error).statistic),
        "rho_dynamic_range_vs_raw_pc": float(stats.spearmanr(merged.inferred_dynamic_range, merged.raw_pc).statistic),
        "rho_normalized_pc_vs_normalized_error": float(stats.spearmanr(merged.normalized_pc, merged.range_normalized_error).statistic),
    }


def under_ranked_tables() -> dict[str, object]:
    counts = {}
    for dataset in ("ningxia", "fastmri"):
        if dataset == "fastmri":
            source = pd.read_csv(HERE.parent / "rasinet" / "outputs" / "nested_optimization" / "cross_scale_consistency_per_case.csv")
            frame = source[source.dataset.eq("fastmri") & source.target_model.isin(["i3net", "hat", "swinir"])][["case", "scale", "target_model", "common_error", "consistency"]]
            frame = frame.rename(columns={"consistency": "pc_score"})
        else:
            source = pd.read_csv(HERE.parent / "rasinet" / "outputs" / "nested_optimization" / "all_finalist_outer_predictions.csv")
            frame = source[source.method.eq("physical_consistency")][["case", "scale", "target_model", "common_error", "triage_score"]].rename(columns={"triage_score": "pc_score"})
        frame["error_pct"] = frame.groupby(["scale", "target_model"]).common_error.rank(pct=True)
        frame["pc_pct"] = frame.groupby(["scale", "target_model"]).pc_score.rank(pct=True)
        frame["under_ranking"] = frame.error_pct - frame.pc_pct
        worst = frame.sort_values("under_ranking", ascending=False).head(15)
        worst.to_csv(OUT / f"{dataset}_most_under_ranked.csv", index=False)
        counts[dataset] = {"max_under_ranking": float(worst.under_ranking.max()), "top_case": str(worst.iloc[0].case)}
    return counts


def plots() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    stress = pd.read_csv(OUT / "common_mode_mechanism" / "summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.3))
    for mode, label in (("shared_uniform", "Shared uniform blur"), ("shared_factor_dependent", "Shared factor-dependent blur"), ("target_only_factor_dependent", "Target-only factor-dependent blur")):
        g = stress[stress["mode"].eq(mode)]
        axes[0].plot(g.severity, g.error_change, marker="o", label=label)
        axes[1].plot(g.severity, g.physical_change, marker="o", label=label)
    axes[0].set(title="Reconstruction error rises", xlabel="Blur severity", ylabel="Change in MAE")
    axes[1].set(title="Physical consistency falls", xlabel="Blur severity", ylabel="Change in PC score")
    axes[0].legend(frameon=False, fontsize=7)
    for ax in axes: ax.axhline(0, color="gray", linewidth=.8); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(FIG / "common_mode_failure.png", dpi=200); plt.close(fig)

    endpoint = pd.read_csv(OUT / "endpoint_sensitivity_aggregate.csv")
    pivot = endpoint.pivot(index="variant", columns="endpoint", values="normalized_aurc").loc[["frozen_baseline", "raw", "pooled_dynamic_range"]]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    x = np.arange(len(pivot)); width = .36
    ax.bar(x-width/2, pivot.common_error, width, label="Raw MAE endpoint", color="#176B87")
    ax.bar(x+width/2, pivot.range_normalized_error, width, label="Range-normalized endpoint", color="#CDA434")
    ax.set_xticks(x, ["Frozen committee", "Raw PC", "Range-normalized PC"])
    ax.set_ylabel("Mean nAURC (lower is better)"); ax.legend(frameon=False); ax.grid(axis="y", alpha=.25)
    fig.tight_layout(); fig.savefig(FIG / "intensity_endpoint_sensitivity.png", dpi=200); plt.close(fig)

    loc = pd.read_csv(OUT / "localization" / "confirmation" / "per_plane.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.2))
    axes[0].hist(loc.pixel_spearman, bins=30, color="#176B87", alpha=.9)
    axes[0].axvline(loc.pixel_spearman.median(), color="black", linestyle="--")
    axes[0].set(xlabel="Pixelwise Spearman", ylabel="Matched planes", title="Held-out localization")
    axes[1].scatter(loc.mean_inconsistency, loc.mean_error, s=8, alpha=.35, color="#C44536")
    axes[1].set(xlabel="Mean physical inconsistency", ylabel="Mean retrospective error", title="Slice-level association")
    fig.tight_layout(); fig.savefig(FIG / "localization_confirmation.png", dpi=200); plt.close(fig)


def main() -> None:
    payload = {
        "risk_coverage": {d: risk_summary(d) for d in ("ningxia", "fastmri")},
        "intensity_driver": intensity_driver(),
        "under_ranked": under_ranked_tables(),
    }
    plots()
    (OUT / "synthesis_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
