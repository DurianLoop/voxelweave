from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ixi_diffusion.common import ensure_dir, load_nifti, write_csv

from .committee_experiments import (
    _baseline_path,
    _gt_path,
    _prediction_path,
    profile_sources,
)
from .committee_reliability import target_to_committee_disagreement


REPO_ROOT = Path(__file__).resolve().parents[2]
RASINET_ROOT = REPO_ROOT / "design" / "rasinet"
PROFILES = ("full_test115", "fastmri_full", "ningxia_cv")
COMMITTEE_MODES = ("all", "neural", "analytic")
DATASET_NAMES = {
    "full_test115": "IXI",
    "fastmri_full": "fastMRI",
    "ningxia_cv": "NingXia",
}
METHOD_NAMES = {
    "i3net": "I$^3$Net",
    "hat": "HAT",
    "swinir": "SwinIR",
    "acsinet": "ACSI",
}


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_columns(rows: list[dict], required: set[str], label: str) -> None:
    if not rows:
        raise ValueError(f"{label} is empty")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(sorted(missing))}")


def asset_source_manifest(sources: dict[str, Path]) -> list[dict[str, str]]:
    return [
        {"artifact": artifact, "source_csv": str(path)}
        for artifact, path in sorted(sources.items())
    ]


def _is_main(row: dict) -> bool:
    return (
        row["proxy"] == "target_to_committee"
        and row["committee_mode"] == "all"
        and row["excluded_member"] == ""
    )


def _main_table_rows(summaries: list[dict]) -> list[dict]:
    output = []
    for row in summaries:
        if not _is_main(row):
            continue
        output.append(
            {
                "Dataset": DATASET_NAMES[row["profile"]],
                "Target": METHOD_NAMES.get(row["target"], row["target"]),
                "Cases": int(row["cases"]),
                "PixelCorrFG": float(row["pixel_corr_foreground_mean"]),
                "CaseSpearman": float(row["case_error_uncertainty_spearman"]),
                "NormalizedAURC": float(row["normalized_aurc"]),
                "RRR50": float(row["relative_risk_reduction_at_50"]),
            }
        )
    return output


def _composition_table_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row["analysis"] == "committee_composition":
            grouped[(row["profile"], row["committee_mode"])].append(row)
    output = []
    ordered_groups = sorted(
        grouped.items(),
        key=lambda item: (PROFILES.index(item[0][0]), COMMITTEE_MODES.index(item[0][1])),
    )
    for (profile, mode), selected in ordered_groups:
        output.append(
            {
                "Dataset": DATASET_NAMES[profile],
                "Committee": mode,
                "Targets": len(selected),
                "CaseSpearman": float(np.mean([float(row["case_spearman"]) for row in selected])),
                "NormalizedAURC": float(np.mean([float(row["normalized_aurc"]) for row in selected])),
                "RRR50": float(np.mean([float(row["relative_risk_reduction_at_50"]) for row in selected])),
            }
        )
    return output


def _main_ci_table_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    for row in rows:
        grouped[(row["profile"], row["target"])][row["metric"]] = row
    output = []
    ordered_groups = sorted(grouped.items(), key=lambda item: (PROFILES.index(item[0][0]), item[0][1]))
    for (profile, target), metrics in ordered_groups:
        required = {
            "pixel_corr_mean",
            "case_spearman",
            "normalized_aurc",
            "relative_risk_reduction_at_50",
        }
        if required - set(metrics):
            raise ValueError(f"main CI rows are incomplete for {profile}/{target}")
        output.append(
            {
                "Dataset": DATASET_NAMES[profile],
                "Target": METHOD_NAMES.get(target, target),
                "Cases": int(metrics["pixel_corr_mean"]["cases"]),
                "PixelPoint": float(metrics["pixel_corr_mean"]["point"]),
                "PixelLow": float(metrics["pixel_corr_mean"]["ci95_low"]),
                "PixelHigh": float(metrics["pixel_corr_mean"]["ci95_high"]),
                "SpearmanPoint": float(metrics["case_spearman"]["point"]),
                "SpearmanLow": float(metrics["case_spearman"]["ci95_low"]),
                "SpearmanHigh": float(metrics["case_spearman"]["ci95_high"]),
                "NAURCPoint": float(metrics["normalized_aurc"]["point"]),
                "NAURCLow": float(metrics["normalized_aurc"]["ci95_low"]),
                "NAURCHigh": float(metrics["normalized_aurc"]["ci95_high"]),
                "RRR50Point": float(metrics["relative_risk_reduction_at_50"]["point"]),
                "RRR50Low": float(metrics["relative_risk_reduction_at_50"]["ci95_low"]),
                "RRR50High": float(metrics["relative_risk_reduction_at_50"]["ci95_high"]),
            }
        )
    return output


