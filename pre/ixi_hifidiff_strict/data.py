from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset

from ixi_diffusion.common import load_nifti, normalize_volume, read_case_ids

from .settings import IXI_ROOT


def to_model_space(image: np.ndarray) -> np.ndarray:
    return (image.astype(np.float32) * 2.0) - 1.0


def from_model_space(image: np.ndarray) -> np.ndarray:
    return np.clip((image.astype(np.float32) + 1.0) * 0.5, 0.0, 1.0)


class VolumeCache:
    def __init__(self, max_items: int = 4):
        self.max_items = max_items
        self._cache: OrderedDict[Path, np.ndarray] = OrderedDict()

    def get(self, path: Path) -> np.ndarray:
        if path in self._cache:
            value = self._cache.pop(path)
            self._cache[path] = value
            return value
        volume, _, _ = load_nifti(path)
        norm, _, _ = normalize_volume(volume)
        self._cache[path] = norm
        while len(self._cache) > self.max_items:
            self._cache.popitem(last=False)
        return norm


class IXIHiFiSliceDataset(Dataset):
    def __init__(
        self,
        split: str,
        modality: str,
        stride: int,
        target_size: int,
        case_limit: int | None = None,
        seed: int = 3407,
    ):
        self.split = split
        self.modality = modality
        self.stride = stride
        self.target_shape = (target_size, target_size)
        self.cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
        split_path = IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt"
        self.case_ids = read_case_ids(split_path, case_limit)
        self.items: list[tuple[Path, int, int, int]] = []
        for case_id in self.case_ids:
            row = self.cases[self.cases["case_id"] == case_id].iloc[0]
            path = Path(row[f"{modality}_path"])
            depth = int(str(row[f"{modality}_shape"]).split("x")[2])
            for z in range(0, depth - stride):
                for offset in range(1, stride):
                    self.items.append((path, z, offset, depth))
        self.cache = VolumeCache(max_items=4)
        print(
            f"IXI strict HiFi {split}: modality={modality}, cases={len(self.case_ids)}, "
            f"samples={len(self.items)}, stride={stride}, target={self.target_shape}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, z, offset, _depth = self.items[index]
        volume = self.cache.get(path)
        left = resize(volume[:, :, z], self.target_shape, preserve_range=True, anti_aliasing=True)
        right = resize(volume[:, :, z + self.stride], self.target_shape, preserve_range=True, anti_aliasing=True)
        target = resize(volume[:, :, z + offset], self.target_shape, preserve_range=True, anti_aliasing=True)
        offset_value = np.array([float(offset) / float(self.stride)], dtype=np.float32)
        cond = np.stack([to_model_space(left), to_model_space(right)], axis=0).astype(np.float32)
        return {
            "cond": torch.from_numpy(cond),
            "target": torch.from_numpy(to_model_space(target)[None, :, :]),
            "offset": torch.from_numpy(offset_value),
        }


def case_paths(split: str, modality: str, limit: int | None, seed: int = 3407) -> list[Path]:
    cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
    ids = read_case_ids(IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt", limit)
    paths: list[Path] = []
    for case_id in ids:
        row = cases[cases["case_id"] == case_id].iloc[0]
        paths.append(Path(row[f"{modality}_path"]))
    return paths
