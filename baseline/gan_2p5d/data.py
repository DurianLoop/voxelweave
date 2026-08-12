from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from skimage.transform import resize
from torch.utils.data import Dataset


def normalize_volume(volume: np.ndarray) -> tuple[np.ndarray, float, float]:
    values = volume.astype(np.float32)
    lo = float(np.nanmin(values))
    hi = float(np.nanmax(values))
    if hi <= lo:
        return np.zeros_like(values, dtype=np.float32), lo, hi
    return ((values - lo) / (hi - lo + 1e-8)).astype(np.float32), lo, hi


def make_gan_sample(
    volume: np.ndarray,
    z: int,
    stride: int = 4,
    target_shape: tuple[int, int] = (256, 256),
) -> tuple[np.ndarray, np.ndarray]:
    if stride < 2:
        raise ValueError(f"stride must be at least 2, got {stride}")
    if z < 0 or z + stride >= volume.shape[2]:
        raise IndexError(f"z={z} is outside valid x4 range for depth={volume.shape[2]}")

    def resize_slice(slice_2d: np.ndarray) -> np.ndarray:
        if tuple(slice_2d.shape) == tuple(target_shape):
            return slice_2d.astype(np.float32, copy=False)
        return resize(slice_2d, target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)

    left = resize_slice(volume[:, :, z])
    right = resize_slice(volume[:, :, z + stride])
    targets = []
    for offset in range(1, stride):
        targets.append(resize_slice(volume[:, :, z + offset]))
    z_pos = (z + stride / 2.0) / max(volume.shape[2] - 1, 1)
    relative_positions = [offset / float(stride) for offset in range(1, stride)]
    cond = np.stack(
        [
            left,
            right,
            np.full(target_shape, z_pos, dtype=np.float32),
            *[np.full(target_shape, pos, dtype=np.float32) for pos in relative_positions],
        ],
        axis=0,
    )
    return cond, np.stack(targets, axis=0).astype(np.float32)


class VolumeCache:
    def __init__(self, loader, max_items: int = 4):
        self.loader = loader
        self.max_items = max_items
        self._cache: OrderedDict[Path, np.ndarray] = OrderedDict()

    def get(self, path: Path) -> np.ndarray:
        if path in self._cache:
            value = self._cache.pop(path)
            self._cache[path] = value
            return value
        volume = self.loader(path)
        norm, _, _ = normalize_volume(volume)
        self._cache[path] = norm
        while len(self._cache) > self.max_items:
            self._cache.popitem(last=False)
        return norm


class GANMultiSliceDataset(Dataset):
    def __init__(
        self,
        paths: Sequence[Path],
        loader,
        stride: int = 4,
        target_shape: tuple[int, int] = (256, 256),
        max_cache_items: int = 4,
    ):
        self.paths = [Path(path) for path in paths]
        self.loader = loader
        self.stride = stride
        self.target_shape = target_shape
        self.items: list[tuple[Path, int]] = []
        for path in self.paths:
            volume = loader(path)
            for z in range(0, int(volume.shape[2]) - stride):
                self.items.append((path, z))
        self.cache = VolumeCache(loader, max_items=max_cache_items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        path, z = self.items[index]
        volume = self.cache.get(path)
        cond, target = make_gan_sample(volume, z=z, stride=self.stride, target_shape=self.target_shape)
        return torch.from_numpy(cond), torch.from_numpy(target)