def _write_main_tex(path: Path, rows: list[dict]) -> None:
    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Dataset & Target & $n$ & Pixel $r$ & Case $\rho$ & nAURC / RRR$_{50}$ \\",
        r"\midrule",
    ]
    previous = None
    for row in rows:
        dataset = row["Dataset"] if row["Dataset"] != previous else ""
        previous = row["Dataset"]
        lines.append(
            f"{dataset} & {row['Target']} & {row['Cases']} & {row['PixelCorrFG']:.3f} & "
            f"{row['CaseSpearman']:.3f} & {row['NormalizedAURC']:.3f} / {100.0 * row['RRR50']:.1f}\\% \\\\" 
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def _write_composition_tex(path: Path, rows: list[dict]) -> None:
    lines = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Dataset & Committee & Targets & Case $\rho$ & nAURC / RRR$_{50}$ \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['Dataset']} & {row['Committee']} & {row['Targets']} & {row['CaseSpearman']:.3f} & "
            f"{row['NormalizedAURC']:.3f} / {100.0 * row['RRR50']:.1f}\\% \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def _write_main_ci_tex(path: Path, rows: list[dict]) -> None:
    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Dataset & Target & $n$ & Pixel $r$ & Case $\rho$ & nAURC / RRR$_{50}$ \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['Dataset']} & {row['Target']} & {row['Cases']} & "
            f"{row['PixelPoint']:.3f} [{row['PixelLow']:.3f},{row['PixelHigh']:.3f}] & "
            f"{row['SpearmanPoint']:.3f} [{row['SpearmanLow']:.3f},{row['SpearmanHigh']:.3f}] & "
            f"{row['NAURCPoint']:.3f} [{row['NAURCLow']:.3f},{row['NAURCHigh']:.3f}] / "
            f"{100.0 * row['RRR50Point']:.1f} [{100.0 * row['RRR50Low']:.1f},{100.0 * row['RRR50High']:.1f}]\\% \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def _plot_framework(output: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 2.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    boxes = [
        (0.01, 0.25, 0.20, 0.50, "Stored outputs\n(target + committee)", "#e8f1f8"),
        (0.29, 0.25, 0.21, 0.50, "Target-specific\nmedian absolute\ndisagreement", "#eef5e9"),
        (0.58, 0.25, 0.18, 0.50, "Pixel map\ncase score", "#fff3d9"),
        (0.84, 0.25, 0.15, 0.50, "Review queue\nrisk--coverage", "#f8e7e7"),
    ]
    for x, y, width, height, text, color in boxes:
        rectangle = plt.Rectangle((x, y), width, height, facecolor=color, edgecolor="#334155", linewidth=1.0)
        ax.add_patch(rectangle)
        ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=7.5)
    for start, end in ((0.21, 0.29), (0.50, 0.58), (0.76, 0.84)):
        ax.annotate("", xy=(end, 0.5), xytext=(start, 0.5), arrowprops={"arrowstyle": "->", "lw": 1.2})
    ax.text(0.39, 0.10, "Ground truth is used for evaluation only", ha="center", va="center", fontsize=8, color="#7f1d1d")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output.with_suffix(".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def _plot_risk(risk_rows: list[dict], output: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.35), sharey=True)
    colors = {"estimated": "#176b87", "oracle": "#238636", "random": "#9ca3af"}
    for axis, profile in zip(axes, PROFILES):
        selected = [
            row
            for row in risk_rows
            if row["profile"] == profile
            and row["proxy"] == "target_to_committee"
            and row["committee_mode"] == "all"
            and row["excluded_member"] == ""
        ]
        targets = sorted({row["target"] for row in selected})
        curves: dict[str, list[np.ndarray]] = defaultdict(list)
        coverage = None
        for target in targets:
            target_rows = [row for row in selected if row["target"] == target]
            random_rows = sorted(
                [row for row in target_rows if row["curve"] == "random"],
                key=lambda row: float(row["coverage"]),
            )
            random = np.asarray([float(row["risk"]) for row in random_rows])
            coverage = np.asarray([float(row["coverage"]) for row in random_rows])
            for curve in ("estimated", "oracle", "random"):
                ordered = sorted(
                    [row for row in target_rows if row["curve"] == curve],
                    key=lambda row: float(row["coverage"]),
                )
                values = np.asarray([float(row["risk"]) for row in ordered])
                curves[curve].append(values / np.maximum(random, 1e-12))
        for curve in ("estimated", "oracle", "random"):
            mean_curve = np.mean(np.stack(curves[curve], axis=0), axis=0)
            axis.plot(coverage, mean_curve, label=curve.capitalize(), color=colors[curve], lw=1.8 if curve == "estimated" else 1.2, linestyle="--" if curve == "random" else "-")
        axis.set_title(DATASET_NAMES[profile], fontsize=9)
        axis.set_xlabel("Coverage", fontsize=8)
        axis.grid(alpha=0.2, linewidth=0.5)
        axis.tick_params(labelsize=7)
    axes[0].set_ylabel("Retained MAE / random MAE", fontsize=8)
    axes[-1].legend(frameon=False, fontsize=7, loc="lower right")
    fig.tight_layout(w_pad=0.8)
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output.with_suffix(".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def _plot_composition(rows: list[dict], output: Path) -> None:
    selected = [row for row in rows if row["analysis"] == "committee_composition"]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.35), sharey=True)
    modes = ("all", "neural", "analytic")
    colors = ("#176b87", "#d97706", "#6b7280")
    for axis, profile in zip(axes, PROFILES):
        profile_rows = [row for row in selected if row["profile"] == profile]
        targets = sorted({row["target"] for row in profile_rows})
        x = np.arange(len(targets))
        width = 0.24
        for offset, (mode, color) in enumerate(zip(modes, colors)):
            values = [
                float(next(row for row in profile_rows if row["target"] == target and row["committee_mode"] == mode)["normalized_aurc"])
                for target in targets
            ]
            axis.bar(x + (offset - 1) * width, values, width=width, label=mode.capitalize(), color=color)
        axis.set_xticks(x, [METHOD_NAMES.get(target, target) for target in targets], fontsize=7)
        axis.set_title(DATASET_NAMES[profile], fontsize=9)
        axis.grid(axis="y", alpha=0.2, linewidth=0.5)
        axis.tick_params(axis="y", labelsize=7)
    axes[0].set_ylabel("Normalized AURC (lower is better)", fontsize=8)
    axes[-1].legend(frameon=False, fontsize=7)
    fig.tight_layout(w_pad=0.8)
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output.with_suffix(".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def _visual_case_selection(rows: list[dict]) -> list[tuple[str, dict]]:
    selected = [
        row
        for row in rows
        if row["target"] == "swinir"
        and row["proxy"] == "target_to_committee"
        and row["committee_mode"] == "all"
        and row["excluded_member"] == ""
    ]
    if len(selected) < 8:
        raise ValueError("at least eight IXI SwinIR cases are required for qualitative selection")
    by_score = sorted(selected, key=lambda row: float(row["mean_uncertainty"]))
    quartile = max(2, len(selected) // 4)
    high_score = max(by_score[-quartile:], key=lambda row: float(row["mean_abs_error"]))
    low_score = min(by_score[:quartile], key=lambda row: float(row["mean_abs_error"]))
    error_ranks = {
        row["case"]: rank
        for rank, row in enumerate(sorted(selected, key=lambda row: float(row["mean_abs_error"])))
    }
    score_ranks = {row["case"]: rank for rank, row in enumerate(by_score)}
    reserved = {high_score["case"], low_score["case"]}
    missed = max(
        [row for row in selected if row["case"] not in reserved],
        key=lambda row: error_ranks[row["case"]] - score_ranks[row["case"]],
    )
    return [
        ("Flagged high-error", high_score),
        ("Retained low-error", low_score),
        ("False reassurance", missed),
    ]


def _plot_qualitative(per_case_rows: list[dict], output: Path) -> None:
    sources = profile_sources(REPO_ROOT, "full_test115")
    reference = sources[0]
    target_source = next(source for source in sources if source.name == "swinir")
    selections = _visual_case_selection(per_case_rows)
    fig, axes = plt.subplots(len(selections), 4, figsize=(7.2, 5.0))
    column_titles = ("Ground truth", "SwinIR", "Absolute error", "Disagreement")
    for axis, title in zip(axes[0], column_titles):
        axis.set_title(title, fontsize=9)
    for row_index, (category, row) in enumerate(selections):
        case_name = row["case"]
        gt, _, _ = load_nifti(_gt_path(reference, None, case_name, "full_test115"))
        prediction, _, _ = load_nifti(_prediction_path(target_source, None, case_name))
        members = []
        linear, _, _ = load_nifti(_baseline_path(reference, None, "linear", case_name))
        cubic, _, _ = load_nifti(_baseline_path(reference, None, "cubic", case_name))
        members.extend([linear, cubic])
        for source in sources:
            if source.name == "swinir":
                continue
            member, _, _ = load_nifti(_prediction_path(source, None, case_name))
            members.append(member)
        disagreement = target_to_committee_disagreement(prediction, members)
        generated = [index for index in range(gt.shape[2]) if index % 4 != 0]
        slice_errors = [float(np.mean(np.abs(prediction[:, :, index] - gt[:, :, index]))) for index in generated]
        slice_index = generated[int(np.argmax(slice_errors))]
        gt_slice = gt[:, :, slice_index]
        pred_slice = prediction[:, :, slice_index]
        error_slice = np.abs(pred_slice - gt_slice)
        disagreement_slice = disagreement[:, :, slice_index]
        finite_intensity = gt_slice[np.isfinite(gt_slice)]
        intensity_lo, intensity_hi = np.percentile(finite_intensity, [1.0, 99.0])
        heat_hi = max(
            float(np.percentile(error_slice[np.isfinite(error_slice)], 99.0)),
            float(np.percentile(disagreement_slice[np.isfinite(disagreement_slice)], 99.0)),
            1e-6,
        )
        images = (
            (gt_slice, "gray", intensity_lo, intensity_hi),
            (pred_slice, "gray", intensity_lo, intensity_hi),
            (error_slice, "magma", 0.0, heat_hi),
            (disagreement_slice, "magma", 0.0, heat_hi),
        )
        for axis, (image, cmap, vmin, vmax) in zip(axes[row_index], images):
            axis.imshow(np.rot90(image), cmap=cmap, vmin=vmin, vmax=vmax)
            axis.axis("off")
        axes[row_index, 0].text(
            -0.08,
            0.5,
            f"{category}\nMAE={float(row['mean_abs_error']):.2f}\nscore={float(row['mean_uncertainty']):.2f}",
            transform=axes[row_index, 0].transAxes,
            ha="right",
            va="center",
            fontsize=7,
        )
    fig.tight_layout(h_pad=0.3, w_pad=0.15)
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output.with_suffix(".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def build_assets() -> Path:
    paper_root = ensure_dir(RASINET_ROOT / "paper")
    table_root = ensure_dir(paper_root / "tables")
    figure_root = ensure_dir(paper_root / "figures")
    source_root = ensure_dir(figure_root / "source_data")
    report_root = RASINET_ROOT / "reports" / "committee_reliability"

    summaries: list[dict] = []
    risk_rows: list[dict] = []
    sources: dict[str, Path] = {}
    for profile in PROFILES:
        metrics_root = RASINET_ROOT / "runs" / "committee_reliability" / profile / "metrics"
        summary_path = metrics_root / "summary_committee.csv"
        risk_path = metrics_root / "risk_coverage_committee.csv"
        summaries.extend(_read_csv(summary_path))
        risk_rows.extend(_read_csv(risk_path))
        sources[f"summary_{profile}"] = summary_path
        sources[f"risk_{profile}"] = risk_path
    composition_path = report_root / "committee_composition.csv"
    composition = _read_csv(composition_path)
    sources["committee_composition"] = composition_path
    main_ci_path = report_root / "main_bootstrap_ci.csv"
    main_ci = _read_csv(main_ci_path)
    sources["main_bootstrap_ci"] = main_ci_path

    require_columns(
        summaries,
        {
            "profile",
            "target",
            "proxy",
            "committee_mode",
            "excluded_member",
            "pixel_corr_foreground_mean",
            "case_error_uncertainty_spearman",
            "normalized_aurc",
            "relative_risk_reduction_at_50",
        },
        "committee summary",
    )
    require_columns(composition, {"profile", "target", "analysis", "committee_mode", "normalized_aurc"}, "composition")

    main_rows = _main_table_rows(summaries)
    composition_rows = _composition_table_rows(composition)
    main_ci_rows = _main_ci_table_rows(main_ci)
    write_csv(table_root / "table_committee_main.csv", main_rows)
    write_csv(table_root / "table_committee_composition.csv", composition_rows)
    write_csv(table_root / "supp_table_main_ci.csv", main_ci_rows)
    _write_main_tex(table_root / "table_committee_main.tex", main_rows)
    _write_composition_tex(table_root / "table_committee_composition.tex", composition_rows)
    _write_main_ci_tex(table_root / "supp_table_main_ci.tex", main_ci_rows)

    write_csv(source_root / "figure_committee_risk.csv", risk_rows)
    write_csv(source_root / "figure_committee_composition.csv", composition)
    write_csv(paper_root / "asset_source_manifest.csv", asset_source_manifest(sources))
    _plot_framework(figure_root / "figure1_framework_compact")
    _plot_risk(risk_rows, figure_root / "figure2_committee_risk")
    _plot_composition(composition, figure_root / "figure3_committee_composition")
    ixi_per_case = _read_csv(
        RASINET_ROOT / "runs" / "committee_reliability" / "full_test115" / "metrics" / "per_case_committee.csv"
    )
    _plot_qualitative(ixi_per_case, figure_root / "figure4_committee_qualitative")
    return paper_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate compact committee-reliability paper assets.")
    parser.parse_args()
    output = build_assets()
    print(f"Wrote compact paper assets to {output}")


if __name__ == "__main__":
    main()
