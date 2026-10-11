"""Common projected observed anchors, then independent direct/dense encoding.

No native image/GT loader argument. New control; does not replace the old input.
"""
from dataclasses import dataclass
import numpy as np
from torch.nn import functional as F
from mc_rc_3d_direct_observed_2026_10_07 import (
    ROOT, read, sha, array_sha, lattice, physical_mr, torch,
    development_observed_cases, load_development_observed, augment_pair,
)
from mc_rc_observed_only_training_input import ObservedMRI, reconstruct, stats


@dataclass(frozen=True)
class ProjectedObserved:
    anchors_rca: np.ndarray
    indices: tuple
    native_planes: int
    affine_rcz_ras: tuple
    observed_statistics: dict


def shared_source(observed, grid):
    st = stats(observed.pixels)
    normalized = ((observed.pixels.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
    target = tuple(grid['unpadded_shape_zrc'][1:])
    x = torch.from_numpy(np.ascontiguousarray(normalized.transpose(2, 0, 1)))[:, None]
    with torch.no_grad():
        projected = F.interpolate(x, size=target, mode='bilinear', align_corners=False)[:, 0].numpy()
    anchors = np.ascontiguousarray(projected.transpose(1, 2, 0))
    assert anchors.dtype == np.float32 and np.isfinite(anchors).all()
    center = np.eye(4)
    scale = np.asarray(observed.pixels.shape[:2], dtype=float)/target
    center[0, 0], center[1, 1] = scale
    center[:2, 3] = scale/2-.5
    affine = np.asarray(observed.affine_rcz_ras)@center
    anchors.flags.writeable = False
    return ProjectedObserved(anchors, observed.indices, observed.native_planes,
                             tuple(map(tuple, affine)), dict(st)), array_sha(normalized)


def branched_native(source):
    assert not source.anchors_rca.flags.writeable
    assert source.indices == tuple(range(0, source.native_planes, 4))
    wrapper = ObservedMRI(source.anchors_rca, source.indices, source.native_planes,
                          source.affine_rcz_ras, (), ())
    dense = reconstruct(wrapper, 'raw_pchip')
    numerator = np.zeros((*source.anchors_rca.shape[:2], source.native_planes), dtype=np.float32)
    numerator[:, :, source.indices] = source.anchors_rca
    return dense, numerator


def z_to_physical(field_rcz, grid):
    assert list(field_rcz.shape[:2]) == grid['unpadded_shape_zrc'][1:]
    image = torch.from_numpy(np.ascontiguousarray(field_rcz.transpose(2, 0, 1)))[None, None]
    with torch.no_grad():
        core = F.interpolate(image, size=grid['unpadded_shape_zrc'], mode='trilinear',
                             align_corners=False)[0, 0].numpy()
    return np.pad(core, grid['padding'], mode='constant').astype(np.float32, copy=False)


def availability_from_geometry(source, grid):
    nz, nr, nc = map(int, grid['native_shape_zrc'])
    assert nz == source.native_planes
    mask = np.zeros((nr, nc, nz), dtype=np.float32)
    mask[:, :, source.indices] = 1
    return physical_mr(mask, grid)


def projected_pair_fields(source, grid):
    dense, numerator = branched_native(source)
    availability = availability_from_geometry(source, grid)
    fields = dict(dense=z_to_physical(dense, grid), numerator=z_to_physical(numerator, grid),
                  availability=availability,
                  valid_grid=np.pad(np.ones(grid['unpadded_shape_zrc'], dtype=np.float32),
                                    grid['padding'], mode='constant'))
    return fields, dict(dense=array_sha(dense), numerator=array_sha(numerator))


def final_affines(source, grid):
    center = np.eye(4)
    scale = source.native_planes/grid['unpadded_shape_zrc'][0]
    center[0, 0] = scale
    center[0, 3] = scale/2-.5
    permutation = np.eye(4)
    permutation[:3, :3] = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    physical = np.asarray(source.affine_rcz_ras)@permutation@center
    pad = np.eye(4)
    pad[:3, 3] = -np.array([lo for lo, hi in grid['padding']])
    return physical, physical@pad
