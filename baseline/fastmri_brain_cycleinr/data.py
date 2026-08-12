from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset

from ixi_arssr.inference import _densify_sparse
from ixi_diffusion.common import load_nifti, normalize_volume, read_case_ids

from .settings import INDEX_PATH, SPLIT_ROOT


def load_index() -> pd.DataFrame:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"{INDEX_PATH} does not exist. Check CycleINR DATA_ROOT.")
    return pd.read_csv(INDEX_PATH)


def split_case_ids(split: str, limit: int | None = None) -> list[str]:
    path = SPLIT_ROOT / f"{split}_cases.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Check split root {SPLIT_ROOT}.")
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


def _resize_volume(volume: np.ndarray, shape: tuple[int, int] = (256, 256)) -> np.ndarray:
    slices = [
        resize(volume[:, :, z], shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
        for z in range(volume.shape[2])
    ]
    return np.stack(slices, axis=0)


def _coords_from_indices(z: np.ndarray, y: np.ndarray, x: np.ndarray, shape: tuple[int, int, int]) -> np.ndarray:
    return np.stack(
        [
            x.astype(np.float32) / max(shape[2] - 1, 1) * 2.0 - 1.0,
            y.astype(np.float32) / max(shape[1] - 1, 1) * 2.0 - 1.0,
            z.astype(np.float32) / max(shape[0] - 1, 1) * 2.0 - 1.0,
        ],
        axis=1,
    ).astype(np.float32)


def _sample_volume_coords(hr: np.ndarray, samples: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    total = hr.shape[0] * hr.shape[1] * hr.shape[2]
    flat = rng.choice(total, size=min(samples, total), replace=False)
    z = flat // (hr.shape[1] * hr.shape[2])
    rem = flat % (hr.shape[1] * hr.shape[2])
    y = rem // hr.shape[2]
    x = rem % hr.shape[2]
    return _coords_from_indices(z, y, x, hr.shape), hr[z, y, x].astype(np.float32)[:, None]


def _sample_sparse_cycle_coords(
    hr: np.ndarray,
    stride: int,
    samples: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    observed_z = np.arange(0, hr.shape[0], stride, dtype=np.int64)
    total = len(observed_z) * hr.shape[1] * hr.shape[2]
    flat = rng.choice(total, size=min(samples, total), replace=False)
    z_index = flat // (hr.shape[1] * hr.shape[2])
    rem = flat % (hr.shape[1] * hr.shape[2])
    y = rem // hr.shape[2]
    x = rem % hr.shape[2]
    z = observed_z[z_index]
    return _coords_from_indices(z, y, x, hr.shape), hr[z, y, x].astype(np.float32)[:, None]


class FastMRICycleINRDataset(Dataset):
    def __init__(
        self,
        split: str,
        stride: int = 4,
        case_limit: int | None = None,
        chunks_per_volume: int = 1,
        samples_per_chunk: int = 2048,
        cycle_samples_per_chunk: int = 1024,
        target_shape: tuple[int, int] = (256, 256),
    ):
        self.split = split
        self.stride = stride
        self.chunks_per_volume = chunks_per_volume
        self.samples_per_chunk = samples_per_chunk
        self.cycle_samples_per_chunk = cycle_samples_per_chunk
        self.target_shape = target_shape
        self.paths = case_paths(split, case_limit)
        self.items = [(path, chunk) for path in self.paths for chunk in range(chunks_per_volume)]
        print(
            f"fastMRI CycleINR {split}: cases={len(self.paths)}, items={len(self.items)}, "
            f"stride={stride}, samples={samples_per_chunk}, cycle={cycle_samples_per_chunk}"
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
        sparse = hr[:: self.stride]
        lr_dense = _densify_sparse(sparse, self.stride)

        rng = np.random.default_rng(abs(hash((str(path), chunk, "cycleinr"))) % (2**32))
        coords, values = _sample_volume_coords(hr, self.samples_per_chunk, rng)
        cycle_coords, cycle_values = _sample_sparse_cycle_coords(hr, self.stride, self.cycle_samples_per_chunk, rng)
        return {
            "volume": torch.from_numpy(lr_dense[None].astype(np.float32)),
            "coords": torch.from_numpy(coords),
            "values": torch.from_numpy(values),
            "cycle_coords": torch.from_numpy(cycle_coords),
            "cycle_values": torch.from_numpy(cycle_values),
        }


def validation_batches(
    split: str,
    stride: int,
    case_limit: int | None,
    samples: int,
    target_shape: tuple[int, int] = (256, 256),
) -> list[dict[str, torch.Tensor]]:
    rows = []
    for path in case_paths(split, case_limit):
        volume, _, _ = load_nifti(path)
        norm, _, _ = normalize_volume(volume)
        hr = _resize_volume(norm, target_shape)
        full_depth = ((hr.shape[0] - 1) // stride) * stride + 1
        hr = hr[:full_depth]
        sparse = hr[::stride]
        lr_dense = _densify_sparse(sparse, stride)
        rng = np.random.default_rng(abs(hash((str(path), "val-cycleinr"))) % (2**32))
        coords, values = _sample_volume_coords(hr, samples, rng)
        rows.append(
            {
                "volume": torch.from_numpy(lr_dense[None].astype(np.float32)).unsqueeze(0),
                "coords": torch.from_numpy(coords).unsqueeze(0),
                "values": torch.from_numpy(values).unsqueeze(0),
            }
        )
    return rows
