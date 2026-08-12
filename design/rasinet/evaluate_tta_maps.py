from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import yaml

from .committee_experiments import _case_names, _gt_path, _prediction_path, profile_sources
from .committee_reliability import risk_coverage_summary
from .icassp_scores import deployment_mask, generated_indices
from .icassp_statistics import paired_case_bootstrap, pixel_correlation_summary, ranking_metrics, safe_pearson


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    image = nib.load(str(path))
    data = image.get_fdata(dtype=np.float32)
    if data.ndim != 3 or not np.isfinite(data).all():
        raise ValueError(f"invalid volume: {path}")
    return data, image.affine


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _paired_primary_comparison(
    tta_rows: list[dict[str, object]],
    primary_path: Path,
    samples: int,
    seed: int,
) -> list[dict[str, object]]:
    if not primary_path.exists():
        return []
    with primary_path.open("r", newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))
    primary = {
        row["case"]: row
        for row in candidates
        if row["profile"] == "fastmri_full"
        and row["target"] == "swinir"
        and row["analysis"] == "score_variants"
        and row["score"] == "target_abs_median"
        and row["mask"] == "target_0.01"
        and row["normalization"] == "raw"
        and row["subset_id"] == "full"
    }
    tta = {str(row["case"]): row for row in tta_rows}
    if set(primary) != set(tta):
        raise ValueError("TTA and primary case sets differ")
    cases = sorted(tta)
    primary_errors = np.asarray([float(primary[case]["foreground_mae"]) for case in cases])
    tta_errors = np.asarray([float(tta[case]["foreground_mae"]) for case in cases])
    if not np.allclose(primary_errors, tta_errors, rtol=1e-6, atol=1e-5):
        raise ValueError("TTA and primary foreground error endpoints differ")
    primary_scores = np.asarray([float(primary[case]["case_score"]) for case in cases])
    tta_scores = np.asarray([float(tta[case]["case_score"]) for case in cases])
    primary_point = ranking_metrics(primary_errors, primary_scores)
    tta_point = ranking_metrics(tta_errors, tta_scores)
    metrics = ("case_spearman", "normalized_aurc", "rrr_50")
    differences = {metric: np.empty(samples, dtype=np.float64) for metric in metrics}
    rng = np.random.default_rng(seed + 810000)
    for sample_index in range(samples):
        indices = rng.integers(0, len(cases), size=len(cases))
        primary_sample = ranking_metrics(primary_errors[indices], primary_scores[indices])
        tta_sample = ranking_metrics(tta_errors[indices], tta_scores[indices])
        for metric in metrics:
            differences[metric][sample_index] = tta_sample[metric] - primary_sample[metric]
    return [
        {
            "metric": metric,
            "primary_point": primary_point[metric],
            "tta_point": tta_point[metric],
            "tta_minus_primary": tta_point[metric] - primary_point[metric],
            "difference_ci95_low": float(np.percentile(differences[metric], 2.5)),
            "difference_ci95_high": float(np.percentile(differences[metric], 97.5)),
        }
        for metric in metrics
    ]


