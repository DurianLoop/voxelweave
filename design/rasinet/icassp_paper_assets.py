from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle
from scipy import stats


REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_ROOT = REPO_ROOT / "design" / "rasinet" / "paper"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _primary(row: dict[str, str]) -> bool:
    return (
        row["analysis"] == "score_variants"
        and row["score"] == "target_abs_median"
        and row["mask"] == "target_0.01"
        and row["normalization"] == "raw"
        and row["subset_id"] == "full"
    )


def _dataset(value: str) -> str:
    return {"ixi": "IXI", "fastmri": "fastMRI-brain", "ningxia": "NingXia"}.get(value, value)


def _target(value: str) -> str:
    return {"i3net": r"I$^3$Net", "hat": "HAT", "swinir": "SwinIR", "acsinet": "ACSI"}.get(value, value)


def _ci(row: dict[str, str], metric: str, digits: int = 3) -> str:
    point = float(row[f"{metric}_point"])
    low = float(row[f"{metric}_ci95_low"])
    high = float(row[f"{metric}_ci95_high"])
    return f"{point:.{digits}f} [{low:.{digits}f}, {high:.{digits}f}]"


def _main_table(rows: list[dict[str, str]], output: Path) -> None:
    selected = sorted((row for row in rows if _primary(row)), key=lambda row: (row["dataset"], row["target"]))
    lines = [
        r"\begin{tabular}{llrrrrrr}",
        r"\toprule",
        r"Dataset & Target & $n$ & Pixel $r_z$ & Case $\rho$ [95\% CI] & nAURC [95\% CI] & RRR$_{50}$ & MAE$_{50}$ \\",
        r"\midrule",
    ]
    previous = None
    for row in selected:
        if previous is not None and previous != row["dataset"]:
            lines.append(r"\midrule")
        lines.append(
            " & ".join(
                (
                    _dataset(row["dataset"]),
                    _target(row["target"]),
                    row["cases"],
                    f"{float(row['pixel_fisher_z_mean']):.3f}",
                    _ci(row, "case_spearman"),
                    _ci(row, "normalized_aurc"),
                    f"{100 * float(row['rrr_50']):.1f}\\%",
                    f"{float(row['retained_mae_50']):.2f}",
                )
            )
            + r" \\"
        )
        previous = row["dataset"]
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _failure_table(rows: list[dict[str, str]], output: Path) -> None:
    selected = sorted((row for row in rows if _primary(row)), key=lambda row: (row["dataset"], row["target"]))
    lines = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Dataset & Target & Positives & AUROC [95\% CI] & AUPRC [95\% CI] \\",
        r"\midrule",
    ]
    previous = None
    for row in selected:
        if previous is not None and previous != row["dataset"]:
            lines.append(r"\midrule")
        positives = max(1, int(np.ceil(0.10 * int(row["cases"]))))
        lines.append(
            " & ".join(
                (
                    _dataset(row["dataset"]),
                    _target(row["target"]),
                    str(positives),
                    _ci(row, "failure_auroc"),
                    _ci(row, "failure_auprc"),
                )
            )
            + r" \\"
        )
        previous = row["dataset"]
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _pixel_support_table(rows: list[dict[str, str]], output: Path, source_root: Path) -> None:
    selected = [row for row in rows if _primary(row)]
    aggregate = _aggregate(
        selected,
        ("dataset",),
        ("pixel_fisher_z_mean", "all_pixel_fisher_z_mean"),
    )
    _write_csv(source_root / "pixel_foreground_vs_all.csv", aggregate)
    lines = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Dataset & Foreground $r_z$ & All-pixel $r_z$ & Difference \\",
        r"\midrule",
    ]
    for row in aggregate:
        foreground = float(row["pixel_fisher_z_mean_mean"])
        all_pixel = float(row["all_pixel_fisher_z_mean_mean"])
        lines.append(
            f"{_dataset(str(row['dataset']))} & {foreground:.3f} & {all_pixel:.3f} & {all_pixel - foreground:+.3f} \\\\"
        )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _result_macros(rows: list[dict[str, str]], output: Path) -> None:
    selected = [row for row in rows if _primary(row)]
    metrics = {
        "PixelFisher": ("pixel_fisher_z_mean", 3, 1.0),
        "CaseSpearman": ("case_spearman", 3, 1.0),
        "NAURC": ("normalized_aurc", 3, 1.0),
        "RRRFifty": ("rrr_50", 1, 100.0),
    }
    lines = ["% Automatically generated from outputs/icassp_primary/summary.csv."]
    for name, (metric, digits, scale) in metrics.items():
        values = np.asarray([float(row[metric]) * scale for row in selected])
        suffix = r"\%" if scale == 100.0 else ""
        lines.append(f"\\newcommand{{\\{name}Range}}{{{np.min(values):.{digits}f}--{np.max(values):.{digits}f}{suffix}}}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stress_macros(output: Path) -> None:
    path = REPO_ROOT / "design" / "rasinet" / "outputs" / "shared_error_stress" / "summary.csv"
    if not path.exists():
        output.write_text("% Shared-error experiment has not completed.\n", encoding="utf-8")
        return
    rows = _read(path)
    lookup = {(row["mode"], float(row["strength"]), row["metric"]): float(row["mean"]) for row in rows}
    base_mae = lookup[("target_specific", 0.0, "foreground_mae")]
    final_mae = lookup[("target_specific", 1.0, "foreground_mae")]
    base_target = lookup[("target_specific", 0.0, "disagreement")]
    final_target = lookup[("target_specific", 1.0, "disagreement")]
    base_shared = lookup[("shared", 0.0, "disagreement")]
    final_shared = lookup[("shared", 1.0, "disagreement")]
    base_committee_mae = lookup[("shared", 0.0, "committee_foreground_mae")]
    final_committee_mae = lookup[("shared", 1.0, "committee_foreground_mae")]
    lines = [
        "% Automatically generated from outputs/shared_error_stress/summary.csv.",
        f"\\newcommand{{\\StressMaeIncrease}}{{{100 * (final_mae / base_mae - 1):.1f}\\%}}",
        f"\\newcommand{{\\StressTargetIncrease}}{{{100 * (final_target / base_target - 1):.1f}\\%}}",
        f"\\newcommand{{\\StressSharedChange}}{{{100 * (final_shared / base_shared - 1):.1f}\\%}}",
        f"\\newcommand{{\\StressCommitteeMaeIncrease}}{{{100 * (final_committee_mae / base_committee_mae - 1):.1f}\\%}}",
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _aggregate(rows: list[dict[str, str]], keys: tuple[str, ...], metrics: tuple[str, ...]) -> list[dict[str, object]]:
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    output: list[dict[str, object]] = []
    for key, selected in sorted(groups.items()):
        result: dict[str, object] = dict(zip(keys, key))
        result["groups"] = len(selected)
        for metric in metrics:
            values = np.asarray([float(row[metric]) for row in selected])
            result[f"{metric}_mean"] = float(np.mean(values))
            result[f"{metric}_median"] = float(np.median(values))
            result[f"{metric}_min"] = float(np.min(values))
            result[f"{metric}_max"] = float(np.max(values))
        output.append(result)
    return output


def _sensitivity_tables(rows: list[dict[str, str]], table_root: Path, source_root: Path) -> None:
    definitions = {
        "score_variants": ("score",),
        "normalization": ("normalization",),
        "mask": ("mask",),
    }
    for analysis, variant_keys in definitions.items():
        selected = [row for row in rows if row["analysis"] == analysis and row["subset_id"] == "full"]
        aggregate = _aggregate(
            selected,
            ("dataset",) + variant_keys,
            ("case_spearman", "normalized_aurc", "rrr_50"),
        )
        _write_csv(source_root / f"{analysis}_aggregate.csv", aggregate)
        lines = [r"\begin{tabular}{llrrr}", r"\toprule", r"Dataset & Variant & $\rho$ & nAURC & RRR$_{50}$ \\", r"\midrule"]
        for row in aggregate:
            variant = str(row[variant_keys[0]]).replace("_", r"\_")
            lines.append(
                f"{_dataset(str(row['dataset']))} & {variant} & "
                f"{float(row['case_spearman_mean']):.3f} & {float(row['normalized_aurc_mean']):.3f} & "
                f"{100 * float(row['rrr_50_mean']):.1f}\\% \\\\"
            )
        lines.extend((r"\bottomrule", r"\end{tabular}"))
        (table_root / f"table_{analysis}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _paired_score_table(results: Path, table_root: Path, source_root: Path) -> None:
    rows = _read(results / "paired_primary_comparisons.csv")
    selected = [
        row
        for row in rows
        if row["analysis"] == "score_variants"
        and row["metric"] == "normalized_aurc"
        and row["subset_id"] == "full"
        and row["score"] != "target_abs_median"
    ]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected:
        grouped[row["score"]].append(row)
    source: list[dict[str, object]] = []
    for score, group in sorted(grouped.items()):
        source.append(
            {
                "score": score,
                "profiles": len(group),
                "delta_naurc_mean": float(np.mean([float(row["variant_minus_primary"]) for row in group])),
                "variant_better_ci": sum(float(row["difference_ci95_high"]) < 0.0 for row in group),
                "inconclusive_ci": sum(
                    float(row["difference_ci95_low"]) <= 0.0 <= float(row["difference_ci95_high"])
                    for row in group
                ),
                "primary_better_ci": sum(float(row["difference_ci95_low"]) > 0.0 for row in group),
                "rank_stability_median": float(np.median([float(row["score_rank_stability"]) for row in group])),
            }
        )
    _write_csv(source_root / "score_variant_paired_summary.csv", source)
    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Variant & Mean $\Delta$nAURC & Better & Inconclusive & Worse & Median stability \\",
        r"\midrule",
    ]
    for row in source:
        lines.append(
            f"{str(row['score']).replace('_', r'\_')} & {float(row['delta_naurc_mean']):+.3f} & "
            f"{row['variant_better_ci']} & {row['inconclusive_ci']} & {row['primary_better_ci']} & "
            f"{float(row['rank_stability_median']):.3f} \\\\"
        )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (table_root / "table_score_paired.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stability_tables(results: Path, table_root: Path, source_root: Path) -> None:
    paired = _read(results / "paired_primary_comparisons.csv")
    profile_dataset = {"full_test115": "ixi", "fastmri_full": "fastmri", "ningxia_cv": "ningxia"}
    normalization_rows = [
        {**row, "dataset": profile_dataset[row["profile"]]}
        for row in paired
        if row["analysis"] == "normalization"
        and row["metric"] == "normalized_aurc"
        and row["subset_id"] == "full"
    ]
    norm_aggregate = _aggregate(
        normalization_rows,
        ("dataset", "normalization"),
        ("variant_minus_primary", "score_rank_stability"),
    )
    _write_csv(source_root / "normalization_stability.csv", norm_aggregate)
    norm_lines = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Dataset & Normalization & Mean $\Delta$nAURC & Mean stability & Minimum \\",
        r"\midrule",
    ]
    for row in norm_aggregate:
        norm_lines.append(
            f"{_dataset(str(row['dataset']))} & {str(row['normalization']).replace('_', r'\_')} & "
            f"{float(row['variant_minus_primary_mean']):+.3f} & "
            f"{float(row['score_rank_stability_mean']):.3f} & "
            f"{float(row['score_rank_stability_min']):.3f} \\\\"
        )
    norm_lines.extend((r"\bottomrule", r"\end{tabular}"))
    (table_root / "table_normalization_stability.tex").write_text("\n".join(norm_lines) + "\n", encoding="utf-8")

    per_case = _read(results / "per_case.csv")
    primary: dict[tuple[str, str, str], float] = {}
    for row in per_case:
        if _primary(row):
            primary[(row["profile"], row["target"], row["case"])] = float(row["case_score"])
    mask_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in per_case:
        if row["analysis"] == "mask" and row["subset_id"] == "full":
            mask_groups[(row["dataset"], row["target"], row["mask"])].append(row)
    mask_target_rows: list[dict[str, object]] = []
    for (dataset, target, mask), group in sorted(mask_groups.items()):
        group = sorted(group, key=lambda row: row["case"])
        base = np.asarray([primary[(row["profile"], target, row["case"])] for row in group])
        variant = np.asarray([float(row["case_score"]) for row in group])
        stability = 0.0 if np.std(base) <= 1e-12 or np.std(variant) <= 1e-12 else float(stats.spearmanr(base, variant).statistic)
        mask_target_rows.append({"dataset": dataset, "target": target, "mask": mask, "score_rank_stability": stability})
    mask_aggregate = _aggregate(mask_target_rows, ("dataset", "mask"), ("score_rank_stability",))
    _write_csv(source_root / "mask_score_stability.csv", mask_aggregate)
    mask_lines = [
        r"\begin{tabular}{llrr}",
        r"\toprule",
        r"Dataset & Mask & Mean stability & Minimum \\",
        r"\midrule",
    ]
    for row in mask_aggregate:
        mask_lines.append(
            f"{_dataset(str(row['dataset']))} & {str(row['mask']).replace('_', r'\_')} & "
            f"{float(row['score_rank_stability_mean']):.3f} & {float(row['score_rank_stability_min']):.3f} \\\\"
        )
    mask_lines.extend((r"\bottomrule", r"\end{tabular}"))
    (table_root / "table_mask_stability.tex").write_text("\n".join(mask_lines) + "\n", encoding="utf-8")


def _committee_size(rows: list[dict[str, str]], table_root: Path, figure_root: Path, source_root: Path) -> None:
    selected = [row for row in rows if row["analysis"] == "committee_subset"]
    aggregate = _aggregate(selected, ("dataset", "committee_size"), ("normalized_aurc", "case_spearman", "rrr_50"))
    aggregate.sort(key=lambda row: (str(row["dataset"]), int(str(row["committee_size"]))))
    _write_csv(source_root / "committee_size_aggregate.csv", aggregate)
    diversity_rows: list[dict[str, object]] = []
    for dataset in sorted({row["dataset"] for row in selected}):
        data = [row for row in selected if row["dataset"] == dataset and int(row["committee_size"]) >= 2]
        diversity = np.asarray([float(row["committee_diversity_mean"]) for row in data])
        performance = np.asarray([float(row["normalized_aurc"]) for row in data])
        correlation = float(stats.spearmanr(diversity, performance).statistic) if len(data) >= 2 else float("nan")
        diversity_rows.append({"dataset": dataset, "subset_target_groups": len(data), "spearman_diversity_vs_naurc": correlation})
    _write_csv(source_root / "committee_diversity_relation.csv", diversity_rows)
    diversity_lines = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Dataset & Subset--target groups & $\rho$(diversity, nAURC) \\",
        r"\midrule",
    ]
    for row in diversity_rows:
        diversity_lines.append(
            f"{_dataset(str(row['dataset']))} & {row['subset_target_groups']} & "
            f"{float(row['spearman_diversity_vs_naurc']):.3f} \\\\"
        )
    diversity_lines.extend((r"\bottomrule", r"\end{tabular}"))
    (table_root / "table_committee_diversity.tex").write_text("\n".join(diversity_lines) + "\n", encoding="utf-8")
    lines = [r"\begin{tabular}{lrrrr}", r"\toprule", r"Dataset & $k$ & Mean nAURC & Median & Range \\", r"\midrule"]
    for row in aggregate:
        lines.append(
            f"{_dataset(str(row['dataset']))} & {row['committee_size']} & "
            f"{float(row['normalized_aurc_mean']):.3f} & {float(row['normalized_aurc_median']):.3f} & "
            f"{float(row['normalized_aurc_min']):.3f}--{float(row['normalized_aurc_max']):.3f} \\\\"
        )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (table_root / "table_committee_size.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    figure, axis = plt.subplots(figsize=(3.35, 2.25))
    styles = {"ixi": ("#0072B2", "o"), "fastmri": ("#009E73", "s"), "ningxia": ("#D55E00", "^")}
    for dataset, (color, marker) in styles.items():
        data = [row for row in aggregate if row["dataset"] == dataset]
        x = np.asarray([int(str(row["committee_size"])) for row in data])
        y = np.asarray([float(row["normalized_aurc_mean"]) for row in data])
        low = np.asarray([float(row["normalized_aurc_min"]) for row in data])
        high = np.asarray([float(row["normalized_aurc_max"]) for row in data])
        axis.errorbar(x, y, yerr=np.vstack((y - low, high - y)), color=color, marker=marker, capsize=2, label=_dataset(dataset))
    axis.axhline(1.0, color="#666666", linestyle=":", linewidth=0.8)
    axis.set_xlabel("Committee size $k$")
    axis.set_ylabel("nAURC (lower is better)")
    axis.grid(True, color="#D0D0D0", linewidth=0.5)
    axis.legend(frameon=False, fontsize=7)
    figure.tight_layout(pad=0.5)
    figure.savefig(figure_root / "figure_committee_size.pdf", bbox_inches="tight")
    plt.close(figure)


def _committee_composition(rows: list[dict[str, str]], table_root: Path, source_root: Path) -> None:
    selected = [row for row in rows if row["analysis"] == "committee_subset"]
    max_size = {
        (row["dataset"], row["target"]): max(
            int(other["committee_size"])
            for other in selected
            if other["dataset"] == row["dataset"] and other["target"] == row["target"]
        )
        for row in selected
    }
    categorized: list[dict[str, str]] = []
    for row in selected:
        names = set(row["committee"].split(";"))
        analytical = names & {"linear", "cubic"}
        neural_count = len(names - analytical)
        if int(row["committee_size"]) == max_size[(row["dataset"], row["target"])]:
            category = "full"
        elif neural_count == 0:
            category = "analytical-only"
        elif neural_count == 1 and not analytical:
            category = "one neural"
        elif neural_count == 1 and analytical == {"linear"}:
            category = "one neural + linear"
        elif neural_count == 1 and analytical == {"cubic"}:
            category = "one neural + cubic"
        elif neural_count == 1 and analytical == {"linear", "cubic"}:
            category = "one neural + linear + cubic"
        elif neural_count == 2 and not analytical:
            category = "two neural"
        elif neural_count == 2 and len(analytical) == 1:
            category = "two neural + one analytical"
        else:
            continue
        categorized.append({**row, "deployment_category": category})
    aggregate = _aggregate(
        categorized,
        ("dataset", "deployment_category"),
        ("normalized_aurc", "case_spearman", "rrr_50"),
    )
    order = {
        "one neural": 0,
        "analytical-only": 1,
        "one neural + linear": 2,
        "one neural + cubic": 3,
        "one neural + linear + cubic": 4,
        "two neural": 5,
        "two neural + one analytical": 6,
        "full": 7,
    }
    aggregate.sort(key=lambda row: (str(row["dataset"]), order[str(row["deployment_category"])]))
    _write_csv(source_root / "committee_composition_deployment.csv", aggregate)
    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Dataset & Composition & Groups & Mean nAURC & Median & Worst \\",
        r"\midrule",
    ]
    previous = None
    for row in aggregate:
        if previous is not None and previous != row["dataset"]:
            lines.append(r"\midrule")
        lines.append(
            f"{_dataset(str(row['dataset']))} & {str(row['deployment_category']).replace(' + ', r' $+$ ')} & "
            f"{row['groups']} & {float(row['normalized_aurc_mean']):.3f} & "
            f"{float(row['normalized_aurc_median']):.3f} & {float(row['normalized_aurc_max']):.3f} \\\\"
        )
        previous = row["dataset"]
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (table_root / "table_committee_composition.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _key_ablation_table(rows: list[dict[str, str]], table_root: Path, source_root: Path) -> None:
    """Compact manuscript view; complete variants remain in generated CSV tables."""
    score_rows = [row for row in rows if row["analysis"] == "score_variants"]
    subset_rows = [row for row in rows if row["analysis"] == "committee_subset"]
    output: list[dict[str, object]] = []
    for dataset in sorted({row["dataset"] for row in rows}):
        result: dict[str, object] = {"dataset": dataset}
        for score, label in (
            ("target_abs_median", "median_naurc"),
            ("target_abs_mean", "mean_naurc"),
            ("shared_std", "shared_std_naurc"),
        ):
            values = [
                float(row["normalized_aurc"])
                for row in score_rows
                if row["dataset"] == dataset and row["score"] == score
            ]
            result[label] = float(np.mean(values))

        target_groups = sorted({row["target"] for row in subset_rows if row["dataset"] == dataset})
        neural_values: list[float] = []
        analytical_values: list[float] = []
        for target in target_groups:
            selected = [
                row for row in subset_rows
                if row["dataset"] == dataset and row["target"] == target
            ]
            neural = [row for row in selected if str(row["composition"]).startswith("neural_")]
            analytical = [row for row in selected if str(row["composition"]).startswith("analytical_")]
            max_neural = max(int(row["committee_size"]) for row in neural)
            max_analytical = max(int(row["committee_size"]) for row in analytical)
            neural_values.extend(
                float(row["normalized_aurc"])
                for row in neural if int(row["committee_size"]) == max_neural
            )
            analytical_values.extend(
                float(row["normalized_aurc"])
                for row in analytical if int(row["committee_size"]) == max_analytical
            )
        result["neural_only_naurc"] = float(np.mean(neural_values))
        result["analytical_only_naurc"] = float(np.mean(analytical_values))
        result["full_naurc"] = result["median_naurc"]
        output.append(result)
    _write_csv(source_root / "key_ablation_summary.csv", output)
    lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Dataset & Median & Mean & Shared std. & Neural-only & Analytical-only & Full \\",
        r"\midrule",
    ]
    for row in output:
        lines.append(
            f"{_dataset(str(row['dataset']))} & {float(row['median_naurc']):.3f} & "
            f"{float(row['mean_naurc']):.3f} & {float(row['shared_std_naurc']):.3f} & "
            f"{float(row['neural_only_naurc']):.3f} & {float(row['analytical_only_naurc']):.3f} & "
            f"{float(row['full_naurc']):.3f} \\\\"
        )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (table_root / "table_key_ablations.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    regular_lines = [
        r"\begin{tabular}{lll}",
        r"\toprule",
        r"Dataset & Score nAURC: med./mean/std. & Committee nAURC: neural/analytic/full \\",
        r"\midrule",
    ]
    for row in output:
        regular_lines.append(
            f"{_dataset(str(row['dataset']))} & "
            f"{float(row['median_naurc']):.3f}/{float(row['mean_naurc']):.3f}/{float(row['shared_std_naurc']):.3f} & "
            f"{float(row['neural_only_naurc']):.3f}/{float(row['analytical_only_naurc']):.3f}/{float(row['full_naurc']):.3f} \\\\"
        )
    regular_lines.extend((r"\bottomrule", r"\end{tabular}"))
    (table_root / "table_key_ablations_regular.tex").write_text(
        "\n".join(regular_lines) + "\n", encoding="utf-8"
    )


def _risk_coverage(risk_rows: list[dict[str, str]], summary_rows: list[dict[str, str]], figure_root: Path, source_root: Path) -> None:
    primary_keys = {
        (row["profile"], row["target"], row["analysis"], row["score"], row["mask"], row["normalization"], row["committee"], row["subset_id"])
        for row in summary_rows if _primary(row)
    }
    selected = [
        row for row in risk_rows
        if (row["profile"], row["target"], row["analysis"], row["score"], row["mask"], row["normalization"], row["committee"], row["subset_id"]) in primary_keys
    ]
    full_risk: dict[tuple[str, str, str], float] = {}
    for row in selected:
        if abs(float(row["coverage"]) - 1.0) < 1e-8:
            full_risk[(row["profile"], row["target"], row["curve"])] = float(row["risk"])
    source: list[dict[str, object]] = []
    grouped: dict[tuple[str, str, float], list[float]] = defaultdict(list)
    for row in selected:
        normalizer = full_risk[(row["profile"], row["target"], "random")]
        grouped[(row["profile"], row["curve"], float(row["coverage"]))].append(float(row["risk"]) / normalizer)
    for (profile, curve, coverage), values in sorted(grouped.items()):
        source.append({"profile": profile, "curve": curve, "coverage": coverage, "mean_normalized_risk": float(np.mean(values))})
    _write_csv(source_root / "risk_coverage_primary_aggregate.csv", source)

    profiles = (("full_test115", "IXI"), ("fastmri_full", "fastMRI-brain"), ("ningxia_cv", "NingXia"))
    styles = {"estimated": ("#0072B2", "-", "Disagreement"), "oracle": ("#222222", "--", "Oracle"), "random": ("#777777", ":", "Random")}
    figure, axes = plt.subplots(1, 3, figsize=(7.1, 2.15), sharey=True)
    for axis, (profile, title) in zip(axes, profiles):
        for curve, (color, linestyle, label) in styles.items():
            data = sorted((row for row in source if row["profile"] == profile and row["curve"] == curve), key=lambda row: float(row["coverage"]))
            axis.plot([float(row["coverage"]) for row in data], [float(row["mean_normalized_risk"]) for row in data], color=color, linestyle=linestyle, linewidth=1.25, label=label)
        axis.set_title(title, fontsize=9)
        axis.set_xlabel("Retained coverage")
        axis.grid(True, color="#D0D0D0", linewidth=0.45)
    axes[0].set_ylabel("Retained MAE / full-cohort MAE")
    axes[-1].legend(frameon=False, fontsize=7, loc="upper left")
    figure.tight_layout(pad=0.4, w_pad=0.6)
    figure.savefig(figure_root / "figure_risk_coverage.pdf", bbox_inches="tight")
    plt.close(figure)


def _framework(figure_root: Path) -> None:
    figure, axis = plt.subplots(figsize=(3.45, 1.95))
    axis.set_xlim(0, 7.0)
    axis.set_ylim(0, 4.0)
    axis.axis("off")
    boxes = [
        (0.05, 2.35, 1.25, 0.72, "Sparse input\n$x$", "#E8F1F8"),
        (1.75, 3.05, 1.45, 0.68, "Target $m$\n$\\hat y_m$", "#DCEAF5"),
        (1.75, 1.75, 1.45, 0.68, "Committee $\\mathcal{C}_m$\n$m$ excluded", "#F1ECE3"),
        (3.75, 2.35, 1.75, 0.72, "Target-to-committee\ndisagreement $U_m$", "#E7EFE8"),
        (0.45, 0.45, 1.45, 0.72, "Foreground\naggregation", "#F3E8E5"),
        (2.75, 0.45, 1.25, 0.72, "Examination score\n$s_m$", "#E9E5F1"),
        (5.0, 0.45, 1.25, 0.72, "Selective-review\nqueue", "#ECECEC"),
    ]
    for x, y, width, height, label, color in boxes:
        axis.add_patch(Rectangle((x, y), width, height, facecolor=color, edgecolor="#444444", linewidth=0.8))
        axis.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=8.0)
    arrows = [
        ((1.30, 2.71), (1.75, 3.39)),
        ((1.30, 2.71), (1.75, 2.09)),
        ((3.20, 3.39), (3.75, 2.71)),
        ((3.20, 2.09), (3.75, 2.71)),
        ((4.62, 2.35), (1.18, 1.17)),
        ((1.90, 0.81), (2.75, 0.81)),
        ((4.00, 0.81), (5.00, 0.81)),
    ]
    for start, end in arrows:
        axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=8, color="#444444", linewidth=0.8))
    axis.text(3.5, 0.05, "Ground truth is isolated and used only for offline evaluation", ha="center", va="bottom", fontsize=7.3, color="#555555")
    figure.tight_layout(pad=0.1)
    figure.savefig(figure_root / "figure_framework.pdf", bbox_inches="tight")
    plt.close(figure)


