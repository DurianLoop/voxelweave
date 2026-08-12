from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRE_ROOT = ROOT / "pre"
if PRE_ROOT.exists() and str(PRE_ROOT) not in sys.path:
    sys.path.insert(0, str(PRE_ROOT))

from ixi_diffusion.common import ensure_dir, write_csv


RUN_ROOT = ROOT / "rasinet" / "runs" / "posthoc_uncertainty"
REPORT_ROOT = ROOT / "rasinet" / "reports" / "posthoc_uncertainty"
PAPER_EXP = REPORT_ROOT / "paper_experiments"
PAPER_TABLE_DIR = ROOT / "rasinet" / "paper" / "tables"

PROFILES = {
    "full_test115": "IXI T2",
    "fastmri_full": "fastMRI-brain T2",
    "ningxia_cv": "NingXia T2 CV",
}

METHOD_DISPLAY = {
    "i3net": "I3Net",
    "hat": "HAT",
    "swinir": "SwinIR",
    "acsinet": "ACSI",
    "linear": "Linear",
    "cubic": "Cubic",
}
METHOD_ORDER = {"Linear": 0, "Cubic": 1, "I3Net": 2, "HAT": 3, "SwinIR": 4, "ACSI": 5}
PROXY_ORDER = {
    "Baseline disagreement": 0,
    "Residual to linear": 1,
    "Residual to cubic": 2,
    "TTA variance": 3,
}
DATASET_ORDER = {"IXI T2": 0, "fastMRI-brain T2": 1, "NingXia T2 CV": 2}

RECON_SOURCES = {
    "IXI T2": {
        "linear/cubic/i3net": ROOT / "ixi_i3net" / "runs" / "full_test115_stable" / "metrics" / "summary_metrics.csv",
        "hat": ROOT / "ixi_hat_2p5d" / "runs" / "full_test115" / "metrics" / "summary_metrics.csv",
        "swinir": ROOT / "ixi_swinir_2p5d" / "runs" / "full_test115" / "metrics" / "summary_metrics.csv",
        "acsinet": ROOT / "acsinet" / "runs" / "full_test115" / "metrics" / "summary_metrics.csv",
    },
    "fastMRI-brain T2": {
        "linear/cubic/i3net": ROOT / "fastmri_brain_i3net" / "runs" / "full" / "metrics" / "summary_metrics.csv",
        "hat": ROOT / "fastmri_brain_hat_2p5d" / "runs" / "full" / "metrics" / "summary_metrics.csv",
        "swinir": ROOT / "fastmri_brain_swinir_2p5d" / "runs" / "full" / "metrics" / "summary_metrics.csv",
    },
}

