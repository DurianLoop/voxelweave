from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .cross_scale_protocol import (
    ANALYTICAL,
    DATASETS,
    EXPANDED_NEURAL,
    PRIMARY_NEURAL,
    SCALES,
    folds_for,
    sources_for,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DISPLAY = {
    "fastmri": "fastMRI-brain",
    "ningxia": "NingXia",
    "i3net": r"I$^3$Net",
    "hat": "HAT",
    "swinir": "SwinIR",
    "arssr": "ArSSR",
    "cycleinr": "CycleINR",
    "pix2pixgan": "Pix2PixGAN",
    "smamba_unet": "SMamba-UNet",
}


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _fmt(value: float, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def _ci(row: pd.Series, metric: str, digits: int = 3) -> str:
    return (
        f"{_fmt(row[metric], digits)} "
        f"[{_fmt(row[f'{metric}_ci_low'], digits)}, {_fmt(row[f'{metric}_ci_high'], digits)}]"
    )


def cross_scale_figure(aggregate: pd.DataFrame, primary: pd.DataFrame, path: Path) -> None:
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 7.5,
        "axes.linewidth": 0.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    metrics = [
        ("case_spearman", r"Case Spearman $\rho$", (0.45, 1.01)),
        ("normalized_aurc", "nAURC (lower is better)", (-0.01, 0.30)),
        ("rrr_50", "RRR50", (-0.05, 0.75)),
    ]
    markers = {"i3net": "o", "hat": "s", "swinir": "^"}
    colors = {"i3net": "#111111", "hat": "#666666", "swinir": "#AAAAAA"}
    fig, axes = plt.subplots(2, 3, figsize=(7.15, 3.35), sharex=True)
    for row_index, dataset in enumerate(DATASETS):
        subset = primary[primary.dataset == dataset]
        for column_index, (metric, label, limits) in enumerate(metrics):
            ax = axes[row_index, column_index]
            for target in PRIMARY_NEURAL:
                rows = subset[subset.target == target].sort_values("scale")
                x = rows.scale.to_numpy(dtype=float)
                y = rows[metric].to_numpy(dtype=float)
                low = y - rows[f"{metric}_ci_low"].to_numpy(dtype=float)
                high = rows[f"{metric}_ci_high"].to_numpy(dtype=float) - y
                ax.errorbar(
                    x,
                    y,
                    yerr=np.vstack([low, high]),
                    color=colors[target],
                    marker=markers[target],
                    markersize=3.8,
                    linewidth=1.0,
                    capsize=2.0,
                    label=DISPLAY[target],
                )
            ax.set_xlim(1.7, 6.3)
            ax.set_ylim(*limits)
            ax.set_xticks(SCALES, [r"$\times2$", r"$\times4$", r"$\times6$"])
            ax.grid(axis="y", color="#D8D8D8", linewidth=0.5)
            if row_index == 0:
                ax.set_title(label, fontsize=8)
            if column_index == 0:
                ax.set_ylabel(DISPLAY[dataset], fontsize=8, fontweight="bold")
            if row_index == 1:
                ax.set_xlabel("Interpolation factor")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.94), pad=0.7, w_pad=0.8, h_pad=0.8)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def matched_heatmap(matrix: pd.DataFrame, path: Path) -> None:
    plt.rcParams.update({"font.family": "serif", "font.size": 7.5, "pdf.fonttype": 42})
    data = matrix[matrix.method == "target_median"]
    fig, axes = plt.subplots(2, 3, figsize=(7.15, 4.1))
    image = None
    for row_index, dataset in enumerate(DATASETS):
        for column_index, scale in enumerate(SCALES):
            ax = axes[row_index, column_index]
            subset = data[(data.dataset == dataset) & (data.scale == scale)]
            values = np.zeros((3, 3), dtype=float)
            for i, scored in enumerate(PRIMARY_NEURAL):
                for j, error_target in enumerate(PRIMARY_NEURAL):
                    values[i, j] = float(
                        subset[(subset.scored_target == scored) & (subset.error_target == error_target)].spearman.iloc[0]
                    )
            image = ax.imshow(values, cmap="Greys", vmin=0.75, vmax=1.0)
            for i in range(3):
                for j in range(3):
                    ax.text(j, i, f"{values[i, j]:.3f}", ha="center", va="center", color="white" if values[i, j] > 0.89 else "black", fontsize=7)
                    if i == j:
                        ax.add_patch(plt.Rectangle((j - 0.47, i - 0.47), 0.94, 0.94, fill=False, edgecolor="#C00000", linewidth=1.2))
            ax.set_xticks(range(3), [DISPLAY[name] for name in PRIMARY_NEURAL], rotation=25, ha="right")
            ax.set_yticks(range(3), [DISPLAY[name] for name in PRIMARY_NEURAL])
            ax.set_title(f"{DISPLAY[dataset]} " + rf"$\times${scale}", fontsize=8)
            if column_index == 0:
                ax.set_ylabel("Scored target")
            if row_index == 1:
                ax.set_xlabel("Error target")
    if image is not None:
        color_axis = fig.add_axes([0.915, 0.20, 0.014, 0.60])
        fig.colorbar(image, cax=color_axis, label=r"Spearman $\rho$")
    fig.subplots_adjust(left=0.08, right=0.88, bottom=0.10, top=0.94, wspace=0.32, hspace=0.38)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def paired_forest(comparisons: pd.DataFrame, path: Path) -> None:
    plt.rcParams.update({"font.family": "serif", "font.size": 7.0, "pdf.fonttype": 42})
    wanted = [
        ("target_median_vs_all_output_spread", "Median vs all-output spread"),
        ("target_median_vs_target_mean", "Median vs mean"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 6.2), sharey=True)
    labels = [
        f"{DISPLAY[dataset]} x{scale} {DISPLAY[target]}"
        for dataset in DATASETS
        for scale in SCALES
        for target in PRIMARY_NEURAL
    ] + ["Equal-profile aggregate"]
    for ax, (comparison, title) in zip(axes, wanted):
        rows = comparisons[comparisons.comparison == comparison]
        ordered = []
        for dataset in DATASETS:
            for scale in SCALES:
                for target in PRIMARY_NEURAL:
                    ordered.append(rows[(rows.dataset == dataset) & (rows.scale.astype(str) == str(scale)) & (rows.target == target)].iloc[0])
        ordered.append(rows[rows.dataset == "aggregate_equal_profile_weight"].iloc[0])
        y = np.arange(len(ordered))[::-1]
        point = np.asarray([float(row.delta_naurc) for row in ordered])
        low = np.asarray([float(row.delta_naurc_ci_low) for row in ordered])
        high = np.asarray([float(row.delta_naurc_ci_high) for row in ordered])
        ax.axvline(0, color="#777777", linewidth=0.8)
        ax.errorbar(point, y, xerr=np.vstack([point - low, high - point]), fmt="o", color="#222222", markersize=3, capsize=1.8, linewidth=0.8)
        ax.set_title(title, fontsize=8)
        ax.set_xlabel(r"$\Delta$nAURC (median $-$ comparator)")
        ax.grid(axis="x", color="#E0E0E0", linewidth=0.5)
        ax.set_yticks(y, labels)
    axes[0].text(0.02, -0.08, "Median better", transform=axes[0].transAxes, ha="left", fontsize=6.5)
    axes[0].text(0.98, -0.08, "Comparator better", transform=axes[0].transAxes, ha="right", fontsize=6.5)
    fig.tight_layout(w_pad=1.2)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fidelity_rows() -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for dataset in DATASETS:
        for scale in SCALES:
            sources = sources_for(REPO_ROOT, dataset, scale, expanded=True)
            for canonical, source in sources.items():
                rows: list[pd.DataFrame] = []
                for fold in folds_for(dataset):
                    path = source.run_dir(fold) / "metrics" / "per_case_metrics.csv"
                    frame = _read(path)
                    frame = frame[~frame.method.isin(ANALYTICAL)].copy()
                    if frame.empty:
                        raise ValueError(f"no neural fidelity rows in {path}")
                    rows.append(frame)
                combined = pd.concat(rows, ignore_index=True)
                if combined.case.nunique() != (24 if dataset == "fastmri" else 22):
                    raise ValueError(f"unexpected fidelity case count: {dataset} x{scale} {canonical}")
                records.append(
                    {
                        "dataset": dataset,
                        "scale": scale,
                        "model": canonical,
                        "cases": combined.case.nunique(),
                        "psnr": combined.psnr.mean(),
                        "ssim": combined.ssim.mean(),
                        "mae": combined.mae.mean(),
                        "mse": combined.mse.mean(),
                        "ncc": combined.ncc.mean(),
                        "source_files": ";".join(str(source.run_dir(fold) / "metrics" / "per_case_metrics.csv") for fold in folds_for(dataset)),
                    }
                )
    return pd.DataFrame(records)


