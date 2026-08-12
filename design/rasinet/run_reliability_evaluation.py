from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
import platform
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import nibabel as nib
import numpy as np
import yaml
from scipy import stats

from .committee_experiments import (
    PROFILE_ALIASES,
    ReconstructionSource,
    _baseline_path,
    _case_names,
    _folds,
    _gt_path,
    _prediction_path,
    profile_sources,
)
from .committee_reliability import risk_coverage_summary
from .icassp_scores import (
    ANALYTICAL_MEMBERS,
    deployment_mask,
    generated_indices,
    normalize_output,
    score_map,
)
from .icassp_statistics import paired_case_bootstrap, pixel_correlation_summary, ranking_metrics, safe_pearson


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = 20260715
PRIMARY_SCORE = "target_abs_median"
PRIMARY_MASK = "target_0.01"
PRIMARY_NORMALIZATION = "raw"


@dataclass(frozen=True)
class EvaluationSpec:
    analysis: str
    score: str
    mask: str
    normalization: str
    committee: tuple[str, ...]
    subset_id: str

    @property
    def key(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.analysis,
            self.score,
            self.mask,
            self.normalization,
            ";".join(self.committee),
            self.subset_id,
        )


def _read_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"configuration must be a mapping: {path}")
    return payload


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _append_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_image(path: Path) -> tuple[np.ndarray, np.ndarray, nib.Nifti1Header]:
    if not path.exists():
        raise FileNotFoundError(path)
    image = nib.load(str(path))
    data = image.get_fdata(dtype=np.float32)
    if data.ndim != 3 or not np.isfinite(data).all():
        raise ValueError(f"invalid NIfTI volume: path={path}, shape={data.shape}")
    return data, image.affine.copy(), image.header.copy()


def _geometry_signature(affine: np.ndarray, header: nib.Nifti1Header) -> dict[str, Any]:
    return {
        "orientation": "".join(nib.aff2axcodes(affine)),
        "zooms": tuple(float(value) for value in header.get_zooms()[:3]),
        "qform_code": int(header["qform_code"]),
        "sform_code": int(header["sform_code"]),
    }


def _assert_geometry(
    reference_name: str,
    reference_shape: tuple[int, ...],
    reference_affine: np.ndarray,
    candidate_name: str,
    candidate_shape: tuple[int, ...],
    candidate_affine: np.ndarray,
    tolerance: float,
) -> None:
    if candidate_shape != reference_shape:
        raise ValueError(
            f"shape mismatch: {reference_name}={reference_shape}, {candidate_name}={candidate_shape}"
        )
    if not np.allclose(candidate_affine, reference_affine, rtol=0.0, atol=tolerance):
        maximum = float(np.max(np.abs(candidate_affine - reference_affine)))
        raise ValueError(
            f"affine mismatch: reference={reference_name}, candidate={candidate_name}, max_abs={maximum:.6g}"
        )
    if nib.aff2axcodes(candidate_affine) != nib.aff2axcodes(reference_affine):
        raise ValueError(f"orientation mismatch: {reference_name} vs {candidate_name}")


def _file_set(directory: Path, prefix: str) -> set[str]:
    if not directory.exists():
        raise FileNotFoundError(directory)
    names = [path.name[len(prefix) :] for path in directory.glob(f"{prefix}*.nii.gz")]
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate case identities in {directory}")
    return set(names)


def _validate_case_sets(
    sources: tuple[ReconstructionSource, ...],
    fold: str | None,
    profile: str,
) -> list[str]:
    reference = sources[0]
    expected = set(_case_names(reference, fold))
    if not expected:
        raise ValueError(f"empty reference case set: profile={profile}, fold={fold}")
    for source in sources:
        actual = _file_set(source.run_dir(fold) / "model_outputs", "diff_")
        if actual != expected:
            raise ValueError(
                f"case-set mismatch for {source.name}: missing={sorted(expected - actual)}, "
                f"extra={sorted(actual - expected)}"
            )
    gt_dir = "eval_inputs" if profile == "full_test115" else "eval_gt"
    gt_root = reference.run_dir(fold) / gt_dir
    if gt_dir == "eval_inputs":
        gt_root = gt_root / "gt"
    gt_cases = _file_set(gt_root, "")
    if gt_cases != expected:
        raise ValueError(f"ground-truth case-set mismatch: missing={sorted(expected - gt_cases)}, extra={sorted(gt_cases - expected)}")
    for baseline in ("linear", "cubic"):
        actual = _file_set(reference.run_dir(fold) / "baseline_outputs" / baseline, f"{baseline}_")
        if actual != expected:
            raise ValueError(
                f"{baseline} case-set mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
            )
    return sorted(expected)


