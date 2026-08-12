from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import nibabel as nib
import numpy as np
import yaml
from scipy import stats

from .cross_scale_protocol import (
    ANALYTICAL,
    DATASETS,
    EXPANDED_NEURAL,
    PRIMARY_NEURAL,
    SCALES,
    analytical_path,
    case_ids,
    case_set_id,
    folds_for,
    ground_truth_path,
    ningxia_case_group,
    ningxia_test_group,
    prediction_path,
    sources_for,
    sparse_input_path,
)
from .icassp_scores import deployment_mask, generated_indices, score_map
from .icassp_statistics import paired_case_bootstrap, ranking_metrics, safe_pearson


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = 20260724
PRIMARY_METHOD = "target_median"
COMPARATORS = (
    "target_mean",
    "all_output_spread",
    "target_excluded_spread",
    "neural_only",
    "analytical_only",
)


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    records = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in records:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_volume(path: Path) -> tuple[np.ndarray, np.ndarray, str]:
    if not path.exists():
        raise FileNotFoundError(path)
    image = nib.load(str(path))
    data = image.get_fdata(dtype=np.float32)
    if data.ndim != 3:
        raise ValueError(f"expected 3-D NIfTI: {path}, shape={data.shape}")
    if not np.isfinite(data).all():
        raise ValueError(f"non-finite NIfTI: {path}")
    return data, image.affine.copy(), "".join(nib.aff2axcodes(image.affine))


def affine_hash(affine: np.ndarray) -> str:
    rounded = np.round(np.asarray(affine, dtype=np.float64), decimals=6)
    return hashlib.sha256(rounded.tobytes()).hexdigest()[:16]


def threshold_mask(volume: np.ndarray, fraction: float = 0.01) -> np.ndarray:
    absolute = np.abs(np.asarray(volume, dtype=np.float32))
    threshold = max(1e-6, fraction * float(np.max(absolute)))
    result = absolute > threshold
    return result if np.any(result) else np.ones_like(result, dtype=bool)


def _sets_for_profile(dataset: str, scale: int, expanded: bool) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    sources = sources_for(REPO_ROOT, dataset, scale, expanded=expanded)
    reference = sources[PRIMARY_NEURAL[0]]
    issues: list[dict[str, Any]] = []
    profile_cases: list[str] = []
    per_fold: dict[str, list[str]] = {}
    for fold in folds_for(dataset):
        fold_name = fold or ""
        expected = set(case_ids(reference, fold))
        per_fold[fold_name] = sorted(expected)
        profile_cases.extend(sorted(expected))
        for name, source in sources.items():
            actual = set(case_ids(source, fold))
            if actual != expected:
                issues.append(
                    {
                        "dataset": dataset,
                        "scale": scale,
                        "fold": fold_name,
                        "model": name,
                        "issue": "case_set_mismatch",
                        "missing": ";".join(sorted(expected - actual)),
                        "extra": ";".join(sorted(actual - expected)),
                    }
                )
        for method in ANALYTICAL:
            directory = reference.run_dir(fold) / "baseline_outputs" / method
            actual = {
                path.name[len(method) + 1 :]
                for path in directory.glob(f"{method}_*.nii.gz")
            }
            if actual != expected:
                issues.append(
                    {
                        "dataset": dataset,
                        "scale": scale,
                        "fold": fold_name,
                        "model": method,
                        "issue": "case_set_mismatch",
                        "missing": ";".join(sorted(expected - actual)),
                        "extra": ";".join(sorted(actual - expected)),
                    }
                )
    if len(profile_cases) != len(set(profile_cases)):
        issues.append(
            {
                "dataset": dataset,
                "scale": scale,
                "fold": "",
                "model": "all",
                "issue": "duplicate_case_across_folds",
                "missing": "",
                "extra": "",
            }
        )
    return {
        "sources": sources,
        "reference": reference,
        "cases": tuple(sorted(profile_cases)),
        "per_fold": per_fold,
    }, issues


