from __future__ import annotations

import argparse
import csv
from pathlib import Path
import random

import nibabel as nib
import numpy as np

from .dicom import load_case_volume, read_header


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "dataset" / "fastMRI_brain_DICOM"
DEFAULT_OUT = ROOT / "dataset" / "fastMRI_brain_prepared"


def _write_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(values) + "\n", encoding="utf-8")


def _split_cases(case_ids: list[str], seed: int) -> dict[str, list[str]]:
    rng = random.Random(seed)
    ids = list(case_ids)
    rng.shuffle(ids)
    n = len(ids)
    n_train = int(n * 0.8)
    n_val = int(n * 0.1)
    return {
        "train": sorted(ids[:n_train]),
        "val": sorted(ids[n_train : n_train + n_val]),
        "test": sorted(ids[n_train + n_val :]),
    }


def scan_cases(source: Path, out: Path, seed: int) -> list[dict]:
    rows = []
    case_dirs = sorted(path for path in source.iterdir() if path.is_dir())
    for idx, case_dir in enumerate(case_dirs, start=1):
        dcm_files = sorted(case_dir.glob("*.dcm"))
        if not dcm_files:
            continue
        header = read_header(dcm_files[0])
        rows.append(
            {
                "case_id": case_dir.name,
                "case_dir": str(case_dir),
                "num_slices": len(dcm_files),
                "rows": header.rows,
                "cols": header.cols,
                "pixel_spacing": ""
                if header.pixel_spacing is None
                else f"{header.pixel_spacing[0]:.6g}x{header.pixel_spacing[1]:.6g}",
                "slice_thickness": "" if header.slice_thickness is None else f"{header.slice_thickness:.6g}",
                "spacing_between_slices": ""
                if header.spacing_between_slices is None
                else f"{header.spacing_between_slices:.6g}",
                "transfer_syntax": header.transfer_syntax,
            }
        )
        if idx % 500 == 0:
            print(f"Scanned {idx}/{len(case_dirs)} cases")

    metadata = out / "metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    csv_path = metadata / "fastmri_brain_cases.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["case_id"])
        writer.writeheader()
        writer.writerows(rows)
    splits = _split_cases([row["case_id"] for row in rows], seed=seed)
    split_root = out / "splits" / f"seed{seed}"
    for split, ids in splits.items():
        _write_lines(split_root / f"{split}_cases.txt", ids)
    print(f"Wrote metadata: {csv_path}")
    print(
        "Splits: "
        + ", ".join(f"{name}={len(ids)}" for name, ids in splits.items())
    )
    return rows


def convert_cases(rows: list[dict], out: Path, limit: int | None, target_successes: int | None = None) -> None:
    selected = rows[:limit] if limit is not None else rows
    nifti_dir = out / "nifti"
    nifti_dir.mkdir(parents=True, exist_ok=True)
    successes = 0
    for idx, row in enumerate(selected, start=1):
        case_id = row["case_id"]
        try:
            volume, headers = load_case_volume(Path(row["case_dir"]))
        except Exception as exc:
            print(f"Skip {case_id}: {exc}")
            continue
        spacing = headers[0].pixel_spacing or (1.0, 1.0)
        z_spacing = headers[0].spacing_between_slices or headers[0].slice_thickness or 1.0
        affine = np.diag([float(spacing[0]), float(spacing[1]), float(z_spacing), 1.0])
        out_path = nifti_dir / f"{case_id}.nii.gz"
        nib.save(nib.Nifti1Image(volume.astype(np.float32), affine), str(out_path))
        successes += 1
        print(f"Converted {idx}/{len(selected)}: {case_id} -> {out_path}")
        if target_successes is not None and successes >= target_successes:
            break


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=3407)
    parser.add_argument("--convert-limit", type=int, default=0, help="0 only scans metadata; N converts first N cases; -1 converts all")
    parser.add_argument("--target-successes", type=int, default=0, help="Stop conversion after this many successful NIfTI cases; 0 disables")
    args = parser.parse_args()

    if not args.source.exists():
        raise FileNotFoundError(args.source)
    rows = scan_cases(args.source, args.out, seed=args.seed)
    if args.convert_limit != 0:
        convert_cases(
            rows,
            args.out,
            limit=None if args.convert_limit < 0 else args.convert_limit,
            target_successes=args.target_successes or None,
        )


if __name__ == "__main__":
    main()
