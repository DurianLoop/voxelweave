from __future__ import annotations

import csv
import json
from pathlib import Path

import nibabel as nib
import numpy as np


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_case_ids(path: Path, limit: int | None = None) -> list[str]:
    ids = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return ids[:limit] if limit is not None else ids


def load_nifti(path: Path) -> tuple[np.ndarray, np.ndarray, nib.Nifti1Header]:
    image = nib.load(str(path))
    return image.get_fdata(dtype=np.float32), image.affine, image.header


def save_nifti(data: np.ndarray, affine: np.ndarray, header: nib.Nifti1Header, path: Path) -> None:
    ensure_dir(path.parent)
    nib.save(nib.Nifti1Image(data.astype(np.float32), affine, header), str(path))


def normalize_volume(volume: np.ndarray) -> tuple[np.ndarray, float, float]:
    lo = float(np.nanmin(volume))
    hi = float(np.nanmax(volume))
    if hi <= lo:
        return np.zeros_like(volume, dtype=np.float32), lo, hi
    return ((volume - lo) / (hi - lo + 1e-8)).astype(np.float32), lo, hi


def write_json(path: Path, payload: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    ensure_dir(path.parent)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
