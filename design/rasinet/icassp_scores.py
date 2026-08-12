from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
from scipy import ndimage


ANALYTICAL_MEMBERS = frozenset({"linear", "cubic"})


def _as_finite(volume: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(volume, dtype=np.float32)
    if array.ndim != 3:
        raise ValueError(f"{name} must be a 3-D volume, got shape={array.shape}")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains non-finite values")
    return array


def validate_named_outputs(target_name: str, target: np.ndarray, committee: Mapping[str, np.ndarray]) -> None:
    if target_name in committee:
        raise ValueError(f"target {target_name!r} must be excluded from its committee")
    target_array = _as_finite(target, f"target[{target_name}]")
    if not committee:
        raise ValueError("committee must contain at least one named output")
    for name, member in committee.items():
        member_array = _as_finite(member, f"committee[{name}]")
        if member_array.shape != target_array.shape:
            raise ValueError(
                f"shape mismatch for target={target_name} and member={name}: "
                f"{target_array.shape} != {member_array.shape}"
            )


def _support(volume: np.ndarray, fraction: float = 0.01) -> np.ndarray:
    array = np.abs(_as_finite(volume, "volume"))
    maximum = float(np.max(array))
    threshold = max(1e-6, fraction * maximum)
    mask = array > threshold
    return mask if np.any(mask) else np.ones_like(array, dtype=bool)


def normalize_output(volume: np.ndarray, mode: str) -> np.ndarray:
    """Normalize one deterministic output without ground-truth information."""
    array = _as_finite(volume, "volume")
    if mode == "raw":
        return array.copy()

    foreground = _support(array)
    values = array[foreground].astype(np.float64)
    if mode == "percentile_p1_p99":
        lo, hi = np.percentile(values, [1.0, 99.0])
        scale = max(float(hi - lo), 1e-6)
        return np.clip((array - lo) / scale, 0.0, 1.0).astype(np.float32)
    if mode == "robust_median_iqr":
        median = float(np.median(values))
        q1, q3 = np.percentile(values, [25.0, 75.0])
        scale = max(float(q3 - q1), 1e-6)
        return ((array - median) / scale).astype(np.float32)
    if mode == "minmax":
        lo = float(np.min(array))
        hi = float(np.max(array))
        scale = max(hi - lo, 1e-6)
        return ((array - lo) / scale).astype(np.float32)
    raise ValueError(f"unknown normalization mode: {mode}")


def normalize_named_outputs(outputs: Mapping[str, np.ndarray], mode: str) -> dict[str, np.ndarray]:
    return {name: normalize_output(volume, mode) for name, volume in outputs.items()}


def generated_indices(depth: int, factor: int, anchor_start: int = 0) -> tuple[int, ...]:
    if factor < 2:
        raise ValueError("interpolation factor must be at least two")
    if not 0 <= anchor_start < factor:
        raise ValueError("anchor_start must satisfy 0 <= anchor_start < factor")
    indices = tuple(index for index in range(depth) if (index - anchor_start) % factor != 0)
    if not indices:
        raise ValueError(f"no generated slices for depth={depth}, factor={factor}")
    return indices


def _gradient_magnitude(volume: np.ndarray) -> np.ndarray:
    gradients = np.gradient(volume.astype(np.float32), edge_order=1)
    return np.sqrt(sum(component * component for component in gradients)).astype(np.float32)


def _trimmed_mean(stack: np.ndarray) -> np.ndarray:
    if stack.shape[0] < 3:
        return np.mean(stack, axis=0)
    ordered = np.sort(stack, axis=0)
    return np.mean(ordered[1:-1], axis=0)


def score_map(
    target_name: str,
    target: np.ndarray,
    committee: Mapping[str, np.ndarray],
    score: str,
    all_outputs: Mapping[str, np.ndarray] | None = None,
) -> np.ndarray:
    """Compute a deployment score map. This API intentionally has no ground-truth argument."""
    validate_named_outputs(target_name, target, committee)
    target_array = np.asarray(target, dtype=np.float32)
    names = tuple(sorted(committee))
    members = [np.asarray(committee[name], dtype=np.float32) for name in names]
    differences = np.stack([np.abs(target_array - member) for member in members], axis=0)

    if score == "target_abs_median":
        result = np.median(differences, axis=0)
    elif score == "target_abs_mean":
        result = np.mean(differences, axis=0)
    elif score == "target_abs_max":
        result = np.max(differences, axis=0)
    elif score == "target_abs_trimmed_mean":
        result = _trimmed_mean(differences)
    elif score == "distance_committee_mean":
        result = np.abs(target_array - np.mean(np.stack(members, axis=0), axis=0))
    elif score == "distance_committee_median":
        result = np.abs(target_array - np.median(np.stack(members, axis=0), axis=0))
    elif score in {"shared_std", "pairwise_mean", "pairwise_median"}:
        source = all_outputs if all_outputs is not None else {target_name: target_array, **committee}
        arrays = [np.asarray(source[name], dtype=np.float32) for name in sorted(source)]
        if score == "shared_std":
            result = np.std(np.stack(arrays, axis=0), axis=0)
        else:
            pairwise = np.stack(
                [np.abs(arrays[i] - arrays[j]) for i in range(len(arrays)) for j in range(i + 1, len(arrays))],
                axis=0,
            )
            result = np.mean(pairwise, axis=0) if score == "pairwise_mean" else np.median(pairwise, axis=0)
    elif score.startswith("residual_"):
        analytical = [name for name in ("linear", "cubic") if name in committee]
        if not analytical:
            raise ValueError(f"score {score} requires linear and/or cubic in the committee")
        residuals = np.stack([np.abs(target_array - committee[name]) for name in analytical], axis=0)
        if score == "residual_linear":
            if "linear" not in committee:
                raise ValueError("residual_linear requires linear")
            result = np.abs(target_array - committee["linear"])
        elif score == "residual_cubic":
            if "cubic" not in committee:
                raise ValueError("residual_cubic requires cubic")
            result = np.abs(target_array - committee["cubic"])
        elif score == "residual_analytic_mean":
            result = np.mean(residuals, axis=0)
        elif score == "residual_analytic_min":
            result = np.min(residuals, axis=0)
        elif score == "residual_analytic_max":
            result = np.max(residuals, axis=0)
        else:
            raise ValueError(f"unknown analytical score: {score}")
    elif score == "gradient_target_abs_median":
        target_gradient = _gradient_magnitude(target_array)
        gradients = np.stack(
            [np.abs(target_gradient - _gradient_magnitude(member)) for member in members], axis=0
        )
        result = np.median(gradients, axis=0)
    elif score == "laplacian_target_abs_median":
        target_laplacian = ndimage.laplace(target_array, mode="nearest")
        laplacians = np.stack(
            [np.abs(target_laplacian - ndimage.laplace(member, mode="nearest")) for member in members], axis=0
        )
        result = np.median(laplacians, axis=0)
    else:
        raise ValueError(f"unknown score: {score}")
    return np.asarray(result, dtype=np.float32)


def _threshold_mask(
    volume: np.ndarray,
    threshold_fraction: float,
    threshold_indices: Sequence[int] | None = None,
) -> np.ndarray:
    absolute = np.abs(_as_finite(volume, "mask source"))
    reference = absolute if threshold_indices is None else absolute[:, :, list(threshold_indices)]
    threshold = max(1e-6, threshold_fraction * float(np.max(reference)))
    mask = absolute > threshold
    return mask if np.any(mask) else np.ones_like(mask, dtype=bool)


def _input_derived_mask(target: np.ndarray, factor: int, threshold_fraction: float) -> np.ndarray:
    anchor_indices = list(range(0, target.shape[2], factor))
    anchors = _threshold_mask(target[:, :, anchor_indices], threshold_fraction)
    output = np.empty(target.shape, dtype=bool)
    for index in range(target.shape[2]):
        nearest = min(range(len(anchor_indices)), key=lambda j: abs(anchor_indices[j] - index))
        output[:, :, index] = anchors[:, :, nearest]
    return output


def deployment_mask(
    target: np.ndarray,
    committee: Mapping[str, np.ndarray],
    mode: str,
    factor: int,
) -> np.ndarray:
    """Build a deployment-compatible mask without a reference target."""
    target_array = _as_finite(target, "target")
    eval_indices = generated_indices(target_array.shape[2], factor)
    if mode.startswith("target_"):
        fraction = float(mode.split("_", 1)[1])
        return _threshold_mask(target_array, fraction, eval_indices)
    if mode == "committee_union":
        masks = [_threshold_mask(member, 0.01, eval_indices) for member in committee.values()]
        return np.logical_or.reduce(masks)
    if mode == "committee_intersection":
        masks = [_threshold_mask(member, 0.01, eval_indices) for member in committee.values()]
        result = np.logical_and.reduce(masks)
        return result if np.any(result) else np.logical_or.reduce(masks)
    if mode == "committee_median":
        median_image = np.median(np.stack(list(committee.values()), axis=0), axis=0)
        return _threshold_mask(median_image, 0.01, eval_indices)
    if mode == "input_derived":
        return _input_derived_mask(target_array, factor, 0.01)
    raise ValueError(f"unknown mask mode: {mode}")


def examination_score(score: np.ndarray, mask: np.ndarray, indices: Sequence[int]) -> float:
    score_eval = np.asarray(score, dtype=np.float32)[:, :, list(indices)]
    mask_eval = np.asarray(mask, dtype=bool)[:, :, list(indices)]
    if score_eval.shape != mask_eval.shape:
        raise ValueError("score and mask must have equal shapes")
    if not np.any(mask_eval):
        raise ValueError("deployment mask is empty on generated slices")
    return float(np.mean(score_eval[mask_eval]))