def _composition(names: tuple[str, ...]) -> str:
    neural = sum(name not in ANALYTICAL_MEMBERS for name in names)
    analytical = len(names) - neural
    if neural and analytical:
        return f"mixed_{neural}n_{analytical}a"
    if neural:
        return f"neural_{neural}"
    return f"analytical_{analytical}"


def _median_maps(maps: list[np.ndarray]) -> np.ndarray:
    """Exact median specialized for the small committees in this study."""
    if not maps:
        raise ValueError("cannot compute a median over an empty committee")
    if len(maps) == 1:
        return maps[0]
    if len(maps) == 2:
        return ((maps[0] + maps[1]) * 0.5).astype(np.float32)
    minimum = np.minimum.reduce(maps)
    maximum = np.maximum.reduce(maps)
    total = np.add.reduce(maps)
    if len(maps) == 3:
        return (total - minimum - maximum).astype(np.float32)
    if len(maps) == 4:
        return ((total - minimum - maximum) * 0.5).astype(np.float32)
    return np.median(np.stack(maps, axis=0), axis=0).astype(np.float32)


def _specs(target: str, available: tuple[str, ...], config: dict[str, Any]) -> list[EvaluationSpec]:
    committee = tuple(name for name in available if name != target)
    if target in committee:
        raise AssertionError("target leaked into committee")
    analyses = config.get("analyses", {})
    specs: list[EvaluationSpec] = []
    for score in analyses.get("score_variants", []):
        specs.append(EvaluationSpec("score_variants", score, PRIMARY_MASK, PRIMARY_NORMALIZATION, committee, "full"))
    for normalization in analyses.get("normalizations", []):
        specs.append(EvaluationSpec("normalization", PRIMARY_SCORE, PRIMARY_MASK, normalization, committee, "full"))
    for mask in analyses.get("masks", []):
        specs.append(EvaluationSpec("mask", PRIMARY_SCORE, mask, PRIMARY_NORMALIZATION, committee, "full"))
    if analyses.get("committee_subsets", False):
        for size in range(1, len(committee) + 1):
            for subset in itertools.combinations(committee, size):
                subset_id = f"k{size}_{'_'.join(subset)}"
                specs.append(EvaluationSpec("committee_subset", PRIMARY_SCORE, PRIMARY_MASK, PRIMARY_NORMALIZATION, subset, subset_id))
    for score in analyses.get("structural_scores", []):
        specs.append(EvaluationSpec("structural", score, PRIMARY_MASK, PRIMARY_NORMALIZATION, committee, "full"))
    unique: dict[tuple[str, str, str, str, str, str], EvaluationSpec] = {}
    for spec in specs:
        unique[spec.key] = spec
    return list(unique.values())


def _primary_spec(spec: EvaluationSpec, full_committee: tuple[str, ...]) -> bool:
    return (
        spec.score == PRIMARY_SCORE
        and spec.mask == PRIMARY_MASK
        and spec.normalization == PRIMARY_NORMALIZATION
        and spec.committee == full_committee
        and spec.analysis == "score_variants"
    )


def _save_map(
    path: Path,
    score: np.ndarray,
    affine: np.ndarray,
    header: nib.Nifti1Header,
) -> None:
    if not str(path).endswith(".nii.gz"):
        path = Path(f"{path}.nii.gz")
    path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(nib.Nifti1Image(score.astype(np.float32), affine, header), str(path))


