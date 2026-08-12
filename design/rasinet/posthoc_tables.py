from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from ixi_diffusion.common import ensure_dir, write_csv


ROOT = Path(__file__).resolve().parents[1]


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


def _display_method(name: str) -> str:
    names = {
        "i3net": "I3Net",
        "hat": "HAT",
        "swinir": "SwinIR",
        "acsinet": "ACSI",
    }
    return names.get(name, name)


def _display_proxy(name: str) -> str:
    names = {
        "baseline_disagreement": "Baseline disagreement",
        "residual_linear": "Residual to linear",
        "residual_cubic": "Residual to cubic",
    }
    return names.get(name, name)


def _failure_by_method(failure_rows: list[dict]) -> dict[str, dict]:
    return {row["method"]: row for row in failure_rows}


def build_reliability_rows(summary_rows: list[dict], failure_rows: list[dict]) -> list[dict]:
    failure = _failure_by_method(failure_rows)
    rows: list[dict] = []
    for row in sorted(summary_rows, key=lambda item: item["method"]):
        method, proxy = _split_method(row["method"])
        failure_row = failure.get(row["method"], {})
        rows.append(
            {
                "method": _display_method(method),
                "proxy": _display_proxy(proxy),
                "cases": row["cases"],
                "mae_mean": _fmt(_to_float(row, "mean_abs_error_mean")),
                "pixel_corr": _fmt(_to_float(row, "pixel_error_uncertainty_corr_mean")),
                "slice_corr": _fmt(_to_float(row, "slice_error_uncertainty_corr_mean")),
                "aurc": _fmt(_to_float(row, "risk_coverage_aurc_mean")),
                "mae_50pct_low_u": _fmt(_to_float(row, "retained_mae_50pct_low_uncertainty_mean")),
                "failure_auroc": _fmt(_to_float(failure_row, "auroc")),
                "failure_auprc": _fmt(_to_float(failure_row, "auprc")),
                "top_k_recall": _fmt(_to_float(failure_row, "top_k_failure_recall")),
            }
        )
    return rows


