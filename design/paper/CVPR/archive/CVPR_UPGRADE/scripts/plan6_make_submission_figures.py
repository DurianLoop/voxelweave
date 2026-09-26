"""Generate submission figures directly from frozen Plan6 result tables."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve()
UP = HERE.parents[1]
OUT = UP / "outputs"
FIG = UP / "PAPER" / "figures"

COLORS = {
    "Anchor-CV": "#2563A6",
    "Adjacent MAE": "#E07A24",
    "Output PC": "#3E9C76",
}
DATASETS = [("fastmri", "fastMRI"), ("ixi", "IXI")]


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#D7DEE8", linewidth=0.6, alpha=0.75)
    ax.set_axisbelow(True)


def anchor_audit():
    summary = pd.read_csv(OUT / "plan6_anchor_cv_explanation_summary.csv")
    rows = summary[
        (summary["endpoint"] == "x4_error")
        & summary["method"].isin(["anchor_cv", "adjacent_mae"])
    ].copy()
    label = {"anchor_cv": "Anchor-CV", "adjacent_mae": "Adjacent MAE"}
    rows["method_label"] = rows["method"].map(label)

    pc = pd.read_csv(OUT / "orthogonal_two_component_per_case.csv")
    pc = (
        pc.groupby(["dataset", "case"], as_index=False)
        .agg(score=("score", "mean"), error=("error", "mean"))
    )
    pc_rho = pc.groupby("dataset").apply(
        lambda x: x["score"].corr(x["error"], method="spearman"),
        include_groups=False,
    )

    fig, ax = plt.subplots(figsize=(5.15, 2.55))
    datasets = [("fastmri", "fastMRI"), ("ixi", "IXI"), ("ningxia", "NingXia")]
    methods = ["Anchor-CV", "Adjacent MAE", "Output PC"]
    width = 0.23
    x = np.arange(len(datasets))
    for j, method in enumerate(methods):
        values = []
        for key, _ in datasets:
            if method == "Output PC":
                values.append(float(pc_rho.loc[key]))
            else:
                values.append(
                    float(rows[(rows.dataset == key) & (rows.method_label == method)].spearman.iloc[0])
                )
        bars = ax.bar(x + (j - 1) * width, values, width, label=method,
                      color=COLORS[method], edgecolor="white", linewidth=0.4)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.007, f"{value:.3f}",
                    ha="center", va="bottom", fontsize=6.7, rotation=90)
    ax.set_xticks(x, [name for _, name in datasets])
    ax.set_ylim(0.78, 1.035)
    ax.set_ylabel(r"Spearman $\rho$ with x4 error")
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01), fontsize=7)
    style_axis(ax)
    fig.tight_layout(pad=0.6)
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"plan6_anchor_cv_audit.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def consequence_budget():
    table = pd.read_csv(OUT / "plan6_ixi_x2_consequence_budgets.csv")
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.42), sharey=False)
    for ax, (key, title) in zip(axes, DATASETS):
        subset = table[table.dataset == key]
        for method in ["Anchor-CV", "Adjacent MAE", "Output PC"]:
            q = subset[subset.method == method].sort_values("budget")
            x = 100 * q.budget.to_numpy()
            y = q.gain_above_random.to_numpy()
            lo = q.cluster_ci_low.to_numpy()
            hi = q.cluster_ci_high.to_numpy()
            ax.plot(x, y, marker="o", markersize=3.6, linewidth=1.4,
                    color=COLORS[method], label=method)
            ax.fill_between(x, lo, hi, color=COLORS[method], alpha=0.10, linewidth=0)
        ax.axhline(0, color="#394150", linewidth=0.7)
        ax.set_title(title, fontsize=9, pad=3)
        ax.set_xticks([10, 20, 30, 50])
        ax.set_xlabel("Escalation budget (%)")
        style_axis(ax)
    axes[0].set_ylabel("Mean benefit above random")
    axes[0].legend(frameon=False, fontsize=7, ncol=1, loc="upper right")
    fig.tight_layout(pad=0.55, w_pad=1.1)
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"plan6_ixi_x2_budget.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    anchor_audit()
    consequence_budget()
    print("wrote plan6_anchor_cv_audit and plan6_ixi_x2_budget")