def _evaluate_case(
    profile: str,
    fold: str | None,
    case_name: str,
    sources: tuple[ReconstructionSource, ...],
    factor: int,
    affine_tolerance: float,
    config: dict[str, Any],
    output_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    reference = sources[0]
    paths: dict[str, Path] = {
        "linear": _baseline_path(reference, fold, "linear", case_name),
        "cubic": _baseline_path(reference, fold, "cubic", case_name),
    }
    paths.update({source.name: _prediction_path(source, fold, case_name) for source in sources})
    outputs: dict[str, np.ndarray] = {}
    affines: dict[str, np.ndarray] = {}
    headers: dict[str, nib.Nifti1Header] = {}
    for name, path in paths.items():
        outputs[name], affines[name], headers[name] = _load_image(path)
    reference_name = sources[0].name
    reference_shape = outputs[reference_name].shape
    for name in outputs:
        _assert_geometry(
            reference_name,
            reference_shape,
            affines[reference_name],
            name,
            outputs[name].shape,
            affines[name],
            affine_tolerance,
        )

    indices = generated_indices(reference_shape[2], factor)
    eval_index_list = list(indices)
    eval_outputs = {name: volume[:, :, eval_index_list] for name, volume in outputs.items()}
    normalized_cache: dict[str, dict[str, np.ndarray]] = {}
    deployment_rows: list[dict[str, Any]] = []
    timing_rows: list[dict[str, Any]] = []

    # Offline reference data are held by the evaluator and are never passed to
    # score_map(), deployment_mask(), or examination_score().
    gt_path = _gt_path(reference, fold, case_name, profile)
    gt, gt_affine, gt_header = _load_image(gt_path)
    _assert_geometry(
        reference_name,
        reference_shape,
        affines[reference_name],
        "ground_truth",
        gt.shape,
        gt_affine,
        affine_tolerance,
    )
    error_cache = {
        source.name: np.abs(outputs[source.name][:, :, list(indices)] - gt[:, :, list(indices)])
        for source in sources
    }
    for target in (source.name for source in sources):
        full_committee = tuple(name for name in outputs if name != target)
        target_specs = _specs(target, tuple(outputs), config)
        score_use_count: dict[tuple[str, str, tuple[str, ...]], int] = defaultdict(int)
        mask_use_count: dict[tuple[str, tuple[str, ...]], int] = defaultdict(int)
        for spec in target_specs:
            score_use_count[(spec.score, spec.normalization, spec.committee)] += 1
            mask_use_count[(spec.mask, spec.committee)] += 1
        score_cache: dict[tuple[str, str, tuple[str, ...]], np.ndarray] = {}
        mask_cache: dict[tuple[str, tuple[str, ...]], np.ndarray] = {}
        difference_cache: dict[str, dict[str, np.ndarray]] = {}
        pair_mean_cache: dict[tuple[str, str, str], float] = {}
        for spec in target_specs:
            started = time.perf_counter()
            if spec.normalization not in normalized_cache:
                if spec.normalization == "raw":
                    normalized_cache[spec.normalization] = eval_outputs
                else:
                    normalized_cache[spec.normalization] = {
                        name: normalize_output(volume, spec.normalization)[:, :, eval_index_list]
                        for name, volume in outputs.items()
                    }
            normalized = normalized_cache[spec.normalization]
            committee = {name: normalized[name] for name in spec.committee}
            score_key = (spec.score, spec.normalization, spec.committee)
            score = score_cache.get(score_key)
            if score is None:
                if spec.score == PRIMARY_SCORE:
                    if spec.normalization not in difference_cache:
                        difference_cache[spec.normalization] = {
                            name: np.abs(normalized[target] - normalized[name])
                            for name in normalized
                            if name != target
                        }
                    score = _median_maps(
                        [difference_cache[spec.normalization][name] for name in spec.committee]
                    )
                elif spec.score in {"gradient_target_abs_median", "laplacian_target_abs_median"}:
                    full_normalized = {
                        name: normalize_output(outputs[name], spec.normalization)
                        for name in (target,) + spec.committee
                    }
                    full_score = score_map(
                        target,
                        full_normalized[target],
                        {name: full_normalized[name] for name in spec.committee},
                        spec.score,
                        all_outputs=full_normalized,
                    )
                    score = full_score[:, :, eval_index_list]
                else:
                    score = score_map(target, normalized[target], committee, spec.score, all_outputs=normalized)
                if score_use_count[score_key] > 1:
                    score_cache[score_key] = score
            raw_committee = {name: outputs[name] for name in spec.committee}
            mask_key = (spec.mask, spec.committee)
            mask = mask_cache.get(mask_key)
            if mask is None:
                if spec.mask == "ground_truth_offline":
                    gt_eval = np.abs(gt[:, :, eval_index_list])
                    threshold = max(1e-6, 0.01 * float(np.max(gt_eval)))
                    mask = gt_eval > threshold
                    if not np.any(mask):
                        mask = np.ones_like(gt_eval, dtype=bool)
                else:
                    mask = deployment_mask(outputs[target], raw_committee, spec.mask, factor)[:, :, eval_index_list]
                if mask_use_count[mask_key] > 1:
                    mask_cache[mask_key] = mask
            if not np.any(mask):
                raise ValueError(f"empty evaluation mask: target={target}, mode={spec.mask}")
            case_score = float(np.mean(score[mask]))
            pair_values: list[float] = []
            for first_index, first_name in enumerate(spec.committee):
                for second_name in spec.committee[first_index + 1 :]:
                    pair_name = tuple(sorted((first_name, second_name)))
                    pair_key = (spec.mask, pair_name[0], pair_name[1])
                    if pair_key not in pair_mean_cache:
                        pair_mean_cache[pair_key] = float(
                            np.mean(np.abs(eval_outputs[pair_name[0]][mask] - eval_outputs[pair_name[1]][mask]))
                        )
                    pair_values.append(pair_mean_cache[pair_key])
            committee_diversity = float(np.mean(pair_values)) if pair_values else 0.0
            elapsed = time.perf_counter() - started
            row = {
                "profile": profile,
                "dataset": PROFILE_ALIASES[profile],
                "fold": fold or "",
                "case": f"{fold}/{case_name}" if fold else case_name,
                "target": target,
                "analysis": spec.analysis,
                "score": spec.score,
                "mask": spec.mask,
                "normalization": spec.normalization,
                "committee": ";".join(spec.committee),
                "committee_size": len(spec.committee),
                "composition": _composition(spec.committee),
                "subset_id": spec.subset_id,
                "generated_slices": len(indices),
                "foreground_fraction": float(np.mean(mask)),
                "case_score": case_score,
                "committee_diversity": committee_diversity,
                "scoring_seconds": elapsed,
            }
            mask_eval = mask
            score_eval = score
            error = error_cache[target]
            row["foreground_mae"] = float(np.mean(error[mask_eval]))
            row["pixel_corr_foreground"] = safe_pearson(error[mask_eval], score_eval[mask_eval])
            row["pixel_corr_all"] = safe_pearson(error, score_eval)
            deployment_rows.append(row)
            timing_rows.append(
                {
                    "profile": profile,
                    "case": row["case"],
                    "target": target,
                    "analysis": spec.analysis,
                    "score": spec.score,
                    "normalization": spec.normalization,
                    "mask": spec.mask,
                    "committee_size": len(spec.committee),
                    "seconds": elapsed,
                }
            )
            if config.get("save_primary_voxel_maps", False) and _primary_spec(spec, full_committee):
                map_path = output_root / "voxel_maps" / profile / target / f"score_{case_name}"
                full_map = np.zeros(reference_shape, dtype=np.float32)
                full_map[:, :, eval_index_list] = score
                _save_map(map_path, full_map, affines[target], headers[target])

    geometry = _geometry_signature(affines[reference_name], headers[reference_name])
    manifest = {
        "profile": profile,
        "fold": fold or "",
        "case": f"{fold}/{case_name}" if fold else case_name,
        "shape": str(reference_shape),
        "affine_aligned": 1,
        **geometry,
        "generated_slices": len(indices),
        "source_files": len(paths) + 1,
        "source_bytes": sum(path.stat().st_size for path in paths.values()) + gt_path.stat().st_size,
        "deployment_source_files": len(paths),
        "deployment_source_bytes": sum(path.stat().st_size for path in paths.values()),
        "offline_ground_truth_bytes": gt_path.stat().st_size,
        "intensity_ranges": json.dumps(
            {
                name: {
                    "min": float(np.min(volume)),
                    "p1": float(np.percentile(volume, 1.0)),
                    "median": float(np.median(volume)),
                    "p99": float(np.percentile(volume, 99.0)),
                    "max": float(np.max(volume)),
                }
                for name, volume in outputs.items()
            },
            sort_keys=True,
        ),
    }
    return deployment_rows, manifest, timing_rows


def _evaluate_ground_truth_mask_case(
    profile: str,
    fold: str | None,
    case_name: str,
    sources: tuple[ReconstructionSource, ...],
    factor: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Evaluate the explicitly offline ground-truth mask without exposing it to score APIs."""
    reference = sources[0]
    # Match the deployment evaluator's stable analytical-then-neural order so
    # an identical committee cannot be split into separate summary groups.
    outputs = {
        "linear": _load_image(_baseline_path(reference, fold, "linear", case_name))[0],
        "cubic": _load_image(_baseline_path(reference, fold, "cubic", case_name))[0],
    }
    outputs.update(
        {
            source.name: _load_image(_prediction_path(source, fold, case_name))[0]
            for source in sources
        }
    )
    gt = _load_image(_gt_path(reference, fold, case_name, profile))[0]
    if any(volume.shape != gt.shape for volume in outputs.values()):
        raise ValueError(f"offline ground-truth mask shape mismatch: profile={profile}, case={case_name}")
    indices = list(generated_indices(gt.shape[2], factor))
    gt_eval = np.abs(gt[:, :, indices])
    threshold = max(1e-6, 0.01 * float(np.max(gt_eval)))
    mask = gt_eval > threshold
    if not np.any(mask):
        mask = np.ones_like(gt_eval, dtype=bool)
    case_identity = f"{fold}/{case_name}" if fold else case_name
    rows: list[dict[str, Any]] = []
    timings: list[dict[str, Any]] = []
    eval_outputs = {name: volume[:, :, indices] for name, volume in outputs.items()}
    for target in (source.name for source in sources):
        started = time.perf_counter()
        committee_names = tuple(name for name in outputs if name != target)
        score = _median_maps(
            [np.abs(eval_outputs[target] - eval_outputs[name]) for name in committee_names]
        )
        pair_values = [
            float(np.mean(np.abs(eval_outputs[first][mask] - eval_outputs[second][mask])))
            for first_index, first in enumerate(committee_names)
            for second in committee_names[first_index + 1 :]
        ]
        elapsed = time.perf_counter() - started
        error = np.abs(eval_outputs[target] - gt[:, :, indices])
        row = {
            "profile": profile,
            "dataset": PROFILE_ALIASES[profile],
            "fold": fold or "",
            "case": case_identity,
            "target": target,
            "analysis": "mask",
            "score": PRIMARY_SCORE,
            "mask": "ground_truth_offline",
            "normalization": PRIMARY_NORMALIZATION,
            "committee": ";".join(committee_names),
            "committee_size": len(committee_names),
            "composition": _composition(committee_names),
            "subset_id": "full",
            "generated_slices": len(indices),
            "foreground_fraction": float(np.mean(mask)),
            "case_score": float(np.mean(score[mask])),
            "committee_diversity": float(np.mean(pair_values)) if pair_values else 0.0,
            "scoring_seconds": elapsed,
            "foreground_mae": float(np.mean(error[mask])),
            "pixel_corr_foreground": safe_pearson(error[mask], score[mask]),
            "pixel_corr_all": safe_pearson(error, score),
        }
        rows.append(row)
        timings.append(
            {
                "profile": profile,
                "case": case_identity,
                "target": target,
                "analysis": "mask",
                "score": PRIMARY_SCORE,
                "normalization": PRIMARY_NORMALIZATION,
                "mask": "ground_truth_offline",
                "committee_size": len(committee_names),
                "seconds": elapsed,
            }
        )
    return rows, timings


def _group_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(row[key])
        for key in (
            "profile",
            "target",
            "analysis",
            "score",
            "mask",
            "normalization",
            "committee",
            "subset_id",
        )
    )


def _summarize(
    rows: list[dict[str, Any]],
    bootstrap_samples: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_group_key(row)].append(row)
    summaries: list[dict[str, Any]] = []
    bootstrap_rows: list[dict[str, Any]] = []
    risk_rows: list[dict[str, Any]] = []
    for group_index, (key, selected) in enumerate(sorted(grouped.items())):
        selected = sorted(selected, key=lambda row: str(row["case"]))
        errors = np.asarray([float(row["foreground_mae"]) for row in selected])
        scores = np.asarray([float(row["case_score"]) for row in selected])
        pixels = np.asarray([float(row["pixel_corr_foreground"]) for row in selected])
        all_pixels = np.asarray([float(row["pixel_corr_all"]) for row in selected])
        pixel_summary = pixel_correlation_summary(pixels)
        all_pixel_summary = pixel_correlation_summary(all_pixels)
        ranking = ranking_metrics(errors, scores)
        intervals, samples = paired_case_bootstrap(
            errors,
            scores,
            pixels,
            samples=bootstrap_samples,
            seed=seed + group_index,
            all_pixel_correlations=all_pixels,
        )
        first = selected[0]
        summary = {
            **{name: first[name] for name in ("profile", "dataset", "target", "analysis", "score", "mask", "normalization", "committee", "committee_size", "composition", "subset_id")},
            "cases": len(selected),
            **{f"pixel_{name}": value for name, value in pixel_summary.items()},
            **{f"all_pixel_{name}": value for name, value in all_pixel_summary.items()},
            **ranking,
            "scoring_seconds_mean": float(np.mean([float(row["scoring_seconds"]) for row in selected])),
            "scoring_seconds_p95": float(np.percentile([float(row["scoring_seconds"]) for row in selected], 95.0)),
            "committee_diversity_mean": float(np.mean([float(row["committee_diversity"]) for row in selected])),
        }
        for metric, (point, low, high) in intervals.items():
            summary[f"{metric}_point"] = point
            summary[f"{metric}_ci95_low"] = low
            summary[f"{metric}_ci95_high"] = high
        summaries.append(summary)
        group_id = f"g{group_index:04d}"
        for sample in samples:
            bootstrap_rows.append({"group_id": group_id, **{name: first[name] for name in ("profile", "target", "analysis", "score", "mask", "normalization", "committee", "subset_id")}, **sample})
        risk = risk_coverage_summary(errors, scores)
        for curve, values in (("estimated", risk["risk"]), ("oracle", risk["oracle_risk"]), ("random", risk["random_risk"])):
            for coverage, value in zip(risk["coverage"], values):
                risk_rows.append({"group_id": group_id, **{name: first[name] for name in ("profile", "target", "analysis", "score", "mask", "normalization", "committee", "subset_id")}, "curve": curve, "coverage": float(coverage), "risk": float(value)})
    return summaries, bootstrap_rows, risk_rows


def _paired_variant_rows(summaries: list[dict[str, Any]], per_case: list[dict[str, Any]], samples: int, seed: int) -> list[dict[str, Any]]:
    primary: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for row in per_case:
        if row["analysis"] == "score_variants" and row["score"] == PRIMARY_SCORE and row["mask"] == PRIMARY_MASK and row["normalization"] == PRIMARY_NORMALIZATION and row["subset_id"] == "full":
            primary.setdefault((str(row["profile"]), str(row["target"])), {})[str(row["case"])] = row
    output: list[dict[str, Any]] = []
    rng = np.random.default_rng(seed + 900000)
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in per_case:
        grouped[_group_key(row)].append(row)
    for key, selected in sorted(grouped.items()):
        first = selected[0]
        # A mask variant changes the foreground over which MAE is defined, so
        # it is a sensitivity endpoint rather than a paired score comparison.
        if first["analysis"] == "mask":
            continue
        lookup = primary.get((str(first["profile"]), str(first["target"])))
        if not lookup:
            continue
        variant = {str(row["case"]): row for row in selected}
        cases = sorted(set(lookup) & set(variant))
        if len(cases) != len(lookup):
            raise ValueError(f"paired variant case mismatch for {key}")
        errors = np.asarray([float(lookup[case]["foreground_mae"]) for case in cases])
        primary_scores = np.asarray([float(lookup[case]["case_score"]) for case in cases])
        variant_scores = np.asarray([float(variant[case]["case_score"]) for case in cases])
        point_primary = ranking_metrics(errors, primary_scores)
        point_variant = ranking_metrics(errors, variant_scores)
        differences = {metric: [] for metric in ("case_spearman", "normalized_aurc", "rrr_50")}
        for _ in range(samples):
            indices = rng.integers(0, len(cases), size=len(cases))
            p = ranking_metrics(errors[indices], primary_scores[indices])
            v = ranking_metrics(errors[indices], variant_scores[indices])
            for metric in differences:
                differences[metric].append(float(v[metric]) - float(p[metric]))
        stability = (
            0.0
            if float(np.std(primary_scores)) <= 1e-12 or float(np.std(variant_scores)) <= 1e-12
            else float(stats.spearmanr(primary_scores, variant_scores).statistic)
        )
        for metric, values in differences.items():
            array = np.asarray(values, dtype=np.float64)
            output.append(
                {
                    **{name: first[name] for name in ("profile", "target", "analysis", "score", "mask", "normalization", "committee", "committee_size", "composition", "subset_id")},
                    "metric": metric,
                    "primary_point": point_primary[metric],
                    "variant_point": point_variant[metric],
                    "variant_minus_primary": point_variant[metric] - point_primary[metric],
                    "difference_ci95_low": float(np.nanpercentile(array, 2.5)),
                    "difference_ci95_high": float(np.nanpercentile(array, 97.5)),
                    "score_rank_stability": stability,
                    "exploratory_unadjusted": 1,
                }
            )
    return output


def _append_registry(output_root: Path, summaries: list[dict[str, Any]], seed: int) -> Path:
    registry = REPO_ROOT / "design" / "rasinet" / "outputs" / "results_registry.csv"
    existing: list[dict[str, Any]] = []
    if registry.exists() and registry.stat().st_size:
        with registry.open("r", newline="", encoding="utf-8") as handle:
            existing = list(csv.DictReader(handle))
    run_date = date.today().isoformat()
    for index, row in enumerate(summaries):
        for metric in ("pixel_fisher_z_mean", "all_pixel_fisher_z_mean", "case_spearman", "case_kendall", "normalized_aurc", "rrr_25", "rrr_50", "rrr_75", "retained_mae_50", "failure_auroc", "failure_auprc"):
            existing.append(
                {
                    "experiment_id": f"{output_root.name}_{row['profile']}_{row['target']}_{row['analysis']}_{index:04d}_{metric}",
                    "dataset": row["dataset"],
                    "target_model": row["target"],
                    "committee": row["committee"],
                    "score": row["score"],
                    "mask": row["mask"],
                    "normalization": row["normalization"],
                    "metric": metric,
                    "seed": seed,
                    "number_of_cases": row["cases"],
                    "development_or_test": "retrospective_test_observed",
                    "run_date": run_date,
                    "code_commit": "unversioned-workspace",
                    "output_file": str(output_root / "summary.csv"),
                }
            )
    deduplicated = {str(row["experiment_id"]): row for row in existing}
    _write_csv(registry, list(deduplicated.values()))
    return registry


def resummarize(config_path: Path) -> Path:
    """Regenerate statistics from saved case rows without reopening volumes."""
    config = _read_config(config_path)
    seed = int(config.get("seed", DEFAULT_SEED))
    bootstrap_samples = int(config.get("bootstrap_samples", 2000))
    output_root = (REPO_ROOT / str(config.get("output", "design/rasinet/outputs/icassp_primary"))).resolve()
    per_case_path = output_root / "per_case.csv"
    per_case = _read_csv(per_case_path)
    if not per_case:
        raise FileNotFoundError(f"no saved case rows: {per_case_path}")

    full_committees: dict[tuple[str, str], str] = {}
    for row in per_case:
        if (
            row["analysis"] == "score_variants"
            and row["score"] == PRIMARY_SCORE
            and row["mask"] == PRIMARY_MASK
            and row["normalization"] == PRIMARY_NORMALIZATION
            and row["subset_id"] == "full"
        ):
            full_committees[(str(row["profile"]), str(row["target"]))] = str(row["committee"])
    for row in per_case:
        if row["analysis"] == "mask" and row["mask"] == "ground_truth_offline":
            key = (str(row["profile"]), str(row["target"]))
            if key not in full_committees:
                raise ValueError(f"missing canonical full committee for {key}")
            row["committee"] = full_committees[key]

    _write_csv(per_case_path, per_case)
    _write_csv(output_root / "per_case.partial.csv", per_case)
    summaries, bootstrap_rows, risk_rows = _summarize(per_case, bootstrap_samples, seed)
    _write_csv(output_root / "summary.csv", summaries)
    _write_csv(output_root / "bootstrap_samples.csv", bootstrap_rows)
    _write_csv(output_root / "risk_coverage.csv", risk_rows)
    paired = _paired_variant_rows(summaries, per_case, bootstrap_samples, seed)
    _write_csv(output_root / "paired_primary_comparisons.csv", paired)
    print(
        f"[icassp] resummarized rows={len(per_case)} groups={len(summaries)} output={output_root}",
        flush=True,
    )
    return output_root


def run(config_path: Path) -> Path:
    config = _read_config(config_path)
    seed = int(config.get("seed", DEFAULT_SEED))
    np.random.seed(seed)
    factor = int(config.get("factor", 4))
    bootstrap_samples = int(config.get("bootstrap_samples", 2000))
    affine_tolerance = float(config.get("affine_tolerance", 1e-5))
    workers = max(1, int(config.get("workers", 1)))
    output_root = (REPO_ROOT / str(config.get("output", "design/rasinet/outputs/icassp_primary"))).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    partial_per_case = output_root / "per_case.partial.csv"
    partial_manifest = output_root / "input_manifest.partial.csv"
    partial_timing = output_root / "scoring_runtime.partial.csv"
    per_case = _read_csv(partial_per_case)
    manifests = _read_csv(partial_manifest)
    timing_rows = _read_csv(partial_timing)
    required_checkpoint_fields = {
        "profile",
        "case",
        "target",
        "analysis",
        "score",
        "mask",
        "normalization",
        "committee",
        "subset_id",
        "case_score",
        "committee_diversity",
        "foreground_mae",
        "pixel_corr_foreground",
    }
    if per_case:
        missing_fields = sorted(required_checkpoint_fields - set(per_case[0]))
        if missing_fields:
            raise ValueError(
                f"incompatible checkpoint schema in {partial_per_case}; missing fields={missing_fields}. "
                "Use a new output directory or archive the old checkpoint."
            )
    completed = {(str(row["profile"]), str(row["fold"]), str(row["case"])) for row in manifests}
    profiles = tuple(config.get("profiles", PROFILE_ALIASES.keys()))
    for profile in profiles:
        sources = profile_sources(REPO_ROOT, str(profile))
        for fold in _folds(sources):
            cases = _validate_case_sets(sources, fold, str(profile))
            case_limit = config.get("case_limit")
            if case_limit is not None:
                cases = cases[: int(case_limit)]
            pending: list[tuple[int, str]] = []
            for case_index, case_name in enumerate(cases, start=1):
                case_identity = f"{fold}/{case_name}" if fold else case_name
                if (str(profile), fold or "", case_identity) in completed:
                    print(f"[icassp] resume-skip profile={profile} fold={fold or '-'} case={case_index}/{len(cases)} {case_name}", flush=True)
                    continue
                pending.append((case_index, case_name))

            def record(case_index: int, case_name: str, result: tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]) -> None:
                rows, manifest, timings = result
                case_identity = f"{fold}/{case_name}" if fold else case_name
                per_case.extend(rows)
                manifests.append(manifest)
                timing_rows.extend(timings)
                _append_csv(partial_per_case, rows)
                _append_csv(partial_manifest, [manifest])
                _append_csv(partial_timing, timings)
                completed.add((str(profile), fold or "", case_identity))
                print(f"[icassp] completed profile={profile} fold={fold or '-'} case={case_index}/{len(cases)} {case_name}", flush=True)

            if workers == 1:
                for case_index, case_name in pending:
                    print(f"[icassp] profile={profile} fold={fold or '-'} case={case_index}/{len(cases)} {case_name}", flush=True)
                    record(
                        case_index,
                        case_name,
                        _evaluate_case(str(profile), fold, case_name, sources, factor, affine_tolerance, config, output_root),
                    )
            else:
                with ProcessPoolExecutor(max_workers=workers) as executor:
                    futures = {
                        executor.submit(
                            _evaluate_case,
                            str(profile),
                            fold,
                            case_name,
                            sources,
                            factor,
                            affine_tolerance,
                            config,
                            output_root,
                        ): (case_index, case_name)
                        for case_index, case_name in pending
                    }
                    for future in as_completed(futures):
                        case_index, case_name = futures[future]
                        record(case_index, case_name, future.result())

    requested_masks = set(config.get("analyses", {}).get("masks", []))
    if "ground_truth_offline" in requested_masks:
        existing_offline = {
            (str(row["profile"]), str(row["target"]), str(row["case"]))
            for row in per_case
            if row["analysis"] == "mask" and row["mask"] == "ground_truth_offline"
        }
        offline_tasks: list[tuple[str, str | None, str, tuple[ReconstructionSource, ...], set[str]]] = []
        for profile in profiles:
            sources = profile_sources(REPO_ROOT, str(profile))
            for fold in _folds(sources):
                cases = _case_names(sources[0], fold)
                case_limit = config.get("case_limit")
                if case_limit is not None:
                    cases = cases[: int(case_limit)]
                for case_name in cases:
                    case_identity = f"{fold}/{case_name}" if fold else case_name
                    missing_targets = {
                        source.name
                        for source in sources
                        if (str(profile), source.name, case_identity) not in existing_offline
                    }
                    if missing_targets:
                        offline_tasks.append((str(profile), fold, case_name, sources, missing_targets))
        if offline_tasks:
            print(f"[icassp] completing offline-ground-truth-mask tasks={len(offline_tasks)}", flush=True)

            def record_offline(
                profile: str,
                case_name: str,
                missing_targets: set[str],
                result: tuple[list[dict[str, Any]], list[dict[str, Any]]],
            ) -> None:
                rows, timings = result
                rows = [row for row in rows if row["target"] in missing_targets]
                timings = [row for row in timings if row["target"] in missing_targets]
                per_case.extend(rows)
                timing_rows.extend(timings)
                _append_csv(partial_per_case, rows)
                _append_csv(partial_timing, timings)
                print(f"[icassp] offline-mask completed profile={profile} case={case_name}", flush=True)

            if workers == 1:
                for profile, fold, case_name, sources, missing_targets in offline_tasks:
                    record_offline(
                        profile,
                        case_name,
                        missing_targets,
                        _evaluate_ground_truth_mask_case(profile, fold, case_name, sources, factor),
                    )
            else:
                with ProcessPoolExecutor(max_workers=workers) as executor:
                    futures = {
                        executor.submit(
                            _evaluate_ground_truth_mask_case,
                            profile,
                            fold,
                            case_name,
                            sources,
                            factor,
                        ): (profile, case_name, missing_targets)
                        for profile, fold, case_name, sources, missing_targets in offline_tasks
                    }
                    for future in as_completed(futures):
                        profile, case_name, missing_targets = futures[future]
                        record_offline(profile, case_name, missing_targets, future.result())
    _write_csv(output_root / "per_case.csv", per_case)
    _write_csv(output_root / "input_manifest.csv", manifests)
    _write_csv(output_root / "scoring_runtime.csv", timing_rows)
    summaries, bootstrap_rows, risk_rows = _summarize(per_case, bootstrap_samples, seed)
    _write_csv(output_root / "summary.csv", summaries)
    _write_csv(output_root / "bootstrap_samples.csv", bootstrap_rows)
    _write_csv(output_root / "risk_coverage.csv", risk_rows)
    paired = _paired_variant_rows(summaries, per_case, bootstrap_samples, seed)
    _write_csv(output_root / "paired_primary_comparisons.csv", paired)
    registry = (
        _append_registry(output_root, summaries, seed)
        if bool(config.get("register_results", True))
        else REPO_ROOT / "design" / "rasinet" / "outputs" / "results_registry.csv"
    )
    environment = {
        "run_date": date.today().isoformat(),
        "elapsed_seconds": time.time() - started,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "nibabel": nib.__version__,
        "config": str(config_path.resolve()),
        "seed": seed,
        "bootstrap_samples": bootstrap_samples,
        "workers": workers,
        "results_registry": str(registry),
        "pid": os.getpid(),
    }
    (output_root / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    print(f"[icassp] complete rows={len(per_case)} groups={len(summaries)} output={output_root}", flush=True)
    return output_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ground-truth-separated ICASSP reliability evaluation.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--summarize-only",
        action="store_true",
        help="regenerate statistics from the saved per_case.csv without reopening image volumes",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.summarize_only:
        resummarize(args.config)
    else:
        run(args.config)


if __name__ == "__main__":
    main()
