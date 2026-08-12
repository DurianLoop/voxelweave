from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.interpolate import interp1d

from .common import ensure_dir, load_nifti, save_nifti


def _upsample_z(volume: np.ndarray, factor: int, kind: str) -> np.ndarray:
    in_depth = volume.shape[2]
    out_depth = (in_depth - 1) * factor + 1
    z_in = np.arange(in_depth, dtype=np.float32) * factor
    z_out = np.arange(out_depth, dtype=np.float32)
    actual_kind = kind
    if kind == "cubic" and in_depth < 4:
        actual_kind = "linear"
    interpolator = interp1d(z_in, volume, axis=2, kind=actual_kind, bounds_error=False, fill_value="extrapolate")
    return interpolator(z_out).astype(np.float32)


def run_baseline_folder(input_dir: Path, output_dir: Path, factor: int, kind: str) -> int:
    ensure_dir(output_dir)
    count = 0
    for src in sorted(input_dir.glob("*.nii.gz")):
        volume, affine, header = load_nifti(src)
        out = _upsample_z(volume, factor=factor, kind=kind)
        save_nifti(out, affine, header, output_dir / f"{kind}_{src.name}")
        count += 1
    return count
