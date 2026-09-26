"""Build the rule-frozen same-model densification consequence figure."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve()
PLAN12 = HERE.parents[1]
PAPER = PLAN12.parent
ROOT = PAPER.parents[1]
SOURCE = PAPER / "PLAN11_CLAIM_STRENGTHENING/outputs"
CVPR_FIGURES = PAPER / "CVPR/CVPR_ARCH_GENERALIZED/PAPER/figures"

SCORES = ["anchor_cv", "adjacent_mae", "bank_median_disagreement"]
LABELS = ["Anchor-CV", "Adjacent MAE", "Bank disagreement"]
COLORS = ["#0072B2", "#E69F00", "#009E73"]


def correlation_panel(ax, frame: pd.DataFrame, dataset: str, title: str) -> None:
    rng = np.random.default_rng(20260905)
    subset = frame[frame.dataset.eq(dataset)]
    for index, (score, label, color) in enumerate(zip(SCORES, LABELS, COLORS)):
        values = subset.loc[subset.score.eq(score), "spearman"].to_numpy(float)
        jitter = rng.uniform(-0.13, 0.13, len(values))
        ax.scatter(index + jitter, values, s=17, facecolor=color, edgecolor="white", linewidth=0.35, alpha=0.82)
        negative = values <= 0
        if negative.any():
            ax.scatter((index + jitter)[negative], values[negative], s=35, marker="x", color="#B2182B", linewidth=1.1, zorder=4)
        median = float(np.median(values))
        ax.plot([index - 0.27, index + 0.27], [median, median], color="black", linewidth=1.7, zorder=5)
        ax.text(index, min(1.02, median + 0.055), f"{median:.2f}", ha="center", va="bottom", fontsize=7)
    ax.axhline(0, color="#777777", linewidth=0.7, linestyle="--")
    ax.set_xticks(range(len(LABELS)), LABELS, rotation=19, ha="right")
    ax.set_ylim(-0.34, 1.05)
    ax.set_ylabel("Within-model Spearman $\\rho$")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.55)


def budget_panel(ax, frame: pd.DataFrame) -> None:
    dataset_colors = {"fastmri": "#0072B2", "ningxia": "#D55E00"}
    score_styles = {"anchor_cv": "-", "adjacent_mae": "--", "bank_median_disagreement": ":"}
    for dataset in ["fastmri", "ningxia"]:
        for score, label in zip(SCORES, LABELS):
            group = frame[frame.dataset.eq(dataset) & frame.score.eq(score)]
            points = []
            lower = []
            upper = []
            budgets = sorted(group.budget.unique())
            for budget in budgets:
                values = group.loc[group.budget.eq(budget), "oracle_normalized_gain"].dropna().to_numpy(float)
                points.append(float(np.median(values)))
                lower.append(float(np.quantile(values, 0.25)))
                upper.append(float(np.quantile(values, 0.75)))
            x = 100 * np.asarray(budgets)
            color = dataset_colors[dataset]
            ax.plot(
                x,
                points,
                score_styles[score],
                color=color,
                linewidth=1.35,
                marker="o",
                markersize=3.0,
                label=f"{dataset} · {label}",
            )
            ax.fill_between(x, lower, upper, color=color, alpha=0.055)
    ax.axhline(0, color="#777777", linewidth=0.7, linestyle="--")
    ax.set_xticks([10, 20, 30, 50])
    ax.set_xlabel("Selection budget (%)")
    ax.set_ylabel("Median oracle-normalized gain")
    ax.set_ylim(-0.05, 1.04)
    ax.set_title("(c) Retrospective allocation", loc="left", fontweight="bold")
    ax.grid(color="#D9D9D9", linewidth=0.55)
    ax.legend(frameon=False, fontsize=6.0, ncol=2, loc="lower right", columnspacing=0.8, handlelength=2.3)


def main() -> None:
    correlations = pd.read_csv(SOURCE / "p11_same_model_benefit_correlations.csv")
    budgets = pd.read_csv(SOURCE / "p11_same_model_benefit_budgets.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.15), gridspec_kw={"width_ratios": [1, 1, 1.35]})
    correlation_panel(axes[0], correlations, "fastmri", "(a) fastMRI")
    correlation_panel(axes[1], correlations, "ningxia", "(b) NingXia")
    axes[1].set_ylabel("")
    budget_panel(axes[2], budgets)
    fig.suptitle(
        "Same-model retrospective ×4→×2 benefit prediction across the recovered reconstruction bank",
        x=0.06,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    fig.text(
        0.06,
        0.005,
        "Points are eligible models; bars are medians. Red × marks non-positive direction. Bands are model IQRs, not confidence intervals.",
        fontsize=6.6,
    )
    fig.tight_layout(rect=(0.02, 0.055, 0.995, 0.91), w_pad=1.4)
    PLAN12.mkdir(parents=True, exist_ok=True)
    CVPR_FIGURES.mkdir(parents=True, exist_ok=True)
    for folder in [PLAN12, CVPR_FIGURES]:
        fig.savefig(folder / "fig_same_model_consequence.pdf", bbox_inches="tight")
        fig.savefig(folder / "fig_same_model_consequence.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
