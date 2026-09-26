from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import nibabel as nib


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREPARED = ROOT / "dataset" / "fastMRI_brain_prepared"


def _write_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(values) + ("\n" if values else ""), encoding="utf-8")


def _split(ids: list[str], seed: int) -> dict[str, list[str]]:
    shuffled = list(ids)
    random.Random(seed).shuffle(shuffled)
    n = len(shuffled)
    if n < 3:
        return {"train": sorted(shuffled), "val": [], "test": []}
    n_train = max(1, int(n * 0.7))
    n_val = max(1, int(n * 0.15))
    if n_train + n_val >= n:
        n_train = max(1, n - 2)
        n_val = 1
    return {
        "train": sorted(shuffled[:n_train]),
        "val": sorted(shuffled[n_train : n_train + n_val]),
        "test": sorted(shuffled[n_train + n_val :]),
    }


def build_index(prepared: Path, seed: int) -> None:
    nifti_dir = prepared / "nifti"
    if not nifti_dir.exists():
        raise FileNotFoundError(nifti_dir)
    rows = []
    for path in sorted(nifti_dir.glob("*.nii.gz")):
        image = nib.load(str(path))
        case_id = path.name.removesuffix(".nii.gz")
        rows.append(
            {
                "case_id": case_id,
                "nifti_path": str(path),
                "shape": "x".join(str(int(v)) for v in image.shape),
                "contrast_status": "unknown_from_dicom_header",
                "note": "fastMRI brain DICOM may include T1/T2/T2-FLAIR; filter before calling this T2-only.",
            }
        )
    if not rows:
        raise RuntimeError(f"No NIfTI files found under {nifti_dir}")

    metadata = prepared / "metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    index_path = metadata / "fastmri_brain_nifti_cases.csv"
    with index_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    split_root = prepared / "splits" / f"nifti_seed{seed}"
    splits = _split([row["case_id"] for row in rows], seed)
    for split_name, values in splits.items():
        _write_lines(split_root / f"{split_name}_cases.txt", values)

    print(f"Wrote {index_path}")
    print("NIfTI splits: " + ", ".join(f"{key}={len(value)}" for key, value in splits.items()))
    print("Contrast status: unknown from local DICOM headers; do not label this subset T2-only until filtered.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared", type=Path, default=DEFAULT_PREPARED)
    parser.add_argument("--seed", type=int, default=3407)
    args = parser.parse_args()
    build_index(args.prepared, args.seed)


if __name__ == "__main__":
    main()
