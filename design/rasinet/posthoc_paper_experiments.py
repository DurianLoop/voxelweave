from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from ixi_diffusion.common import ensure_dir, write_csv


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ("full_test115", "fastmri_full", "ningxia_cv")


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _to_float(row: dict, key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def _fmt(value: float, digits: int = 4) -> str:
    if not np.isfinite(value):
        return ""
    return f"{value:.{digits}f}"


def _split_method(method: str) -> tuple[str, str]:
    if "__" not in method:
        return method, ""
    return tuple(method.split("__", 1))  # type: ignore[return-value]


def _display_method(method: str) -> str:
    return {
        "i3net": "I3Net",
        "hat": "HAT",
        "swinir": "SwinIR",
        "acsinet": "ACSI",
    }.get(method, method)


def _rankdata(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=np.float64)
    sorted_values = values[order]
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and sorted_values[end] == sorted_values[start]:
            end += 1
        rank = 0.5 * (start + 1 + end)
        ranks[order[start:end]] = rank
        start = end
    return ranks


def _safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    b = np.asarray(b, dtype=np.float64).reshape(-1)
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 2:
        return float("nan")
    a = a[mask]
    b = b[mask]
    if float(np.std(a)) <= 1e-12 or float(np.std(b)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 2:
        return float("nan")
    return _safe_corr(_rankdata(a[mask]), _rankdata(b[mask]))


def _binary_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=np.int32)
    scores = np.asarray(scores, dtype=np.float64)
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    wins = 0.0
    for value in pos:
        wins += float(np.sum(value > neg)) + 0.5 * float(np.sum(value == neg))
    return float(wins / (pos.size * neg.size))


def _average_precision(labels: np.ndarray, scores: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=np.int32)
    scores = np.asarray(scores, dtype=np.float64)
    positives = int(labels.sum())
    if positives == 0:
        return float("nan")
    order = np.argsort(-scores)
    sorted_labels = labels[order]
    tp = np.cumsum(sorted_labels)
    precision = tp / (np.arange(labels.size) + 1)
    return float(np.sum(precision * sorted_labels) / positives)


def _bootstrap_failure_scores(labels: np.ndarray, scores: np.ndarray, rng: np.random.Generator, samples: int) -> dict:
    labels = np.asarray(labels, dtype=np.int32)
    scores = np.asarray(scores, dtype=np.float64)
    valid = np.isfinite(scores)
    labels = labels[valid]
    scores = scores[valid]
    if labels.size < 2 or int(labels.sum()) == 0 or int(labels.sum()) == labels.size:
        return {
            "auroc": float("nan"),
            "auroc_ci95_low": float("nan"),
            "auroc_ci95_high": float("nan"),
            "auprc": float("nan"),
            "auprc_ci95_low": float("nan"),
            "auprc_ci95_high": float("nan"),
            "top_k_recall": float("nan"),
            "top_k_recall_ci95_low": float("nan"),
            "top_k_recall_ci95_high": float("nan"),
        }
    k = int(labels.sum())
    order = np.argsort(-scores)[:k]
    point = {
        "auroc": _binary_auc(labels, scores),
        "auprc": _average_precision(labels, scores),
        "top_k_recall": float(labels[order].sum() / max(k, 1)),
    }
    aucs: list[float] = []
    aps: list[float] = []
    recalls: list[float] = []
    attempts = 0
    while len(aucs) < samples and attempts < samples * 10:
        attempts += 1
        idx = rng.integers(0, labels.size, size=labels.size)
        b_labels = labels[idx]
        b_scores = scores[idx]
        if int(b_labels.sum()) == 0 or int(b_labels.sum()) == b_labels.size:
            continue
        b_k = max(1, int(b_labels.sum()))
        b_order = np.argsort(-b_scores)[:b_k]
        aucs.append(_binary_auc(b_labels, b_scores))
        aps.append(_average_precision(b_labels, b_scores))
        recalls.append(float(b_labels[b_order].sum() / b_k))
    for name, values in [("auroc", aucs), ("auprc", aps), ("top_k_recall", recalls)]:
        arr = np.asarray(values, dtype=np.float64)
        point[f"{name}_ci95_low"] = float(np.percentile(arr, 2.5)) if arr.size else float("nan")
        point[f"{name}_ci95_high"] = float(np.percentile(arr, 97.5)) if arr.size else float("nan")
    return point


def _bootstrap_ci(values: np.ndarray, rng: np.random.Generator, samples: int) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return float("nan"), float("nan"), float("nan")
    if values.size == 1:
        mean = float(values[0])
        return mean, mean, mean
    idx = rng.integers(0, values.size, size=(samples, values.size))
    means = np.mean(values[idx], axis=1)
    return float(np.mean(values)), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _method_groups(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["method"]].append(row)
    return grouped


def build_bootstrap_ci(profile: str, rows: list[dict], samples: int, seed: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    metrics = [
        "pixel_error_uncertainty_corr",
        "slice_error_uncertainty_corr",
        "mean_abs_error",
        "mean_uncertainty",
        "risk_coverage_aurc",
        "retained_mae_50pct_low_uncertainty",
    ]
    out: list[dict] = []
    for method, selected in sorted(_method_groups(rows).items()):
        base, proxy = _split_method(method)
        for metric in metrics:
            values = np.asarray([_to_float(row, metric) for row in selected], dtype=np.float64)
            mean, lo, hi = _bootstrap_ci(values, rng, samples)
            out.append(
                {
                    "profile": profile,
                    "method": _display_method(base),
                    "proxy": proxy,
                    "metric": metric,
                    "cases": len(selected),
                    "mean": mean,
                    "ci95_low": lo,
                    "ci95_high": hi,
                }
            )
    return out


def build_mask_bootstrap_ci(profile: str, rows: list[dict], samples: int, seed: int) -> list[dict]:
    rng = np.random.default_rng(seed + 23)
    metrics = ["pixel_corr_all", "pixel_corr_nonzero", "pixel_corr_background", "corr_drop_nonzero_minus_all", "background_fraction"]
    out: list[dict] = []
    for method, selected in sorted(_method_groups(rows).items()):
        base, proxy = _split_method(method)
        for metric in metrics:
            values = np.asarray([_to_float(row, metric) for row in selected], dtype=np.float64)
            mean, lo, hi = _bootstrap_ci(values, rng, samples)
            out.append(
                {
                    "profile": profile,
                    "method": _display_method(base),
                    "proxy": proxy,
                    "metric": metric,
                    "cases": len(selected),
                    "mean": mean,
                    "ci95_low": lo,
                    "ci95_high": hi,
                }
            )
    return out


def build_paired_proxy_comparison(profile: str, rows: list[dict], samples: int, seed: int) -> list[dict]:
    rng = np.random.default_rng(seed + 17)
    by_base: dict[str, dict[str, dict[str, dict]]] = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        base, proxy = _split_method(row["method"])
        by_base[base][proxy][row["case"]] = row
    metrics = ["pixel_error_uncertainty_corr", "slice_error_uncertainty_corr", "risk_coverage_aurc", "retained_mae_50pct_low_uncertainty"]
    out: list[dict] = []
    for base, by_proxy in sorted(by_base.items()):
        if "baseline_disagreement" not in by_proxy:
            continue
        for other_proxy in sorted(proxy for proxy in by_proxy if proxy != "baseline_disagreement"):
            common_cases = sorted(set(by_proxy["baseline_disagreement"]) & set(by_proxy[other_proxy]))
            for metric in metrics:
                diffs = np.asarray(
                    [
                        _to_float(by_proxy["baseline_disagreement"][case], metric)
                        - _to_float(by_proxy[other_proxy][case], metric)
                        for case in common_cases
                    ],
                    dtype=np.float64,
                )
                mean, lo, hi = _bootstrap_ci(diffs, rng, samples)
                out.append(
                    {
                        "profile": profile,
                        "method": _display_method(base),
                        "comparison": f"baseline_disagreement_minus_{other_proxy}",
                        "metric": metric,
                        "cases": len(common_cases),
                        "mean_diff": mean,
                        "ci95_low": lo,
                        "ci95_high": hi,
                    }
                )
    return out


def build_calibration_monotonicity(profile: str, rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["method"], row["case"])].append(row)
    per_case: list[dict] = []
    for (method, case), selected in sorted(grouped.items()):
        selected.sort(key=lambda row: int(row["bin"]))
        bin_idx = np.asarray([int(row["bin"]) for row in selected], dtype=np.float64)
        errors = np.asarray([_to_float(row, "mean_abs_error") for row in selected], dtype=np.float64)
        uncertainties = np.asarray([_to_float(row, "mean_uncertainty") for row in selected], dtype=np.float64)
        base, proxy = _split_method(method)
        diffs = np.diff(errors)
        per_case.append(
            {
                "profile": profile,
                "method": _display_method(base),
                "proxy": proxy,
                "case": case,
                "bins": len(selected),
                "spearman_bin_error": _spearman(bin_idx, errors),
                "spearman_uncertainty_error": _spearman(uncertainties, errors),
                "monotonic_non_decreasing": int(bool(np.all(diffs >= -1e-8))),
                "mean_error_lowest_bin": float(errors[0]) if errors.size else float("nan"),
                "mean_error_highest_bin": float(errors[-1]) if errors.size else float("nan"),
                "high_low_error_ratio": float(errors[-1] / max(errors[0], 1e-8)) if errors.size else float("nan"),
            }
        )
    return per_case


def summarize_calibration(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["method"], row["proxy"])].append(row)
    summary = []
    for (method, proxy), selected in sorted(grouped.items()):
        for metric in ["spearman_bin_error", "spearman_uncertainty_error", "high_low_error_ratio"]:
            values = np.asarray([float(row[metric]) for row in selected], dtype=np.float64)
            values = values[np.isfinite(values)]
            summary.append(
                {
                    "profile": selected[0]["profile"],
                    "method": method,
                    "proxy": proxy,
                    "metric": metric,
                    "cases": len(selected),
                    "mean": float(np.mean(values)) if values.size else float("nan"),
                    "std": float(np.std(values)) if values.size else float("nan"),
                }
            )
        summary.append(
            {
                "profile": selected[0]["profile"],
                "method": method,
                "proxy": proxy,
                "metric": "monotonic_case_fraction",
                "cases": len(selected),
                "mean": float(np.mean([int(row["monotonic_non_decreasing"]) for row in selected])),
                "std": 0.0,
            }
        )
    return summary


