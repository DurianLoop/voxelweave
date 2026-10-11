"""NumPy pixel-center resampling, physical context and coverage reference; no Torch import."""
import numpy as np


def bilinear(values, rows, cols):
    """Evaluate border-clamped RC bilinear samples independently in float64."""
    a = np.asarray(values, dtype=np.float64)
    rows = np.clip(np.asarray(rows, dtype=np.float64), 0, a.shape[-2] - 1)
    cols = np.clip(np.asarray(cols, dtype=np.float64), 0, a.shape[-1] - 1)
    r0, c0 = np.floor(rows).astype(int), np.floor(cols).astype(int)
    r1, c1 = np.minimum(r0 + 1, a.shape[-2] - 1), np.minimum(c0 + 1, a.shape[-1] - 1)
    wr, wc = rows - r0, cols - c0
    return ((1-wr)*(1-wc)*a[..., r0, c0] + wr*(1-wc)*a[..., r1, c0]
            + (1-wr)*wc*a[..., r0, c1] + wr*wc*a[..., r1, c1])


def resize_reference(values, target_shape):
    rows = (np.arange(target_shape[0]) + .5) * values.shape[-2] / target_shape[0] - .5
    cols = (np.arange(target_shape[1]) + .5) * values.shape[-1] / target_shape[1] - .5
    rr, cc = np.meshgrid(rows, cols, indexing='ij')
    return bilinear(values, rr, cc)


def physical_context_reference(image, z, spacing):
    output = []
    for distance in (-2., -1., 0., 1., 2.):
        coordinate = min(max(z + distance / spacing, 0.), len(image)-1.)
        low = int(np.floor(coordinate))
        high = min(low+1, len(image)-1)
        fraction = coordinate-low
        # Match the float32 arithmetic contract; coordinates independently derived.
        output.append(image[low]*(1-fraction) + image[high]*fraction)
    return np.ascontiguousarray(output, dtype=np.float32)


def tile_locations(shape, size=128, stride=96):
    axes = []
    for n in shape:
        assert n >= size
        starts, at = [], 0
        while at <= n-size:
            starts.append(at)
            at += stride
        if starts[-1] != n-size:
            starts.append(n-size)
        axes.append(starts)
    return axes, [(r, c) for r in axes[0] for c in axes[1]]


def grid_context_reference(features, location, shape, size=128):
    rows = (np.arange(size)+location[0]+.5)*features.shape[-2]/shape[0]-.5
    cols = (np.arange(size)+location[1]+.5)*features.shape[-1]/shape[1]-.5
    rr, cc = np.meshgrid(rows, cols, indexing='ij')
    return bilinear(features, rr, cc).astype(np.float32)
