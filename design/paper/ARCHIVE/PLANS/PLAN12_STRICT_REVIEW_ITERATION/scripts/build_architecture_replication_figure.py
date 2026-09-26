from __future__ import annotations

from pathlib import Path
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"D:\MRI")
P9 = ROOT / "design/paper/PLAN9_ARCH_GENERALIZATION/outputs/p9_architecture_forest.csv"
P11 = ROOT / "design/paper/PLAN11_CLAIM_STRENGTHENING/outputs"
OUT = ROOT / "design/paper/PLAN12_STRICT_REVIEW_ITERATION"

ORDER = ["hat", "swinir", "i3net", "saint", "cycleinr"]
LABEL = {
    "hat": "HAT",
    "swinir": "SwinIR",
    "i3net": "I3Net",
    "saint": "SAINT-style",
    "cycleinr": "CycleINR-style",
}


def errorbar(ax, frame, value, low, high, y, offset, color, marker, label):
    x = frame[value].to_numpy(float)
    lo = frame[low].to_numpy(float)
    hi = frame[high].to_numpy(float)
    ax.errorbar(
        x,
        y + offset,
        xerr=np.vstack([x - lo, hi - x]),
        fmt=marker,
        ms=5.0,
        capsize=2.2,
        elinewidth=1.15,
        color=color,
        mec=color,
        mfc="white" if marker == "s" else color,
        label=label,
        zorder=3,
    )


def main() -> None:
    fast = pd.read_csv(P9).set_index("model").loc[ORDER].reset_index()
    ixi = pd.read_csv(P11 / "p11_ixi_clean_model_summary_full.csv").set_index("model").loc[ORDER].reset_index()
    matched = pd.read_csv(P11 / "p11_identity_swap_model_summary_full.csv").set_index("model").loc[ORDER].reset_index()

    for columns, frame in [
        (["observable_gain", "observable_ci_low", "observable_ci_high"], fast),
        (["median_observable_gain", "observable_gain_ci_low", "observable_gain_ci_high"], ixi),
        (["median_balanced_observable_gain", "gain_ci_low", "gain_ci_high"], matched),
    ]:
        frame[columns] = 100.0 * frame[columns]

    y = np.arange(len(ORDER))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 3.35), gridspec_kw={"wspace": 0.20})

    ax = axes[0]
    errorbar(ax, fast, "observable_gain", "observable_ci_low", "observable_ci_high", y, 0.20, "#2878B5", "o", "fastMRI clean (n=24)")
    errorbar(ax, ixi, "median_observable_gain", "observable_gain_ci_low", "observable_gain_ci_high", y, 0.00, "#E1812C", "D", "IXI clean (n=115)")
    errorbar(ax, matched, "median_balanced_observable_gain", "gain_ci_low", "gain_ci_high", y, -0.20, "#2B9B69", "s", "IXI reflection-balanced")
    ax.axvline(0, color="#555555", lw=0.8, ls="--")
    ax.set_yticks(y, [LABEL[m] for m in ORDER])
    ax.set_xlabel("Disjoint − shared observable error (percentage points)")
    ax.set_title("(a) Local error observability", loc="left", fontweight="bold")
    ax.set_xlim(-1, 33)
    ax.legend(frameon=False, fontsize=7.4, loc="upper left")
    ax.text(0.02, 0.03, "IXI positive cases: 115/115 for every model\norientation warnings: 0/5", transform=ax.transAxes, fontsize=7.2)

    fast_rank = fast.copy()
    ixi_rank = ixi.copy()
    ax = axes[1]
    errorbar(ax, fast_rank, "ranking_delta", "ranking_ci_low", "ranking_ci_high", y, 0.12, "#2878B5", "o", "fastMRI (n=24)")
    errorbar(ax, ixi_rank, "ranking_delta_rho", "ranking_delta_ci_low", "ranking_delta_ci_high", y, -0.12, "#E1812C", "D", "IXI (n=115)")
    ax.axvline(0, color="#555555", lw=0.8, ls="--")
    ax.set_yticks(y, [])
    ax.set_xlabel(r"Disjoint − shared examination-ranking $\Delta\rho$")
    ax.set_title("(b) Ranking consequence", loc="left", fontweight="bold")
    ax.set_xlim(-0.18, 0.76)
    ax.legend(frameon=False, fontsize=7.6, loc="upper right")

    for ax in axes:
        ax.grid(axis="x", color="#D9D9D9", lw=0.6, alpha=0.8)
        ax.tick_params(axis="both", labelsize=8)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

    fig.savefig(OUT / "fig_architecture_replication.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig_architecture_replication.png", dpi=260, bbox_inches="tight")
    plt.close(fig)

    targets = [
        ROOT / "design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/figures",
        ROOT / "design/paper/TMI/TMI_ARCH_GENERALIZED/figures",
    ]
    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(OUT / "fig_architecture_replication.pdf", target / "fig_architecture_replication.pdf")
        shutil.copy2(OUT / "fig_architecture_replication.png", target / "fig_architecture_replication.png")


if __name__ == "__main__":
    main()
