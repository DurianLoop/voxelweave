from __future__ import annotations

import os
import random
from pathlib import Path

import numpy as np

from .common import ensure_dir, load_nifti, mr_label_path, mr_train_files, mr_val_files, save_nifti
from .settings import RunPaths


def stage_training_links(paths: RunPaths, train_limit: int | None) -> int:
    ensure_dir(paths.train_links)
    count = 0
    for src in mr_train_files(train_limit):
        dst = paths.train_links / src.name
        if not dst.exists():
            try:
                os.link(src, dst)
            except OSError as exc:
                raise RuntimeError(f"Unable to create hard link for {src}") from exc
        count += 1
    return count


def _link_files(files: list[Path], dst_dir: Path) -> int:
    ensure_dir(dst_dir)
    count = 0
    for src in files:
        dst = dst_dir / src.name
        if not dst.exists():
            try:
                os.link(src, dst)
            except OSError as exc:
                raise RuntimeError(f"Unable to create hard link for {src}") from exc
        count += 1
    return count


def _sync_links(files: list[Path], dst_dir: Path) -> int:
    ensure_dir(dst_dir)
    expected = {src.name for src in files}
    for item in dst_dir.glob("*.nii.gz"):
        if item.name not in expected:
            item.unlink()
    return _link_files(files, dst_dir)


def stage_case_level_training(
    paths: RunPaths,
    train_limit: int | None,
    train_fraction: float,
    seed: int = 3407,
) -> dict:
    files = mr_train_files(train_limit)
    rng = random.Random(seed)
    shuffled = files[:]
    rng.shuffle(shuffled)
    split_idx = max(1, int(round(len(shuffled) * train_fraction)))
    split_idx = min(split_idx, len(shuffled) - 1) if len(shuffled) > 1 else len(shuffled)
    train_files = sorted(shuffled[:split_idx])
    val_files = sorted(shuffled[split_idx:])
    _sync_links(train_files, paths.train_links)
    _sync_links(val_files, paths.val_links)
    return {
        "seed": seed,
        "train_fraction": train_fraction,
        "train_cases": [p.name for p in train_files],
        "val_cases": [p.name for p in val_files],
    }


def prepare_eval_inputs(paths: RunPaths, val_limit: int | None, stride: int = 4) -> list[dict]:
    ensure_dir(paths.eval_sparse)
    ensure_dir(paths.eval_gt)
    manifest: list[dict] = []
    for src in mr_val_files(val_limit):
        volume, affine, header = load_nifti(src)
        sparse = volume[:, :, ::stride]
        full_depth = (sparse.shape[2] - 1) * stride + 1
        gt = volume[:, :, :full_depth]
        sparse_path = paths.eval_sparse / src.name
        gt_path = paths.eval_gt / src.name
        save_nifti(sparse, affine, header, sparse_path)
        save_nifti(gt, affine, header, gt_path)
        manifest.append(
            {
                "case": src.name,
                "source_depth": int(volume.shape[2]),
                "sparse_depth": int(sparse.shape[2]),
                "target_depth": int(gt.shape[2]),
                "stride": stride,
            }
        )
    return manifest


def prepare_labeled_eval_inputs(paths: RunPaths, stride: int = 4) -> list[dict]:
    ensure_dir(paths.labeled_sparse)
    ensure_dir(paths.labeled_gt)
    ensure_dir(paths.labeled_labels)
    manifest: list[dict] = []
    for src in sorted(paths.val_links.glob("*.nii.gz")):
        label_src = mr_label_path(src.name)
        if not label_src.exists():
            continue
        volume, affine, header = load_nifti(src)
        label, label_affine, label_header = load_nifti(label_src)
        sparse = volume[:, :, ::stride]
        full_depth = (sparse.shape[2] - 1) * stride + 1
        gt = volume[:, :, :full_depth]
        label_gt = label[:, :, :full_depth]
        save_nifti(sparse, affine, header, paths.labeled_sparse / src.name)
        save_nifti(gt, affine, header, paths.labeled_gt / src.name)
        save_nifti(label_gt, label_affine, label_header, paths.labeled_labels / src.name)
        manifest.append(
            {
                "case": src.name,
                "label": label_src.name,
                "source_depth": int(volume.shape[2]),
                "sparse_depth": int(sparse.shape[2]),
                "target_depth": int(gt.shape[2]),
                "stride": stride,
            }
        )
    return manifest