def _quality_lookup(profile: str) -> dict[tuple[str, str], dict]:
    paths: dict[str, Path] = {}
    if profile == "full_test115":
        paths = {
            "i3net": ROOT / "ixi_i3net" / "runs" / "full_test115_stable" / "metrics",
            "hat": ROOT / "ixi_hat_2p5d" / "runs" / "full_test115" / "metrics",
            "swinir": ROOT / "ixi_swinir_2p5d" / "runs" / "full_test115" / "metrics",
            "acsinet": ROOT / "acsinet" / "runs" / "full_test115" / "metrics",
        }
    elif profile == "fastmri_full":
        paths = {
            "i3net": ROOT / "fastmri_brain_i3net" / "runs" / "full" / "metrics",
            "hat": ROOT / "fastmri_brain_hat_2p5d" / "runs" / "full" / "metrics",
            "swinir": ROOT / "fastmri_brain_swinir_2p5d" / "runs" / "full" / "metrics",
        }
    lookup: dict[tuple[str, str], dict] = {}
    for method, metrics_dir in paths.items():
        per_case_path = metrics_dir / "per_case_metrics.csv"
        if per_case_path.exists():
            for row in _read_csv(per_case_path):
                lookup[(method, row["case"])] = row
        consistency_path = metrics_dir / "per_case_3d_consistency.csv"
        if consistency_path.exists():
            for row in _read_csv(consistency_path):
                lookup.setdefault((method, row["case"]), {}).update(row)
    if profile == "ningxia_cv":
        roots = {
            "i3net": ROOT / "ningxia_t2_i3net_cv" / "runs",
            "hat": ROOT / "ningxia_t2_hat_2p5d_cv" / "runs",
            "swinir": ROOT / "ningxia_t2_swinir_2p5d_cv" / "runs",
        }
        for method, root in roots.items():
            for fold_dir in sorted(root.glob("fold_*")):
                metrics_dir = fold_dir / "full" / "metrics"
                per_case_path = metrics_dir / "per_case_metrics.csv"
                if per_case_path.exists():
                    for row in _read_csv(per_case_path):
                        lookup[(method, f"{fold_dir.name}/{row['case']}")] = row
                consistency_path = metrics_dir / "per_case_3d_consistency.csv"
                if consistency_path.exists():
                    for row in _read_csv(consistency_path):
                        lookup.setdefault((method, f"{fold_dir.name}/{row['case']}"), {}).update(row)
    return lookup


