from __future__ import annotations

import argparse
import csv
import random
import re
from collections import defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np

from fastmri_brain.dicom import read_header, read_pixel_array

try:
    import pydicom
except Exception:  # pragma: no cover - optional dependency
    pydicom = None


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "dataset" / "fastMRI_brain_DICOM"
DEFAULT_OUT = ROOT / "dataset" / "fastMRI_brain_T2" / "processed"

SERIES_KEYWORDS = re.compile(
    r"(T1|T2|FLAIR|FSE|TSE|POST|PRE|AX|AXIAL|SAG|SAGITTAL|COR|CORONAL|DWI|ADC|TRACE)",
    re.IGNORECASE,
)
GENERIC_PATTERNS = (
    "MRI BRAIN",
    "NYU NEURO",
    "IMG",
    "STENTOR",
    "HEADER",
    "COMPLETED",
    "SIEMENS",
    "HITACHI",
    "OASIS",
    "BRAIN",
    "WITH AND WITHOUT",
)


def _write_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(values) + ("\n" if values else ""), encoding="utf-8")


def _clean_label(text: str) -> str:
    text = re.sub(r"\s+", " ", text.replace("\x00", " ")).strip()
    return text[:120]


def _printable_strings(path: Path, max_bytes: int = 24000) -> list[str]:
    data = path.read_bytes()[:max_bytes]
    values = []
    for item in re.findall(rb"[ -~]{4,}", data):
        text = _clean_label(item.decode("latin-1", errors="ignore"))
        if text:
            values.append(text)
    return values


def infer_series_label(path: Path) -> str:
    strings = _printable_strings(path)
    candidates = []
    for text in strings:
        upper = text.upper()
        if not SERIES_KEYWORDS.search(text):
            continue
        if any(pattern in upper for pattern in GENERIC_PATTERNS):
            continue
        if re.fullmatch(r"[0-9.\\ -]+", text):
            continue
        score = 0
        if re.search(r"\bT2\b|T2_", upper):
            score += 50
        if re.search(r"\bT1\b|T1_", upper):
            score += 40
        if "FLAIR" in upper:
            score += 35
        if "AX" in upper or "AXIAL" in upper:
            score += 10
        if "FSE" in upper or "TSE" in upper:
            score += 8
        score += min(len(text), 40) / 100.0
        candidates.append((score, text))
    if not candidates:
        return "unknown"
    return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]


def is_strict_t2(label: str) -> bool:
    upper = label.upper()
    if "T2" not in upper:
        return False
    if any(bad in upper for bad in ["T1", "POST", "FLAIR", "DWI", "ADC", "DIFF", "TRACE"]):
        return False
    return True


def _safe_group_key(label: str) -> str:
    key = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_").lower()
    return key or "unknown"


