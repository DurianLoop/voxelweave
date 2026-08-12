from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset
from tqdm import tqdm

from ixi_diffusion.common import load_nifti, normalize_volume, read_case_ids

from .settings import DATASET_NAME, INDEX_PATH, SPLIT_ROOT


def load_index() -> pd.DataFrame:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"{INDEX_PATH} does not exist. Check DATA_ROOT={SPLIT_ROOT.parent.parent}.")
    return pd.read_csv(INDEX_PATH)


def split_case_ids(split: str, limit: int | None = None) -> list[str]:
    path = SPLIT_ROOT / f"{split}_cases.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Check DATA_ROOT={SPLIT_ROOT.parent.parent}.")
    return read_case_ids(path, limit)


def case_paths(split: str, limit: int | None = None) -> list[Path]:
    cases = load_index()
    lookup: dict[str, list[Path]] = {}
    for _, row in cases.iterrows():
        lookup.setdefault(str(row["case_id"]), []).append(Path(str(row["nifti_path"])))
    out: list[Path] = []
    for case_id in split_case_ids(split, limit):
        out.extend(lookup.get(case_id, []))
    return out


class CachedFastMRISingleSliceInterpolationDataset(Dataset):
    def __init__(self, split: str, stride: int = 4, case_limit: int | None = None, target_shape: tuple[int, int] = (256, 256)):
        self.split = split
        self.stride = stride
        self.target_shape = target_shape
        self.volumes: list[np.ndarray] = []
        self.items: list[tuple[int, int, int]] = []
        paths = case_paths(split, case_limit)
        print(f"{DATASET_NAME} {split} cached single-slice: loading/resizing {len(paths)} cases...")
        for case_index, path in enumerate(tqdm(paths, desc=f"ResSRDiff-cache-{split}")):
            volume, _, _ = load_nifti(path)
            norm, _, _ = normalize_volume(volume)
            depth = int(norm.shape[2])
            resized = np.empty((depth, *target_shape), dtype=np.float16)
            for z in range(depth):
                resized[z] = resize(norm[:, :, z], target_shape, preserve_range=True, anti_aliasing=True).astype(np.float16)
            self.volumes.append(resized)
            for z in range(0, depth - stride):
                for offset in range(1, stride):
                    self.items.append((case_index, z, offset))
        print(
            f"{DATASET_NAME} {split} cached single-slice: cases={len(paths)}, samples={len(self.items)}, "
            f"stride={stride}, cache_gb={self.cache_gb:.2f}"
        )

    @property
    def cache_gb(self) -> float:
        return sum(volume.nbytes for volume in self.volumes) / 1024**3

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        case_index, z, offset = self.items[index]
        volume = self.volumes[case_index]
        left = volume[z].astype(np.float32, copy=False)
        right = volume[z + self.stride].astype(np.float32, copy=False)
        target = volume[z + offset].astype(np.float32, copy=False)
        rel = float(offset) / float(self.stride)
        coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
        return {
            "coarse": torch.from_numpy(coarse[None, :, :]),
            "target": torch.from_numpy(target[None, :, :]),
        }
