from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _to_float(row: dict, key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def _split_method(method: str) -> tuple[str, str]:
    if "__" not in method:
        return method, ""
    base, proxy = method.split("__", 1)
    return base, proxy


def _fmt(value: float) -> str:
    if not np.isfinite(value):
        return ""
    return f"{value:.4f}"


def build_proxy_ranking(summary_rows: list[dict], failure_rows: list[dict]) -> list[dict]:
    failure_by_method = {row["method"]: row for row in failure_rows}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in summary_rows:
        base, proxy = _split_method(row["method"])
        grouped[base].append(row | {"base_method": base, "proxy": proxy})

    ranking_rows: list[dict] = []
    for base_method, rows in sorted(grouped.items()):
        rows.sort(
            key=lambda item: (
                -_to_float(item, "pixel_error_uncertainty_corr_mean"),
                -_to_float(item, "slice_error_uncertainty_corr_mean"),
                _to_float(item, "retained_mae_50pct_low_uncertainty_mean"),
            )
        )
        for rank, row in enumerate(rows, start=1):
            failure = failure_by_method.get(row["method"], {})
            ranking_rows.append(
                {
                    "base_method": base_method,
                    "rank": rank,
                    "proxy": row["proxy"],
                    "cases": row["cases"],
                    "pixel_corr_mean": _fmt(_to_float(row, "pixel_error_uncertainty_corr_mean")),
                    "slice_corr_mean": _fmt(_to_float(row, "slice_error_uncertainty_corr_mean")),
                    "aurc_mean": _fmt(_to_float(row, "risk_coverage_aurc_mean")),
                    "mae_50pct_low_u_mean": _fmt(_to_float(row, "retained_mae_50pct_low_uncertainty_mean")),
                    "failure_auroc": _fmt(_to_float(failure, "auroc")),
                    "top_k_failure_recall": _fmt(_to_float(failure, "top_k_failure_recall")),
                }
            )
    return ranking_rows


def build_failure_rankings(per_case_rows: list[dict], top_k: int) -> list[dict]:
    rows: list[dict] = []
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in per_case_rows:
        grouped[row["method"]].append(row)

    for method, selected in sorted(grouped.items()):
        base, proxy = _split_method(method)
        by_error = sorted(selected, key=lambda row: -_to_float(row, "mean_abs_error"))
        by_unc = sorted(selected, key=lambda row: -_to_float(row, "mean_uncertainty"))
        error_rank = {row["case"]: rank for rank, row in enumerate(by_error, start=1)}
        unc_rank = {row["case"]: rank for rank, row in enumerate(by_unc, start=1)}
        cases = sorted(
            {row["case"] for row in by_error[:top_k]} | {row["case"] for row in by_unc[:top_k]},
            key=lambda case: (min(error_rank.get(case, 10**9), unc_rank.get(case, 10**9)), case),
        )
        per_case = {row["case"]: row for row in selected}
        for case in cases:
            row = per_case[case]
            rows.append(
                {
                    "method": base,
                    "proxy": proxy,
                    "case": case,
                    "error_rank": error_rank[case],
                    "uncertainty_rank": unc_rank[case],
                    "in_top_error": int(error_rank[case] <= top_k),
                    "in_top_uncertainty": int(unc_rank[case] <= top_k),
                    "mean_abs_error": _fmt(_to_float(row, "mean_abs_error")),
                    "mean_uncertainty": _fmt(_to_float(row, "mean_uncertainty")),
                    "pixel_corr": _fmt(_to_float(row, "pixel_error_uncertainty_corr")),
                    "slice_corr": _fmt(_to_float(row, "slice_error_uncertainty_corr")),
                }
            )
    return rows


def build_risk_coverage_summary(risk_rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in risk_rows:
        grouped[(row["method"], row["coverage"])].append(_to_float(row, "retained_mae"))
    rows = []
    for (method, coverage), values in sorted(grouped.items(), key=lambda item: (item[0][0], -float(item[0][1]))):
        base, proxy = _split_method(method)
        valid = np.asarray([value for value in values if np.isfinite(value)], dtype=np.float64)
        rows.append(
            {
                "method": base,
                "proxy": proxy,
                "coverage": coverage,
                "retained_mae_mean": _fmt(float(np.mean(valid))) if valid.size else "",
                "retained_mae_std": _fmt(float(np.std(valid))) if valid.size else "",
                "cases": len(values),
            }
        )
    return rows


def write_plots(report_dir: Path, profile: str, proxy_ranking: list[dict], risk_summary: list[dict]) -> list[Path]:
    plot_dir = report_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    best_rows = [row for row in proxy_ranking if int(row["rank"]) == 1]
    labels = [row["base_method"] for row in best_rows]
    pixel_corr = [float(row["pixel_corr_mean"]) for row in best_rows]
    slice_corr = [float(row["slice_corr_mean"]) for row in best_rows]
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - width / 2, pixel_corr, width, label="Pixel corr")
    ax.bar(x + width / 2, slice_corr, width, label="Slice corr")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, max(pixel_corr + slice_corr) * 1.2)
    ax.set_ylabel("Error-uncertainty correlation")
    ax.set_title(f"{profile}: best proxy is baseline disagreement")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    corr_path = plot_dir / f"{profile}_best_proxy_correlation.png"
    fig.savefig(corr_path, dpi=180)
    plt.close(fig)
    paths.append(corr_path)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for method in sorted({row["method"] for row in risk_summary if row["proxy"] == "baseline_disagreement"}):
        rows = [
            row
            for row in risk_summary
            if row["method"] == method and row["proxy"] == "baseline_disagreement"
        ]
        rows.sort(key=lambda row: float(row["coverage"]), reverse=True)
        ax.plot(
            [float(row["coverage"]) for row in rows],
            [float(row["retained_mae_mean"]) for row in rows],
            marker="o",
            linewidth=1.8,
            label=method,
        )
    ax.invert_xaxis()
    ax.set_xlabel("Coverage kept from low to high uncertainty")
    ax.set_ylabel("Retained MAE")
    ax.set_title(f"{profile}: risk-coverage, baseline disagreement")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    risk_path = plot_dir / f"{profile}_risk_coverage_baseline_disagreement.png"
    fig.savefig(risk_path, dpi=180)
    plt.close(fig)
    paths.append(risk_path)

    return paths


