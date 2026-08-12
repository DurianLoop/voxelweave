from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from gan_2p5d.data import normalize_volume

from .settings import ROOT


IXI_ROOT = ROOT / "dataset" / "IXI"


def read_case_ids(path: Path, limit: int | None = None) -> list[str]:
    ids = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return ids[:limit] if limit is not None else ids


def case_paths(split: str, modality: str, limit: int | None, seed: int = 3407) -> list[Path]:
    cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
    ids = read_case_ids(IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt", limit)
    paths = []
    for case_id in ids:
        row = cases[cases["case_id"] == case_id].iloc[0]
        paths.append(Path(row[f"{modality}_path"]))
    return paths


def prepare_eval_inputs(paths, profile) -> list[dict]:
    from ixi_diffusion.common import ensure_dir, load_nifti, save_nifti

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
    if not manifest:
        raise RuntimeError("No IXI test cases available for evaluation.")
    return manifest
