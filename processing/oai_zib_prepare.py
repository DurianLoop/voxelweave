from __future__ import annotations

import argparse
import csv
import random
import re
from collections import defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "dataset" / "OAI-ZIB"
DEFAULT_OUT = ROOT / "dataset" / "OAI-ZIB-prepared"


def _write_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(values) + ("\n" if values else ""), encoding="utf-8")


def parse_oai_name(path: Path) -> tuple[str, str, str]:
    match = re.match(r"^(?P<subject>\d+)_(?P<side>LEFT|RIGHT)_(?P<visit>\d+)\.npz$", path.name)
    if not match:
        raise ValueError(f"Unexpected OAI-ZIB filename: {path.name}")
    return match.group("subject"), match.group("side"), match.group("visit")


def collect_files(source: Path, subject_limit: int | None, max_series_per_subject: int | None) -> dict[str, list[Path]]:
    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(source.rglob("*.npz")):
        subject, _side, _visit = parse_oai_name(path)
        grouped[subject].append(path)
    subjects = sorted(grouped)
    if subject_limit is not None:
        subjects = subjects[:subject_limit]
    selected: dict[str, list[Path]] = {}
    for subject in subjects:
        files = sorted(grouped[subject], key=lambda item: (item.parent.name, parse_oai_name(item)[1], int(parse_oai_name(item)[2])))
        if max_series_per_subject is not None:
            files = files[:max_series_per_subject]
        selected[subject] = files
    return selected


def write_splits(out: Path, subject_to_cases: dict[str, list[str]], seed: int = 3407) -> dict[str, list[str]]:
    subjects = sorted(subject_to_cases)
    random.Random(seed).shuffle(subjects)
    n = len(subjects)
    if n < 3:
        split_subjects = {"train": subjects, "val": [], "test": []}
    else:
        n_train = max(1, int(n * 0.7))
        n_val = max(1, int(n * 0.15))
        if n_train + n_val >= n:
            n_train = max(1, n - 2)
            n_val = 1
        split_subjects = {
            "train": sorted(subjects[:n_train]),
            "val": sorted(subjects[n_train : n_train + n_val]),
            "test": sorted(subjects[n_train + n_val :]),
        }
    split_cases = {
        split: sorted(case for subject in split_subjects[split] for case in subject_to_cases[subject])
        for split in ["train", "val", "test"]
    }
    split_root = out / "splits" / "nifti_seed3407"
    for split, values in split_cases.items():
        _write_lines(split_root / f"{split}_cases.txt", values)
    with (out / "metadata" / "oai_zib_subject_splits.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["split", "subject_id", "case_count"])
        writer.writeheader()
        for split, values in split_subjects.items():
            for subject in values:
                writer.writerow({"split": split, "subject_id": subject, "case_count": len(subject_to_cases[subject])})
    return split_cases


def convert(source: Path, out: Path, subject_limit: int | None, max_series_per_subject: int | None) -> None:
    metadata = out / "metadata"
    nifti_dir = out / "nifti"
    metadata.mkdir(parents=True, exist_ok=True)
    nifti_dir.mkdir(parents=True, exist_ok=True)
    selected = collect_files(source, subject_limit, max_series_per_subject)
    rows: list[dict[str, str]] = []
    subject_to_cases: dict[str, list[str]] = defaultdict(list)

    for subject, files in selected.items():
        for path in files:
            subject_id, side, visit = parse_oai_name(path)
            visit_folder = path.parent.name
            case_id = f"{subject_id}_{side.lower()}_{visit_folder.lower()}_{visit}"
            out_path = nifti_dir / f"{case_id}.nii.gz"
            status = "ok"
            message = ""
            shape = ""
            unique_values = ""
            try:
                with np.load(path) as payload:
                    if "x" not in payload.files:
                        raise KeyError(f"missing key x; keys={payload.files}")
                    volume = payload["x"]
                if volume.ndim != 3:
                    raise ValueError(f"expected 3D volume, got shape={volume.shape}")
                if volume.shape[2] < 8:
                    raise ValueError(f"too few slices for x4 interpolation: depth={volume.shape[2]}")
                values = np.unique(volume)
                unique_values = " ".join(str(int(v)) for v in values[:20])
                shape = "x".join(str(int(v)) for v in volume.shape)
                image = nib.Nifti1Image(volume.astype(np.uint8), np.eye(4, dtype=np.float32))
                image.header.set_data_dtype(np.uint8)
                nib.save(image, str(out_path))
                subject_to_cases[subject].append(case_id)
            except Exception as exc:
                status = "failed"
                message = f"{type(exc).__name__}: {exc}"
            rows.append(
                {
                    "case_id": case_id,
                    "subject_id": subject_id,
                    "side": side,
                    "visit": visit,
                    "visit_folder": visit_folder,
                    "npz_path": str(path),
                    "nifti_path": str(out_path) if status == "ok" else "",
                    "shape": shape,
                    "dtype": "uint8",
                    "unique_values": unique_values,
                    "contrast_status": "label_like_low_gray_oai_zib",
                    "status": status,
                    "message": message,
                }
            )

    manifest = metadata / "oai_zib_nifti_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["case_id"])
        writer.writeheader()
        writer.writerows(rows)

    ok_rows = [row for row in rows if row["status"] == "ok"]
    index = metadata / "fastmri_brain_nifti_cases.csv"
    with index.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case_id", "nifti_path", "shape", "contrast_status", "note"])
        writer.writeheader()
        for row in ok_rows:
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "nifti_path": row["nifti_path"],
                    "shape": row["shape"],
                    "contrast_status": row["contrast_status"],
                    "note": f"OAI-ZIB {row['side']} {row['visit_folder']} visit={row['visit']}; unique={row['unique_values']}",
                }
            )
    split_cases = write_splits(out, subject_to_cases)
    print(f"Wrote {manifest}")
    print(f"Wrote {index}")
    print(
        "Converted OAI-ZIB: "
        f"subjects={len(subject_to_cases)}, cases={len(ok_rows)}, "
        + ", ".join(f"{name}={len(values)}" for name, values in split_cases.items())
    )
    print("Warning: OAI-ZIB x values are label-like low gray levels (usually 0..7); treat as structure sanity, not MRI intensity.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--subject-limit", type=int, default=40)
    parser.add_argument("--max-series-per-subject", type=int, default=2)
    args = parser.parse_args()
    convert(args.source, args.out, args.subject_limit, args.max_series_per_subject)


if __name__ == "__main__":
    main()
