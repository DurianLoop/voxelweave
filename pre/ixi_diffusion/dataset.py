from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


def _linear_coarse(left: np.ndarray, right: np.ndarray, left_z: int, right_z: int, target_z: int) -> np.ndarray:
    denom = max(float(right_z - left_z), 1.0)
    weight = float(target_z - left_z) / denom
    return ((1.0 - weight) * left + weight * right).astype(np.float32)


class IXIResidualDataset(Dataset):
    def __init__(self, root: Path, split: str):
        self.root = Path(root)
        self.split = split
        self.files = sorted((self.root / split).glob("*.npz"))
        if not self.files:
            raise FileNotFoundError(f"No npz samples found in {self.root / split}")

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, idx: int):
        path = self.files[idx]
        with np.load(path, allow_pickle=False) as item:
            inputs = item["input"].astype(np.float32)
            target = item["target"].astype(np.float32)[0]
            left_z = int(item["left_z"])
            right_z = int(item["right_z"])
            target_z = int(item["target_z"])

        left, right = inputs[0], inputs[1]
        coarse = _linear_coarse(left, right, left_z, right_z, target_z)
        rel = float(target_z - left_z) / max(float(right_z - left_z), 1.0)
        rel_map = np.full_like(coarse, rel, dtype=np.float32)

        residual = np.clip(target - coarse, -1.0, 1.0)
        residual01 = ((residual + 1.0) * 0.5).astype(np.float32)

        cond = np.stack([left, right, coarse, rel_map], axis=0).astype(np.float32)
        return {
            "cond": torch.from_numpy(cond),
            "residual01": torch.from_numpy(residual01[None, :, :]),
            "coarse": torch.from_numpy(coarse[None, :, :]),
            "target": torch.from_numpy(target[None, :, :]),
            "name": path.stem,
        }