def build_proxy_comparison_rows(reliability_rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in reliability_rows:
        grouped[row["method"]].append(row)
    rows: list[dict] = []
    for method, selected in sorted(grouped.items()):
        selected.sort(key=lambda row: (-float(row["pixel_corr"]), -float(row["slice_corr"]), float(row["mae_50pct_low_u"])))
        for rank, row in enumerate(selected, start=1):
            rows.append({"method": method, "rank": rank, **{key: row[key] for key in row if key != "method"}})
    return rows


def build_method_comparison_rows(reliability_rows: list[dict], proxy_name: str = "Baseline disagreement") -> list[dict]:
    rows = [row for row in reliability_rows if row["proxy"] == proxy_name]
    rows.sort(key=lambda row: (-float(row["pixel_corr"]), -float(row["slice_corr"]), float(row["mae_50pct_low_u"])))
    return [{"rank": rank, **row} for rank, row in enumerate(rows, start=1)]


def build_masked_rows(mask_summary_rows: list[dict]) -> list[dict]:
    grouped: dict[str, dict[str, float]] = defaultdict(dict)
    for row in mask_summary_rows:
        grouped[row["method"]][row["metric"]] = _to_float(row, "mean")
    rows: list[dict] = []
    for method_name, metrics in sorted(grouped.items()):
        method, proxy = _split_method(method_name)
        rows.append(
            {
                "method": _display_method(method),
                "proxy": _display_proxy(proxy),
                "all_pixel_corr": _fmt(metrics.get("pixel_corr_all", float("nan"))),
                "nonzero_corr": _fmt(metrics.get("pixel_corr_nonzero", float("nan"))),
                "background_corr": _fmt(metrics.get("pixel_corr_background", float("nan"))),
                "nonzero_minus_all": _fmt(metrics.get("corr_drop_nonzero_minus_all", float("nan"))),
                "background_fraction": _fmt(metrics.get("background_fraction", float("nan"))),
            }
        )
    rows.sort(key=lambda row: (row["proxy"] != "Baseline disagreement", row["method"]))
    return rows


def build_failure_rows(failure_rows: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for row in failure_rows:
        method, proxy = _split_method(row["method"])
        rows.append(
            {
                "method": _display_method(method),
                "proxy": _display_proxy(proxy),
                "cases": row["cases"],
                "failure_cases": row["failure_cases"],
                "auroc": _fmt(_to_float(row, "auroc")),
                "auprc": _fmt(_to_float(row, "auprc")),
                "top_k_recall": _fmt(_to_float(row, "top_k_failure_recall")),
            }
        )
    rows.sort(key=lambda row: (-float(row["auroc"]), -float(row["auprc"]), row["method"], row["proxy"]))
    return rows


def _md_table(headers: list[str], rows: list[dict], keys: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---" for _ in headers]) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(key, "")) for key in keys) + " |")
    return lines


def write_summary_md(
    path: Path,
    profile: str,
    reliability_rows: list[dict],
    proxy_rows: list[dict],
    method_rows: list[dict],
    failure_rows: list[dict],
    masked_rows: list[dict],
) -> None:
    main_methods = [row["method"] for row in method_rows]
    main_corr = [float(row["pixel_corr"]) for row in method_rows if row.get("pixel_corr")]
    if main_corr:
        corr_range = f"{min(main_corr):.2f}-{max(main_corr):.2f}"
    else:
        corr_range = ""
    main_method_text = "、".join(main_methods)
    lines = [
        f"# {profile} RASI post-hoc reliability 中文总结",
        "",
        "说明：本页只汇总 post-hoc uncertainty 结果，不包含任何新 RASI-Net 训练结论。",
        "",
        "## 1. 主结论",
        "",
        f"- `baseline_disagreement` 是当前最稳的 proxy：在 {main_method_text} 上全像素 corr 约 `{corr_range}`，非零脑区 corr 仍为正。",
        "- 背景区域会抬高 pixel-level corr，因此论文表述中应优先报告 masked/nonzero 版本。",
        "- residual-to-linear / residual-to-cubic 可以作为 sanity 或 ablation，不应作为主故事。",
        "",
        "## 2. 全部 method/proxy 可靠性表",
        "",
    ]
    lines.extend(
        _md_table(
            ["方法", "Proxy", "Cases", "MAE", "Pixel corr", "Slice corr", "AURC", "MAE@50% low-U", "Failure AUROC", "Failure AUPRC", "Top-k recall"],
            reliability_rows,
            ["method", "proxy", "cases", "mae_mean", "pixel_corr", "slice_corr", "aurc", "mae_50pct_low_u", "failure_auroc", "failure_auprc", "top_k_recall"],
        )
    )
    lines.extend(["", "## 3. Proxy 对比表", ""])
    lines.extend(
        _md_table(
            ["方法", "排名", "Proxy", "Cases", "Pixel corr", "Slice corr", "AURC", "MAE@50% low-U", "Failure AUROC", "Top-k recall"],
            proxy_rows,
            ["method", "rank", "proxy", "cases", "pixel_corr", "slice_corr", "aurc", "mae_50pct_low_u", "failure_auroc", "top_k_recall"],
        )
    )
    lines.extend(["", "## 4. Baseline disagreement 方法对比表", ""])
    lines.extend(
        _md_table(
            ["排名", "方法", "Cases", "Pixel corr", "Slice corr", "AURC", "MAE@50% low-U", "Failure AUROC", "Top-k recall"],
            method_rows,
            ["rank", "method", "cases", "pixel_corr", "slice_corr", "aurc", "mae_50pct_low_u", "failure_auroc", "top_k_recall"],
        )
    )
    lines.extend(["", "## 5. Failure detection 表", ""])
    lines.extend(
        _md_table(
            ["方法", "Proxy", "Cases", "Failure cases", "AUROC", "AUPRC", "Top-k recall"],
            failure_rows,
            ["method", "proxy", "cases", "failure_cases", "auroc", "auprc", "top_k_recall"],
        )
    )
    lines.extend(["", "## 6. Masked / nonzero 主表", ""])
    lines.extend(
        _md_table(
            ["方法", "Proxy", "All pixel corr", "Nonzero corr", "Background corr", "Nonzero-All", "Background fraction"],
            masked_rows,
            ["method", "proxy", "all_pixel_corr", "nonzero_corr", "background_corr", "nonzero_minus_all", "background_fraction"],
        )
    )
    lines.extend(
        [
            "",
            "## 7. 建议写法",
            "",
            "当前更稳的表述是：在不重新训练模型的情况下，多个强插值模型之间的 baseline disagreement 可以作为低成本 failure-aware reliability signal；它与真实误差保持正相关，并能较好识别高误差 case。由于全像素结果受背景影响，主文应优先报告 nonzero/masked 版本，all-pixel 结果作为补充。",
        ]
    )
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_tables(profile: str) -> Path:
    metrics_dir = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / profile / "metrics"
    report_dir = ensure_dir(ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / profile)
    summary_rows = _read_csv(metrics_dir / "summary_posthoc_reliability.csv")
    failure_raw = _read_csv(metrics_dir / "failure_detection_posthoc.csv")
    mask_summary = _read_csv(report_dir / "qc_mask_background_summary.csv")

    reliability_rows = build_reliability_rows(summary_rows, failure_raw)
    proxy_rows = build_proxy_comparison_rows(reliability_rows)
    method_rows = build_method_comparison_rows(reliability_rows)
    failure_rows = build_failure_rows(failure_raw)
    masked_rows = build_masked_rows(mask_summary)

    write_csv(report_dir / f"{profile}_reliability_summary_cn.csv", reliability_rows)
    write_csv(report_dir / f"{profile}_proxy_comparison.csv", proxy_rows)
    write_csv(report_dir / f"{profile}_method_comparison_baseline_disagreement.csv", method_rows)
    write_csv(report_dir / f"{profile}_failure_detection_table.csv", failure_rows)
    write_csv(report_dir / f"{profile}_masked_nonzero_table.csv", masked_rows)
    write_summary_md(report_dir / f"{profile}_summary.md", profile, reliability_rows, proxy_rows, method_rows, failure_rows, masked_rows)
    return report_dir / f"{profile}_summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Chinese summary tables for RASI post-hoc uncertainty.")
    parser.add_argument("--profile", default="full_test115")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = build_tables(args.profile)
    print(f"Wrote Chinese table summary to {path}")


if __name__ == "__main__":
    main()