def audit(config: dict[str, Any], output: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tolerance = float(config.get("affine_tolerance", 1e-5))
    manifest_rows: list[dict[str, Any]] = []
    issue_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    profile_case_sets: dict[tuple[str, int], tuple[str, ...]] = {}

    for dataset in config.get("datasets", DATASETS):
        for scale in config.get("scales", SCALES):
            profile, set_issues = _sets_for_profile(str(dataset), int(scale), expanded=True)
            issue_rows.extend(set_issues)
            sources = profile["sources"]
            reference = profile["reference"]
            cases = profile["cases"]
            profile_case_sets[(str(dataset), int(scale))] = cases
            common_id = case_set_id(cases)
            shape_mismatches = 0
            affine_mismatches = 0
            orientation_mismatches = 0
            nonfinite = 0
            oof_failures = 0

            for fold in folds_for(str(dataset)):
                held_out = ningxia_test_group(REPO_ROOT, fold) if fold is not None else ""
                for case_id in profile["per_fold"][fold or ""]:
                    gt_path = ground_truth_path(reference, fold, case_id)
                    input_path = sparse_input_path(reference, fold, case_id)
                    gt, gt_affine, gt_orientation = load_volume(gt_path)
                    generated = generated_indices(gt.shape[2], int(scale), anchor_start=0)
                    expected_oof = fold is not None and ningxia_case_group(case_id) == held_out
                    if fold is not None and not expected_oof:
                        oof_failures += 1
                        issue_rows.append(
                            {
                                "dataset": dataset,
                                "scale": scale,
                                "fold": fold,
                                "model": "all",
                                "case_id": case_id,
                                "issue": "not_held_out_for_fold",
                                "missing": held_out,
                                "extra": ningxia_case_group(case_id),
                            }
                        )
                    method_paths = {
                        name: prediction_path(source, fold, case_id)
                        for name, source in sources.items()
                    }
                    method_paths.update(
                        {name: analytical_path(reference, fold, name, case_id) for name in ANALYTICAL}
                    )
                    for method, path in method_paths.items():
                        data, affine, orientation = load_volume(path)
                        shape_ok = data.shape == gt.shape
                        affine_ok = bool(np.allclose(affine, gt_affine, rtol=0.0, atol=tolerance))
                        orientation_ok = orientation == gt_orientation
                        finite_ok = bool(np.isfinite(data).all())
                        shape_mismatches += int(not shape_ok)
                        affine_mismatches += int(not affine_ok)
                        orientation_mismatches += int(not orientation_ok)
                        nonfinite += int(not finite_ok)
                        complete = shape_ok and affine_ok and orientation_ok and finite_ok and expected_oof if fold else shape_ok and affine_ok and orientation_ok and finite_ok
                        if not complete:
                            issue_rows.append(
                                {
                                    "dataset": dataset,
                                    "scale": scale,
                                    "fold": fold or "",
                                    "model": method,
                                    "case_id": case_id,
                                    "issue": "volume_integrity_failure",
                                    "missing": "",
                                    "extra": "",
                                }
                            )
                        manifest_rows.append(
                            {
                                "dataset": dataset,
                                "scale": scale,
                                "case_id": case_id,
                                "fold": fold or "",
                                "target_model": method,
                                "prediction_path": str(path),
                                "ground_truth_path": str(gt_path),
                                "input_path": str(input_path),
                                "shape": "x".join(str(value) for value in data.shape),
                                "affine_hash": affine_hash(affine),
                                "orientation": orientation,
                                "intensity_min": float(np.min(data)),
                                "intensity_max": float(np.max(data)),
                                "generated_slice_indices": ";".join(str(value) for value in generated),
                                "anchor_start": 0,
                                "is_out_of_fold": expected_oof if fold else "not_applicable",
                                "is_complete": complete,
                                "common_case_set": common_id,
                            }
                        )
            summary_rows.append(
                {
                    "dataset": dataset,
                    "scale": scale,
                    "cases": len(cases),
                    "common_case_set": common_id,
                    "models": ";".join(tuple(sources) + ANALYTICAL),
                    "shape_mismatches": shape_mismatches,
                    "affine_mismatches": affine_mismatches,
                    "orientation_mismatches": orientation_mismatches,
                    "nonfinite_predictions": nonfinite,
                    "oof_failures": oof_failures,
                    "issues": sum(1 for row in issue_rows if row.get("dataset") == dataset and int(row.get("scale", -1)) == int(scale)),
                }
            )

    for dataset in config.get("datasets", DATASETS):
        sets = [set(profile_case_sets[(str(dataset), int(scale))]) for scale in config.get("scales", SCALES)]
        if any(case_set != sets[0] for case_set in sets[1:]):
            issue_rows.append(
                {
                    "dataset": dataset,
                    "scale": "all",
                    "fold": "",
                    "model": "all",
                    "issue": "cross_scale_case_set_mismatch",
                    "missing": "",
                    "extra": "",
                }
            )

    write_csv(output / "common_case_manifest.csv", manifest_rows)
    write_csv(output / "cross_scale_audit_summary.csv", summary_rows)
    write_csv(output / "cross_scale_audit_issues.csv", issue_rows)
    report = [
        "# Cross-scale prediction audit",
        "",
        "The primary model intersection was frozen before reliability outcomes were inspected: "
        "I3Net, HAT, SwinIR, linear, and cubic. ArSSR, CycleINR, Pix2PixGAN, and SMamba-UNet "
        "were admitted only to a separately labelled expanded-committee sensitivity analysis because "
        "case-level predictions exist at every audited dataset-scale profile.",
        "",
        "| Dataset | Scale | Cases | Models audited | Shape | Affine | Orientation | Non-finite | OOF failures |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        report.append(
            f"| {row['dataset']} | x{row['scale']} | {row['cases']} | {len(str(row['models']).split(';'))} | "
            f"{row['shape_mismatches']} | {row['affine_mismatches']} | {row['orientation_mismatches']} | "
            f"{row['nonfinite_predictions']} | {row['oof_failures']} |"
        )
    report.extend(
        [
            "",
            "## Sampling support",
            "",
            "Run manifests specify stride 2, 4, or 6 and reconstructed grids beginning at the first "
            "observed anchor (index 0). The audited generated support is therefore "
            "`(z - anchor_start) mod scale != 0`, with `anchor_start=0` for all six profiles. "
            "Only these generated slices enter scoring and retrospective error evaluation.",
            "",
            "## OOF verification",
            "",
            "For NingXia, each prediction filename's examination prefix was checked against the single "
            "held-out test group in `processed_saint_cv/fold_XX/splits/nifti_seed3407/test_cases.txt`. "
            "The eight held-out groups are mutually exclusive at examination-group level.",
            "",
            f"Integrity issues recorded: **{len(issue_rows)}**. See `cross_scale_audit_issues.csv`.",
        ]
    )
    (output / "cross_scale_audit.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    if issue_rows:
        raise RuntimeError(f"cross-scale audit failed with {len(issue_rows)} issue(s)")
    return manifest_rows, summary_rows


def _profile_records(dataset: str, scale: int, include_expanded: bool) -> list[dict[str, Any]]:
    sources = sources_for(REPO_ROOT, dataset, scale, expanded=include_expanded)
    reference = sources[PRIMARY_NEURAL[0]]
    records: list[dict[str, Any]] = []
    for fold in folds_for(dataset):
        for case_id in case_ids(reference, fold):
            started = time.perf_counter()
            gt, _, _ = load_volume(ground_truth_path(reference, fold, case_id))
            outputs = {
                name: load_volume(prediction_path(source, fold, case_id))[0]
                for name, source in sources.items()
            }
            outputs.update(
                {
                    name: load_volume(analytical_path(reference, fold, name, case_id))[0]
                    for name in ANALYTICAL
                }
            )
            shapes = {name: value.shape for name, value in outputs.items()}
            if any(shape != gt.shape for shape in shapes.values()):
                raise ValueError(f"shape mismatch in {dataset} x{scale} {case_id}: gt={gt.shape}, outputs={shapes}")
            indices = generated_indices(gt.shape[2], scale, anchor_start=0)
            idx = list(indices)
            eval_outputs = {name: volume[:, :, idx] for name, volume in outputs.items()}
            gt_eval = gt[:, :, idx]
            primary_all = {name: eval_outputs[name] for name in PRIMARY_NEURAL + ANALYTICAL}
            common_image = np.median(np.stack(list(primary_all.values()), axis=0), axis=0)
            common_mask = threshold_mask(common_image, 0.01)
            all_spread = np.std(np.stack(list(primary_all.values()), axis=0), axis=0).astype(np.float32)
            all_spread_score = float(np.mean(all_spread[common_mask]))

            for target in PRIMARY_NEURAL:
                target_eval = eval_outputs[target]
                full_committee = {name: primary_all[name] for name in PRIMARY_NEURAL + ANALYTICAL if name != target}
                target_mask_full = deployment_mask(
                    outputs[target],
                    {name: outputs[name] for name in PRIMARY_NEURAL + ANALYTICAL if name != target},
                    "target_0.01",
                    scale,
                )
                target_mask = target_mask_full[:, :, idx]
                error = np.abs(target_eval - gt_eval)
                case_error = float(np.mean(error[target_mask]))

                maps: dict[str, np.ndarray] = {
                    "target_median": score_map(target, target_eval, full_committee, "target_abs_median"),
                    "target_mean": score_map(target, target_eval, full_committee, "target_abs_mean"),
                    "all_output_spread": all_spread,
                    "target_excluded_spread": np.std(
                        np.stack(list(full_committee.values()), axis=0), axis=0
                    ).astype(np.float32),
                    "neural_only": score_map(
                        target,
                        target_eval,
                        {name: eval_outputs[name] for name in PRIMARY_NEURAL if name != target},
                        "target_abs_median",
                    ),
                    "analytical_only": score_map(
                        target,
                        target_eval,
                        {name: eval_outputs[name] for name in ANALYTICAL},
                        "target_abs_median",
                    ),
                }
                if include_expanded:
                    maps["expanded_median"] = score_map(
                        target,
                        target_eval,
                        {name: eval_outputs[name] for name in EXPANDED_NEURAL + ANALYTICAL if name != target},
                        "target_abs_median",
                    )

                for method, score in maps.items():
                    aggregation_mask = common_mask if method == "all_output_spread" else target_mask
                    records.append(
                        {
                            "dataset": dataset,
                            "scale": scale,
                            "fold": fold or "",
                            "case_id": case_id,
                            "target": target,
                            "method": method,
                            "committee": (
                                ";".join(PRIMARY_NEURAL + ANALYTICAL)
                                if method == "all_output_spread"
                                else ";".join(name for name in PRIMARY_NEURAL + ANALYTICAL if name != target)
                            ),
                            "case_error": case_error,
                            "case_score": all_spread_score if method == "all_output_spread" else float(np.mean(score[aggregation_mask])),
                            "pixel_corr_foreground": safe_pearson(score[target_mask], error[target_mask]),
                            "generated_slices": len(indices),
                            "foreground_fraction": float(np.mean(target_mask)),
                            "score_mask": "committee_median_0.01" if method == "all_output_spread" else "target_0.01",
                            "runtime_seconds": time.perf_counter() - started,
                            "primary_or_sensitivity": "primary" if method == PRIMARY_METHOD else "sensitivity",
                        }
                    )
            del outputs, eval_outputs, gt, gt_eval
    return records


def summarize(per_case: list[dict[str, Any]], samples: int, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[str, int, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in per_case:
        grouped[(str(row["dataset"]), int(row["scale"]), str(row["target"]), str(row["method"]))].append(row)
    summaries: list[dict[str, Any]] = []
    bootstraps: list[dict[str, Any]] = []
    for (dataset, scale, target, method), rows in sorted(grouped.items()):
        rows = sorted(rows, key=lambda item: str(item["case_id"]))
        errors = np.asarray([float(row["case_error"]) for row in rows])
        scores = np.asarray([float(row["case_score"]) for row in rows])
        pixels = np.asarray([float(row["pixel_corr_foreground"]) for row in rows])
        intervals, samples_rows = paired_case_bootstrap(errors, scores, pixels, samples=samples, seed=seed)
        summary: dict[str, Any] = {
            "dataset": dataset,
            "scale": scale,
            "target": target,
            "method": method,
            "cases": len(rows),
            "mean_mae": float(np.mean(errors)),
            "score_runtime_seconds_mean": float(np.mean([float(row["runtime_seconds"]) for row in rows])),
        }
        for metric, (point, low, high) in intervals.items():
            summary[metric] = point
            summary[f"{metric}_ci_low"] = low
            summary[f"{metric}_ci_high"] = high
        summaries.append(summary)
        for sample_row in samples_rows:
            bootstraps.append(
                {
                    "dataset": dataset,
                    "scale": scale,
                    "target": target,
                    "method": method,
                    **sample_row,
                }
            )
    return summaries, bootstraps


def _metric_difference(
    rows_a: list[dict[str, Any]],
    rows_b: list[dict[str, Any]],
    samples: int,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    a = {str(row["case_id"]): row for row in rows_a}
    b = {str(row["case_id"]): row for row in rows_b}
    if set(a) != set(b):
        raise ValueError("paired comparison requires identical case identities")
    ids = sorted(a)
    errors_a = np.asarray([float(a[case]["case_error"]) for case in ids])
    errors_b = np.asarray([float(b[case]["case_error"]) for case in ids])
    if not np.allclose(errors_a, errors_b, rtol=0.0, atol=1e-7):
        raise ValueError("within-profile comparators must share target errors")
    scores_a = np.asarray([float(a[case]["case_score"]) for case in ids])
    scores_b = np.asarray([float(b[case]["case_score"]) for case in ids])
    point = ranking_metrics(errors_a, scores_a)["normalized_aurc"] - ranking_metrics(errors_a, scores_b)["normalized_aurc"]
    rng = np.random.default_rng(seed)
    differences: list[float] = []
    rows: list[dict[str, Any]] = []
    for replicate in range(samples):
        indices = rng.integers(0, len(ids), size=len(ids))
        value = (
            ranking_metrics(errors_a[indices], scores_a[indices])["normalized_aurc"]
            - ranking_metrics(errors_a[indices], scores_b[indices])["normalized_aurc"]
        )
        differences.append(value)
        rows.append({"replicate": replicate, "delta_naurc": value})
    array = np.asarray(differences)
    low, high = np.percentile(array, [2.5, 97.5])
    outcome = "win" if high < 0 else "loss" if low > 0 else "tie"
    return {
        "delta_naurc": float(point),
        "delta_naurc_ci_low": float(low),
        "delta_naurc_ci_high": float(high),
        "outcome": outcome,
        "cases": len(ids),
    }, rows


def paired_comparisons(per_case: list[dict[str, Any]], samples: int, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    lookup: dict[tuple[str, int, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in per_case:
        lookup[(str(row["dataset"]), int(row["scale"]), str(row["target"]), str(row["method"]))].append(row)
    results: list[dict[str, Any]] = []
    bootstrap_rows: list[dict[str, Any]] = []
    profiles = sorted({(str(row["dataset"]), int(row["scale"])) for row in per_case})
    for dataset, scale in profiles:
        for target in PRIMARY_NEURAL:
                primary = lookup[(dataset, scale, target, PRIMARY_METHOD)]
                for comparator in COMPARATORS:
                    result, boot = _metric_difference(
                        primary,
                        lookup[(dataset, scale, target, comparator)],
                        samples,
                        seed,
                    )
                    comparison = f"{PRIMARY_METHOD}_vs_{comparator}"
                    results.append(
                        {
                            "dataset": dataset,
                            "scale": scale,
                            "target": target,
                            "method_a": PRIMARY_METHOD,
                            "method_b": comparator,
                            "comparison": comparison,
                            **result,
                        }
                    )
                    bootstrap_rows.extend(
                        {
                            "dataset": dataset,
                            "scale": scale,
                            "target": target,
                            "comparison": comparison,
                            **row,
                        }
                        for row in boot
                    )

    for comparison in sorted({str(row["comparison"]) for row in results}):
        fixed = [row for row in results if row["comparison"] == comparison]
        fixed_boot = [row for row in bootstrap_rows if row["comparison"] == comparison]
        by_rep: dict[int, list[float]] = defaultdict(list)
        for row in fixed_boot:
            by_rep[int(row["replicate"])].append(float(row["delta_naurc"]))
        values = np.asarray([np.mean(by_rep[index]) for index in sorted(by_rep)])
        low, high = np.percentile(values, [2.5, 97.5])
        point = float(np.mean([float(row["delta_naurc"]) for row in fixed]))
        results.append(
            {
                "dataset": "aggregate_equal_profile_weight",
                "scale": "all",
                "target": "all",
                "method_a": PRIMARY_METHOD,
                "method_b": comparison.split("_vs_", 1)[1],
                "comparison": comparison,
                "delta_naurc": point,
                "delta_naurc_ci_low": float(low),
                "delta_naurc_ci_high": float(high),
                "outcome": "win" if high < 0 else "loss" if low > 0 else "tie",
                "cases": sum(int(row["cases"]) for row in fixed),
                "profiles": len(fixed),
            }
        )
    return results, bootstrap_rows


def _spearman(first: np.ndarray, second: np.ndarray) -> float:
    if np.std(first) <= 1e-12 or np.std(second) <= 1e-12:
        return 0.0
    return float(stats.spearmanr(first, second).statistic)


def matched_target(per_case: list[dict[str, Any]], samples: int, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    primary = [row for row in per_case if row["method"] == PRIMARY_METHOD]
    shared = [row for row in per_case if row["method"] == "all_output_spread"]
    matrices: list[dict[str, Any]] = []
    bootstrap_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    profiles = sorted({(str(row["dataset"]), int(row["scale"])) for row in primary})
    for dataset, scale in profiles:
            profile_primary = [row for row in primary if row["dataset"] == dataset and int(row["scale"]) == scale]
            profile_shared = [row for row in shared if row["dataset"] == dataset and int(row["scale"]) == scale]
            ids = sorted({str(row["case_id"]) for row in profile_primary})
            score_by_target = {
                target: np.asarray([
                    float(next(row["case_score"] for row in profile_primary if row["target"] == target and row["case_id"] == case_id))
                    for case_id in ids
                ])
                for target in PRIMARY_NEURAL
            }
            error_by_target = {
                target: np.asarray([
                    float(next(row["case_error"] for row in profile_primary if row["target"] == target and row["case_id"] == case_id))
                    for case_id in ids
                ])
                for target in PRIMARY_NEURAL
            }
            shared_score = np.asarray([
                float(next(row["case_score"] for row in profile_shared if row["target"] == PRIMARY_NEURAL[0] and row["case_id"] == case_id))
                for case_id in ids
            ])

            def matrix_for(method: str, indices: np.ndarray | None = None) -> np.ndarray:
                use = np.arange(len(ids)) if indices is None else indices
                score_vectors = score_by_target if method == PRIMARY_METHOD else {target: shared_score for target in PRIMARY_NEURAL}
                return np.asarray(
                    [
                        [_spearman(score_vectors[scored][use], error_by_target[error][use]) for error in PRIMARY_NEURAL]
                        for scored in PRIMARY_NEURAL
                    ]
                )

            for method in (PRIMARY_METHOD, "all_output_spread"):
                matrix = matrix_for(method)
                for row_index, scored in enumerate(PRIMARY_NEURAL):
                    for column_index, error_target in enumerate(PRIMARY_NEURAL):
                        matrices.append(
                            {
                                "dataset": dataset,
                                "scale": scale,
                                "method": method,
                                "scored_target": scored,
                                "error_target": error_target,
                                "matched": scored == error_target,
                                "spearman": float(matrix[row_index, column_index]),
                            }
                        )
                diagonal = float(np.mean(np.diag(matrix)))
                off = float(np.mean(matrix[~np.eye(len(PRIMARY_NEURAL), dtype=bool)]))
                point = diagonal - off
                rng = np.random.default_rng(seed)
                advantages = []
                for replicate in range(samples):
                    indices = rng.integers(0, len(ids), size=len(ids))
                    boot_matrix = matrix_for(method, indices)
                    value = float(
                        np.mean(np.diag(boot_matrix))
                        - np.mean(boot_matrix[~np.eye(len(PRIMARY_NEURAL), dtype=bool)])
                    )
                    advantages.append(value)
                    bootstrap_rows.append(
                        {
                            "dataset": dataset,
                            "scale": scale,
                            "method": method,
                            "replicate": replicate,
                            "matched_advantage": value,
                        }
                    )
                low, high = np.percentile(np.asarray(advantages), [2.5, 97.5])
                row_wins = sum(
                    matrix[index, index] > np.mean(np.delete(matrix[index], index))
                    for index in range(len(PRIMARY_NEURAL))
                )
                summaries.append(
                    {
                        "dataset": dataset,
                        "scale": scale,
                        "method": method,
                        "cases": len(ids),
                        "matched_mean": diagonal,
                        "mismatched_mean": off,
                        "matched_advantage": point,
                        "matched_advantage_ci_low": float(low),
                        "matched_advantage_ci_high": float(high),
                        "diagonal_row_wins": row_wins,
                    }
                )

            raw_scores = np.stack([score_by_target[target] for target in PRIMARY_NEURAL], axis=1)
            raw_errors = np.stack([error_by_target[target] for target in PRIMARY_NEURAL], axis=1)
            top1 = float(np.mean(np.argmax(raw_scores, axis=1) == np.argmax(raw_errors, axis=1)))
            within = [_spearman(raw_scores[index], raw_errors[index]) for index in range(len(ids))]
            summaries.append(
                {
                    "dataset": dataset,
                    "scale": scale,
                    "method": "within_case_identity",
                    "cases": len(ids),
                    "top1_highest_error_model_accuracy": top1,
                    "within_case_model_spearman_mean": float(np.mean(within)),
                    "within_case_model_spearman_median": float(np.median(within)),
                }
            )
    return matrices, bootstrap_rows, summaries


def cross_scale_paired(per_case: list[dict[str, Any]], samples: int, seed: int) -> list[dict[str, Any]]:
    primary = [row for row in per_case if row["method"] == PRIMARY_METHOD]
    results: list[dict[str, Any]] = []
    datasets = sorted({str(row["dataset"]) for row in primary})
    for dataset in datasets:
        for target in PRIMARY_NEURAL:
            scale_lookup = {
                scale: {str(row["case_id"]): row for row in primary if row["dataset"] == dataset and int(row["scale"]) == scale and row["target"] == target}
                for scale in SCALES
            }
            for low_scale, high_scale in ((2, 4), (4, 6)):
                if not scale_lookup[low_scale] or not scale_lookup[high_scale]:
                    continue
                if set(scale_lookup[low_scale]) != set(scale_lookup[high_scale]):
                    results.append(
                        {
                            "dataset": dataset,
                            "target": target,
                            "comparison": f"x{high_scale}-x{low_scale}",
                            "paired": False,
                            "reason": "case-set mismatch",
                        }
                    )
                    continue
                ids = sorted(scale_lookup[low_scale])
                low_error = np.asarray([float(scale_lookup[low_scale][case]["case_error"]) for case in ids])
                high_error = np.asarray([float(scale_lookup[high_scale][case]["case_error"]) for case in ids])
                low_score = np.asarray([float(scale_lookup[low_scale][case]["case_score"]) for case in ids])
                high_score = np.asarray([float(scale_lookup[high_scale][case]["case_score"]) for case in ids])
                low_metrics = ranking_metrics(low_error, low_score)
                high_metrics = ranking_metrics(high_error, high_score)
                rng = np.random.default_rng(seed)
                delta_rho: list[float] = []
                delta_naurc: list[float] = []
                for _ in range(samples):
                    indices = rng.integers(0, len(ids), size=len(ids))
                    low_boot = ranking_metrics(low_error[indices], low_score[indices])
                    high_boot = ranking_metrics(high_error[indices], high_score[indices])
                    delta_rho.append(high_boot["case_spearman"] - low_boot["case_spearman"])
                    delta_naurc.append(high_boot["normalized_aurc"] - low_boot["normalized_aurc"])
                rho_low, rho_high = np.percentile(delta_rho, [2.5, 97.5])
                n_low, n_high = np.percentile(delta_naurc, [2.5, 97.5])
                results.append(
                    {
                        "dataset": dataset,
                        "target": target,
                        "comparison": f"x{high_scale}-x{low_scale}",
                        "paired": True,
                        "cases": len(ids),
                        "delta_spearman": high_metrics["case_spearman"] - low_metrics["case_spearman"],
                        "delta_spearman_ci_low": float(rho_low),
                        "delta_spearman_ci_high": float(rho_high),
                        "delta_naurc": high_metrics["normalized_aurc"] - low_metrics["normalized_aurc"],
                        "delta_naurc_ci_low": float(n_low),
                        "delta_naurc_ci_high": float(n_high),
                    }
                )
    return results


def aggregate_scales(summary: list[dict[str, Any]], bootstrap: list[dict[str, Any]]) -> list[dict[str, Any]]:
    primary = [row for row in summary if row["method"] == PRIMARY_METHOD]
    boot = [row for row in bootstrap if row["method"] == PRIMARY_METHOD]
    output: list[dict[str, Any]] = []
    profiles = sorted({(str(row["dataset"]), int(row["scale"])) for row in primary})
    for dataset, scale in profiles:
            rows = [row for row in primary if row["dataset"] == dataset and int(row["scale"]) == scale]
            boot_rows = [row for row in boot if row["dataset"] == dataset and int(row["scale"]) == scale]
            by_rep: dict[int, list[dict[str, Any]]] = defaultdict(list)
            for row in boot_rows:
                by_rep[int(row["replicate"])].append(row)
            result: dict[str, Any] = {
                "dataset": dataset,
                "scale": scale,
                "cases": int(rows[0]["cases"]),
                "targets": len(rows),
                "mean_mae": float(np.mean([float(row["mean_mae"]) for row in rows])),
            }
            for metric in ("case_spearman", "normalized_aurc", "rrr_50", "retained_mae_50"):
                values = np.asarray([
                    np.mean([float(row[metric]) for row in by_rep[index]])
                    for index in sorted(by_rep)
                ])
                result[metric] = float(np.mean([float(row[metric]) for row in rows]))
                result[f"{metric}_ci_low"] = float(np.percentile(values, 2.5))
                result[f"{metric}_ci_high"] = float(np.percentile(values, 97.5))
            output.append(result)
    return output


def update_registry(output: Path, summaries: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    run_date = datetime.now().isoformat(timespec="seconds")
    for row in summaries:
        for metric in ("case_spearman", "normalized_aurc", "rrr_50", "pixel_fisher_z_mean"):
            rows.append(
                {
                    "experiment_id": f"multiscale_{row['dataset']}_x{row['scale']}_{row['target']}_{row['method']}_{metric}",
                    "dataset": row["dataset"],
                    "scale": row["scale"],
                    "target_model": row["target"],
                    "committee": "frozen_primary_intersection",
                    "score": row["method"],
                    "mask": "target_0.01" if row["method"] != "all_output_spread" else "committee_median_0.01",
                    "normalization": "raw_common_source_representation",
                    "metric": metric,
                    "seed": DEFAULT_SEED,
                    "number_of_cases": row["cases"],
                    "development_or_test": "test_oof" if row["dataset"] == "ningxia" else "test",
                    "run_date": run_date,
                    "code_commit": "workspace_uncommitted",
                    "output_file": str(output / "all_method_summary.csv"),
                    "common_case_set": "yes",
                    "matched_or_mismatched_target": "matched",
                    "comparator": "",
                    "paired_bootstrap_id": f"seed{DEFAULT_SEED}",
                    "primary_or_sensitivity": "primary" if row["method"] == PRIMARY_METHOD else "sensitivity",
                }
            )
    for row in comparisons:
        if row["dataset"] == "aggregate_equal_profile_weight":
            continue
        rows.append(
            {
                "experiment_id": f"multiscale_paired_{row['dataset']}_x{row['scale']}_{row['target']}_{row['comparison']}",
                "dataset": row["dataset"],
                "scale": row["scale"],
                "target_model": row["target"],
                "committee": "frozen_primary_intersection",
                "score": PRIMARY_METHOD,
                "mask": "deployment_compatible",
                "normalization": "raw_common_source_representation",
                "metric": "delta_naurc",
                "seed": DEFAULT_SEED,
                "number_of_cases": row["cases"],
                "development_or_test": "test_oof" if row["dataset"] == "ningxia" else "test",
                "run_date": run_date,
                "code_commit": "workspace_uncommitted",
                "output_file": str(output / "paired_comparisons.csv"),
                "common_case_set": "yes",
                "matched_or_mismatched_target": "matched",
                "comparator": row["method_b"],
                "paired_bootstrap_id": f"seed{DEFAULT_SEED}",
                "primary_or_sensitivity": "predeclared_comparison",
            }
        )
    write_csv(output / "results_registry.csv", rows)


def run(config_path: Path, audit_only: bool = False) -> None:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output = REPO_ROOT / str(config.get("output", "design/rasinet/outputs/multiscale"))
    output.mkdir(parents=True, exist_ok=True)
    samples = int(config.get("bootstrap_samples", 2000))
    seed = int(config.get("seed", DEFAULT_SEED))
    started = time.perf_counter()
    audit(config, output)
    if audit_only:
        print(f"[multiscale] audit complete output={output}", flush=True)
        return
    all_records: list[dict[str, Any]] = []
    for dataset in config.get("datasets", DATASETS):
        for scale in config.get("scales", SCALES):
            print(f"[multiscale] evaluating dataset={dataset} scale=x{scale}", flush=True)
            all_records.extend(_profile_records(str(dataset), int(scale), include_expanded=True))
            write_csv(output / "per_case_scores.partial.csv", all_records)
    write_csv(output / "per_case_scores.csv", all_records)
    summaries, bootstrap = summarize(all_records, samples=samples, seed=seed)
    write_csv(output / "all_method_summary.csv", summaries)
    write_csv(output / "cross_scale_primary_results.csv", [row for row in summaries if row["method"] == PRIMARY_METHOD])
    write_csv(output / "cross_scale_bootstrap.csv", bootstrap)
    aggregate = aggregate_scales(summaries, bootstrap)
    write_csv(output / "cross_scale_aggregate.csv", aggregate)
    comparisons, comparison_bootstrap = paired_comparisons(all_records, samples=samples, seed=seed)
    write_csv(output / "paired_comparisons.csv", comparisons)
    write_csv(output / "paired_comparison_bootstrap.csv", comparison_bootstrap)
    matrices, matched_bootstrap, matched_summary = matched_target(all_records, samples=samples, seed=seed)
    write_csv(output / "matched_target_matrix.csv", matrices)
    write_csv(output / "matched_target_bootstrap.csv", matched_bootstrap)
    write_csv(output / "matched_target_summary.csv", matched_summary)
    write_csv(output / "cross_scale_paired.csv", cross_scale_paired(all_records, samples=samples, seed=seed))
    update_registry(output, summaries, comparisons)
    environment = {
        "run_date": datetime.now().isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "nibabel": nib.__version__,
        "bootstrap_samples": samples,
        "seed": seed,
        "elapsed_seconds": time.perf_counter() - started,
        "primary_models": list(PRIMARY_NEURAL + ANALYTICAL),
        "expanded_models": list(EXPANDED_NEURAL + ANALYTICAL),
        "config": str(config_path),
    }
    (output / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    print(f"[multiscale] complete output={output} elapsed={environment['elapsed_seconds']:.1f}s", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-scale MRI reliability evaluation")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    run(args.config.resolve(), audit_only=args.audit_only)


if __name__ == "__main__":
    main()
