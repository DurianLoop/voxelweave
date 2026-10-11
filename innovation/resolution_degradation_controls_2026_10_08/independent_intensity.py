"""Separately written intensity reference; no import/call into production augmentation.

Each transform returns float32, as required by the frozen production interface.
Statistics use float64 accumulators as a numerical reference. The seeded normal
draws intentionally share NumPy's documented PCG64/float32-normal convention;
this is not an independently implemented random-number generator.
"""
import numpy as np


def apply_reference(image, primitive):
    assert image.dtype == np.float32 and image.ndim == 3
    result = np.ascontiguousarray(image).copy()
    if primitive['gamma_enabled']:
        minimum = float(np.min(result))
        width = float(np.max(result)) - minimum
        mean = float(np.sum(result, dtype=np.float64) / result.size)
        centered = result.astype(np.float64) - mean
        deviation = float(np.sqrt(np.sum(centered * centered) / result.size))
        if width > 0 and deviation > 0:
            normalized = ((result - minimum) / width).astype(np.float32)
            powered = np.power(normalized, primitive['gamma']).astype(np.float32)
            powered_mean = float(np.sum(powered, dtype=np.float64) / powered.size)
            residual = powered.astype(np.float64) - powered_mean
            powered_sd = float(np.sqrt(np.sum(residual * residual) / powered.size))
            if powered_sd > 0:
                result = ((powered - powered_mean) * (deviation / powered_sd) + mean).astype(np.float32)
    if primitive['bias_enabled']:
        coefficients = np.asarray(primitive['bias_coefficients'], dtype=np.float32)
        positions = [((2 * np.arange(n, dtype=np.float64) / (n - 1) - 1)
                      if n > 1 else np.array([-1.], dtype=np.float64)).astype(np.float32)
                     for n in result.shape]
        # Keep the specified float32 field and exponential before multiplying.
        field = (coefficients[0] * positions[0][:, None, None]
                 + coefficients[1] * positions[1][None, :, None]
                 + coefficients[2] * positions[2][None, None, :])
        result = (result * np.exp(field)).astype(np.float32)
    if primitive['noise_enabled']:
        generator = np.random.Generator(np.random.PCG64(int(primitive['noise_seed'])))
        draws = generator.standard_normal(size=result.shape, dtype=np.float32)
        result = (result + draws * primitive['noise_std']).astype(np.float32)
    assert result.dtype == np.float32 and np.isfinite(result).all()
    return result