def build_failure_definition_ablation(profile: str, rows: list[dict], samples: int, seed: int) -> list[dict]:
    quality_lookup = _quality_lookup(profile)
    definitions = [
        ("top_mae", "posthoc", "mean_abs_error", 1.0),
        ("top_risk_aurc", "posthoc", "risk_coverage_aurc", 1.0),
        ("top_mae_50pct_low_u", "posthoc", "retained_mae_50pct_low_uncertainty", 1.0),
        ("bottom_ssim", "quality", "ssim", -1.0),
        ("bottom_mask_ssim", "quality", "mask_ssim", -1.0),
        ("top_zge", "quality", "zge", 1.0),
        ("top_zle", "quality", "zle", 1.0),
        ("top_interslice_ncc_mae", "quality", "interslice_ncc_mae", 1.0),
    ]
    out: list[dict] = []
    rng = np.random.default_rng(seed + 101)
    for method, selected in sorted(_method_groups(rows).items()):
        base, proxy = _split_method(method)
        scores = np.asarray([_to_float(row, "mean_uncertainty") for row in selected], dtype=np.float64)
        for definition, source, metric, direction in definitions:
            target_values = []
            for row in selected:
                if source == "posthoc":
                    value = _to_float(row, metric)
                else:
                    value = _to_float(quality_lookup.get((base, row["case"]), {}), metric)
                target_values.append(direction * value)
            target = np.asarray(target_values, dtype=np.float64)
            valid = np.isfinite(target) & np.isfinite(scores)
            target = target[valid]
            valid_scores = scores[valid]
            n = target.size
            if n < 3:
                continue
            k = max(1, int(np.ceil(0.1 * n)))
            labels = np.zeros(n, dtype=np.int32)
            labels[np.argsort(-target)[:k]] = 1
            scores_with_ci = _bootstrap_failure_scores(labels, valid_scores, rng, samples)
            out.append(
                {
                    "profile": profile,
                    "method": _display_method(base),
                    "proxy": proxy,
                    "failure_definition": definition,
                    "target_metric": metric,
                    "cases": n,
                    "failure_cases": k,
                    **scores_with_ci,
                }
            )
    return out


