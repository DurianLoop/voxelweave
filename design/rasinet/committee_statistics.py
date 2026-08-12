from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from ixi_diffusion.common import ensure_dir, write_csv

from .committee_reliability import risk_coverage_summary


REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILES = ("full_test115", "fastmri_full", "ningxia_cv")


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def paired_bootstrap_difference(
    first: np.ndarray,
    second: np.ndarray,
    samples: int = 2000,
    seed: int = 20260715,
) -> dict[str, float]:
    first_array = np.asarray(first, dtype=np.float64).reshape(-1)
    second_array = np.asarray(second, dtype=np.float64).reshape(-1)
    if first_array.size == 0 or first_array.size != second_array.size:
        raise ValueError("paired arrays must be non-empty and have equal length")
    if not np.isfinite(first_array).all() or not np.isfinite(second_array).all():
        raise ValueError("paired arrays must be finite")
    differences = first_array - second_array
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, differences.size, size=(samples, differences.size))
    bootstrap_means = np.mean(differences[indices], axis=1)
    return {
        "mean_difference": float(np.mean(differences)),
        "ci95_low": float(np.percentile(bootstrap_means, 2.5)),
        "ci95_high": float(np.percentile(bootstrap_means, 97.5)),
    }


def _rankdata(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=np.float64)
    sorted_values = values[order]
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and sorted_values[end] == sorted_values[start]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1)
        start = end
    return ranks


def _safe_corr(first: np.ndarray, second: np.ndarray) -> float:
    first = np.asarray(first, dtype=np.float64).reshape(-1)
    second = np.asarray(second, dtype=np.float64).reshape(-1)
    if first.size != second.size or first.size < 2:
        return float("nan")
    if float(np.std(first)) <= 1e-12 or float(np.std(second)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(first, second)[0, 1])


def _spearman(first: np.ndarray, second: np.ndarray) -> float:
    return _safe_corr(_rankdata(first), _rankdata(second))


def bootstrap_reliability_metrics(
    errors: np.ndarray,
    scores: np.ndarray,
    pixel_correlations: np.ndarray,
    samples: int = 2000,
    seed: int = 20260715,
) -> dict[str, dict[str, float]]:
    errors = np.asarray(errors, dtype=np.float64).reshape(-1)
    scores = np.asarray(scores, dtype=np.float64).reshape(-1)
    pixel_correlations = np.asarray(pixel_correlations, dtype=np.float64).reshape(-1)
    if errors.size == 0 or errors.size != scores.size or errors.size != pixel_correlations.size:
        raise ValueError("errors, scores, and pixel correlations must have equal non-zero length")
    if not np.isfinite(errors).all() or not np.isfinite(scores).all() or not np.isfinite(pixel_correlations).all():
        raise ValueError("bootstrap inputs must be finite")

    point_risk = risk_coverage_summary(errors, scores)
    points = {
        "pixel_corr_mean": float(np.mean(pixel_correlations)),
        "case_spearman": _spearman(errors, scores),
        "normalized_aurc": float(point_risk["normalized_aurc"]),
        "relative_risk_reduction_at_50": float(point_risk["relative_risk_reduction_at_50"]),
    }
    rng = np.random.default_rng(seed)
    bootstrap: dict[str, list[float]] = {name: [] for name in points}
    for _ in range(samples):
        indices = rng.integers(0, errors.size, size=errors.size)
        sampled_errors = errors[indices]
        sampled_scores = scores[indices]
        sampled_risk = risk_coverage_summary(sampled_errors, sampled_scores)
        bootstrap["pixel_corr_mean"].append(float(np.mean(pixel_correlations[indices])))
        bootstrap["case_spearman"].append(_spearman(sampled_errors, sampled_scores))
        bootstrap["normalized_aurc"].append(float(sampled_risk["normalized_aurc"]))
        bootstrap["relative_risk_reduction_at_50"].append(
            float(sampled_risk["relative_risk_reduction_at_50"])
        )
    output: dict[str, dict[str, float]] = {}
    for name, point in points.items():
        values = np.asarray(bootstrap[name], dtype=np.float64)
        values = values[np.isfinite(values)]
        output[name] = {
            "point": point,
            "ci95_low": float(np.percentile(values, 2.5)),
            "ci95_high": float(np.percentile(values, 97.5)),
        }
    return output


