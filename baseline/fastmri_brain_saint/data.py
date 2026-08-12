from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset

from ixi_diffusion.common import load_nifti, read_case_ids
from ixi_diffusion.data import VolumeCache

from .settings import INDEX_PATH, SPLIT_ROOT


def load_index() -> pd.DataFrame:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"{INDEX_PATH} does not exist. Run: python -B -m processing.fastmri_brain_nifti_index"
        )
    return pd.read_csv(INDEX_PATH)


def split_case_ids(split: str, limit: int | None = None) -> list[str]:
    path = SPLIT_ROOT / f"{split}_cases.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist. Run: python -B -m processing.fastmri_brain_nifti_index"
        )
    return read_case_ids(path, limit)


def case_paths(split: str, limit: int | None = None) -> list[Path]:
    cases = load_index()
    lookup: dict[str, list[Path]] = {}
    for _, row in cases.iterrows():
        lookup.setdefault(str(row["case_id"]), []).append(Path(str(row["nifti_path"])))
    out = []
    for case_id in split_case_ids(split, limit):
        if case_id in lookup:
            out.extend(lookup[case_id])
    return out


class FastMRIBrainSAINTDataset(Dataset):
    """SAINT-style neighboring-slice dataset for prepared fastMRI brain NIfTI volumes."""

    def __init__(
        self,
        split: str,
        stride: int = 4,
        case_limit: int | None = None,
        target_shape: tuple[int, int] = (256, 256),
    ):
        self.split = split
        self.stride = stride
        self.target_shape = target_shape
        self.paths = case_paths(split, case_limit)
        self.items: list[tuple[Path, str, int, int, int]] = []
        for path in self.paths:
            volume, _, _ = load_nifti(path)
            depth = int(volume.shape[2])
            if depth <= stride:
                continue
            case_id = path.name.removesuffix(".nii.gz")
            for z in range(0, depth - stride):
                for offset in range(1, stride):
                    self.items.append((path, case_id, z, offset, depth))
        yy = np.linspace(-1.0, 1.0, target_shape[0], dtype=np.float32)[:, None]
        xx = np.linspace(-1.0, 1.0, target_shape[1], dtype=np.float32)[None, :]
        self.y_map = np.repeat(yy, target_shape[1], axis=1)
        self.x_map = np.repeat(xx, target_shape[0], axis=0)
        self.cache = VolumeCache(max_items=4)
        print(
            f"fastMRI-brain SAINT {split}: cases={len(self.paths)}, samples={len(self.items)}, stride={stride}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, _case_id, z, offset, depth = self.items[index]
        volume = self.cache.get(path)
        left = resize(volume[:, :, z], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
        right = resize(volume[:, :, z + self.stride], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
        target = resize(
            volume[:, :, z + offset],
            self.target_shape,
            preserve_range=True,
            anti_aliasing=True,
        ).astype(np.float32)
        rel = float(offset) / float(self.stride)
        z_abs = float(z + offset) / max(float(depth - 1), 1.0)
        cond = np.stack(
            [
                left,
                right,
                np.full(self.target_shape, rel, dtype=np.float32),
                np.full(self.target_shape, z_abs, dtype=np.float32),
                self.y_map,
                self.x_map,
            ],
            axis=0,
        ).astype(np.float32)
        return {
            "cond": torch.from_numpy(cond),
            "target": torch.from_numpy(target[None, :, :]),
            "coarse": torch.from_numpy(((1.0 - rel) * left + rel * right)[None, :, :].astype(np.float32)),
        }
