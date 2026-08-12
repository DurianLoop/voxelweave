from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset

from ixi_diffusion.common import load_nifti, normalize_volume, read_case_ids
from ixi_diffusion.settings import IXI_ROOT


def case_paths(split: str, modality: str, limit: int | None, seed: int = 3407) -> list[Path]:
    cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
    ids = read_case_ids(IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt", limit)
    paths: list[Path] = []
    for case_id in ids:
        row = cases[cases["case_id"] == case_id].iloc[0]
        paths.append(Path(row[f"{modality}_path"]))
    return paths


def _resize_volume(volume: np.ndarray, shape: tuple[int, int] = (128, 128)) -> np.ndarray:
    slices = [
        resize(volume[:, :, z], shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
        for z in range(volume.shape[2])
    ]
    return np.stack(slices, axis=0)


def _make_sparse_lr(hr: np.ndarray, stride: int) -> np.ndarray:
    sparse = hr[::stride]
    depth = sparse.shape[0]
    if depth < 2:
        return sparse
    full_depth = (depth - 1) * stride + 1
    dense = np.zeros((full_depth, hr.shape[1], hr.shape[2]), dtype=np.float32)
    for idx in range(depth):
        dense[idx * stride] = sparse[idx]
    for idx in range(depth - 1):
        left = sparse[idx]
        right = sparse[idx + 1]
        for offset in range(1, stride):
            rel = offset / stride
            dense[idx * stride + offset] = (1.0 - rel) * left + rel * right
    return dense


class IXIArSSRDataset(Dataset):
    """Volume-level coordinate samples for ArSSR-style training.

    Each item contains a linearly densified sparse volume and random coordinates
    from the aligned high-resolution target volume. This keeps the ArSSR
    coordinate-query idea while using the same IXI T2 x4 protocol as the table.
    """

    def __init__(
        self,
        split: str,
        modality: str,
        stride: int = 4,
        case_limit: int | None = None,
        chunks_per_volume: int = 2,
        samples_per_chunk: int = 2048,
        seed: int = 3407,
        target_shape: tuple[int, int] = (256, 256),
    ):
        self.split = split
        self.modality = modality
        self.stride = stride
        self.chunks_per_volume = chunks_per_volume
        self.samples_per_chunk = samples_per_chunk
        self.target_shape = target_shape
        self.paths = case_paths(split, modality, case_limit, seed=seed)
        self.items = [(path, chunk) for path in self.paths for chunk in range(chunks_per_volume)]
        print(
            f"IXI ArSSR {split}: modality={modality}, cases={len(self.paths)}, "
            f"items={len(self.items)}, stride={stride}, samples={samples_per_chunk}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, chunk = self.items[index]
        volume, _, _ = load_nifti(path)
        norm, _, _ = normalize_volume(volume)
        hr = _resize_volume(norm, self.target_shape)
        full_depth = ((hr.shape[0] - 1) // self.stride) * self.stride + 1
        hr = hr[:full_depth]
        lr_dense = _make_sparse_lr(hr, self.stride)

        rng = np.random.default_rng(abs(hash((str(path), chunk))) % (2**32))
        total = hr.shape[0] * hr.shape[1] * hr.shape[2]
        flat = rng.choice(total, size=min(self.samples_per_chunk, total), replace=False)
        z = flat // (hr.shape[1] * hr.shape[2])
        rem = flat % (hr.shape[1] * hr.shape[2])
        y = rem // hr.shape[2]
        x = rem % hr.shape[2]
        coords = np.stack(
            [
                (x.astype(np.float32) / max(hr.shape[2] - 1, 1)) * 2.0 - 1.0,
                (y.astype(np.float32) / max(hr.shape[1] - 1, 1)) * 2.0 - 1.0,
                (z.astype(np.float32) / max(hr.shape[0] - 1, 1)) * 2.0 - 1.0,
            ],
            axis=1,
        ).astype(np.float32)
        values = hr[z, y, x].astype(np.float32)[:, None]
        return {
            "volume": torch.from_numpy(lr_dense[None].astype(np.float32)),
            "coords": torch.from_numpy(coords),
            "values": torch.from_numpy(values),
        }


def validation_batch(
    split: str,
    modality: str,
    stride: int,
    case_limit: int | None,
    samples: int,
    target_shape: tuple[int, int] = (256, 256),
) -> list[dict[str, torch.Tensor]]:
    rows = []
    for path in case_paths(split, modality, case_limit):
        volume, _, _ = load_nifti(path)
        norm, _, _ = normalize_volume(volume)
        hr = _resize_volume(norm, target_shape)
        full_depth = ((hr.shape[0] - 1) // stride) * stride + 1
        hr = hr[:full_depth]
        lr_dense = _make_sparse_lr(hr, stride)
        rng = np.random.default_rng(abs(hash(str(path))) % (2**32))
        total = hr.shape[0] * hr.shape[1] * hr.shape[2]
        flat = rng.choice(total, size=min(samples, total), replace=False)
        z = flat // (hr.shape[1] * hr.shape[2])
        rem = flat % (hr.shape[1] * hr.shape[2])
        y = rem // hr.shape[2]
        x = rem % hr.shape[2]
        coords = np.stack(
            [
                (x.astype(np.float32) / max(hr.shape[2] - 1, 1)) * 2.0 - 1.0,
                (y.astype(np.float32) / max(hr.shape[1] - 1, 1)) * 2.0 - 1.0,
                (z.astype(np.float32) / max(hr.shape[0] - 1, 1)) * 2.0 - 1.0,
            ],
            axis=1,
        ).astype(np.float32)
        values = hr[z, y, x].astype(np.float32)[:, None]
        rows.append(
            {
                "volume": torch.from_numpy(lr_dense[None].astype(np.float32)).unsqueeze(0),
                "coords": torch.from_numpy(coords).unsqueeze(0),
                "values": torch.from_numpy(values).unsqueeze(0),
            }
        )
    return rows