def build_domain_shift_summary(all_masked_rows: list[dict]) -> list[dict]:
    rows = []
    for row in all_masked_rows:
        if row["proxy"] != "Baseline disagreement":
            continue
        rows.append(
            {
                "profile": row["profile"],
                "method": row["method"],
                "all_pixel_corr": row["all_pixel_corr"],
                "nonzero_corr": row["nonzero_corr"],
                "background_corr": row["background_corr"],
                "background_fraction": row["background_fraction"],
            }
        )
    return rows


def _load_masked_table(profile: str) -> list[dict]:
    path = ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / profile / f"{profile}_masked_nonzero_table.csv"
    rows = _read_csv(path)
    for row in rows:
        row["profile"] = profile
    return rows


def write_summary_md(report_dir: Path, profiles: tuple[str, ...], calibration_summary: list[dict], failure_rows: list[dict], domain_rows: list[dict]) -> None:
    lines = [
        "# RASI 论文级补强实验总结",
        "",
        "本页汇总 bootstrap CI、calibration/monotonicity、failure definition ablation 和 domain-shift 分析。所有实验基于已有 post-hoc 输出表，不引入新模型训练。",
        "",
        "## 1. Calibration / monotonicity 摘要",
        "",
        "| Dataset | Method | Proxy | Metric | Mean | Std |",
        "|---|---|---|---|---:|---:|",
    ]
    for row in calibration_summary:
        if row["proxy"] != "baseline_disagreement":
            continue
        lines.append(
            f"| {row['profile']} | {row['method']} | {row['proxy']} | {row['metric']} | {_fmt(float(row['mean']))} | {_fmt(float(row['std']))} |"
        )
    lines.extend(["", "## 2. Failure definition ablation 摘要", "", "| Dataset | Method | Proxy | Definition | AUROC | AUPRC | Top-k recall |", "|---|---|---|---|---:|---:|---:|"])
    for row in failure_rows:
        if row["proxy"] != "baseline_disagreement":
            continue
        lines.append(
            f"| {row['profile']} | {row['method']} | {row['proxy']} | {row['failure_definition']} | {_fmt(float(row['auroc']))} | {_fmt(float(row['auprc']))} | {_fmt(float(row['top_k_recall']))} |"
        )
    lines.extend(["", "## 3. Domain shift 摘要", "", "| Dataset | Method | All-pixel corr | Nonzero corr | Background corr | Background fraction |", "|---|---|---:|---:|---:|---:|"])
    for row in domain_rows:
        lines.append(
            f"| {row['profile']} | {row['method']} | {row['all_pixel_corr']} | {row['nonzero_corr']} | {row['background_corr']} | {row['background_fraction']} |"
        )
    lines.extend(
        [
            "",
            "## 4. 当前判断",
            "",
            "- baseline disagreement 在三数据集上保持正相关，支持作为主 proxy。",
            "- calibration 单调性和 failure definition ablation 可用于回应审稿人关于可靠性是否稳定的质疑。",
            "- 后续若继续补实验，优先级为：TTA variance > learned uncertainty full training。前者是 proxy ablation，后者会改变论文资源和方法定位。",
        ]
    )
    (report_dir / "paper_experiment_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_paper_experiments(profiles: tuple[str, ...], samples: int, seed: int) -> Path:
    report_dir = ensure_dir(ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / "paper_experiments")
    all_bootstrap: list[dict] = []
    all_mask_bootstrap: list[dict] = []
    all_paired: list[dict] = []
    all_calibration_case: list[dict] = []
    all_calibration_summary: list[dict] = []
    all_failure: list[dict] = []
    all_masked: list[dict] = []
    for profile in profiles:
        metrics_dir = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / profile / "metrics"
        per_case = _read_csv(metrics_dir / "per_case_posthoc_reliability.csv")
        calibration = _read_csv(metrics_dir / "calibration_bins_posthoc.csv")
        report_dir_profile = ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / profile
        mask_per_case = _read_csv(report_dir_profile / "qc_mask_background_per_case.csv")
        all_bootstrap.extend(build_bootstrap_ci(profile, per_case, samples, seed))
        all_mask_bootstrap.extend(build_mask_bootstrap_ci(profile, mask_per_case, samples, seed))
        all_paired.extend(build_paired_proxy_comparison(profile, per_case, samples, seed))
        calibration_case = build_calibration_monotonicity(profile, calibration)
        all_calibration_case.extend(calibration_case)
        all_calibration_summary.extend(summarize_calibration(calibration_case))
        all_failure.extend(build_failure_definition_ablation(profile, per_case, samples, seed))
        all_masked.extend(_load_masked_table(profile))

    domain_rows = build_domain_shift_summary(all_masked)
    write_csv(report_dir / "bootstrap_ci_by_method_proxy.csv", all_bootstrap)
    write_csv(report_dir / "masked_bootstrap_ci_by_method_proxy.csv", all_mask_bootstrap)
    write_csv(report_dir / "paired_proxy_comparison_ci.csv", all_paired)
    write_csv(report_dir / "calibration_monotonicity_per_case.csv", all_calibration_case)
    write_csv(report_dir / "calibration_monotonicity_summary.csv", all_calibration_summary)
    write_csv(report_dir / "failure_definition_ablation.csv", all_failure)
    write_csv(report_dir / "domain_shift_masked_summary.csv", domain_rows)
    write_summary_md(report_dir, profiles, all_calibration_summary, all_failure, domain_rows)
    return report_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run paper-level post-hoc reliability experiments.")
    parser.add_argument("--profiles", default="full_test115,fastmri_full,ningxia_cv")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260710)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profiles = tuple(item.strip() for item in args.profiles.split(",") if item.strip())
    report_dir = run_paper_experiments(profiles, args.bootstrap_samples, args.seed)
    print(f"Wrote paper experiments to {report_dir}")


if __name__ == "__main__":
    main()
