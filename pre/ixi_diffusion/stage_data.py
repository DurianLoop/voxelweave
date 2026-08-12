from __future__ import annotations

from pathlib import Path

import numpy as np

from .common import ensure_dir, load_nifti, save_nifti
from .data import case_paths
from .settings import Profile, RunPaths


def prepare_eval_inputs(paths: RunPaths, profile: Profile) -> list[dict]:
    ensure_dir(paths.eval_sparse)
    ensure_dir(paths.eval_gt)
    manifest = []
    for src in case_paths("test", profile.modality, profile.test_cases):
        volume, affine, header = load_nifti(src)
        sparse = volume[:, :, :: profile.stride]
        full_depth = (sparse.shape[2] - 1) * profile.stride + 1
        gt = volume[:, :, :full_depth]
        sparse_name = f"{src.stem.replace('.nii', '')}.nii.gz"
        save_nifti(sparse.astype(np.float32), affine, header, paths.eval_sparse / sparse_name)
        save_nifti(gt.astype(np.float32), affine, header, paths.eval_gt / sparse_name)
        manifest.append(
            {
                "case": sparse_name,
                "source": str(src),
                "source_depth": int(volume.shape[2]),
                "sparse_depth": int(sparse.shape[2]),
                "target_depth": int(gt.shape[2]),
                "stride": profile.stride,
            }
        )
    return manifest
