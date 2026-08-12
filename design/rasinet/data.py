from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import numpy as np
import torch
from skimage.transform import resize
from torch.utils.data import Dataset
from tqdm import tqdm

from ixi_diffusion.common import load_nifti, normalize_volume
from ixi_diffusion.data import case_paths


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


def build_rasinet_condition(
    left: np.ndarray,
    right: np.ndarray,
    stride: int,
    target_shape: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    coarse_slices = []
    phase_maps = []
    for offset in range(1, stride):
        rel = float(offset) / float(stride)
        coarse_slices.append(((1.0 - rel) * left + rel * right).astype(np.float32))
        phase_maps.append(np.full(target_shape, rel, dtype=np.float32))
    diff = (right - left).astype(np.float32)
    cond = np.stack(
        [left, right, *coarse_slices, *phase_maps, diff, np.abs(diff).astype(np.float32)],
        axis=0,
    ).astype(np.float32)
    return cond, np.stack(coarse_slices, axis=0).astype(np.float32)


class RASIGroupInterpolationDataset(Dataset):
    def __init__(
        self,
        split: str,
        modality: str,
        stride: int = 4,
        case_limit: int | None = None,
        target_shape: tuple[int, int] = (256, 256),
        window_step: int = 1,
    ):
        if stride < 2:
            raise ValueError("RASI-Net requires stride >= 2")
        self.split = split
        self.modality = modality
        self.stride = stride
        self.target_shape = target_shape
        self.window_step = max(1, int(window_step))
        self.paths = case_paths(split, modality, case_limit)
        self.items: list[tuple[Path, int, int]] = []
        self.cache = VolumeCache(max_items=4)
        for path in self.paths:
            volume, _, _ = load_nifti(path)
            depth = int(volume.shape[2])
            for z in range(0, depth - stride, self.window_step):
                self.items.append((path, z, depth))
        print(
            f"IXI {split} RASI group: modality={modality}, cases={len(self.paths)}, "
            f"windows={len(self.items)}, stride={stride}, window_step={self.window_step}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, z, _depth = self.items[index]
        volume = self.cache.get(path)
        left = resize(volume[:, :, z], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
        right = resize(volume[:, :, z + self.stride], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
        target = np.stack(
            [
                resize(volume[:, :, z + offset], self.target_shape, preserve_range=True, anti_aliasing=True)
                for offset in range(1, self.stride)
            ],
            axis=0,
        ).astype(np.float32)
        cond, coarse = build_rasinet_condition(left, right, self.stride, self.target_shape)
        return {
            "cond": torch.from_numpy(cond),
            "coarse": torch.from_numpy(coarse),
            "target": torch.from_numpy(target),
        }


class CachedRASIGroupInterpolationDataset(Dataset):
    def __init__(
        self,
        split: str,
        modality: str,
        stride: int = 4,
        case_limit: int | None = None,
        target_shape: tuple[int, int] = (256, 256),
        window_step: int = 1,
    ):
        if stride < 2:
            raise ValueError("RASI-Net requires stride >= 2")
        self.split = split
        self.modality = modality
        self.stride = stride
        self.target_shape = target_shape
        self.window_step = max(1, int(window_step))
        self.volumes: list[np.ndarray] = []
        self.items: list[tuple[int, int, int]] = []
        paths = case_paths(split, modality, case_limit)
        print(f"IXI {split} cached RASI group: loading/resizing {len(paths)} cases...")
        for case_index, path in enumerate(tqdm(paths, desc=f"RASI-cache-{split}")):
            volume, _, _ = load_nifti(path)
            norm, _, _ = normalize_volume(volume)
            depth = int(norm.shape[2])
            resized = np.empty((depth, *target_shape), dtype=np.float16)
            for z in range(depth):
                resized[z] = resize(norm[:, :, z], target_shape, preserve_range=True, anti_aliasing=True).astype(np.float16)
            self.volumes.append(resized)
            for z in range(0, depth - stride, self.window_step):
                self.items.append((case_index, z, depth))
        print(
            f"IXI {split} cached RASI group: modality={modality}, cases={len(paths)}, "
            f"windows={len(self.items)}, stride={stride}, window_step={self.window_step}, cache_gb={self.cache_gb:.2f}"
        )

    @property
    def cache_gb(self) -> float:
        return sum(volume.nbytes for volume in self.volumes) / 1024**3

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        case_index, z, _depth = self.items[index]
        volume = self.volumes[case_index]
        left = volume[z].astype(np.float32, copy=False)
        right = volume[z + self.stride].astype(np.float32, copy=False)
        target = np.stack(
            [volume[z + offset].astype(np.float32, copy=False) for offset in range(1, self.stride)],
            axis=0,
        ).astype(np.float32)
        cond, coarse = build_rasinet_condition(left, right, self.stride, self.target_shape)
        return {
            "cond": torch.from_numpy(cond),
            "coarse": torch.from_numpy(coarse),
            "target": torch.from_numpy(target),
        }
