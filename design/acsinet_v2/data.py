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


def build_acsi_v2_condition(window: np.ndarray, profile: Profile) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build v2 condition from an HR window shaped H x W x D."""
    hr_depth = profile.hr_slice_patch
    anchor_indices = list(range(0, hr_depth, profile.stride))
    anchors = [window[:, :, idx].astype(np.float32) for idx in anchor_indices]

    coarse = np.empty((*window.shape[:2], hr_depth), dtype=np.float32)
    for left_i, right_i in zip(anchor_indices[:-1], anchor_indices[1:]):
        left = window[:, :, left_i].astype(np.float32)
        right = window[:, :, right_i].astype(np.float32)
        for idx in range(left_i, right_i + 1):
            rel = float(idx - left_i) / float(right_i - left_i)
            coarse[:, :, idx] = (1.0 - rel) * left + rel * right

    phases = np.zeros((*window.shape[:2], hr_depth), dtype=np.float32)
    for idx in range(hr_depth):
        phases[:, :, idx] = float(idx) / float(hr_depth - 1)

    diffs = []
    absdiffs = []
    for left, right in zip(anchors[:-1], anchors[1:]):
        diff = (right - left).astype(np.float32)
        diffs.append(diff)
        absdiffs.append(np.abs(diff).astype(np.float32))

    cond = np.stack([*anchors, *np.moveaxis(coarse, -1, 0), *np.moveaxis(phases, -1, 0), *diffs, *absdiffs], axis=0)
    gen_mask = np.ones((hr_depth,), dtype=np.float32)
    gen_mask[anchor_indices] = 0.0
    return cond.astype(np.float32), np.moveaxis(coarse, -1, 0).astype(np.float32), gen_mask


class ACSIV2WindowDataset(Dataset):
    """I3Net-aligned 4 sparse anchors -> 13 HR window dataset."""

    def __init__(self, split: str, profile: Profile, seed: int = 3407):
        self.split = split
        self.profile = profile
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
            target_shape=profile.target_shape if profile.cache_resized_volumes else None,
        )
        print(
            f"IXI {split} ACSI-v2: modality={profile.modality}, cases={len(case_ids)}, "
            f"windows={len(self.items)}, anchors={profile.lr_slice_patch}, hr_patch={profile.hr_slice_patch}, "
            f"step={profile.window_step}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, _case_id, z = self.items[index]
        volume = self.cache.get(path)
        if self.profile.cache_resized_volumes:
            window = volume[:, :, z : z + self.profile.hr_slice_patch].astype(np.float32, copy=False)
        else:
            slices = []
            for offset in range(self.profile.hr_slice_patch):
                slices.append(
                    resize(
                        volume[:, :, z + offset],
                        self.profile.target_shape,
                        preserve_range=True,
                        anti_aliasing=True,
                    ).astype(np.float32)
                )
            window = np.stack(slices, axis=-1)
        cond, coarse, gen_mask = build_acsi_v2_condition(window, self.profile)
        target = np.moveaxis(window, -1, 0).astype(np.float32)
        return {
            "cond": torch.from_numpy(cond),
            "coarse": torch.from_numpy(coarse),
            "target": torch.from_numpy(target),
            "gen_mask": torch.from_numpy(gen_mask),
        }