def scan_series(source: Path, out: Path, case_limit: int | None = None) -> list[dict]:
    case_dirs = sorted(path for path in source.iterdir() if path.is_dir())
    if case_limit is not None:
        case_dirs = case_dirs[:case_limit]
    rows: list[dict] = []
    for case_idx, case_dir in enumerate(case_dirs, start=1):
        groups: dict[str, list[Path]] = defaultdict(list)
        for dcm in sorted(case_dir.glob("*.dcm")):
            label = infer_series_label(dcm)
            groups[label].append(dcm)
        for label, paths in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
            first = paths[0]
            try:
                header = read_header(first)
                rows_value = header.rows
                cols_value = header.cols
                transfer = header.transfer_syntax
                spacing = ""
                if header.pixel_spacing is not None:
                    spacing = f"{header.pixel_spacing[0]:.6g}x{header.pixel_spacing[1]:.6g}"
            except Exception as exc:
                rows_value = cols_value = 0
                transfer = ""
                spacing = ""
                label = f"{label} [header_error={type(exc).__name__}]"
            rows.append(
                {
                    "case_id": case_dir.name,
                    "series_label": label,
                    "series_key": _safe_group_key(label),
                    "is_t2": is_strict_t2(label),
                    "num_slices": len(paths),
                    "first_dicom": str(first),
                    "rows": rows_value,
                    "cols": cols_value,
                    "pixel_spacing": spacing,
                    "transfer_syntax": transfer,
                }
            )
        if case_idx % 100 == 0:
            print(f"Scanned {case_idx}/{len(case_dirs)} cases")
    metadata = out / "metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    manifest = metadata / "fastmri_brain_series_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(rows[0].keys()) if rows else ["case_id"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    t2_rows = [row for row in rows if row["is_t2"]]
    t2_manifest = metadata / "fastmri_brain_t2_series_manifest.csv"
    with t2_manifest.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(rows[0].keys()) if rows else ["case_id"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(t2_rows)
    print(f"Wrote {manifest}")
    print(f"Wrote {t2_manifest}")
    print(f"Series: all={len(rows)}, strict_t2={len(t2_rows)}")
    return t2_rows


def _load_series_with_pydicom(paths: list[Path]) -> tuple[np.ndarray, np.ndarray]:
    if pydicom is None:
        raise RuntimeError("pydicom is not available")
    datasets = [pydicom.dcmread(str(path), force=True) for path in paths]
    order = sorted(range(len(datasets)), key=lambda idx: int(getattr(datasets[idx], "InstanceNumber", idx)))
    sorted_datasets = [datasets[idx] for idx in order]
    volume = np.stack([ds.pixel_array for ds in sorted_datasets], axis=-1).astype(np.float32)
    first = sorted_datasets[0]
    spacing_value = getattr(first, "PixelSpacing", [1.0, 1.0])
    spacing = [float(spacing_value[0]), float(spacing_value[1])] if len(spacing_value) >= 2 else [1.0, 1.0]
    z_spacing = float(
        getattr(first, "SpacingBetweenSlices", None)
        or getattr(first, "SliceThickness", None)
        or 1.0
    )
    affine = np.diag([spacing[0], spacing[1], z_spacing, 1.0])
    return volume, affine


def _load_series(paths: list[Path]) -> tuple[np.ndarray, np.ndarray, str]:
    try:
        volume, affine = _load_series_with_pydicom(paths)
        return volume, affine, "pydicom"
    except Exception as pydicom_exc:
        pydicom_message = f"{type(pydicom_exc).__name__}: {pydicom_exc}"

    headers = [read_header(path) for path in paths]
    order = sorted(range(len(headers)), key=lambda idx: headers[idx].instance_number)
    sorted_headers = [headers[idx] for idx in order]
    sorted_paths = [paths[idx] for idx in order]
    try:
        volume = np.stack([read_pixel_array(path) for path in sorted_paths], axis=-1).astype(np.float32)
    except Exception as fallback_exc:
        raise RuntimeError(
            f"pydicom failed ({pydicom_message}); fallback reader failed ({type(fallback_exc).__name__}: {fallback_exc})"
        ) from fallback_exc
    spacing = sorted_headers[0].pixel_spacing or (1.0, 1.0)
    z_spacing = sorted_headers[0].spacing_between_slices or sorted_headers[0].slice_thickness or 1.0
    affine = np.diag([float(spacing[0]), float(spacing[1]), float(z_spacing), 1.0])
    return volume, affine, "fallback"


def convert_t2_series(source: Path, out: Path, t2_rows: list[dict], target_successes: int | None = None) -> None:
    nifti_dir = out / "nifti"
    nifti_dir.mkdir(parents=True, exist_ok=True)
    by_key: dict[tuple[str, str, str], list[Path]] = defaultdict(list)
    lookup = {(row["case_id"], row["series_label"]) for row in t2_rows}
    for case_id, label in lookup:
        case_dir = source / case_id
        for dcm in sorted(case_dir.glob("*.dcm")):
            if infer_series_label(dcm) == label:
                by_key[(case_id, _safe_group_key(label), label)].append(dcm)

    rows = []
    successes = 0
    for (case_id, series_key, label), paths in sorted(by_key.items()):
        out_name = f"{case_id}_{series_key}.nii.gz"
        out_path = nifti_dir / out_name
        status = "ok"
        message = ""
        shape = ""
        try:
            volume, affine, reader = _load_series(paths)
            shape = "x".join(str(int(v)) for v in volume.shape)
            if volume.shape[2] < 8:
                raise ValueError(f"Too few slices for x4 interpolation: depth={volume.shape[2]}")
            nib.save(nib.Nifti1Image(volume.astype(np.float32), affine), str(out_path))
            successes += 1
            print(f"Converted T2 {successes}: {out_path.name} shape={shape} reader={reader}")
        except Exception as exc:
            status = "failed"
            message = f"{type(exc).__name__}: {exc}"
            print(f"Skip {case_id}/{label}: {message}")
        rows.append(
            {
                "case_id": f"{case_id}_{series_key}",
                "source_case_id": case_id,
                "series_label": label,
                "nifti_path": str(out_path) if status == "ok" else "",
                "shape": shape,
                "status": status,
                "message": message,
            }
        )
        if target_successes is not None and successes >= target_successes:
            break

    metadata = out / "metadata"
    manifest = metadata / "fastmri_brain_t2_nifti_manifest.csv"
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
                    "contrast_status": "strict_t2_from_series_label",
                    "note": row["series_label"],
                }
            )
    _write_splits(out, [row["case_id"] for row in ok_rows])
    print(f"Wrote {manifest}")
    print(f"Wrote {index}")
    print(f"Converted T2 NIfTI successes={len(ok_rows)}")


def _write_splits(out: Path, case_ids: list[str], seed: int = 3407) -> None:
    ids = list(case_ids)
    random.Random(seed).shuffle(ids)
    n = len(ids)
    if n < 3:
        splits = {"train": sorted(ids), "val": [], "test": []}
    else:
        n_train = max(1, int(n * 0.7))
        n_val = max(1, int(n * 0.15))
        if n_train + n_val >= n:
            n_train = max(1, n - 2)
            n_val = 1
        splits = {
            "train": sorted(ids[:n_train]),
            "val": sorted(ids[n_train : n_train + n_val]),
            "test": sorted(ids[n_train + n_val :]),
        }
    split_root = out / "splits" / "nifti_seed3407"
    for name, values in splits.items():
        _write_lines(split_root / f"{name}_cases.txt", values)
    print("Splits: " + ", ".join(f"{name}={len(values)}" for name, values in splits.items()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--case-limit", type=int, default=200)
    parser.add_argument("--convert", action="store_true")
    parser.add_argument("--target-successes", type=int, default=24)
    args = parser.parse_args()
    t2_rows = scan_series(args.source, args.out, case_limit=args.case_limit)
    if args.convert:
        convert_t2_series(args.source, args.out, t2_rows, target_successes=args.target_successes or None)


if __name__ == "__main__":
    main()
