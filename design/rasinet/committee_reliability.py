from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np


def _validated_volumes(volumes: Iterable[np.ndarray], label: str) -> list[np.ndarray]:
    arrays = [np.asarray(volume, dtype=np.float32) for volume in volumes]
    if not arrays:
        raise ValueError(f"{label} must contain at least one volume")
    shape = arrays[0].shape
    if any(array.shape != shape for array in arrays):
        raise ValueError(f"all {label} volumes must have the same shape")
    if any(not np.isfinite(array).all() for array in arrays):
        raise ValueError(f"all {label} volumes must be finite")
    return arrays


def target_to_committee_disagreement(
    target: np.ndarray,
    committee: Iterable[np.ndarray],
) -> np.ndarray:
    """Return the pixel-wise median absolute target-to-committee difference."""
    target_array = np.asarray(target, dtype=np.float32)
    if not np.isfinite(target_array).all():
        raise ValueError("target prediction must be finite")
    raw_members = list(committee)
    if any(member is target for member in raw_members):
        raise ValueError("target prediction must be excluded from the committee")
    members = _validated_volumes(raw_members, "committee")
    if any(member.shape != target_array.shape for member in members):
        raise ValueError("target and committee volumes must have the same shape")
    differences = np.stack(
        [np.abs(target_array - member) for member in members],
        axis=0,
    )
    return np.median(differences, axis=0).astype(np.float32)


def committee_dispersion(committee: Iterable[np.ndarray]) -> np.ndarray:
    """Return the shared pixel-wise standard deviation of committee outputs."""
    members = _validated_volumes(committee, "committee")
    return np.std(np.stack(members, axis=0), axis=0).astype(np.float32)


def _discrete_risk_curve(errors: np.ndarray, order: np.ndarray) -> np.ndarray:
    ordered = errors[order]
    return np.cumsum(ordered) / np.arange(1, ordered.size + 1, dtype=np.float64)


def risk_coverage_summary(
    errors: Sequence[float] | np.ndarray,
    scores: Sequence[float] | np.ndarray,
    coverages: Sequence[float] = (0.25, 0.5, 0.75),
) -> dict[str, float | np.ndarray]:
    """Summarize selective risk against random and oracle case rankings."""
    error_array = np.asarray(errors, dtype=np.float64).reshape(-1)
    score_array = np.asarray(scores, dtype=np.float64).reshape(-1)
    if error_array.size == 0 or error_array.size != score_array.size:
        raise ValueError("errors and scores must be non-empty arrays of equal length")
    if not np.isfinite(error_array).all() or not np.isfinite(score_array).all():
        raise ValueError("errors and scores must contain only finite values")
    if np.any(error_array < 0.0):
        raise ValueError("errors must be non-negative")

    coverage_values = tuple(float(value) for value in coverages)
    if any(value <= 0.0 or value > 1.0 for value in coverage_values):
        raise ValueError("coverages must lie in (0, 1]")

    order = np.argsort(score_array, kind="mergesort")
    oracle_order = np.argsort(error_array, kind="mergesort")
    risk = _discrete_risk_curve(error_array, order)
    oracle_risk = _discrete_risk_curve(error_array, oracle_order)
    random_risk = np.full(error_array.size, float(np.mean(error_array)), dtype=np.float64)
    coverage_axis = np.arange(1, error_array.size + 1, dtype=np.float64) / error_array.size

    aurc = float(np.mean(risk))
    oracle_aurc = float(np.mean(oracle_risk))
    random_aurc = float(np.mean(random_risk))
    excess_aurc = aurc - oracle_aurc
    denominator = random_aurc - oracle_aurc
    normalized_aurc = excess_aurc / denominator if denominator > 1e-12 else 0.0

    result: dict[str, float | np.ndarray] = {
        "coverage": coverage_axis,
        "risk": risk,
        "oracle_risk": oracle_risk,
        "random_risk": random_risk,
        "aurc": aurc,
        "oracle_aurc": oracle_aurc,
        "random_aurc": random_aurc,
        "excess_aurc": excess_aurc,
        "normalized_aurc": float(normalized_aurc),
    }
    global_risk = float(np.mean(error_array))
    for coverage in coverage_values:
        count = max(1, int(np.ceil(coverage * error_array.size)))
        key = int(round(100.0 * coverage))
        retained_risk = float(risk[count - 1])
        result[f"risk_at_{key}"] = retained_risk
        result[f"relative_risk_reduction_at_{key}"] = (
            (global_risk - retained_risk) / global_risk if global_risk > 1e-12 else 0.0
        )
    return result