NINGXIA_RECON_ROOTS = {
    "linear/cubic/i3net": ROOT / "ningxia_t2_i3net_cv" / "runs",
    "hat": ROOT / "ningxia_t2_hat_2p5d_cv" / "runs",
    "swinir": ROOT / "ningxia_t2_swinir_2p5d_cv" / "runs",
}


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _to_float(row: dict, key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def _fmt(value: object, digits: int = 3) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if not np.isfinite(number):
        return ""
    return f"{number:.{digits}f}"


def _fmt_ci(mean: object, low: object, high: object, digits: int = 3) -> str:
    if _fmt(mean, digits) == "":
        return ""
    return f"{_fmt(mean, digits)} [{_fmt(low, digits)}, {_fmt(high, digits)}]"


def _fmt_interval(low: object, high: object, digits: int = 3) -> str:
    if _fmt(low, digits) == "" or _fmt(high, digits) == "":
        return ""
    return f"[{_fmt(low, digits)}, {_fmt(high, digits)}]"


def _split_method(method: str) -> tuple[str, str]:
    if "__" not in method:
        return method, ""
    base, proxy = method.split("__", 1)
    return base, proxy


def _display_method(method: str) -> str:
    return METHOD_DISPLAY.get(method, method)


def _display_proxy(proxy: str) -> str:
    return {
        "baseline_disagreement": "Baseline disagreement",
        "residual_linear": "Residual to linear",
        "residual_cubic": "Residual to cubic",
        "tta_variance": "TTA variance",
    }.get(proxy, proxy)


def _markdown_table(headers: list[str], rows: list[dict]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines) + "\n"


def _write_markdown(path: Path, title: str, headers: list[str], rows: list[dict], note: str = "") -> None:
    ensure_dir(path.parent)
    parts = [f"# {title}", ""]
    if note:
        parts.extend([note, ""])
    parts.append(_markdown_table(headers, rows))
    path.write_text("\n".join(parts), encoding="utf-8")


def _write_pair(stem: str, title: str, headers: list[str], rows: list[dict], note: str = "") -> None:
    out_dir = ensure_dir(PAPER_TABLE_DIR)
    write_csv(out_dir / f"{stem}.csv", rows)
    _write_markdown(out_dir / f"{stem}.md", title, headers, rows, note)


def _load_summary(profile: str) -> list[dict]:
    return _read_csv(RUN_ROOT / profile / "metrics" / "summary_posthoc_reliability.csv")


def _load_failure(profile: str) -> list[dict]:
    return _read_csv(RUN_ROOT / profile / "metrics" / "failure_detection_posthoc.csv")


def _bootstrap_lookup(path: Path) -> dict[tuple[str, str, str, str], dict]:
    lookup = {}
    for row in _read_csv(path):
        lookup[(row["profile"], row["method"], row["proxy"], row["metric"])] = row
    return lookup


def _failure_ablation_lookup() -> dict[tuple[str, str, str, str], dict]:
    lookup = {}
    for row in _read_csv(PAPER_EXP / "failure_definition_ablation.csv"):
        lookup[(row["profile"], row["method"], row["proxy"], row["failure_definition"])] = row
    return lookup


def build_main_reliability_table() -> list[dict]:
    ci_lookup = _bootstrap_lookup(PAPER_EXP / "bootstrap_ci_by_method_proxy.csv")
    mask_lookup = _bootstrap_lookup(PAPER_EXP / "masked_bootstrap_ci_by_method_proxy.csv")
    rows = []
    for profile, dataset in PROFILES.items():
        for summary in _load_summary(profile):
            base, proxy = _split_method(summary["method"])
            if proxy != "baseline_disagreement":
                continue
            method = _display_method(base)
            pixel_ci = ci_lookup.get((profile, method, proxy, "pixel_error_uncertainty_corr"), {})
            nonzero_ci = mask_lookup.get((profile, method, proxy, "pixel_corr_nonzero"), {})
            rows.append(
                {
                    "Dataset": dataset,
                    "Method": method,
                    "Cases": summary["cases"],
                    "Pixel Corr": _fmt(pixel_ci.get("mean", summary["pixel_error_uncertainty_corr_mean"])),
                    "Pixel Corr 95% CI": _fmt_interval(pixel_ci.get("ci95_low", ""), pixel_ci.get("ci95_high", "")),
                    "Nonzero Corr": _fmt(nonzero_ci.get("mean", "")),
                    "Nonzero Corr 95% CI": _fmt_interval(nonzero_ci.get("ci95_low", ""), nonzero_ci.get("ci95_high", "")),
                    "Slice Corr": _fmt(summary["slice_error_uncertainty_corr_mean"]),
                    "Risk AURC": _fmt(summary["risk_coverage_aurc_mean"]),
                    "MAE@50% low-U": _fmt(summary["retained_mae_50pct_low_uncertainty_mean"]),
                }
            )
    rows.sort(key=lambda row: (DATASET_ORDER.get(row["Dataset"], 99), METHOD_ORDER.get(row["Method"], 99)))
    return rows


def build_failure_detection_table() -> list[dict]:
    ci_lookup = _failure_ablation_lookup()
    rows = []
    for profile, dataset in PROFILES.items():
        for failure in _load_failure(profile):
            base, proxy = _split_method(failure["method"])
            if proxy != "baseline_disagreement":
                continue
            method = _display_method(base)
            ci = ci_lookup.get((profile, method, proxy, "top_mae"), {})
            rows.append(
                {
                    "Dataset": dataset,
                    "Method": method,
                    "Cases": failure["cases"],
                    "Failure cases": failure["failure_cases"],
                    "AUROC": _fmt(failure["auroc"]),
                    "AUROC 95% CI": _fmt_interval(ci.get("auroc_ci95_low", ""), ci.get("auroc_ci95_high", "")),
                    "AUPRC": _fmt(failure["auprc"]),
                    "AUPRC 95% CI": _fmt_interval(ci.get("auprc_ci95_low", ""), ci.get("auprc_ci95_high", "")),
                    "Top-k recall": _fmt(failure["top_k_failure_recall"]),
                    "Top-k recall 95% CI": _fmt_interval(ci.get("top_k_recall_ci95_low", ""), ci.get("top_k_recall_ci95_high", "")),
                }
            )
    rows.sort(key=lambda row: (DATASET_ORDER.get(row["Dataset"], 99), METHOD_ORDER.get(row["Method"], 99)))
    return rows


def _tta_summary(profile: str) -> dict:
    rows = _read_csv(RUN_ROOT / profile / "metrics" / "summary_tta_reliability.csv")
    return next((row for row in rows if row["method"] == "swinir_tta_mean__tta_variance"), {})


def _tta_failure(profile: str) -> dict:
    rows = _read_csv(RUN_ROOT / profile / "metrics" / "failure_detection_tta.csv")
    return next((row for row in rows if row["method"] == "swinir_tta_mean__tta_variance"), {})


def build_proxy_ablation_table() -> list[dict]:
    tta_profiles = {
        "full_test115": "ixi_swinir_tta",
        "fastmri_full": "fastmri_swinir_tta",
        "ningxia_cv": "ningxia_swinir_tta",
    }
    rows = []
    for profile, dataset in PROFILES.items():
        failure_by_method = {row["method"]: row for row in _load_failure(profile)}
        for summary in _load_summary(profile):
            base, proxy = _split_method(summary["method"])
            if base != "swinir":
                continue
            failure = failure_by_method.get(summary["method"], {})
            rows.append(
                {
                    "Dataset": dataset,
                    "Method": "SwinIR",
                    "Proxy": _display_proxy(proxy),
                    "Pixel Corr": _fmt(summary["pixel_error_uncertainty_corr_mean"]),
                    "Slice Corr": _fmt(summary["slice_error_uncertainty_corr_mean"]),
                    "Risk AURC": _fmt(summary["risk_coverage_aurc_mean"]),
                    "MAE@50% low-U": _fmt(summary["retained_mae_50pct_low_uncertainty_mean"]),
                    "Failure AUROC": _fmt(failure.get("auroc")),
                    "Top-k recall": _fmt(failure.get("top_k_failure_recall")),
                }
            )
        tta = _tta_summary(tta_profiles[profile])
        tta_failure = _tta_failure(tta_profiles[profile])
        if tta:
            rows.append(
                {
                    "Dataset": dataset,
                    "Method": "SwinIR",
                    "Proxy": "TTA variance",
                    "Pixel Corr": _fmt(tta["pixel_error_uncertainty_corr_mean"]),
                    "Slice Corr": _fmt(tta["slice_error_uncertainty_corr_mean"]),
                    "Risk AURC": _fmt(tta["risk_coverage_aurc_mean"]),
                    "MAE@50% low-U": _fmt(tta["retained_mae_50pct_low_uncertainty_mean"]),
                    "Failure AUROC": _fmt(tta_failure.get("auroc")),
                    "Top-k recall": _fmt(tta_failure.get("top_k_failure_recall")),
                }
            )
    rows.sort(key=lambda row: (DATASET_ORDER.get(row["Dataset"], 99), PROXY_ORDER.get(row["Proxy"], 99)))
    return rows


def build_runtime_cost_table() -> list[dict]:
    rows = []
    for row in _read_csv(PAPER_EXP / "runtime_storage_cost.csv"):
        rows.append(
            {
                "Profile": row["profile"],
                "Dataset": row["dataset"],
                "Cases": row["cases"],
                "Source NIfTI files": row["source_nii_files"],
                "Source size GB": row["source_size_gb"],
                "Posthoc metrics MB": row["posthoc_metrics_size_mb"],
                "Reports MB": row["report_size_mb"],
                "Training needed": row["training_needed"],
                "GPU needed": row["gpu_needed_for_posthoc"],
            }
        )
    return rows


def build_tta_ablation_table() -> list[dict]:
    profile_map = {
        "IXI T2": "ixi_swinir_tta",
        "fastMRI-brain T2": "fastmri_swinir_tta",
        "NingXia T2 CV": "ningxia_swinir_tta",
    }
    metric_display = {
        "pixel_corr": "Pixel Corr",
        "slice_corr": "Slice Corr",
        "risk_coverage_aurc": "Risk AURC",
        "mae_50pct_low_u": "MAE@50% low-U",
        "failure_auroc": "Failure AUROC",
        "top_k_failure_recall": "Top-k recall",
    }
    rows = []
    for dataset, profile in profile_map.items():
        path = RUN_ROOT / profile / "metrics" / "comparison_tta_vs_baseline_disagreement.csv"
        for row in _read_csv(path):
            rows.append(
                {
                    "Dataset": dataset,
                    "Metric": metric_display.get(row["metric"], row["metric"]),
                    "TTA variance": _fmt(row["tta_value"]),
                    "Baseline disagreement": _fmt(row["baseline_value"]),
                    "Delta": _fmt(row["delta"]),
                }
            )
    rows.sort(key=lambda row: (DATASET_ORDER.get(row["Dataset"], 99), row["Metric"]))
    return rows


def _rank_desc(values: list[float]) -> list[int]:
    order = np.argsort(-np.asarray(values, dtype=np.float64), kind="mergesort")
    ranks = np.empty(len(values), dtype=np.int32)
    for rank, idx in enumerate(order, start=1):
        ranks[idx] = rank
    return [int(v) for v in ranks]


def build_failure_ranking_table() -> list[dict]:
    rows = []
    for profile, dataset in PROFILES.items():
        per_case = _read_csv(RUN_ROOT / profile / "metrics" / "per_case_posthoc_reliability.csv")
        by_method: dict[str, list[dict]] = defaultdict(list)
        for row in per_case:
            method, proxy = _split_method(row["method"])
            if proxy != "baseline_disagreement":
                continue
            by_method[method].append(row)
        for method, selected in by_method.items():
            errors = [_to_float(row, "mean_abs_error") for row in selected]
            uncertainties = [_to_float(row, "mean_uncertainty") for row in selected]
            error_ranks = _rank_desc(errors)
            uncertainty_ranks = _rank_desc(uncertainties)
            for row, error_rank, uncertainty_rank in zip(selected, error_ranks, uncertainty_ranks):
                rows.append(
                    {
                        "Dataset": dataset,
                        "Method": _display_method(method),
                        "Case": row["case"],
                        "Mean abs error": _fmt(row["mean_abs_error"]),
                        "Mean uncertainty": _fmt(row["mean_uncertainty"]),
                        "Error rank": error_rank,
                        "Uncertainty rank": uncertainty_rank,
                        "Rank gap": abs(error_rank - uncertainty_rank),
                    }
                )
    rows.sort(key=lambda row: (DATASET_ORDER.get(row["Dataset"], 99), METHOD_ORDER.get(row["Method"], 99), int(row["Error rank"])))
    return rows


def _write_large_supplement(stem: str, title: str, headers: list[str], rows: list[dict], note: str = "", preview_rows: int = 60) -> None:
    out_dir = ensure_dir(PAPER_TABLE_DIR)
    write_csv(out_dir / f"{stem}.csv", rows)
    preview = rows[:preview_rows]
    preview_note = note
    if len(rows) > preview_rows:
        preview_note = (note + " " if note else "") + f"Markdown preview shows first {preview_rows} rows; CSV contains all {len(rows)} rows."
    _write_markdown(out_dir / f"{stem}.md", title, headers, preview, preview_note)


def _mean_std(values: list[float]) -> tuple[float, float]:
    arr = np.asarray([value for value in values if np.isfinite(value)], dtype=np.float64)
    if arr.size == 0:
        return float("nan"), float("nan")
    return float(np.mean(arr)), float(np.std(arr))


def _aggregate_per_case_metrics(paths: list[Path], wanted: set[str]) -> list[dict]:
    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    cases: dict[str, int] = defaultdict(int)
    for path in paths:
        for row in _read_csv(path):
            method = row.get("method", "")
            if method not in wanted:
                continue
            cases[method] += 1
            for metric in ["psnr", "ssim", "mae", "ncc", "mask_ssim"]:
                grouped[method][metric].append(_to_float(row, metric))
    out = []
    for method, metrics in sorted(grouped.items()):
        result = {"method": method, "cases": cases[method]}
        for metric, values in metrics.items():
            mean, std = _mean_std(values)
            result[f"{metric}_mean"] = mean
            result[f"{metric}_std"] = std
        out.append(result)
    return out


def _recon_rows_from_summary(dataset: str, paths_by_group: dict[str, Path]) -> list[dict]:
    wanted_by_group = {
        "linear/cubic/i3net": {"linear", "cubic", "i3net"},
        "hat": {"hat"},
        "swinir": {"swinir"},
        "acsinet": {"acsinet"},
    }
    rows = []
    seen = set()
    for group, path in paths_by_group.items():
        for row in _read_csv(path):
            method = row.get("method", "")
            if method not in wanted_by_group.get(group, set()) or method in seen:
                continue
            seen.add(method)
            rows.append(
                {
                    "Dataset": dataset,
                    "Method": _display_method(method),
                    "Cases": row["cases"],
                    "PSNR": _fmt(row["psnr_mean"]),
                    "SSIM": _fmt(row["ssim_mean"], 4),
                    "MAE": _fmt(row["mae_mean"]),
                    "NCC": _fmt(row["ncc_mean"], 4),
                    "Mask SSIM": _fmt(row.get("mask_ssim_mean"), 4),
                    "Role": "context baseline" if method in {"linear", "cubic"} else "reconstruction method",
                }
            )
    return rows


def _ningxia_recon_rows() -> list[dict]:
    wanted_by_group = {
        "linear/cubic/i3net": {"linear", "cubic", "i3net"},
        "hat": {"hat"},
        "swinir": {"swinir"},
    }
    rows = []
    for group, root in NINGXIA_RECON_ROOTS.items():
        per_case_paths = sorted(root.glob("fold_*\\full\\metrics\\per_case_metrics.csv"))
        for row in _aggregate_per_case_metrics(per_case_paths, wanted_by_group[group]):
            method = row["method"]
            rows.append(
                {
                    "Dataset": "NingXia T2 CV",
                    "Method": _display_method(method),
                    "Cases": row["cases"],
                    "PSNR": _fmt(row["psnr_mean"]),
                    "SSIM": _fmt(row["ssim_mean"], 4),
                    "MAE": _fmt(row["mae_mean"]),
                    "NCC": _fmt(row["ncc_mean"], 4),
                    "Mask SSIM": _fmt(row.get("mask_ssim_mean"), 4),
                    "Role": "context baseline" if method in {"linear", "cubic"} else "reconstruction method",
                }
            )
    return rows


def build_reconstruction_context_table() -> list[dict]:
    rows = []
    for dataset, paths in RECON_SOURCES.items():
        rows.extend(_recon_rows_from_summary(dataset, paths))
    rows.extend(_ningxia_recon_rows())
    rows.sort(key=lambda row: (DATASET_ORDER.get(row["Dataset"], 99), METHOD_ORDER.get(row["Method"], 99)))
    return rows


def write_paper_tables() -> None:
    ensure_dir(PAPER_TABLE_DIR)
    _write_pair(
        "table_reconstruction_context",
        "Table 1. Reconstruction Context",
        ["Dataset", "Method", "Cases", "PSNR", "SSIM", "MAE", "NCC", "Mask SSIM", "Role"],
        build_reconstruction_context_table(),
        "Linear/cubic are context baselines only; the paper's main claim is reliability estimation on existing reconstruction outputs.",
    )
    _write_pair(
        "table_main_reliability",
        "Table 2. Main Reliability Results",
        [
            "Dataset",
            "Method",
            "Cases",
            "Pixel Corr",
            "Pixel Corr 95% CI",
            "Nonzero Corr",
            "Nonzero Corr 95% CI",
            "Slice Corr",
            "Risk AURC",
            "MAE@50% low-U",
        ],
        build_main_reliability_table(),
        "Main proxy: baseline disagreement. Each metric cell is the per-method mean; CI columns report bootstrap 95% confidence intervals.",
    )
    _write_pair(
        "table_failure_detection",
        "Table 3. Failure Detection",
        [
            "Dataset",
            "Method",
            "Cases",
            "Failure cases",
            "AUROC",
            "AUROC 95% CI",
            "AUPRC",
            "AUPRC 95% CI",
            "Top-k recall",
            "Top-k recall 95% CI",
        ],
        build_failure_detection_table(),
        "Failure definition: top-MAE cases. Each metric cell is the per-method point estimate; CI columns report bootstrap 95% confidence intervals.",
    )
    _write_pair(
        "table_proxy_ablation",
        "Table 4. Proxy Ablation",
        ["Dataset", "Method", "Proxy", "Pixel Corr", "Slice Corr", "Risk AURC", "MAE@50% low-U", "Failure AUROC", "Top-k recall"],
        build_proxy_ablation_table(),
        "TTA variance is included as an auxiliary proxy; it improves slice-level correlation but does not replace baseline disagreement.",
    )
    _write_pair(
        "table_runtime_cost",
        "Table 5. Runtime and Storage Cost",
        ["Profile", "Dataset", "Cases", "Source NIfTI files", "Source size GB", "Posthoc metrics MB", "Reports MB", "Training needed", "GPU needed"],
        build_runtime_cost_table(),
        "Post-hoc disagreement uses existing predictions and does not require model training.",
    )
    _write_pair(
        "supp_table_tta_ablation",
        "Supplementary Table. TTA Variance Cross-Dataset Ablation",
        ["Dataset", "Metric", "TTA variance", "Baseline disagreement", "Delta"],
        build_tta_ablation_table(),
        "Positive delta means TTA variance is numerically larger. For Risk AURC and MAE@50% low-U, lower is better.",
    )
    _write_large_supplement(
        "supp_table_failure_ranking",
        "Supplementary Table. Per-case Failure Ranking",
        ["Dataset", "Method", "Case", "Mean abs error", "Mean uncertainty", "Error rank", "Uncertainty rank", "Rank gap"],
        build_failure_ranking_table(),
        "Ranks are descending: rank 1 means highest error or highest uncertainty within the dataset-method group.",
    )


def main() -> None:
    write_paper_tables()
    print(f"Wrote paper tables to {PAPER_TABLE_DIR}")


if __name__ == "__main__":
    main()
