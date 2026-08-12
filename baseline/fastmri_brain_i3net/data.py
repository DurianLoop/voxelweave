from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset

from ixi_diffusion.common import load_nifti, normalize_volume, read_case_ids

from .settings import DATASET_NAME, INDEX_PATH, SPLIT_ROOT, Profile


def load_index() -> pd.DataFrame:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"{INDEX_PATH} does not exist. Run fastMRI-brain-T2 prepare/index first.")
    return pd.read_csv(INDEX_PATH)


def split_case_ids(split: str, limit: int | None = None) -> list[str]:
    path = SPLIT_ROOT / f"{split}_cases.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Check DATA_ROOT={SPLIT_ROOT.parent.parent}")
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


class FastMRII3NetWindowDataset(Dataset):
    def __init__(self, split: str, profile: Profile):
        self.split = split
        self.profile = profile
        self.target_shape = profile.target_shape
        limit = profile.train_cases if split == "train" else profile.val_cases
        self.paths = case_paths(split, limit)
        self.items: list[tuple[Path, int]] = []
        for path in self.paths:
            volume, _, _ = load_nifti(path)
            depth = int(volume.shape[2])
            max_start = depth - profile.hr_slice_patch
            if max_start < 0:
                continue
            for z in range(0, max_start + 1, max(1, profile.window_step)):
                self.items.append((path, z))
        self.cache = VolumeCache(max_items=4)
        print(
            f"{DATASET_NAME} I3Net {split}: cases={len(self.paths)}, windows={len(self.items)}, "
            f"hr_patch={profile.hr_slice_patch}, step={profile.window_step}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> torch.Tensor:
        path, z = self.items[index]
        volume = self.cache.get(path)
        slices = []
        for offset in range(self.profile.hr_slice_patch):
            slice_ = resize(
                volume[:, :, z + offset],
                self.target_shape,
                preserve_range=True,
                anti_aliasing=True,
            )
            slices.append(slice_.astype(np.float32))
        return torch.from_numpy(np.stack(slices, axis=-1))