def _cost_table(results: Path, summary_rows: list[dict[str, str]], table_root: Path, source_root: Path) -> None:
    manifests = _read(results / "input_manifest.csv")
    per_case = _read(results / "per_case.csv")
    primary = [row for row in per_case if _primary(row)]
    memory_path = results / "process_memory_summary.json"
    if not memory_path.exists():
        memory_path = results / "process_memory_single_worker_summary.json"
    memory = json.loads(memory_path.read_text(encoding="utf-8-sig")) if memory_path.exists() else {}
    cost = {
        "posthoc_seconds_mean_per_case_target": float(np.mean([float(row["scoring_seconds"]) for row in primary])),
        "posthoc_seconds_p95_per_case_target": float(np.percentile([float(row["scoring_seconds"]) for row in primary], 95.0)),
        "deployment_source_mb_mean_per_examination": float(np.mean([float(row.get("deployment_source_bytes", row["source_bytes"])) for row in manifests])) / (1024**2),
        "offline_ground_truth_mb_mean_per_examination": float(np.mean([float(row.get("offline_ground_truth_bytes", 0.0)) for row in manifests])) / (1024**2),
        "peak_working_set_gib": float(memory.get("peak_working_set_bytes", float("nan"))) / (1024**3),
        "peak_private_memory_gib": float(memory.get("peak_private_memory_bytes", float("nan"))) / (1024**3),
    }
    analytical_path = REPO_ROOT / "design" / "rasinet" / "outputs" / "analytical_cost" / "per_case.csv"
    analytical = _read(analytical_path) if analytical_path.exists() else []
    for kind in ("linear", "cubic"):
        selected = [row for row in analytical if row["kind"] == kind]
        if selected:
            cost[f"{kind}_seconds_mean"] = float(np.mean([float(row["interpolation_seconds"]) for row in selected]))
            cost[f"{kind}_output_mib_mean"] = float(np.mean([float(row["saved_output_bytes"]) for row in selected])) / (1024**2)
    posthoc_path = REPO_ROOT / "design" / "rasinet" / "outputs" / "posthoc_cost" / "summary.csv"
    posthoc = _read(posthoc_path) if posthoc_path.exists() else []
    overall = next((row for row in posthoc if row["profile"] == "all"), None)
    if overall is not None:
        for metric in (
            "load_seconds_mean",
            "score_seconds_mean",
            "total_seconds_mean",
            "total_seconds_p95",
            "source_mib_mean",
            "observed_peak_rss_gib",
        ):
            cost[f"posthoc_{metric}"] = float(overall[metric])
    _write_csv(source_root / "posthoc_cost_summary.csv", [cost])
    lines = [
        r"\begin{tabular}{lr}",
        r"\toprule",
        r"Measured post-hoc quantity & Value \\",
        r"\midrule",
        f"Stored-output audit / examination, mean & {cost.get('posthoc_total_seconds_mean', cost['posthoc_seconds_mean_per_case_target']):.3f} s \\\\ ",
        f"Stored-output audit / examination, p95 & {cost.get('posthoc_total_seconds_p95', cost['posthoc_seconds_p95_per_case_target']):.3f} s \\\\ ",
        f"NIfTI prediction load / examination, mean & {cost.get('posthoc_load_seconds_mean', float('nan')):.3f} s \\\\ ",
        f"Score and mask kernel / examination, mean & {cost.get('posthoc_score_seconds_mean', cost['posthoc_seconds_mean_per_case_target']):.3f} s \\\\ ",
        f"Stored deployment outputs / examination & {cost.get('posthoc_source_mib_mean', cost['deployment_source_mb_mean_per_examination']):.1f} MiB \\\\ ",
        f"Observed CPU RSS peak & {cost.get('posthoc_observed_peak_rss_gib', cost['peak_working_set_gib']):.2f} GiB \\\\ ",
        f"Linear CPU interpolation / examination$^{{a}}$ & {cost.get('linear_seconds_mean', float('nan')):.3f} s \\\\ ",
        f"Cubic CPU interpolation / examination$^{{a}}$ & {cost.get('cubic_seconds_mean', float('nan')):.3f} s \\\\ ",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (table_root / "table_posthoc_cost.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _tta_table(summary_rows: list[dict[str, str]], table_root: Path, source_root: Path) -> None:
    tta_root = REPO_ROOT / "design" / "rasinet" / "outputs" / "tta_fastmri_unified"
    tta_rows = _read(tta_root / "summary.csv") if (tta_root / "summary.csv").exists() else []
    if not tta_rows:
        return
    primary_rows = [row for row in summary_rows if _primary(row) and row["dataset"] == "fastmri" and row["target"] == "swinir"]
    if not primary_rows:
        return
    primary = primary_rows[0]
    tta = tta_rows[0]
    runtime = json.loads((tta_root / "runtime_summary.json").read_text(encoding="utf-8"))
    source = [
        {
            "method": "target_to_committee_median",
            "pixel_fisher": float(primary["pixel_fisher_z_mean"]),
            "case_spearman": float(primary["case_spearman"]),
            "normalized_aurc": float(primary["normalized_aurc"]),
            "rrr_50": float(primary["rrr_50"]),
            "extra_inference_seconds_mean": 0.0,
        },
        {
            "method": "four_view_tta_variance",
            "pixel_fisher": float(tta["fisher_z_mean"]),
            "case_spearman": float(tta["case_spearman"]),
            "normalized_aurc": float(tta["normalized_aurc"]),
            "rrr_50": float(tta["rrr_50"]),
            "extra_inference_seconds_mean": float(runtime["seconds_mean"]),
        },
    ]
    _write_csv(source_root / "fastmri_swinir_tta_comparison.csv", source)
    paired_path = tta_root / "paired_primary_comparison.csv"
    if paired_path.exists():
        paired = _read(paired_path)
        _write_csv(source_root / "fastmri_swinir_tta_paired.csv", paired)
    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Score & Pixel $r_z$ & $\rho$ & nAURC & RRR$_{50}$ & Extra s/case \\",
        r"\midrule",
        f"Target-to-committee & {source[0]['pixel_fisher']:.3f} & {source[0]['case_spearman']:.3f} & {source[0]['normalized_aurc']:.3f} & {100 * source[0]['rrr_50']:.1f}\\% & stored \\\\ ",
        f"Four-view TTA variance & {source[1]['pixel_fisher']:.3f} & {source[1]['case_spearman']:.3f} & {source[1]['normalized_aurc']:.3f} & {100 * source[1]['rrr_50']:.1f}\\% & {source[1]['extra_inference_seconds_mean']:.2f} \\\\ ",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (table_root / "table_tta_fastmri.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(results: Path) -> None:
    summary = _read(results / "summary.csv")
    risk = _read(results / "risk_coverage.csv")
    table_root = PAPER_ROOT / "tables_icassp"
    figure_root = PAPER_ROOT / "figures_icassp"
    source_root = results / "figure_source_data"
    for directory in (table_root, figure_root, source_root):
        directory.mkdir(parents=True, exist_ok=True)
    _main_table(summary, table_root / "table_main.tex")
    _failure_table(summary, table_root / "table_failure_detection.tex")
    _pixel_support_table(summary, table_root / "table_pixel_support.tex", source_root)
    _result_macros(summary, table_root / "result_macros.tex")
    _stress_macros(table_root / "stress_macros.tex")
    _sensitivity_tables(summary, table_root, source_root)
    _paired_score_table(results, table_root, source_root)
    _stability_tables(results, table_root, source_root)
    _committee_size(summary, table_root, figure_root, source_root)
    _committee_composition(summary, table_root, source_root)
    _key_ablation_table(summary, table_root, source_root)
    _risk_coverage(risk, summary, figure_root, source_root)
    _framework(figure_root)
    _cost_table(results, summary, table_root, source_root)
    _tta_table(summary, table_root, source_root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ICASSP paper assets from registered CSV results.")
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    generate((REPO_ROOT / args.results).resolve() if not args.results.is_absolute() else args.results)


if __name__ == "__main__":
    main()
