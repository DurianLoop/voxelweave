from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import struct
import tarfile
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import nibabel as nib
import numpy as np

try:
    import pydicom
except Exception:  # pragma: no cover - optional dependency
    pydicom = None


LONG_VR = {"OB", "OD", "OF", "OL", "OV", "OW", "SQ", "UC", "UR", "UT", "UN"}
TEXT_VR = {"AE", "AS", "CS", "DA", "DS", "DT", "IS", "LO", "LT", "PN", "SH", "ST", "TM", "UI", "UT"}

TAGS = {
    (0x0002, 0x0010): "transfer_syntax_uid",
    (0x0008, 0x0008): "image_type",
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0020): "study_date",
    (0x0008, 0x0060): "modality",
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0010, 0x0020): "patient_id",
    (0x0018, 0x0020): "scanning_sequence",
    (0x0018, 0x0021): "sequence_variant",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0088): "spacing_between_slices",
    (0x0018, 0x1030): "protocol_name",
    (0x0020, 0x000D): "study_instance_uid",
    (0x0020, 0x000E): "series_instance_uid",
    (0x0020, 0x0011): "series_number",
    (0x0020, 0x0013): "instance_number",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "pixel_spacing",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0101): "bits_stored",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x1052): "rescale_intercept",
    (0x0028, 0x1053): "rescale_slope",
    (0x7FE0, 0x0010): "pixel_data",
}

TAG_VR = {
    (0x0002, 0x0010): "UI",
    (0x0008, 0x0008): "CS",
    (0x0008, 0x0018): "UI",
    (0x0008, 0x0020): "DA",
    (0x0008, 0x0060): "CS",
    (0x0008, 0x1030): "LO",
    (0x0008, 0x103E): "LO",
    (0x0010, 0x0020): "LO",
    (0x0018, 0x0020): "CS",
    (0x0018, 0x0021): "CS",
    (0x0018, 0x0050): "DS",
    (0x0018, 0x0080): "DS",
    (0x0018, 0x0081): "DS",
    (0x0018, 0x0088): "DS",
    (0x0018, 0x1030): "LO",
    (0x0020, 0x000D): "UI",
    (0x0020, 0x000E): "UI",
    (0x0020, 0x0011): "IS",
    (0x0020, 0x0013): "IS",
    (0x0020, 0x0032): "DS",
    (0x0020, 0x0037): "DS",
    (0x0028, 0x0002): "US",
    (0x0028, 0x0004): "CS",
    (0x0028, 0x0010): "US",
    (0x0028, 0x0011): "US",
    (0x0028, 0x0030): "DS",
    (0x0028, 0x0100): "US",
    (0x0028, 0x0101): "US",
    (0x0028, 0x0103): "US",
    (0x0028, 0x1052): "DS",
    (0x0028, 0x1053): "DS",
}


def _decode_text(raw: bytes) -> str:
    raw = raw.rstrip(b"\x00 ")
    for encoding in ("utf-8", "gb18030", "latin1"):
        try:
            return raw.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return raw.decode("latin1", errors="ignore").strip()


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return _decode_text(value)
    if isinstance(value, (list, tuple)):
        return "\\".join(_clean_text(v) for v in value)
    return str(value).replace("\x00", "").strip()


def _number(value: Any) -> float | None:
    try:
        text = _clean_text(value).split("\\")[0]
        if text == "":
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _int_value(value: Any, default: int = 0) -> int:
    num = _number(value)
    return default if num is None else int(num)


def _float_list(value: Any) -> list[float]:
    text = _clean_text(value)
    out = []
    for item in text.split("\\"):
        try:
            out.append(float(item))
        except ValueError:
            pass
    return out


