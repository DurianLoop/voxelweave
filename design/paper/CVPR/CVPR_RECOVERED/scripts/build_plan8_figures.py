"""Build the four evidence-focused figures for the Plan-8B CVPR recovery.

All plotted numbers are read from frozen Plan-4/5/6/7 outputs.  The script does
not refit a model or choose a cohort-specific threshold.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[3]
UP = ROOT / "CVPR" / "CVPR_UPGRADE"
OUT = Path(__file__).resolve().parents[1] / "PAPER" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

COLORS = {
    "blue": "#247BA0",
    "orange": "#F2A541",
    "purple": "#7A4E70",
    "green": "#4F8A5B",
    "gray": "#687386",
    "red": "#C94C4C",
}


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def mechanism() -> None:
    fig, ax = plt.subplots(figsize=(12.2, 2.9))
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.2, "Shared physical\nmeasurements", "#DCEEF4"),
        (3.2, "Shared local\nestimator influence", "#E8E0EF"),
        (6.2, "Aligned reconstruction\nerrors", "#F8E7C8"),
        (9.2, "Small disagreement\ncan hide error", "#E1ECD9"),
    ]
    for x, label, face in boxes:
        box = FancyBboxPatch(
            (x, 1.05), 2.55, 1.1,
            boxstyle="round,pad=0.05,rounding_size=0.09",
            linewidth=1.4, edgecolor="#344050", facecolor=face,
        )
        ax.add_patch(box)
        ax.text(x + 1.275, 1.60, label, ha="center", va="center", fontsize=12)
    for x in (2.75, 5.75, 8.75):
        ax.add_patch(FancyArrowPatch((x, 1.60), (x + 0.4, 1.60),
                                     arrowstyle="-|>", mutation_scale=14,
                                     linewidth=1.5, color="#344050"))
    ax.text(6.1, 2.62,
            "Disagreement is informative only to the extent that its generating information is independent",
            ha="center", fontsize=13, fontweight="bold")
    ax.text(6.1, 0.45,
            "One-sided boundary: large separation is evidence that at least one estimate is wrong; small separation is not a correctness certificate.",
            ha="center", fontsize=10.5, color=COLORS["gray"])
    save(fig, "fig1_mechanism")


def controlled_intervention() -> None:
    out = UP / "outputs"
    rows = []
    for name in ("clean_max_overlap_summary.json", "clean_max_overlap_ixi_summary.json"):
        rows.extend(json.loads((out / name).read_text(encoding="utf-8"))["rows"])
    order = ["fastmri", "ixi", "ningxia"]
    by = {r["dataset"]: r for r in rows}
    labels = ["fastMRI", "IXI", "NingXia"]
    colors = [COLORS["blue"], COLORS["orange"], COLORS["purple"]]
    y = np.arange(3)

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 3.4))
    delta = np.array([by[d]["delta"] for d in order])
    lo = np.array([by[d]["cluster_95ci"][0] for d in order])
    hi = np.array([by[d]["cluster_95ci"][1] for d in order])
    for i, color in enumerate(colors):
        axes[0].errorbar(delta[i], y[i], xerr=[[delta[i] - lo[i]], [hi[i] - delta[i]]],
                         fmt="none", ecolor=color, elinewidth=2, capsize=4)
    axes[0].scatter(delta, y, c=colors, s=65, zorder=3)
    axes[0].axvline(0, color="#444444", linestyle="--", linewidth=1)
    axes[0].set_yticks(y, labels)
    axes[0].invert_yaxis()
    axes[0].set_xlabel(r"$\Delta\rho$: disjoint minus shared")
    axes[0].set_title("Disjoint contexts rank error better")
    axes[0].grid(axis="x", alpha=.2)

    shared = 100 * np.array([by[d]["max_shared_fraction_mean"] for d in order])
    observable = 100 * np.array([by[d]["max_observable_fraction_mean"] for d in order])
    axes[1].barh(y, shared, color=colors, alpha=.82, label="shared error")
    axes[1].barh(y, observable, left=shared, color="#DDE2E8", label="observable error")
    axes[1].set_yticks(y, labels)
    axes[1].invert_yaxis()
    axes[1].set_xlim(0, 101)
    axes[1].set_xlabel("Paired error energy (%)")
    axes[1].set_title("Shared contexts hide 97.4--99.7% of error energy")
    for i, obs in enumerate(observable):
        axes[1].text(99.5, i, f"{obs:.2f}% obs.", va="center", ha="right", fontsize=9)
    fig.suptitle("Controlled same-target measurement dependence", fontsize=14, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig2_controlled_intervention")


def influence() -> None:
    df = pd.read_csv(UP / "outputs" / "plan6_neural_shared_influence_confirm3_summary.csv")
    endpoints = ["error_cosine", "shared_fraction", "observable_fraction"]
    titles = ["Error alignment", "Shared error fraction", "Observable error fraction"]
    strata = [(d, m) for d in ("fastmri", "ixi", "ningxia") for m in ("hat", "swinir")]
    labels = [f"{d.replace('fastmri', 'fastMRI').replace('ixi', 'IXI').replace('ningxia', 'NingXia')} · {m.upper() if m == 'hat' else 'SwinIR'}" for d, m in strata]
    y = np.arange(len(strata))
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.0), sharey=True)
    for ax, endpoint, title in zip(axes, endpoints, titles):
        sub = df[df.endpoint == endpoint].set_index(["dataset", "model"])
        est = np.array([sub.loc[s, "abs_rho_advantage"] for s in strata])
        lo = np.array([sub.loc[s, "advantage_ci_low"] for s in strata])
        hi = np.array([sub.loc[s, "advantage_ci_high"] for s in strata])
        point_colors = [COLORS["blue"], COLORS["blue"], COLORS["orange"], COLORS["orange"], COLORS["purple"], COLORS["purple"]]
        for i, color in enumerate(point_colors):
            ax.errorbar(est[i], y[i], xerr=[[est[i] - lo[i]], [hi[i] - est[i]]],
                        fmt="none", ecolor=color, elinewidth=1.8, capsize=3)
        ax.scatter(est, y, c=point_colors, s=45, zorder=3)
        ax.axvline(0, color="#555", linestyle="--", linewidth=1)
        ax.set_title(title)
        ax.set_xlabel(r"$|\rho_{influence}|-|\rho_{count}|$")
        ax.grid(axis="x", alpha=.2)
    axes[0].set_yticks(y, labels)
    axes[0].invert_yaxis()
    fig.suptitle("Local neural shared influence explains error geometry better than overlap count",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig3_shared_influence")


def consequence() -> None:
    out = UP / "outputs"
    expl = json.loads((out / "plan6_anchor_cv_explanation.json").read_text(encoding="utf-8"))
    methods = ["anchor_cv", "adjacent_mae", "adjacent_rmse"]
    cohort = ["fastmri", "ixi", "ningxia"]
    labels = ["fastMRI", "IXI", "NingXia"]
    display = {"anchor_cv": "Anchor-CV", "adjacent_mae": "Adjacent MAE", "adjacent_rmse": "Adjacent RMSE"}
    colors = {"anchor_cv": COLORS["blue"], "adjacent_mae": COLORS["orange"], "adjacent_rmse": COLORS["gray"]}
    lookup = {(r["dataset"], r["method"]): r["spearman"] for r in expl["summaries"] if r.get("endpoint") == "x4_error"}

    corr = pd.read_csv(out / "plan6_ixi_x2_consequence_correlations.csv")
    bud = pd.read_csv(out / "plan6_ixi_x2_consequence_budgets.csv")
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 3.6))
    x = np.arange(3)
    width = .23
    for i, method in enumerate(methods):
        axes[0].bar(x + (i - 1) * width, [lookup[(d, method)] for d in cohort], width,
                    color=colors[method], label=display[method])
    axes[0].set_xticks(x, labels)
    axes[0].set_ylim(.88, 1.0)
    axes[0].set_ylabel("Spearman with x4 error")
    axes[0].set_title("Acquired-only difficulty ranking")
    axes[0].legend(frameon=False, fontsize=8)

    for i, method in enumerate(["Anchor-CV", "Adjacent MAE", "Output PC"]):
        s = corr[corr.method == method]
        axes[1].bar(x[:2] + (i - 1) * width,
                    [float(s[s.dataset == d].spearman_vs_benefit.iloc[0]) for d in ("fastmri", "ixi")],
                    width, label=method, color=[COLORS["blue"], COLORS["orange"], COLORS["green"]][i])
    axes[1].set_xticks(x[:2], ["fastMRI", "IXI"])
    axes[1].set_ylim(.80, 1.0)
    axes[1].set_ylabel("Spearman with x4→x2 benefit")
    axes[1].set_title("Retrospective densification consequence")

    for method, color in (("Anchor-CV", COLORS["blue"]), ("Adjacent MAE", COLORS["orange"]), ("Output PC", COLORS["green"])):
        s = bud[(bud.dataset == "ixi") & (bud.method == method)]
        axes[2].plot(100 * s.budget, s.oracle_normalized_gain, marker="o", color=color, label=method)
    axes[2].set_ylim(.88, 1.01)
    axes[2].set_xlabel("IXI densification budget (%)")
    axes[2].set_ylabel("Oracle-normalized gain")
    axes[2].set_title("Useful, not uniquely superior")
    axes[2].legend(frameon=False, fontsize=8)
    for ax in axes:
        ax.grid(axis="y", alpha=.2)
    fig.suptitle("Practical consequence: examination triage from already acquired anchors",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig4_practical_consequence")


if __name__ == "__main__":
    mechanism()
    controlled_intervention()
    influence()
    consequence()
    print(f"Wrote Plan-8 figures to {OUT}")