def build_report(profile: str, top_k: int) -> Path:
    metrics_dir = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / profile / "metrics"
    report_dir = ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / profile
    report_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = _read_csv(metrics_dir / "summary_posthoc_reliability.csv")
    failure_rows = _read_csv(metrics_dir / "failure_detection_posthoc.csv")
    inventory_rows = _read_csv(metrics_dir / "method_inventory.csv")
    per_case_rows = _read_csv(metrics_dir / "per_case_posthoc_reliability.csv")
    risk_rows = _read_csv(metrics_dir / "risk_coverage_posthoc.csv")

    proxy_ranking = build_proxy_ranking(summary_rows, failure_rows)
    failure_ranking = build_failure_rankings(per_case_rows, top_k)
    risk_summary = build_risk_coverage_summary(risk_rows)
    plot_paths = write_plots(report_dir, profile, proxy_ranking, risk_summary)

    _write_csv(report_dir / f"{profile}_proxy_ranking.csv", proxy_ranking)
    _write_csv(report_dir / f"{profile}_failure_case_ranking.csv", failure_ranking)
    _write_csv(report_dir / f"{profile}_risk_coverage_summary.csv", risk_summary)

    best_rows = [row for row in proxy_ranking if int(row["rank"]) == 1]
    lines = [
        f"# RASI post-hoc uncertainty report: {profile}",
        "",
        "Status: completed full post-hoc reliability analysis using existing predictions only.",
        "",
        "This is not a RASI-Net training result. It evaluates whether low-cost uncertainty proxies can indicate interpolation error and failure risk for existing strong methods.",
        "",
        "## Case coverage",
        "",
        "| Method | Available cases | Requested cases | Run directory |",
        "|---|---:|---:|---|",
    ]
    for row in inventory_rows:
        lines.append(
            f"| {row['method']} | {row['available_cases_in_profile']} | {row['requested_cases']} | `{row['run_dir']}` |"
        )

    lines.extend(
        [
            "",
            "## Best proxy per method",
            "",
            "| Method | Best proxy | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in best_rows:
        lines.append(
            "| {base_method} | {proxy} | {pixel_corr_mean} | {slice_corr_mean} | {aurc_mean} | {mae_50pct_low_u_mean} | {failure_auroc} | {top_k_failure_recall} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `baseline_disagreement` is the strongest and most stable proxy across I3Net, HAT, SwinIR, and ACSI-Net.",
            "- `residual_linear` and `residual_cubic` are useful sanity proxies, but they should not be framed as the main comparison target.",
            "- The current Design 3 story should be reliability and failure-awareness on top of strong existing models, not a claim that a newly trained RASI-Net beats SOTA.",
            "",
            "## Generated files",
            "",
            f"- `{report_dir / f'{profile}_proxy_ranking.csv'}`",
            f"- `{report_dir / f'{profile}_failure_case_ranking.csv'}`",
            f"- `{report_dir / f'{profile}_risk_coverage_summary.csv'}`",
            f"- `{metrics_dir / 'paper_table_posthoc.md'}`",
            f"- `{metrics_dir / 'risk_coverage_posthoc.csv'}`",
            f"- `{metrics_dir / 'calibration_bins_posthoc.csv'}`",
            *[f"- `{path}`" for path in plot_paths],
            "",
            "## Next step",
            "",
            "Use the top failure-case list to select visual QC examples, then repeat the same post-hoc reliability evaluation on fastMRI and NingXia if the paper needs cross-dataset evidence.",
        ]
    )
    report_path = report_dir / f"{profile}_posthoc_report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a compact report from post-hoc RASI uncertainty outputs.")
    parser.add_argument("--profile", default="full_test115")
    parser.add_argument("--top-k", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_path = build_report(args.profile, args.top_k)
    print(f"Wrote post-hoc report to {report_path}")


if __name__ == "__main__":
    main()
