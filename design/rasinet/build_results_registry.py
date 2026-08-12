from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = REPO_ROOT / "design" / "rasinet" / "outputs"


def _read(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build() -> Path:
    rows: list[dict[str, object]] = []
    run_date = date.today().isoformat()
    primary_path = OUTPUT_ROOT / "icassp_primary" / "summary.csv"
    for index, result in enumerate(_read(primary_path)):
        for metric in (
            "pixel_fisher_z_mean",
            "all_pixel_fisher_z_mean",
            "case_spearman",
            "case_kendall",
            "normalized_aurc",
            "rrr_25",
            "rrr_50",
            "rrr_75",
            "retained_mae_50",
            "failure_auroc",
            "failure_auprc",
        ):
            rows.append(
                {
                    "experiment_id": f"primary_{index:04d}_{metric}",
                    "dataset": result["dataset"],
                    "target_model": result["target"],
                    "committee": result["committee"],
                    "score": result["score"],
                    "mask": result["mask"],
                    "normalization": result["normalization"],
                    "metric": metric,
                    "seed": 20260715,
                    "number_of_cases": result["cases"],
                    "development_or_test": "retrospective_test_observed",
                    "run_date": run_date,
                    "code_commit": "unversioned-workspace",
                    "output_file": str(primary_path),
                }
            )
    stress_path = OUTPUT_ROOT / "shared_error_stress" / "summary.csv"
    for index, result in enumerate(_read(stress_path)):
        rows.append(
            {
                "experiment_id": f"stress_{index:03d}_{result['metric']}",
                "dataset": "ixi",
                "target_model": "all_four",
                "committee": "all_non_target_members",
                "score": f"stress_{result['mode']}_strength_{result['strength']}",
                "mask": "frozen_target_0.01",
                "normalization": "raw",
                "metric": result["metric"],
                "seed": 20260715,
                "number_of_cases": result.get("number_of_cases", result["cases_times_targets"]),
                "development_or_test": "retrospective_synthetic_stress",
                "run_date": run_date,
                "code_commit": "unversioned-workspace",
                "output_file": str(stress_path),
            }
        )
    tta_path = OUTPUT_ROOT / "tta_fastmri_unified" / "summary.csv"
    for index, result in enumerate(_read(tta_path)):
        for metric in ("pixel_fisher_z_mean", "all_pixel_fisher_z_mean", "case_spearman", "normalized_aurc", "rrr_50", "failure_auroc", "failure_auprc"):
            rows.append(
                {
                    "experiment_id": f"tta_fastmri_{index:02d}_{metric}",
                    "dataset": result["dataset"],
                    "target_model": result["target"],
                    "committee": "single_model_four_view_flip_tta",
                    "score": "tta_variance",
                    "mask": result["mask"],
                    "normalization": result["normalization"],
                    "metric": metric,
                    "seed": 20260715,
                    "number_of_cases": result["cases"],
                    "development_or_test": "retrospective_test_observed",
                    "run_date": run_date,
                    "code_commit": "unversioned-workspace",
                    "output_file": str(tta_path),
                }
            )
    analytical_path = OUTPUT_ROOT / "analytical_cost" / "summary.csv"
    for index, result in enumerate(_read(analytical_path)):
        for metric in ("seconds_mean", "seconds_p95", "saved_output_mib_mean"):
            rows.append(
                {
                    "experiment_id": f"analytical_cost_{index:02d}_{metric}",
                    "dataset": result["profile"],
                    "target_model": result["kind"],
                    "committee": "not_applicable",
                    "score": "analytical_interpolation_cost",
                    "mask": "not_applicable",
                    "normalization": "raw",
                    "metric": metric,
                    "seed": 20260715,
                    "number_of_cases": result["number_of_cases"],
                    "development_or_test": "fixed_cost_benchmark",
                    "run_date": run_date,
                    "code_commit": "unversioned-workspace",
                    "output_file": str(analytical_path),
                }
            )
    posthoc_path = OUTPUT_ROOT / "posthoc_cost" / "summary.csv"
    for index, result in enumerate(_read(posthoc_path)):
        for metric in (
            "load_seconds_mean",
            "load_seconds_p95",
            "score_seconds_mean",
            "score_seconds_p95",
            "total_seconds_mean",
            "total_seconds_p95",
            "source_mib_mean",
            "observed_peak_rss_gib",
        ):
            rows.append(
                {
                    "experiment_id": f"posthoc_cost_{index:02d}_{metric}",
                    "dataset": result["profile"],
                    "target_model": "swinir",
                    "committee": "all_non_target_members",
                    "score": "target_abs_median_cost",
                    "mask": "target_0.01",
                    "normalization": "raw",
                    "metric": metric,
                    "seed": 20260715,
                    "number_of_cases": result["number_of_cases"],
                    "development_or_test": "fixed_cost_benchmark",
                    "run_date": run_date,
                    "code_commit": "unversioned-workspace",
                    "output_file": str(posthoc_path),
                }
            )
    output = OUTPUT_ROOT / "results_registry.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "experiment_id",
        "dataset",
        "target_model",
        "committee",
        "score",
        "mask",
        "normalization",
        "metric",
        "seed",
        "number_of_cases",
        "development_or_test",
        "run_date",
        "code_commit",
        "output_file",
    )
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return output


if __name__ == "__main__":
    print(build())