def leave_one_member_out_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["profile"]), str(row["target"]), str(row["case"]))].append(row)

    expected_members: dict[tuple[str, str], tuple[str, ...]] = {}
    for (profile, target, _case), selected in grouped.items():
        members = tuple(sorted(str(row["member"]) for row in selected))
        key = (profile, target)
        if key in expected_members and expected_members[key] != members:
            raise ValueError(f"inconsistent committee membership for {profile}/{target}")
        expected_members[key] = members

    output: list[dict] = []
    for (profile, target, case), selected in sorted(grouped.items()):
        member_scores = {str(row["member"]): float(row["mean_member_disagreement"]) for row in selected}
        errors = {float(row["mean_abs_error"]) for row in selected}
        if len(errors) != 1:
            raise ValueError(f"inconsistent case error for {profile}/{target}/{case}")
        error_value = next(iter(errors))
        for excluded in sorted(member_scores):
            retained = [member for member in sorted(member_scores) if member != excluded]
            if not retained:
                raise ValueError(f"empty leave-one-out committee for {profile}/{target}/{case}")
            output.append(
                {
                    "profile": profile,
                    "target": target,
                    "case": case,
                    "excluded_member": excluded,
                    "committee_members": ";".join(retained),
                    "committee_score": float(np.median([member_scores[member] for member in retained])),
                    "mean_abs_error": error_value,
                }
            )
    return output