def run(config: dict[str, object]) -> None:
    profile = str(config.get("profile", "fastmri_full"))
    target_name = str(config.get("target", "swinir"))
    factor = int(config.get("factor", 4))
    samples = int(config.get("bootstrap_samples", 2000))
    seed = int(config.get("seed", 20260715))
    output = (REPO_ROOT / str(config["output"])).resolve()
    maps = (REPO_ROOT / str(config["tta_map_directory"])).resolve()
    sources = profile_sources(REPO_ROOT, profile)
    target_source = next(source for source in sources if source.name == target_name)
    reference = sources[0]
    cases = _case_names(target_source, None)
    rows: list[dict[str, object]] = []
    for index, case_name in enumerate(cases, start=1):
        print(f"[tta-eval] case={index}/{len(cases)} {case_name}", flush=True)
        prediction, pred_affine = _load(_prediction_path(target_source, None, case_name))
        score, score_affine = _load(maps / f"tta_std_{case_name}")
        gt, gt_affine = _load(_gt_path(reference, None, case_name, profile))
        if prediction.shape != score.shape or prediction.shape != gt.shape:
            raise ValueError(f"shape mismatch for {case_name}")
        if not np.allclose(pred_affine, score_affine, atol=1e-5, rtol=0.0) or not np.allclose(pred_affine, gt_affine, atol=1e-5, rtol=0.0):
            raise ValueError(f"affine mismatch for {case_name}")
        indices = list(generated_indices(prediction.shape[2], factor))
        mask = deployment_mask(prediction, {"placeholder": prediction}, "target_0.01", factor)[:, :, indices]
        score_eval = score[:, :, indices]
        error = np.abs(prediction[:, :, indices] - gt[:, :, indices])
        rows.append(
            {
                "profile": profile,
                "dataset": "fastmri",
                "target": target_name,
                "case": case_name,
                "score": "tta_variance",
                "mask": "target_0.01",
                "normalization": "raw",
                "case_score": float(np.mean(score_eval[mask])),
                "foreground_mae": float(np.mean(error[mask])),
                "pixel_corr_foreground": safe_pearson(error[mask], score_eval[mask]),
                "pixel_corr_all": safe_pearson(error, score_eval),
            }
        )
    errors = np.asarray([float(row["foreground_mae"]) for row in rows])
    scores = np.asarray([float(row["case_score"]) for row in rows])
    pixels = np.asarray([float(row["pixel_corr_foreground"]) for row in rows])
    all_pixels = np.asarray([float(row["pixel_corr_all"]) for row in rows])
    pixel_summary = pixel_correlation_summary(pixels)
    all_pixel_summary = pixel_correlation_summary(all_pixels)
    ranking = ranking_metrics(errors, scores)
    intervals, bootstrap = paired_case_bootstrap(
        errors, scores, pixels, samples=samples, seed=seed, all_pixel_correlations=all_pixels
    )
    summary: dict[str, object] = {
        "profile": profile,
        "dataset": "fastmri",
        "target": target_name,
        "score": "tta_variance",
        "mask": "target_0.01",
        "normalization": "raw",
        "cases": len(rows),
        **pixel_summary,
        **{f"all_pixel_{name}": value for name, value in all_pixel_summary.items()},
        **ranking,
    }
    for metric, (point, low, high) in intervals.items():
        summary[f"{metric}_point"] = point
        summary[f"{metric}_ci95_low"] = low
        summary[f"{metric}_ci95_high"] = high
    risk = risk_coverage_summary(errors, scores)
    risk_rows: list[dict[str, object]] = []
    for curve, values in (("estimated", risk["risk"]), ("oracle", risk["oracle_risk"]), ("random", risk["random_risk"])):
        for coverage, value in zip(risk["coverage"], values):
            risk_rows.append({"curve": curve, "coverage": float(coverage), "risk": float(value)})
    output.mkdir(parents=True, exist_ok=True)
    _write(output / "per_case.csv", rows)
    _write(output / "summary.csv", [summary])
    _write(output / "bootstrap_samples.csv", bootstrap)
    _write(output / "risk_coverage.csv", risk_rows)
    primary_results = config.get("primary_per_case")
    if primary_results is not None:
        paired = _paired_primary_comparison(
            rows,
            (REPO_ROOT / str(primary_results)).resolve(),
            samples,
            seed,
        )
        if paired:
            _write(output / "paired_primary_comparison.csv", paired)
    runtime_path = REPO_ROOT / "design" / "rasinet" / "runs" / "posthoc_uncertainty" / "fastmri_swinir_tta" / "metrics" / "runtime_tta.csv"
    if runtime_path.exists():
        with runtime_path.open("r", newline="", encoding="utf-8") as handle:
            runtime = list(csv.DictReader(handle))
        (output / "runtime_summary.json").write_text(
            json.dumps(
                {
                    "cases": len(runtime),
                    "views": sorted({int(row["views"]) for row in runtime}),
                    "seconds_total": sum(float(row["seconds"]) for row in runtime),
                    "seconds_mean": float(np.mean([float(row["seconds"]) for row in runtime])),
                },
                indent=2,
            ),
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-evaluate stored TTA maps under the ICASSP case-level protocol.")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    run(config)


if __name__ == "__main__":
    main()