def _parse_value(vr: str, raw: bytes, little: bool) -> Any:
    if vr in TEXT_VR:
        return _decode_text(raw)
    endian = "<" if little else ">"
    if vr == "US" and len(raw) >= 2:
        return struct.unpack(endian + f"{len(raw) // 2}H", raw[: len(raw) // 2 * 2])
    if vr == "SS" and len(raw) >= 2:
        return struct.unpack(endian + f"{len(raw) // 2}h", raw[: len(raw) // 2 * 2])
    if vr == "UL" and len(raw) >= 4:
        return struct.unpack(endian + f"{len(raw) // 4}I", raw[: len(raw) // 4 * 4])
    if vr == "SL" and len(raw) >= 4:
        return struct.unpack(endian + f"{len(raw) // 4}i", raw[: len(raw) // 4 * 4])
    if vr == "FL" and len(raw) >= 4:
        return struct.unpack(endian + f"{len(raw) // 4}f", raw[: len(raw) // 4 * 4])
    if vr == "FD" and len(raw) >= 8:
        return struct.unpack(endian + f"{len(raw) // 8}d", raw[: len(raw) // 8 * 8])
    return raw


def _single(value: Any) -> Any:
    if isinstance(value, tuple) and len(value) == 1:
        return value[0]
    return value


def read_dicom_header(path: Path, include_pixel: bool = False) -> dict[str, Any]:
    data = path.read_bytes()
    pos = 132 if len(data) > 132 and data[128:132] == b"DICM" else 0
    little = True
    explicit = True
    meta: dict[str, Any] = {}
    pixel_offset = None
    pixel_length = None

    def read_element(offset: int, force_explicit: bool) -> tuple[int, int, str, int, int, bytes] | None:
        if offset + 8 > len(data):
            return None
        endian = "<" if little else ">"
        group, elem = struct.unpack(endian + "HH", data[offset : offset + 4])
        if force_explicit:
            vr = data[offset + 4 : offset + 6].decode("ascii", errors="ignore")
            if vr in LONG_VR:
                if offset + 12 > len(data):
                    return None
                length = struct.unpack(endian + "I", data[offset + 8 : offset + 12])[0]
                value_offset = offset + 12
            else:
                length = struct.unpack(endian + "H", data[offset + 6 : offset + 8])[0]
                value_offset = offset + 8
        else:
            vr = "UN"
            length = struct.unpack(endian + "I", data[offset + 4 : offset + 8])[0]
            value_offset = offset + 8
        if length == 0xFFFFFFFF:
            return group, elem, vr, length, value_offset, b""
        value = data[value_offset : value_offset + length]
        return group, elem, vr, length, value_offset, value

    while pos < len(data):
        item = read_element(pos, explicit)
        if item is None:
            break
        group, elem, vr, length, value_offset, value = item
        if group != 0x0002 and meta.get("transfer_syntax_uid"):
            tsuid = _clean_text(meta["transfer_syntax_uid"])
            desired_explicit = tsuid != "1.2.840.10008.1.2"
            desired_little = tsuid != "1.2.840.10008.1.2.2"
            if desired_explicit != explicit or desired_little != little:
                explicit = desired_explicit
                little = desired_little
                item = read_element(pos, explicit)
                if item is None:
                    break
                group, elem, vr, length, value_offset, value = item
        tag = (group, elem)
        if tag == (0x7FE0, 0x0010):
            pixel_offset = value_offset
            pixel_length = length
            break
        if tag in TAGS:
            effective_vr = TAG_VR.get(tag, vr)
            meta[TAGS[tag]] = _single(_parse_value(effective_vr, value, little))
        pos = value_offset + (0 if length == 0xFFFFFFFF else length)
        if length == 0xFFFFFFFF:
            break
    meta["file_path"] = str(path)
    meta["file_size"] = path.stat().st_size
    meta["pixel_offset"] = pixel_offset
    meta["pixel_length"] = pixel_length
    return meta


def _series_uid(meta: dict[str, Any]) -> str:
    uid = _clean_text(meta.get("series_instance_uid"))
    if uid:
        return uid
    text = str(meta.get("file_path", ""))
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def _modality_guess(meta: dict[str, Any]) -> str:
    fields = [
        meta.get("series_description"),
        meta.get("protocol_name"),
        meta.get("image_type"),
        meta.get("scanning_sequence"),
        meta.get("sequence_variant"),
    ]
    text = " ".join(_clean_text(item) for item in fields).upper()
    echo_time = _number(meta.get("echo_time"))
    if "T1" in text and "T2" not in text:
        return "T1"
    if "PD" in text and "T2" not in text:
        return "PD"
    if "T2" in text:
        return "T2"
    if echo_time is not None and echo_time >= 60:
        return "T2"
    return "unknown"


def _t2_candidate(meta: dict[str, Any]) -> tuple[bool, str]:
    fields = [
        meta.get("series_description"),
        meta.get("protocol_name"),
        meta.get("image_type"),
        meta.get("scanning_sequence"),
        meta.get("sequence_variant"),
    ]
    text = " ".join(_clean_text(item) for item in fields).upper()
    echo_time = _number(meta.get("echo_time"))
    modality = _modality_guess(meta)
    if modality == "T2":
        return True, "strict_t2"
    knee_t2_like_tokens = ["SPAIR", "FS", "FSE", "PROP", "TSE"]
    if modality == "PD" and any(token in text for token in knee_t2_like_tokens) and echo_time is not None and echo_time >= 35:
        return True, "pd_fat_suppressed_t2_like_candidate"
    return False, ""


def _is_uncompressed(meta: dict[str, Any]) -> bool:
    tsuid = _clean_text(meta.get("transfer_syntax_uid"))
    return tsuid in {
        "",
        "1.2.840.10008.1.2",
        "1.2.840.10008.1.2.1",
        "1.2.840.10008.1.2.1.99",
        "1.2.840.10008.1.2.2",
    }


def _read_pixel_array_with_pydicom(path: Path) -> np.ndarray:
    if pydicom is None:
        raise ValueError(f"Compressed DICOM requires pydicom/pylibjpeg: {path}")
    ds = pydicom.dcmread(str(path), force=True)
    arr = ds.pixel_array.astype(np.float32)
    if arr.ndim > 2:
        arr = np.squeeze(arr)
    if arr.ndim != 2:
        raise ValueError(f"Expected a 2D DICOM slice, got shape={arr.shape} for {path}")
    slope = float(getattr(ds, "RescaleSlope", 1.0) or 1.0)
    intercept = float(getattr(ds, "RescaleIntercept", 0.0) or 0.0)
    return arr * slope + intercept


def read_pixel_array(path: Path, meta: dict[str, Any]) -> np.ndarray:
    rows = _int_value(meta.get("rows"))
    cols = _int_value(meta.get("columns"))
    bits = _int_value(meta.get("bits_allocated"), 16)
    pixel_offset = meta.get("pixel_offset")
    pixel_length = meta.get("pixel_length")
    if not rows or not cols or pixel_offset is None or pixel_length is None:
        raise ValueError(f"Missing pixel metadata for {path}")
    if not _is_uncompressed(meta):
        return _read_pixel_array_with_pydicom(path)
    data = path.read_bytes()
    raw = data[int(pixel_offset) : int(pixel_offset) + int(pixel_length)]
    signed = _int_value(meta.get("pixel_representation")) == 1
    if bits == 16:
        dtype = np.dtype("<i2" if signed else "<u2")
    elif bits == 8:
        dtype = np.dtype("i1" if signed else "u1")
    else:
        raise ValueError(f"Unsupported bits_allocated={bits} for {path}")
    arr = np.frombuffer(raw, dtype=dtype, count=rows * cols).reshape(rows, cols).astype(np.float32)
    slope = _number(meta.get("rescale_slope")) or 1.0
    intercept = _number(meta.get("rescale_intercept")) or 0.0
    return arr * float(slope) + float(intercept)


@dataclass
class Series:
    case_id: str
    raw_case_name: str
    uid: str
    files: list[Path]
    metas: list[dict[str, Any]]

    def first(self) -> dict[str, Any]:
        return self.metas[0]

    def row(self, root: Path) -> dict[str, Any]:
        first = self.first()
        modality_guess = _modality_guess(first)
        t2_candidate, t2_candidate_reason = _t2_candidate(first)
        return {
            "case_id": self.case_id,
            "raw_case_name": self.raw_case_name,
            "series_uid": self.uid,
            "series_uid_short": hashlib.sha1(self.uid.encode("utf-8")).hexdigest()[:12],
            "modality_guess": modality_guess,
            "is_t2": modality_guess == "T2",
            "t2_candidate": t2_candidate,
            "t2_candidate_reason": t2_candidate_reason,
            "n_files": len(self.files),
            "modality": _clean_text(first.get("modality")),
            "series_number": _clean_text(first.get("series_number")),
            "series_description": _clean_text(first.get("series_description")),
            "protocol_name": _clean_text(first.get("protocol_name")),
            "image_type": _clean_text(first.get("image_type")),
            "scanning_sequence": _clean_text(first.get("scanning_sequence")),
            "sequence_variant": _clean_text(first.get("sequence_variant")),
            "echo_time": _clean_text(first.get("echo_time")),
            "repetition_time": _clean_text(first.get("repetition_time")),
            "rows": _clean_text(first.get("rows")),
            "columns": _clean_text(first.get("columns")),
            "pixel_spacing": _clean_text(first.get("pixel_spacing")),
            "slice_thickness": _clean_text(first.get("slice_thickness")),
            "spacing_between_slices": _clean_text(first.get("spacing_between_slices")),
            "transfer_syntax_uid": _clean_text(first.get("transfer_syntax_uid")),
            "uncompressed": _is_uncompressed(first),
            "first_file": str(self.files[0].relative_to(root)),
        }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _dataset_overview(data_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in ["MRNet-v1.0", "OAI", "SKI10Data", "NingXia_Data"]:
        root = data_root / name
        files = [p for p in root.rglob("*") if p.is_file()] if root.exists() else []
        rows.append(
            {
                "dataset": name,
                "path": str(root),
                "exists": root.exists(),
                "files": len(files),
                "size_gb": round(sum(p.stat().st_size for p in files) / (1024**3), 4),
                "role": {
                    "MRNet-v1.0": "public knee MRI classification data; not primary interpolation target",
                    "OAI": "public knee MRI/OAI-ZIB structural validation candidate",
                    "SKI10Data": "knee image/segmentation benchmark candidate",
                    "NingXia_Data": "local external clinical knee data; T2 first",
                }.get(name, ""),
            }
        )
    return rows


def _collect_local_series(local_root: Path) -> list[Series]:
    case_dirs = [p for p in local_root.iterdir() if p.is_dir() and p.name != "标注结果"]
    case_dirs = sorted(case_dirs, key=lambda p: p.name)
    series_map: dict[tuple[str, str], Series] = {}
    for case_index, case_dir in enumerate(case_dirs, start=1):
        case_id = f"NX{case_index:03d}"
        dcm_root = case_dir / "MR" / "IMAGE" / "DCM"
        if not dcm_root.exists():
            continue
        for path in sorted(p for p in dcm_root.rglob("*") if p.is_file() and not p.suffix):
            try:
                meta = read_dicom_header(path, include_pixel=False)
            except Exception:
                continue
            uid = _series_uid(meta)
            key = (case_id, uid)
            if key not in series_map:
                series_map[key] = Series(case_id, case_dir.name, uid, [], [])
            series_map[key].files.append(path)
            series_map[key].metas.append(meta)
    return sorted(series_map.values(), key=lambda s: (s.case_id, _clean_text(s.first().get("series_number")), s.uid))


def _sort_series_files(series: Series) -> tuple[list[Path], list[dict[str, Any]]]:
    metas = []
    for path, meta in zip(series.files, series.metas):
        pos = _float_list(meta.get("image_position_patient"))
        orientation = _float_list(meta.get("image_orientation_patient"))
        projection = None
        if len(pos) == 3 and len(orientation) == 6:
            row = np.array(orientation[:3], dtype=np.float64)
            col = np.array(orientation[3:], dtype=np.float64)
            normal = np.cross(row, col)
            projection = float(np.dot(np.array(pos, dtype=np.float64), normal))
        inst = _number(meta.get("instance_number"))
        metas.append((projection if projection is not None else math.inf, inst if inst is not None else math.inf, path.name, path, meta))
    metas.sort(key=lambda item: (item[0], item[1], item[2]))
    return [item[3] for item in metas], [item[4] for item in metas]


def _affine_from_series(metas: list[dict[str, Any]]) -> np.ndarray:
    first = metas[0]
    orientation = _float_list(first.get("image_orientation_patient"))
    pos = _float_list(first.get("image_position_patient"))
    spacing = _float_list(first.get("pixel_spacing"))
    if len(orientation) != 6 or len(pos) != 3 or len(spacing) < 2:
        return np.eye(4, dtype=np.float64)
    row = np.array(orientation[:3], dtype=np.float64)
    col = np.array(orientation[3:], dtype=np.float64)
    normal = np.cross(row, col)
    positions = [_float_list(meta.get("image_position_patient")) for meta in metas]
    projections = [float(np.dot(np.array(item, dtype=np.float64), normal)) for item in positions if len(item) == 3]
    if len(projections) > 1:
        diffs = np.diff(sorted(projections))
        slice_spacing = float(np.median(np.abs(diffs)))
    else:
        slice_spacing = _number(first.get("spacing_between_slices")) or _number(first.get("slice_thickness")) or 1.0
    affine = np.eye(4, dtype=np.float64)
    affine[:3, 0] = row * float(spacing[1])
    affine[:3, 1] = col * float(spacing[0])
    affine[:3, 2] = normal * float(slice_spacing)
    affine[:3, 3] = np.array(pos, dtype=np.float64)
    lps_to_ras = np.diag([-1.0, -1.0, 1.0, 1.0])
    return lps_to_ras @ affine


def _convert_t2_series(series_list: list[Series], processed_root: Path) -> list[dict[str, Any]]:
    out_dir = processed_root / "t2_nifti"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for series in series_list:
        is_candidate, candidate_reason = _t2_candidate(series.first())
        if not is_candidate:
            continue
        out_name = f"{series.case_id}_{hashlib.sha1(series.uid.encode('utf-8')).hexdigest()[:12]}.nii.gz"
        out_path = out_dir / out_name
        sorted_files, sorted_metas = _sort_series_files(series)
        status = "ok"
        error = ""
        if not out_path.exists():
            try:
                slices = [read_pixel_array(path, meta) for path, meta in zip(sorted_files, sorted_metas)]
                volume = np.stack(slices, axis=2).astype(np.float32)
                nib.save(nib.Nifti1Image(volume, _affine_from_series(sorted_metas)), out_path)
            except Exception as exc:
                status = "failed"
                error = str(exc)
        rows.append(
            {
                "case_id": series.case_id,
                "series_uid_short": hashlib.sha1(series.uid.encode("utf-8")).hexdigest()[:12],
                "t2_candidate_reason": candidate_reason,
                "n_files": len(series.files),
                "nifti_path": str(out_path),
                "status": status,
                "error": error,
            }
        )
    return rows


def _write_splits(t2_rows: list[dict[str, Any]], processed_root: Path, seed: int, split_name: str) -> dict[str, Any]:
    cases = sorted({str(row["case_id"]) for row in t2_rows})
    random.Random(seed).shuffle(cases)
    n = len(cases)
    if n <= 2:
        train, val, test = cases, [], []
    else:
        n_train = max(1, int(round(n * 0.6)))
        n_val = max(1, int(round(n * 0.2)))
        if n_train + n_val >= n:
            n_train = max(1, n - 2)
            n_val = 1
        train = sorted(cases[:n_train])
        val = sorted(cases[n_train : n_train + n_val])
        test = sorted(cases[n_train + n_val :])
    split_dir = processed_root / "splits" / f"{split_name}_seed{seed}"
    split_dir.mkdir(parents=True, exist_ok=True)
    for name, values in {
        "train_cases": train,
        "val_cases": val,
        "test_cases": test,
        "holdout_cases": sorted(cases),
    }.items():
        (split_dir / f"{name}.txt").write_text("\n".join(values) + ("\n" if values else ""), encoding="utf-8")
    summary = {
        "seed": seed,
        "cases": n,
        "train_cases": len(train),
        "val_cases": len(val),
        "test_cases": len(test),
        "holdout_cases": n,
        "split_dir": str(split_dir),
    }
    (split_dir / "split_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def _archive_manifest(data_root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in data_root.rglob("*"):
        if not path.is_file():
            continue
        lower = path.name.lower()
        if not (lower.endswith(".zip") or lower.endswith(".tar.gz") or lower.endswith(".tgz") or lower.endswith(".gz")):
            continue
        target = path.with_suffix("") if not lower.endswith(".tar.gz") else Path(str(path)[:-7])
        rows.append(
            {
                "archive": str(path),
                "size_gb": round(path.stat().st_size / (1024**3), 4),
                "target_guess": str(target),
                "target_exists": target.exists(),
            }
        )
    return rows


def extract_small_archives(data_root: Path, max_gb: float = 0.2) -> list[dict[str, Any]]:
    rows = []
    for item in _archive_manifest(data_root):
        archive = Path(item["archive"])
        size_gb = float(item["size_gb"])
        if size_gb > max_gb:
            item["extract_status"] = "skipped_large"
            rows.append(item)
            continue
        target = Path(str(archive) + "_extracted")
        if target.exists():
            item["extract_status"] = "already_exists"
            rows.append(item)
            continue
        try:
            target.mkdir(parents=True, exist_ok=True)
            lower = archive.name.lower()
            if lower.endswith(".zip"):
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(target)
            elif lower.endswith(".tar.gz") or lower.endswith(".tgz"):
                with tarfile.open(archive, "r:gz") as tf:
                    tf.extractall(target)
            else:
                item["extract_status"] = "skipped_gz_single_file"
                rows.append(item)
                continue
            item["extract_status"] = "ok"
            item["extract_target"] = str(target)
        except Exception as exc:
            item["extract_status"] = "failed"
            item["extract_error"] = str(exc)
        rows.append(item)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("dataset") / "NingXiaData" / "Data")
    parser.add_argument("--processed-root", type=Path, default=Path("dataset") / "NingXiaData" / "processed")
    parser.add_argument("--seed", type=int, default=3407)
    parser.add_argument("--extract-small-archives", action="store_true")
    parser.add_argument("--convert-t2", action="store_true")
    args = parser.parse_args()

    data_root = args.data_root
    processed_root = args.processed_root
    metadata_dir = processed_root / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    overview = _dataset_overview(data_root)
    _write_csv(metadata_dir / "dataset_overview.csv", overview)

    archive_rows = extract_small_archives(data_root) if args.extract_small_archives else _archive_manifest(data_root)
    _write_csv(metadata_dir / "archive_manifest.csv", archive_rows)

    local_root = data_root / "NingXia_Data"
    series = _collect_local_series(local_root)
    series_rows = [item.row(data_root) for item in series]
    _write_csv(metadata_dir / "ningxia_local_series_manifest.csv", series_rows)
    t2_rows = [row for row in series_rows if row["is_t2"]]
    t2_candidate_rows = [row for row in series_rows if row["t2_candidate"]]
    _write_csv(metadata_dir / "ningxia_local_t2_series_manifest.csv", t2_rows)
    _write_csv(metadata_dir / "ningxia_local_t2_candidate_series_manifest.csv", t2_candidate_rows)
    strict_split_summary = _write_splits(t2_rows, processed_root, args.seed, "t2_strict")
    candidate_split_summary = _write_splits(t2_candidate_rows, processed_root, args.seed, "t2_candidate")

    conversion_rows = _convert_t2_series(series, processed_root) if args.convert_t2 else []
    if conversion_rows:
        _write_csv(metadata_dir / "ningxia_local_t2_nifti_manifest.csv", conversion_rows)
    nifti_ok_rows = [row for row in conversion_rows if row.get("status") == "ok"]
    nifti_split_summary = _write_splits(nifti_ok_rows, processed_root, args.seed, "t2_nifti_ok") if nifti_ok_rows else {}

    summary = {
        "data_root": str(data_root),
        "processed_root": str(processed_root),
        "datasets": overview,
        "local_series": len(series_rows),
        "local_t2_series": len(t2_rows),
        "local_t2_candidate_series": len(t2_candidate_rows),
        "strict_t2_split": strict_split_summary,
        "t2_candidate_split": candidate_split_summary,
        "t2_nifti_ok_split": nifti_split_summary,
        "t2_nifti_converted": len([r for r in conversion_rows if r["status"] == "ok"]),
        "t2_nifti_failed": len([r for r in conversion_rows if r["status"] == "failed"]),
    }
    (metadata_dir / "prepare_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
