"""Mask before statistics; prediction only accepts retained projected anchors."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[name] = '1'
from dataclasses import dataclass
import numpy as np
import torch
from torch.nn import functional as F
from scipy.interpolate import PchipInterpolator


@dataclass(frozen=True)
class RetainedSource:
    projected_rca: np.ndarray
    retained_positions_mm: tuple
    statistics: dict


def fold_plan(observed_indices, fold):
    assert fold in (0, 1)
    assert len(observed_indices) >= 6
    held = tuple(i for i in range(1, len(observed_indices)-1) if i % 2 == fold)
    kept = tuple(i for i in range(len(observed_indices)) if i not in held)
    assert held and len(kept) >= 4 and kept[0] == 0 and kept[-1] == len(observed_indices)-1
    return kept, held


def statistics(pixels):
    mean = float(np.mean(pixels, dtype=np.float64))
    std = float(np.std(pixels, dtype=np.float64, ddof=0))
    return dict(mean=mean, population_std=std, divisor=std if std > 0 else 1.,
                zero_std=std == 0, elements=int(pixels.size))


def _project(pixels, target_rc, st):
    normalized = ((pixels.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
    x = torch.from_numpy(np.ascontiguousarray(normalized.transpose(2, 0, 1)))[:, None]
    with torch.no_grad():
        y = F.interpolate(x, size=tuple(target_rc), mode='bilinear', align_corners=False)[:, 0].numpy()
    return np.ascontiguousarray(y.transpose(1, 2, 0))


def build_retained_source(retained_pixels, retained_positions_mm, target_rc):
    assert retained_pixels.dtype == np.float32 and np.isfinite(retained_pixels).all()
    assert retained_pixels.shape[2] == len(retained_positions_mm)
    assert np.all(np.diff(retained_positions_mm) > 0)
    st = statistics(retained_pixels)
    projected = _project(retained_pixels, target_rc, st)
    assert np.isfinite(projected).all()
    projected.flags.writeable = False
    return RetainedSource(projected, tuple(map(float, retained_positions_mm)), st)


def predict_heldout(source, query_positions_mm):
    assert not source.projected_rca.flags.writeable
    positions = np.asarray(source.retained_positions_mm, dtype=np.float64)
    query = np.asarray(query_positions_mm, dtype=np.float64)
    assert np.all(np.diff(query) > 0)
    assert ((query > positions[0]) & (query < positions[-1])).all()
    a = source.projected_rca
    linear = np.zeros((*a.shape[:2], len(query)), dtype=np.float32)
    pchip = np.zeros_like(linear)
    definitions = []
    for j, z in enumerate(query):
        i = int(np.searchsorted(positions, z)-1)
        assert positions[i] < z < positions[i+1]
        t = float((z-positions[i])/(positions[i+1]-positions[i]))
        linear[:, :, j] = (1-t)*a[:, :, i]+t*a[:, :, i+1]
        internal = i >= 1 and i+2 < len(positions)
        if internal:
            ix = np.arange(i-1, i+3)
            pchip[:, :, j] = PchipInterpolator(positions[ix], a[:, :, ix], axis=2)(z)
        else:
            pchip[:, :, j] = linear[:, :, j]
        definitions.append(dict(query_position_mm=float(z), bracket_mm=positions[i:i+2].tolist(),
                                local_PCHIP=internal, source_ordinals=list(range(i-1, i+3)) if internal else [i, i+1]))
    assert np.isfinite(linear).all() and np.isfinite(pchip).all()
    return dict(linear=linear, pchip=pchip), definitions


def reference_projection_after_prediction(target_pixels, source):
    return _project(target_pixels, source.projected_rca.shape[:2], source.statistics)


def scores(prediction, reference):
    difference = prediction.astype(np.float64)-reference.astype(np.float64)
    return dict(elements=int(difference.size), sum_error=float(difference.sum()),
                sum_abs_error=float(np.abs(difference).sum()), sum_squared_error=float(np.square(difference).sum()),
                mean_error=float(difference.mean()), MAE=float(np.abs(difference).mean()),
                MSE=float(np.square(difference).mean()), RMSE=float(np.sqrt(np.square(difference).mean())),
                max_abs_error=float(np.abs(difference).max()))
