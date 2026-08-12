from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ixi_diffusion.common import ensure_dir


ROOT = Path(__file__).resolve().parents[1]


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _to_float(row: dict, key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def _split_method(method: str) -> tuple[str, str]:
    if "__" not in method:
        return method, ""
    return tuple(method.split("__", 1))  # type: ignore[return-value]


def _display_method(name: str) -> str:
    return {
        "i3net": "I3Net",
        "hat": "HAT",
        "swinir": "SwinIR",
        "acsinet": "ACSI",
    }.get(name, name)


def _display_proxy(name: str) -> str:
    return {
        "baseline_disagreement": "Disagreement",
        "residual_linear": "Residual-linear",
        "residual_cubic": "Residual-cubic",
    }.get(name, name)


def plot_risk_coverage(risk_rows: list[dict], figure_dir: Path, profile: str) -> Path:
    grouped: dict[str, dict[float, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in risk_rows:
        method, proxy = _split_method(row["method"])
        if proxy != "baseline_disagreement":
            continue
        grouped[_display_method(method)][_to_float(row, "coverage")].append(_to_float(row, "retained_mae"))

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    for method, by_coverage in sorted(grouped.items()):
        coverages = sorted(by_coverage.keys(), reverse=True)
        retained_mae = [float(np.nanmean(by_coverage[coverage])) for coverage in coverages]
        ax.plot(coverages, retained_mae, marker="o", linewidth=2.0, label=method)
    ax.invert_xaxis()
    ax.set_xlabel("Coverage kept, low to high uncertainty")
    ax.set_ylabel("Retained MAE")
    ax.set_title(f"{profile}: risk-coverage using baseline disagreement")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path = figure_dir / "risk_coverage_baseline_disagreement.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_correlation_bars(summary_rows: list[dict], figure_dir: Path, profile: str) -> Path:
    rows = []
    for row in summary_rows:
        method, proxy = _split_method(row["method"])
        rows.append(
            {
                "label": f"{_display_method(method)}\n{_display_proxy(proxy)}",
                "proxy": proxy,
                "pixel": _to_float(row, "pixel_error_uncertainty_corr_mean"),
                "slice": _to_float(row, "slice_error_uncertainty_corr_mean"),
            }
        )
    proxy_order = {"baseline_disagreement": 0, "residual_cubic": 1, "residual_linear": 2}
    rows.sort(key=lambda row: (proxy_order.get(row["proxy"], 9), row["label"]))

    x = np.arange(len(rows))
    width = 0.38
    fig, ax = plt.subplots(figsize=(13.0, 5.2))
    ax.bar(x - width / 2, [row["pixel"] for row in rows], width, label="Pixel corr")
    ax.bar(x + width / 2, [row["slice"] for row in rows], width, label="Slice corr")
    ax.set_xticks(x)
    ax.set_xticklabels([row["label"] for row in rows], rotation=45, ha="right")
    ax.set_ylabel("Error-uncertainty correlation")
    ax.set_title(f"{profile}: correlations by method and proxy")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path = figure_dir / "correlation_all_method_proxy.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_masked_vs_all(mask_rows: list[dict], figure_dir: Path, profile: str) -> Path:
    rows = []
    for row in mask_rows:
        if row["proxy"] != "Baseline disagreement":
            continue
        rows.append(row)
    rows.sort(key=lambda row: row["method"])

    x = np.arange(len(rows))
    width = 0.38
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.bar(x - width / 2, [float(row["all_pixel_corr"]) for row in rows], width, label="All pixels")
    ax.bar(x + width / 2, [float(row["nonzero_corr"]) for row in rows], width, label="Nonzero mask")
    ax.set_xticks(x)
    ax.set_xticklabels([row["method"] for row in rows])
    ax.set_ylabel("Pixel error-uncertainty correlation")
    ax.set_title(f"{profile}: all-pixel vs nonzero masked correlation")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path = figure_dir / "masked_vs_all_correlation.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_failure_recall(failure_rows: list[dict], figure_dir: Path, profile: str) -> Path:
    rows = [row for row in failure_rows if row["proxy"] == "Baseline disagreement"]
    rows.sort(key=lambda row: row["method"])
    x = np.arange(len(rows))
    width = 0.38

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.bar(x - width / 2, [float(row["auroc"]) for row in rows], width, label="AUROC")
    ax.bar(x + width / 2, [float(row["top_k_recall"]) for row in rows], width, label="Top-k recall")
    ax.set_xticks(x)
    ax.set_xticklabels([row["method"] for row in rows])
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Failure detection score")
    ax.set_title(f"{profile}: failure detection with baseline disagreement")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path = figure_dir / "failure_detection_baseline_disagreement.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def write_figure_index(path: Path, figure_paths: list[Path]) -> None:
    lines = [
        "# full_test115 图表索引",
        "",
        "这些图用于 RASI post-hoc uncertainty 的第 5 步。图表只基于已有预测和 QC 表，不涉及新模型训练。",
        "",
    ]
    for figure_path in figure_paths:
        lines.append(f"- `{figure_path.name}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_figures(profile: str) -> list[Path]:
    metrics_dir = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / profile / "metrics"
    report_dir = ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / profile
    figure_dir = ensure_dir(report_dir / "figures")
    summary_rows = _read_csv(metrics_dir / "summary_posthoc_reliability.csv")
    risk_rows = _read_csv(metrics_dir / "risk_coverage_posthoc.csv")
    mask_rows = _read_csv(report_dir / f"{profile}_masked_nonzero_table.csv")
    failure_rows = _read_csv(report_dir / f"{profile}_failure_detection_table.csv")

    paths = [
        plot_risk_coverage(risk_rows, figure_dir, profile),
        plot_correlation_bars(summary_rows, figure_dir, profile),
        plot_masked_vs_all(mask_rows, figure_dir, profile),
        plot_failure_recall(failure_rows, figure_dir, profile),
    ]
    write_figure_index(figure_dir / "figure_index.md", paths)
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build figures for RASI post-hoc uncertainty.")
    parser.add_argument("--profile", default="full_test115")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = build_figures(args.profile)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
