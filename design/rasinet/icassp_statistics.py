from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy import stats

from .committee_reliability import risk_coverage_summary


def safe_pearson(first: np.ndarray, second: np.ndarray) -> float:
    a = np.asarray(first, dtype=np.float64).reshape(-1)
    b = np.asarray(second, dtype=np.float64).reshape(-1)
    valid = np.isfinite(a) & np.isfinite(b)
    if int(valid.sum()) < 2:
        return float("nan")
    a, b = a[valid], b[valid]
    if float(np.std(a)) <= 1e-12 or float(np.std(b)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def pixel_correlation_summary(values: Sequence[float]) -> dict[str, float]:
    correlations = np.asarray(values, dtype=np.float64)
    correlations = correlations[np.isfinite(correlations)]
    if correlations.size == 0:
        raise ValueError("pixel correlations are empty")
    clipped = np.clip(correlations, -0.999999, 0.999999)
    return {
        "fisher_z_mean": float(np.tanh(np.mean(np.arctanh(clipped)))),
        "median": float(np.median(correlations)),
        "q1": float(np.percentile(correlations, 25.0)),
        "q3": float(np.percentile(correlations, 75.0)),
        "arithmetic_mean": float(np.mean(correlations)),
    }


def ranking_metrics(errors: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    errors = np.asarray(errors, dtype=np.float64)
    scores = np.asarray(scores, dtype=np.float64)
    risk = risk_coverage_summary(errors, scores)
    spearman = 0.0 if float(np.std(errors)) <= 1e-12 or float(np.std(scores)) <= 1e-12 else float(stats.spearmanr(errors, scores).statistic)
    kendall = 0.0 if float(np.std(errors)) <= 1e-12 or float(np.std(scores)) <= 1e-12 else float(stats.kendalltau(errors, scores).statistic)
    failure_count = max(1, int(np.ceil(0.10 * errors.size)))
    failure_order = np.argsort(errors, kind="mergesort")
    labels = np.zeros(errors.size, dtype=bool)
    labels[failure_order[-failure_count:]] = True
    positives = scores[labels]
    negatives = scores[~labels]
    if negatives.size:
        ranks = stats.rankdata(scores, method="average")
        rank_sum = float(np.sum(ranks[labels]))
        u_statistic = rank_sum - positives.size * (positives.size + 1) / 2.0
        failure_auroc = float(u_statistic / (positives.size * negatives.size))
    else:
        failure_auroc = 1.0
    ranked_labels = labels[np.argsort(-scores, kind="mergesort")]
    positive_positions = np.flatnonzero(ranked_labels) + 1
    cumulative = np.cumsum(ranked_labels)
    failure_auprc = float(np.mean(cumulative[positive_positions - 1] / positive_positions))
    return {
        "case_spearman": spearman,
        "case_kendall": kendall,
        "aurc": float(risk["aurc"]),
        "oracle_aurc": float(risk["oracle_aurc"]),
        "random_aurc": float(risk["random_aurc"]),
        "normalized_aurc": float(risk["normalized_aurc"]),
        "failure_auroc": failure_auroc,
        "failure_auprc": failure_auprc,
        **{f"retained_mae_{coverage}": float(risk[f"risk_at_{coverage}"]) for coverage in (25, 50, 75)},
        **{
            f"rrr_{coverage}": float(risk[f"relative_risk_reduction_at_{coverage}"])
            for coverage in (25, 50, 75)
        },
    }


def paired_case_bootstrap(
    errors: np.ndarray,
    scores: np.ndarray,
    pixel_correlations: np.ndarray,
    samples: int,
    seed: int,
    all_pixel_correlations: np.ndarray | None = None,
) -> tuple[dict[str, tuple[float, float, float]], list[dict[str, float | int]]]:
    errors = np.asarray(errors, dtype=np.float64)
    scores = np.asarray(scores, dtype=np.float64)
    pixels = np.asarray(pixel_correlations, dtype=np.float64)
    if not (errors.size == scores.size == pixels.size) or errors.size < 2:
        raise ValueError("bootstrap arrays must have equal length >= 2")
    all_pixels = None if all_pixel_correlations is None else np.asarray(all_pixel_correlations, dtype=np.float64)
    if all_pixels is not None and all_pixels.size != errors.size:
        raise ValueError("all-pixel correlations must match the case count")
    point_pixel = pixel_correlation_summary(pixels)["fisher_z_mean"]
    point_ranking = ranking_metrics(errors, scores)
    points = {"pixel_fisher_z_mean": point_pixel, **point_ranking}
    if all_pixels is not None:
        points["all_pixel_fisher_z_mean"] = pixel_correlation_summary(all_pixels)["fisher_z_mean"]
    bootstrap = {name: [] for name in points}
    rows: list[dict[str, float | int]] = []
    rng = np.random.default_rng(seed)
    for replicate in range(samples):
        indices = rng.integers(0, errors.size, size=errors.size)
        sampled_pixels = pixels[indices]
        values = {
            "pixel_fisher_z_mean": pixel_correlation_summary(sampled_pixels)["fisher_z_mean"],
            **ranking_metrics(errors[indices], scores[indices]),
        }
        if all_pixels is not None:
            values["all_pixel_fisher_z_mean"] = pixel_correlation_summary(all_pixels[indices])["fisher_z_mean"]
        for name, value in values.items():
            bootstrap[name].append(value)
        rows.append({"replicate": replicate, **values})
    intervals: dict[str, tuple[float, float, float]] = {}
    for name, point in points.items():
        array = np.asarray(bootstrap[name], dtype=np.float64)
        array = array[np.isfinite(array)]
        intervals[name] = (
            float(point),
            float(np.percentile(array, 2.5)),
            float(np.percentile(array, 97.5)),
        )
    return intervals, rows