def _bootstrap_ranking_difference(
    errors: np.ndarray,
    main_scores: np.ndarray,
    comparator_scores: np.ndarray,
    samples: int,
    seed: int,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    differences = []
    for _ in range(samples):
        indices = rng.integers(0, errors.size, size=errors.size)
        sampled_errors = errors[indices]
        main = risk_coverage_summary(sampled_errors, main_scores[indices])
        comparator = risk_coverage_summary(sampled_errors, comparator_scores[indices])
        differences.append(float(main["normalized_aurc"]) - float(comparator["normalized_aurc"]))
    array = np.asarray(differences, dtype=np.float64)
    point = float(risk_coverage_summary(errors, main_scores)["normalized_aurc"]) - float(
        risk_coverage_summary(errors, comparator_scores)["normalized_aurc"]
    )
    return {
        "mean_difference": point,
        "ci95_low": float(np.percentile(array, 2.5)),
        "ci95_high": float(np.percentile(array, 97.5)),
    }


def _primary_rows(rows: list[dict], target: str, proxy: str, mode: str) -> dict[str, dict]:
    return {
        str(row["case"]): row
        for row in rows
        if row["target"] == target
        and row["proxy"] == proxy
        and row["committee_mode"] == mode
        and row["excluded_member"] == ""
    }


def build_reports(samples: int = 2000, seed: int = 20260715) -> Path:
    report_dir = ensure_dir(REPO_ROOT / "design" / "rasinet" / "reports" / "committee_reliability")
    composition_rows: list[dict] = []
    paired_rows: list[dict] = []
    operating_rows: list[dict] = []
    loo_all: list[dict] = []
    main_ci_rows: list[dict] = []

    for profile_index, profile in enumerate(PROFILES):
        metrics_dir = REPO_ROOT / "design" / "rasinet" / "runs" / "committee_reliability" / profile / "metrics"
        per_case = _read_csv(metrics_dir / "per_case_committee.csv")
        summaries = _read_csv(metrics_dir / "summary_committee.csv")
        member_rows = _read_csv(metrics_dir / "per_member_disagreement_scores.csv")
        loo_rows = leave_one_member_out_rows(member_rows)
        loo_all.extend(loo_rows)

        targets = sorted({str(row["target"]) for row in per_case})
        for target_index, target in enumerate(targets):
            main = _primary_rows(per_case, target, "target_to_committee", "all")
            if not main:
                continue
            main_cases = sorted(main)
            main_errors = np.asarray([float(main[case]["mean_abs_error"]) for case in main_cases])
            main_scores = np.asarray([float(main[case]["mean_uncertainty"]) for case in main_cases])
            main_pixels = np.asarray([float(main[case]["pixel_corr_foreground"]) for case in main_cases])
            main_ci = bootstrap_reliability_metrics(
                main_errors,
                main_scores,
                main_pixels,
                samples=samples,
                seed=seed + 5000 + 100 * profile_index + target_index,
            )
            for metric, values in main_ci.items():
                main_ci_rows.append(
                    {
                        "profile": profile,
                        "target": target,
                        "metric": metric,
                        "cases": len(main_cases),
                        **values,
                    }
                )

            for mode in ("all", "neural", "analytic"):
                selected = _primary_rows(per_case, target, "target_to_committee", mode)
                errors = np.asarray([float(selected[case]["mean_abs_error"]) for case in main_cases])
                scores = np.asarray([float(selected[case]["mean_uncertainty"]) for case in main_cases])
                risk = risk_coverage_summary(errors, scores)
                composition_rows.append(
                    {
                        "profile": profile,
                        "target": target,
                        "analysis": "committee_composition",
                        "committee_mode": mode,
                        "excluded_member": "",
                        "cases": len(main_cases),
                        "case_spearman": _spearman(errors, scores),
                        "normalized_aurc": float(risk["normalized_aurc"]),
                        "risk_at_50": float(risk["risk_at_50"]),
                        "relative_risk_reduction_at_50": float(risk["relative_risk_reduction_at_50"]),
                    }
                )

            target_loo = [row for row in loo_rows if row["target"] == target]
            for excluded in sorted({str(row["excluded_member"]) for row in target_loo}):
                selected = sorted(
                    [row for row in target_loo if row["excluded_member"] == excluded],
                    key=lambda row: str(row["case"]),
                )
                errors = np.asarray([float(row["mean_abs_error"]) for row in selected])
                scores = np.asarray([float(row["committee_score"]) for row in selected])
                risk = risk_coverage_summary(errors, scores)
                composition_rows.append(
                    {
                        "profile": profile,
                        "target": target,
                        "analysis": "score_level_leave_one_out",
                        "committee_mode": "all",
                        "excluded_member": excluded,
                        "cases": len(selected),
                        "case_spearman": _spearman(errors, scores),
                        "normalized_aurc": float(risk["normalized_aurc"]),
                        "risk_at_50": float(risk["risk_at_50"]),
                        "relative_risk_reduction_at_50": float(risk["relative_risk_reduction_at_50"]),
                    }
                )

            main_summary = next(
                row
                for row in summaries
                if row["target"] == target
                and row["proxy"] == "target_to_committee"
                and row["committee_mode"] == "all"
                and row["excluded_member"] == ""
            )
            for coverage in (25, 50, 75):
                operating_rows.append(
                    {
                        "profile": profile,
                        "target": target,
                        "cases": len(main_cases),
                        "coverage": coverage / 100.0,
                        "retained_mae": float(main_summary[f"risk_at_{coverage}"]),
                        "relative_risk_reduction": float(main_summary[f"relative_risk_reduction_at_{coverage}"]),
                        "normalized_aurc": float(main_summary["normalized_aurc"]),
                    }
                )

            comparators = (
                ("target_to_neural", "target_to_committee", "neural"),
                ("target_to_analytic", "target_to_committee", "analytic"),
                ("committee_dispersion", "committee_dispersion", "all"),
                ("residual_linear", "residual_linear", "analytic"),
                ("residual_cubic", "residual_cubic", "analytic"),
            )
            for comparator_index, (label, proxy, mode) in enumerate(comparators):
                comparator = _primary_rows(per_case, target, proxy, mode)
                common_cases = [case for case in main_cases if case in comparator]
                main_pixel = np.asarray([float(main[case]["pixel_corr_foreground"]) for case in common_cases])
                comparator_pixel = np.asarray([float(comparator[case]["pixel_corr_foreground"]) for case in common_cases])
                pixel_ci = paired_bootstrap_difference(
                    main_pixel,
                    comparator_pixel,
                    samples=samples,
                    seed=seed + 100 * profile_index + 10 * target_index + comparator_index,
                )
                errors = np.asarray([float(main[case]["mean_abs_error"]) for case in common_cases])
                main_risk_scores = np.asarray([float(main[case]["mean_uncertainty"]) for case in common_cases])
                comparator_risk_scores = np.asarray(
                    [float(comparator[case]["mean_uncertainty"]) for case in common_cases]
                )
                aurc_ci = _bootstrap_ranking_difference(
                    errors,
                    main_risk_scores,
                    comparator_risk_scores,
                    samples=samples,
                    seed=seed + 1000 + 100 * profile_index + 10 * target_index + comparator_index,
                )
                for metric, result in (
                    ("pixel_corr_foreground", pixel_ci),
                    ("normalized_aurc", aurc_ci),
                ):
                    paired_rows.append(
                        {
                            "profile": profile,
                            "target": target,
                            "main_proxy": "target_to_all",
                            "comparator": label,
                            "metric": metric,
                            "cases": len(common_cases),
                            **result,
                        }
                    )

    write_csv(report_dir / "committee_composition.csv", composition_rows)
    write_csv(report_dir / "leave_one_member_out_per_case.csv", loo_all)
    write_csv(report_dir / "paired_proxy_bootstrap.csv", paired_rows)
    write_csv(report_dir / "main_bootstrap_ci.csv", main_ci_rows)
    write_csv(report_dir / "coverage_operating_points.csv", operating_rows)
    return report_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build committee reliability statistical reports.")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260715)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = build_reports(samples=args.bootstrap_samples, seed=args.seed)
    print(f"Wrote committee reliability reports to {output}")


if __name__ == "__main__":
    main()
