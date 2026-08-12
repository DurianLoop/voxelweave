from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from torch.utils.data import Dataset

from ixi_diffusion.common import load_nifti, normalize_volume, read_case_ids

from .settings import INDEX_PATH, SPLIT_ROOT


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


MA4_ANCHOR_OFFSETS = (0, 4, 8, 12)
MA4_MISSING_OFFSETS = (1, 2, 3, 5, 6, 7, 9, 10, 11)
MA3C_MISSING_OFFSETS = (1, 2, 3)


def _resize_volume_slice(volume: np.ndarray, z: int, target_shape: tuple[int, int]) -> np.ndarray:
    return resize(
        volume[:, :, z],
        target_shape,
        preserve_range=True,
        anti_aliasing=True,
    ).astype(np.float32)


def _ma4_offsets(stride: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    anchor_offsets = tuple(i * stride for i in range(4))
    missing_offsets = tuple(offset for offset in range(anchor_offsets[-1] + 1) if offset % stride != 0)
    return anchor_offsets, missing_offsets


def build_ma4_window_sample(
    volume: np.ndarray,
    z: int,
    stride: int = 4,
    target_shape: tuple[int, int] = (256, 256),
) -> dict[str, np.ndarray]:
    anchor_offsets, missing_offsets = _ma4_offsets(stride)
    anchor_window = np.stack(
        [_resize_volume_slice(volume, z + offset, target_shape) for offset in anchor_offsets],
        axis=0,
    ).astype(np.float32)
    target_window = np.stack(
        [_resize_volume_slice(volume, z + offset, target_shape) for offset in range(anchor_offsets[-1] + 1)],
        axis=0,
    ).astype(np.float32)

    coarse_missing: list[np.ndarray] = []
    phase_maps: list[np.ndarray] = []
    target_missing: list[np.ndarray] = []
    for offset in missing_offsets:
        segment = offset // stride
        rel = float(offset - segment * stride) / float(stride)
        left = anchor_window[segment]
        right = anchor_window[segment + 1]
        coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
        coarse_missing.append(coarse)
        phase_maps.append(np.full(target_shape, rel, dtype=np.float32))
        target_missing.append(target_window[offset])

    coarse_stack = np.stack(coarse_missing, axis=0).astype(np.float32)
    phase_stack = np.stack(phase_maps, axis=0).astype(np.float32)
    target_missing_stack = np.stack(target_missing, axis=0).astype(np.float32)
    cond = np.concatenate([anchor_window, coarse_stack, phase_stack], axis=0).astype(np.float32)
    return {
        "cond_window": cond,
        "anchor_window": anchor_window,
        "coarse_missing": coarse_stack,
        "target_missing": target_missing_stack,
        "target_window": target_window,
    }


class FastMRIMA4WindowInterpolationDataset(Dataset):
    def __init__(
        self,
        split: str,
        stride: int = 4,
        case_limit: int | None = None,
        target_shape: tuple[int, int] = (256, 256),
        window_step: int = 1,
    ):
        self.split = split
        self.stride = stride
        self.target_shape = target_shape
        self.window_step = max(1, window_step)
        self.paths = case_paths(split, case_limit)
        self.anchor_offsets, self.missing_offsets = _ma4_offsets(stride)
        self.hr_slice_patch = self.anchor_offsets[-1] + 1
        self.items: list[tuple[Path, int]] = []
        for path in self.paths:
            volume, _, _ = load_nifti(path)
            depth = int(volume.shape[2])
            max_start = depth - self.hr_slice_patch
            if max_start < 0:
                continue
            for z in range(0, max_start + 1, self.window_step):
                self.items.append((path, z))
        self.cache = VolumeCache(max_items=4)
        print(
            f"fastMRI-brain-T2 {split} MA4-window: cases={len(self.paths)}, "
            f"windows={len(self.items)}, hr_patch={self.hr_slice_patch}, "
            f"stride={stride}, step={self.window_step}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, z = self.items[index]
        sample = build_ma4_window_sample(self.cache.get(path), z, self.stride, self.target_shape)
        return {key: torch.from_numpy(value) for key, value in sample.items()}


def _build_rich_multi_anchor_condition(
    prev_anchor: np.ndarray,
    left: np.ndarray,
    right: np.ndarray,
    next_anchor: np.ndarray,
    coarse: np.ndarray,
    phase: np.ndarray,
    prev_valid_value: float,
    next_valid_value: float,
) -> np.ndarray:
    diff = (right - left).astype(np.float32)
    absdiff = np.abs(diff).astype(np.float32)
    prev_valid = np.full(coarse.shape, prev_valid_value, dtype=np.float32)
    next_valid = np.full(coarse.shape, next_valid_value, dtype=np.float32)
    prev_delta = ((left - prev_anchor) * prev_valid_value).astype(np.float32)
    next_delta = ((next_anchor - right) * next_valid_value).astype(np.float32)
    curvature = (next_delta - prev_delta).astype(np.float32)
    return np.stack(
        [
            prev_anchor,
            left,
            right,
            next_anchor,
            coarse,
            phase,
            diff,
            absdiff,
            prev_valid,
            next_valid,
            prev_delta,
            next_delta,
            curvature,
        ],
        axis=0,
    ).astype(np.float32)


def build_ma3c_interval_sample(
    volume: np.ndarray,
    z: int,
    stride: int = 4,
    target_shape: tuple[int, int] = (256, 256),
) -> dict[str, np.ndarray]:
    depth = int(volume.shape[2])
    left = _resize_volume_slice(volume, z, target_shape)
    right = _resize_volume_slice(volume, z + stride, target_shape)
    prev_idx = z - stride
    next_idx = z + 2 * stride
    prev_valid_value = 1.0 if prev_idx >= 0 else 0.0
    next_valid_value = 1.0 if next_idx < depth else 0.0
    if prev_idx < 0:
        prev_idx = z
    if next_idx >= depth:
        next_idx = z + stride
    prev_anchor = _resize_volume_slice(volume, prev_idx, target_shape)
    next_anchor = _resize_volume_slice(volume, next_idx, target_shape)

    conds: list[np.ndarray] = []
    coarses: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    for offset in MA3C_MISSING_OFFSETS:
        rel = float(offset) / float(stride)
        coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
        phase = np.full(target_shape, rel, dtype=np.float32)
        target = _resize_volume_slice(volume, z + offset, target_shape)
        conds.append(
            _build_rich_multi_anchor_condition(
                prev_anchor,
                left,
                right,
                next_anchor,
                coarse,
                phase,
                prev_valid_value,
                next_valid_value,
            )
        )
        coarses.append(coarse[None, :, :].astype(np.float32))
        targets.append(target[None, :, :].astype(np.float32))

    return {
        "cond_ma_stack": np.stack(conds, axis=0).astype(np.float32),
        "coarse_stack": np.stack(coarses, axis=0).astype(np.float32),
        "target_stack": np.stack(targets, axis=0).astype(np.float32),
        "anchor_pair": np.stack([left[None, :, :], right[None, :, :]], axis=0).astype(np.float32),
    }


class FastMRIMA3CIntervalDataset(Dataset):
    def __init__(
        self,
        split: str,
        stride: int = 4,
        case_limit: int | None = None,
        target_shape: tuple[int, int] = (256, 256),
        window_step: int = 1,
    ):
        self.split = split
        self.stride = stride
        self.target_shape = target_shape
        self.window_step = max(1, window_step)
        self.paths = case_paths(split, case_limit)
        self.items: list[tuple[Path, int]] = []
        for path in self.paths:
            volume, _, _ = load_nifti(path)
            depth = int(volume.shape[2])
            for z in range(0, depth - stride, self.window_step):
                self.items.append((path, z))
        self.cache = VolumeCache(max_items=4)
        print(
            f"fastMRI-brain-T2 {split} MA3C-interval: cases={len(self.paths)}, "
            f"intervals={len(self.items)}, stride={stride}, step={self.window_step}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, z = self.items[index]
        sample = build_ma3c_interval_sample(self.cache.get(path), z, self.stride, self.target_shape)
        return {key: torch.from_numpy(value) for key, value in sample.items()}


class FastMRISingleSliceInterpolationDataset(Dataset):
    def __init__(
        self,
        split: str,
        stride: int = 4,
        case_limit: int | None = None,
        target_shape: tuple[int, int] = (256, 256),
        multi_anchor: bool = False,
        anchor_features: str = "basic",
    ):
        self.split = split
        self.stride = stride
        self.target_shape = target_shape
        self.multi_anchor = multi_anchor
        self.anchor_features = anchor_features
        self.paths = case_paths(split, case_limit)
        self.items: list[tuple[Path, int, int, int]] = []
        for path in self.paths:
            volume, _, _ = load_nifti(path)
            depth = int(volume.shape[2])
            for z in range(0, depth - stride):
                for offset in range(1, stride):
                    self.items.append((path, z, offset, depth))
        self.cache = VolumeCache(max_items=4)
        print(
            f"fastMRI-brain-T2 {split} single-slice: cases={len(self.paths)}, "
            f"samples={len(self.items)}, stride={stride}, multi_anchor={multi_anchor}, "
            f"anchor_features={anchor_features}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, z, offset, depth = self.items[index]
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
        item = {
            "cond": torch.from_numpy(cond),
            "residual01": torch.from_numpy(residual01[None, :, :]),
            "coarse": torch.from_numpy(coarse[None, :, :]),
            "target": torch.from_numpy(target.astype(np.float32)[None, :, :]),
        }
        if self.multi_anchor:
            prev_idx = z - self.stride
            next_idx = z + 2 * self.stride
            prev_valid_value = 1.0 if prev_idx >= 0 else 0.0
            next_valid_value = 1.0 if next_idx < depth else 0.0
            if prev_idx < 0:
                prev_idx = z
            if next_idx >= depth:
                next_idx = z + self.stride
            prev_anchor = resize(volume[:, :, prev_idx], self.target_shape, preserve_range=True, anti_aliasing=True)
            next_anchor = resize(volume[:, :, next_idx], self.target_shape, preserve_range=True, anti_aliasing=True)
            diff = (right - left).astype(np.float32)
            absdiff = np.abs(diff).astype(np.float32)
            prev_valid = np.full(self.target_shape, prev_valid_value, dtype=np.float32)
            next_valid = np.full(self.target_shape, next_valid_value, dtype=np.float32)
            channels = [prev_anchor, left, right, next_anchor, coarse, rel_map, diff, absdiff, prev_valid, next_valid]
            if self.anchor_features == "rich":
                prev_delta = ((left - prev_anchor) * prev_valid_value).astype(np.float32)
                next_delta = ((next_anchor - right) * next_valid_value).astype(np.float32)
                curvature = (next_delta - prev_delta).astype(np.float32)
                channels.extend([prev_delta, next_delta, curvature])
            cond_ma = np.stack(channels, axis=0).astype(np.float32)
            item["cond_ma"] = torch.from_numpy(cond_ma)
        return item
