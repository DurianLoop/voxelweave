from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Iterable

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOPCOW = ROOT / "dataset" / "TopCaw2024"
TRAIN_SRC = TOPCOW / "imagesTr"
VAL_SRC = TOPCOW / "imagesVal"
LABEL_SRC = TOPCOW / "cow_seg_labelsTr"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_nifti(path: Path) -> tuple[np.ndarray, np.ndarray, nib.Nifti1Header]:
    img = nib.load(str(path))
    return img.get_fdata(dtype=np.float32), img.affine, img.header


def save_nifti(data: np.ndarray, affine: np.ndarray, header: nib.Nifti1Header, path: Path) -> None:
    ensure_dir(path.parent)
    out = nib.Nifti1Image(data.astype(np.float32), affine, header=header)
    nib.save(out, str(path))


def mr_train_files(limit: int | None = None) -> list[Path]:
    files = sorted(TRAIN_SRC.glob("topcow_mr_*_0000.nii.gz"))
    return files if limit is None else files[:limit]


def mr_val_files(limit: int | None = None) -> list[Path]:
    files = sorted(VAL_SRC.glob("topcow_mr_*_0000.nii.gz"))
    return files if limit is None else files[:limit]


def mr_label_path(image_name: str) -> Path:
    label_name = image_name.replace("_0000.nii.gz", ".nii.gz")
    return LABEL_SRC / label_name


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    ensure_dir(path.parent)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def set_windows_safe_workers(default: str = "0") -> None:
    os.environ.setdefault("MRI_NUM_WORKERS", default)
