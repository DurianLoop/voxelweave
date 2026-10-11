"""Explicit voxel-surface metrics; no model or patient selection lives here."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_erosion, distance_transform_edt, generate_binary_structure

STRUCTURE = generate_binary_structure(3, 1)


def overlap(prediction, reference, domain=None):
    prediction = np.asarray(prediction, dtype=bool)
    reference = np.asarray(reference, dtype=bool)
    if prediction.shape != reference.shape:
        raise ValueError("Prediction/reference shapes differ")
    if domain is not None:
        prediction = prediction & domain
        reference = reference & domain
    tp = int(np.count_nonzero(prediction & reference))
    fp = int(np.count_nonzero(prediction & ~reference))
    fn = int(np.count_nonzero(~prediction & reference))
    denom = 2 * tp + fp + fn
    return {"tp": tp, "fp": fp, "fn": fn, "reference_voxels": tp + fn,
            "prediction_voxels": tp + fp, "dice": 2 * tp / denom if denom else None,
            "dice_status": "finite" if denom else "both_empty_undefined",
            "missed_lesion": bool(tp + fn and not tp + fp)}


def bbox_union(a, b, margin=1):
    positions = np.where(a | b)
    if not len(positions[0]):
        return None
    return tuple(slice(max(0, int(p.min()) - margin),
                       min(n, int(p.max()) + margin + 1)) for p, n in zip(positions, a.shape))


def surface(mask):
    return mask & ~binary_erosion(mask, structure=STRUCTURE, border_value=0)


def boundary_distances(prediction, reference, spacing_mm):
    if not reference.any() or not prediction.any():
        status = "both_empty_undefined" if not reference.any() and not prediction.any() else "one_empty_infinite"
        # Strict JSON uses null, with explicit infinite/undefined status.
        return {"assd_mm": None, "hd95_mm": None, "status": status,
                "prediction_surface_voxels": 0 if not prediction.any() else int(surface(prediction).sum()),
                "reference_surface_voxels": 0 if not reference.any() else int(surface(reference).sum())}
    bounds = bbox_union(prediction, reference)
    a, b = surface(prediction[bounds]), surface(reference[bounds])
    ab = distance_transform_edt(~b, sampling=spacing_mm)[a]
    ba = distance_transform_edt(~a, sampling=spacing_mm)[b]
    return {"assd_mm": float((ab.mean() + ba.mean()) / 2),
            "hd95_mm": float(np.percentile(np.concatenate((ab, ba)), 95)), "status": "finite",
            "prediction_surface_voxels": int(a.sum()), "reference_surface_voxels": int(b.sum())}


def outside_reference_band(reference, spacing_mm, radius_mm=1.0):
    """Distance from voxel centres to 6-connected foreground boundary centres."""
    if not reference.any():
        return np.ones(reference.shape, dtype=bool)
    # Only the reference bounding box plus the physical radius can intersect the band.
    pos = np.where(reference)
    margin = np.ceil(radius_mm / np.asarray(spacing_mm)).astype(int) + 1
    bounds = tuple(slice(max(0, int(p.min()) - int(m)), min(n, int(p.max()) + int(m) + 1))
                   for p, n, m in zip(pos, reference.shape, margin))
    boundary = surface(reference[bounds])
    keep = np.ones(reference.shape, dtype=bool)
    keep[bounds] = distance_transform_edt(~boundary, sampling=spacing_mm) > radius_mm
    return keep


def task_metrics(prediction, reference, spacing_mm, supported_domain, band_keep=None):
    full = overlap(prediction, reference)
    count = full["reference_voxels"]
    signed = full["prediction_voxels"] - count
    full.update({"signed_volume_difference_mm3": float(signed * np.prod(spacing_mm)),
                 "signed_relative_volume_error": signed / count if count else None,
                 "absolute_relative_volume_error": abs(signed) / count if count else None,
                 "boundary": boundary_distances(prediction, reference, spacing_mm)})
    slab = overlap(prediction, reference, supported_domain)
    slab["boundary"] = boundary_distances(prediction & supported_domain, reference & supported_domain, spacing_mm)
    keep = outside_reference_band(reference, spacing_mm) if band_keep is None else band_keep
    core = overlap(prediction, reference, keep)
    core["reference_core_empty"] = not bool((reference & keep).any())
    if core["reference_core_empty"]:
        core["dice"] = None
        core["dice_status"] = "empty_reference_core_undefined"
    core["excluded_band_voxels"] = int(np.count_nonzero(~keep))
    return {"full": full, "observed_anchor_slab": slab, "exclude_reference_boundary_1mm": core}


def paired_bootstrap(values, seed=20261012, draws=5000):
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Bootstrap requires nonempty finite patient vector")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(draws, len(values)))
    samples = values[indices].mean(axis=1)
    low, high = np.percentile(samples, [2.5, 97.5])
    return {"n": len(values), "mean_difference": float(values.mean()),
            "ci95_percentile": [float(low), float(high)], "seed": seed, "draws": draws,
            "negative_patients": int(np.count_nonzero(values < 0)),
            "zero_patients": int(np.count_nonzero(values == 0))}
