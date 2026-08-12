from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset

from ixi_diffusion.common import load_nifti, normalize_volume, read_case_ids
from ixi_diffusion.settings import IXI_ROOT

from .settings import Profile


class VolumeCache:
    def __init__(self, max_items: int = 3, target_shape: tuple[int, int] | None = None):
        self.max_items = max_items
        self.target_shape = target_shape
        self._cache: dict[Path, np.ndarray] = {}
        self._order: list[Path] = []

    def get(self, path: Path) -> np.ndarray:
        if path in self._cache:
            self._order.remove(path)
            self._order.append(path)
            return self._cache[path]
        volume, _, _ = load_nifti(path)
        norm, _, _ = normalize_volume(volume)
        if self.target_shape is not None:
            norm = np.stack(
                [
                    resize(norm[:, :, idx], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
                    for idx in range(norm.shape[2])
                ],
                axis=-1,
            )
        self._cache[path] = norm
        self._order.append(path)
        while len(self._order) > self.max_items:
            old = self._order.pop(0)
            self._cache.pop(old, None)
        return norm


class IXII3NetWindowDataset(Dataset):
    """Consecutive HR slice windows matching the original I3Net train target."""

    def __init__(self, split: str, profile: Profile, seed: int = 3407):
        self.split = split
        self.profile = profile
        self.target_shape = profile.target_shape
        self.cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
        limit = profile.train_cases if split == "train" else profile.val_cases
        case_ids = read_case_ids(IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt", limit)
        self.items: list[tuple[Path, str, int]] = []
        for case_id in case_ids:
            row = self.cases[self.cases["case_id"] == case_id].iloc[0]
            path = Path(row[f"{profile.modality}_path"])
            depth = int(str(row[f"{profile.modality}_shape"]).split("x")[2])
            max_start = depth - profile.hr_slice_patch
            if max_start < 0:
                continue
            for z in range(0, max_start + 1, max(1, profile.window_step)):
                self.items.append((path, case_id, z))
        self.cache = VolumeCache(
            max_items=profile.cache_items,
            target_shape=self.target_shape if profile.cache_resized_volumes else None,
        )
        print(
            f"IXI I3Net {split}: modality={profile.modality}, cases={len(case_ids)}, "
            f"windows={len(self.items)}, hr_patch={profile.hr_slice_patch}, step={profile.window_step}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> torch.Tensor:
        path, _case_id, z = self.items[index]
        volume = self.cache.get(path)
        if self.profile.cache_resized_volumes:
            window = volume[:, :, z : z + self.profile.hr_slice_patch].astype(np.float32, copy=False)
        else:
            slices = []
            for offset in range(self.profile.hr_slice_patch):
                slice_ = resize(
                    volume[:, :, z + offset],
                    self.target_shape,
                    preserve_range=True,
                    anti_aliasing=True,
                )
                slices.append(slice_.astype(np.float32))
            window = np.stack(slices, axis=-1)
        return torch.from_numpy(window)