def latex_tables(output: Path, paper: Path, aggregate: pd.DataFrame, matched: pd.DataFrame, comparisons: pd.DataFrame, fidelity: pd.DataFrame) -> None:
    table_dir = paper / "tables_icassp"
    table_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Cohort & Factor & $n$ & MAE & $\rho$ & nAURC / RRR50 \\",
        r"\midrule",
    ]
    for _, row in aggregate.iterrows():
        lines.append(
            f"{DISPLAY[row.dataset]} & $\\times${int(row.scale)} & {int(row.cases)} & "
            f"{row.mean_mae:.1f} & {row.case_spearman:.3f} & {row.normalized_aurc:.3f} / {100*row.rrr_50:.1f}\\% \\\\" 
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (table_dir / "cross_scale_summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    matched_primary = matched[matched.method == "target_median"]
    lines = [
        r"\begin{tabular}{llrr}",
        r"\toprule",
        r"Cohort & Factor & Matched advantage [95\% CI] & Row wins \\",
        r"\midrule",
    ]
    for _, row in matched_primary.iterrows():
        lines.append(
            f"{DISPLAY[row.dataset]} & $\\times${int(row.scale)} & "
            f"{row.matched_advantage:.3f} [{row.matched_advantage_ci_low:.3f}, {row.matched_advantage_ci_high:.3f}] & "
            f"{int(row.diagonal_row_wins)}/3 \\\\" 
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (table_dir / "matched_target_summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    aggregate_cmp = comparisons[comparisons.dataset == "aggregate_equal_profile_weight"]
    lines = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Comparator & $\Delta$nAURC [95\% CI] & Profiles \\",
        r"\midrule",
    ]
    for method, label in (("target_mean", "Mean target-to-member"), ("all_output_spread", "All-output spread"), ("target_excluded_spread", "Excluded-committee spread")):
        row = aggregate_cmp[aggregate_cmp.method_b == method].iloc[0]
        lines.append(
            f"{label} & {row.delta_naurc:.3f} [{row.delta_naurc_ci_low:.3f}, {row.delta_naurc_ci_high:.3f}] & {int(row.profiles)} \\\\" 
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (table_dir / "paired_comparison_summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for dataset in DATASETS:
        rows = fidelity[fidelity.dataset == dataset]
        lines = [
            r"\begin{tabular}{llrrrrr}",
            r"\toprule",
            r"Factor & Reconstructor & PSNR & SSIM & MAE & MSE & NCC \\",
            r"\midrule",
        ]
        previous = None
        for _, row in rows.sort_values(["scale", "model"]).iterrows():
            if previous is not None and int(row.scale) != previous:
                lines.append(r"\addlinespace[2pt]")
            lines.append(
                f"$\\times${int(row.scale)} & {DISPLAY[row.model]} & {row.psnr:.2f} & {row.ssim:.3f} & "
                f"{row.mae:.1f} & {row.mse:.1f} & {row.ncc:.3f} \\\\" 
            )
            previous = int(row.scale)
        lines.extend([r"\bottomrule", r"\end{tabular}"])
        (table_dir / f"reconstruction_fidelity_{dataset}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    rho_min, rho_max = aggregate.case_spearman.min(), aggregate.case_spearman.max()
    n_min, n_max = aggregate.normalized_aurc.min(), aggregate.normalized_aurc.max()
    rrr_min, rrr_max = 100 * aggregate.rrr_50.min(), 100 * aggregate.rrr_50.max()
    matched_min, matched_max = matched_primary.matched_advantage.min(), matched_primary.matched_advantage.max()
    mean_cmp = aggregate_cmp[aggregate_cmp.method_b == "target_mean"].iloc[0]
    spread_cmp = aggregate_cmp[aggregate_cmp.method_b == "all_output_spread"].iloc[0]
    macros = "\n".join(
        [
            rf"\newcommand{{\CrossScaleRhoRange}}{{{rho_min:.3f}--{rho_max:.3f}}}",
            rf"\newcommand{{\CrossScaleNAURCRange}}{{{n_min:.3f}--{n_max:.3f}}}",
            rf"\newcommand{{\CrossScaleRRRRange}}{{{rrr_min:.1f}--{rrr_max:.1f}\%}}",
            rf"\newcommand{{\MatchedAdvantageRange}}{{{matched_min:.3f}--{matched_max:.3f}}}",
            rf"\newcommand{{\MedianMeanDelta}}{{{mean_cmp.delta_naurc:.3f} [{mean_cmp.delta_naurc_ci_low:.3f}, {mean_cmp.delta_naurc_ci_high:.3f}]}}",
            rf"\newcommand{{\MedianSpreadDelta}}{{{spread_cmp.delta_naurc:.3f} [{spread_cmp.delta_naurc_ci_low:.3f}, {spread_cmp.delta_naurc_ci_high:.3f}]}}",
        ]
    )
    (table_dir / "multiscale_macros.tex").write_text(macros + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate multiscale paper assets")
    parser.add_argument("--results", type=Path, default=REPO_ROOT / "design/rasinet/outputs/multiscale")
    parser.add_argument("--paper", type=Path, default=REPO_ROOT / "design/rasinet/paper_updated")
    args = parser.parse_args()
    results = args.results.resolve()
    paper = args.paper.resolve()
    aggregate = _read(results / "cross_scale_aggregate.csv")
    primary = _read(results / "cross_scale_primary_results.csv")
    matrix = _read(results / "matched_target_matrix.csv")
    matched = _read(results / "matched_target_summary.csv")
    comparisons = _read(results / "paired_comparisons.csv")
    fidelity = fidelity_rows()
    fidelity.to_csv(results / "reconstruction_fidelity.csv", index=False)
    figure_dir = paper / "figures_icassp"
    cross_scale_figure(aggregate, primary, figure_dir / "cross_scale_figure.pdf")
    matched_heatmap(matrix, figure_dir / "matched_target_heatmap.pdf")
    paired_forest(comparisons, figure_dir / "paired_comparison_forest.pdf")
    latex_tables(results, paper, aggregate, matched, comparisons, fidelity)
    print(f"[assets] wrote figures to {figure_dir}")


if __name__ == "__main__":
    main()
