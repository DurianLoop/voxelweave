from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset

from .common import load_nifti, normalize_volume, read_case_ids
from .settings import IXI_ROOT


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


class IXIInterpolationDataset(Dataset):
    def __init__(
        self,
        split: str,
        modality: str,
        stride: int = 4,
        case_limit: int | None = None,
        seed: int = 3407,
        target_shape: tuple[int, int] = (256, 256),
    ):
        self.split = split
        self.modality = modality
        self.stride = stride
        self.target_shape = target_shape
        self.cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
        split_path = IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt"
        self.case_ids = read_case_ids(split_path, case_limit)
        self.items: list[tuple[Path, str, int, int]] = []
        for case_id in self.case_ids:
            row = self.cases[self.cases["case_id"] == case_id].iloc[0]
            path = Path(row[f"{modality}_path"])
            shape = str(row[f"{modality}_shape"])
            depth = int(shape.split("x")[2])
            for z in range(0, depth - stride):
                self.items.append((path, case_id, z, depth))
        self.cache = VolumeCache(max_items=4)
        print(
            f"IXI {split}: modality={modality}, cases={len(self.case_ids)}, "
            f"pairs={len(self.items)}, stride={stride}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        path, _case_id, z, depth = self.items[index]
        volume = self.cache.get(path)
        left = resize(volume[:, :, z], self.target_shape, preserve_range=True, anti_aliasing=True)
        right = resize(volume[:, :, z + self.stride], self.target_shape, preserve_range=True, anti_aliasing=True)
        target = np.zeros((self.stride - 1, *self.target_shape), dtype=np.float32)
        for offset in range(1, self.stride):
            target[offset - 1] = resize(
                volume[:, :, z + offset],
                self.target_shape,
                preserve_range=True,
                anti_aliasing=True,
            )

        z_pos = (z + self.stride / 2.0) / max(depth - 1, 1)
        cond = np.stack(
            [
                left,
                right,
                np.full(self.target_shape, z_pos, dtype=np.float32),
                np.full(self.target_shape, 0.25, dtype=np.float32),
                np.full(self.target_shape, 0.50, dtype=np.float32),
                np.full(self.target_shape, 0.75, dtype=np.float32),
            ],
            axis=0,
        )
        return torch.from_numpy(cond.astype(np.float32)), torch.from_numpy(target.astype(np.float32))


class IXISingleSliceInterpolationDataset(Dataset):
    def __init__(
        self,
        split: str,
        modality: str,
        stride: int = 4,
        case_limit: int | None = None,
        seed: int = 3407,
        target_shape: tuple[int, int] = (256, 256),
    ):
        self.split = split
        self.modality = modality
        self.stride = stride
        self.target_shape = target_shape
        self.cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
        split_path = IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt"
        self.case_ids = read_case_ids(split_path, case_limit)
        self.items: list[tuple[Path, str, int, int, int]] = []
        for case_id in self.case_ids:
            row = self.cases[self.cases["case_id"] == case_id].iloc[0]
            path = Path(row[f"{modality}_path"])
            shape = str(row[f"{modality}_shape"])
            depth = int(shape.split("x")[2])
            for z in range(0, depth - stride):
                for offset in range(1, stride):
                    self.items.append((path, case_id, z, offset, depth))
        self.cache = VolumeCache(max_items=4)
        print(
            f"IXI {split} single-slice: modality={modality}, cases={len(self.case_ids)}, "
            f"samples={len(self.items)}, stride={stride}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, _case_id, z, offset, _depth = self.items[index]
        volume = self.cache.get(path)
        left = resize(volume[:, :, z], self.target_shape, preserve_range=True, anti_aliasing=True)
        right = resize(volume[:, :, z + self.stride], self.target_shape, preserve_range=True, anti_aliasing=True)
        target = resize(
            volume[:, :, z + offset],
            self.target_shape,
            preserve_range=True,
            anti_aliasing=True,
        )
        rel = float(offset) / float(self.stride)
        coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
        rel_map = np.full(self.target_shape, rel, dtype=np.float32)
        residual = np.clip(target - coarse, -1.0, 1.0).astype(np.float32)
        residual01 = ((residual + 1.0) * 0.5).astype(np.float32)
        cond = np.stack([left, right, coarse, rel_map], axis=0).astype(np.float32)
        return {
            "cond": torch.from_numpy(cond),
            "residual01": torch.from_numpy(residual01[None, :, :]),
            "coarse": torch.from_numpy(coarse[None, :, :]),
            "target": torch.from_numpy(target.astype(np.float32)[None, :, :]),
        }


def case_paths(split: str, modality: str, limit: int | None, seed: int = 3407) -> list[Path]:
    cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
    ids = read_case_ids(IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt", limit)
    paths = []
    for case_id in ids:
        row = cases[cases["case_id"] == case_id].iloc[0]
        paths.append(Path(row[f"{modality}_path"]))
    return paths
