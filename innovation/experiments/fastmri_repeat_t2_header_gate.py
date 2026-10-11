"""Header-only local repeated-T2 feasibility screen; never decodes pixels."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "innovation/FASTMRI_REPEAT_T2_HEADER_GATE_PLAN_2026-10-01.md"
MANIFEST = ROOT / "dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_series_manifest.csv"
MANIFEST_SHA = "042730d2802b4b01326d6f297e6bd46e76d5a56d7b044fe60c87d8ccf41c5c2d"
DATA_ROOT = (ROOT / "dataset/fastMRI_brain_DICOM").resolve()
OUT = ROOT / "innovation/experiments/fastmri_repeat_t2_header_gate"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest() -> list[dict[str, str]]:
    if sha256(MANIFEST) != MANIFEST_SHA:
        raise ValueError("T2 series manifest hash changed")
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def number(ds: pydicom.dataset.Dataset, name: str) -> float | None:
    value = getattr(ds, name, None)
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def vector(ds: pydicom.dataset.Dataset, name: str, size: int) -> tuple[float, ...] | None:
    value = getattr(ds, name, None)
    if value is None or len(value) != size:
        return None
    try:
        numbers = tuple(float(x) for x in value)
    except (TypeError, ValueError):
        return None
    return numbers if all(math.isfinite(x) for x in numbers) else None


def seconds(value: object) -> float | None:
    if value is None:
        return None
    digits = str(value).split(".", 1)
    whole = digits[0]
    if not re.fullmatch(r"\d{6}", whole):
        return None
    hour, minute, second = int(whole[:2]), int(whole[2:4]), int(whole[4:6])
    if hour > 23 or minute > 59 or second > 60:
        return None
    fraction = float("0." + digits[1]) if len(digits) == 2 and digits[1].isdigit() else 0.0
    return hour * 3600 + minute * 60 + second + fraction


def stable(values: list[object], tolerance: float | None = None) -> object | None:
    if not values or any(value is None for value in values):
        return None
    first = values[0]
    if tolerance is None:
        return first if all(value == first for value in values) else None
    if isinstance(first, tuple):
        return first if all(max(abs(a - b) for a, b in zip(first, value)) <= tolerance
                            for value in values) else None
    return first if all(abs(value - first) <= tolerance for value in values) else None


def describe_series(headers: list[pydicom.dataset.Dataset]) -> dict:
    first = headers[0]
    orientation = stable([vector(ds, "ImageOrientationPatient", 6) for ds in headers], 1e-4)
    spacing = stable([vector(ds, "PixelSpacing", 2) for ds in headers], 0.01)
    thickness = stable([number(ds, "SliceThickness") for ds in headers], 0.1)
    echo = stable([number(ds, "EchoTime") for ds in headers], 1.0)
    repetition = stable([number(ds, "RepetitionTime") for ds in headers], 10.0)
    frame = stable([str(getattr(ds, "FrameOfReferenceUID", "")) or None for ds in headers])
    shape = stable([(int(getattr(ds, "Rows", 0)), int(getattr(ds, "Columns", 0))) for ds in headers])
    types = [tuple(str(x).upper() for x in getattr(ds, "ImageType", [])) for ds in headers]
    original_2d = all("ORIGINAL" in t and "PRIMARY" in t and
                      str(getattr(ds, "MRAcquisitionType", "")).upper() == "2D"
                      for ds, t in zip(headers, types))
    sop = [str(getattr(ds, "SOPInstanceUID", "")) for ds in headers]
    positions = [vector(ds, "ImagePositionPatient", 3) for ds in headers]
    coordinates = None
    if orientation is not None and all(pos is not None for pos in positions):
        normal = np.cross(np.array(orientation[:3]), np.array(orientation[3:]))
        if np.linalg.norm(normal) > 0:
            normal /= np.linalg.norm(normal)
            coordinates = sorted(float(np.dot(normal, pos)) for pos in positions)
    distinct_positions = (coordinates is not None and len(coordinates) == 16 and
                          all(b - a > 0.1 for a, b in zip(coordinates, coordinates[1:])))
    series_times = [seconds(getattr(ds, "SeriesTime", None)) for ds in headers]
    acquisition_times = [seconds(getattr(ds, "AcquisitionTime", None)) for ds in headers]
    time = stable(series_times)
    if time is None:
        present = [x for x in acquisition_times if x is not None]
        time = float(np.median(present)) if len(present) == len(headers) else None
    label = str(getattr(first, "SeriesDescription", "")).lower()
    return {
        "t2_label": "t2" in label,
        "repeat_label": "repeat" in label,
        "planes": len(headers),
        "original_primary_2d": original_2d,
        "unique_sop": len(set(sop)) == len(headers) and all(sop),
        "distinct_positions": distinct_positions,
        "orientation": orientation,
        "spacing": spacing,
        "thickness": thickness,
        "echo": echo,
        "repetition": repetition,
        "frame": frame,
        "shape": shape,
        "time": time,
        "coordinates": coordinates,
        "sop_set": set(sop),
    }


def compare(left: dict, right: dict) -> dict:
    reasons = []
    if not left["t2_label"] or not right["t2_label"]:
        reasons.append("not_two_T2_labeled_series")
    if left["planes"] != 16 or right["planes"] != 16:
        reasons.append("not_16_planes_each")
    if not (left["original_primary_2d"] and right["original_primary_2d"]):
        reasons.append("not_both_original_primary_2D")
    if not (left["unique_sop"] and right["unique_sop"]) or left["sop_set"] & right["sop_set"]:
        reasons.append("SOP_identity_not_distinct")
    if not (left["distinct_positions"] and right["distinct_positions"]):
        reasons.append("invalid_plane_positions")
    if left["frame"] is None or left["frame"] != right["frame"]:
        reasons.append("frame_mismatch_or_missing")
    if left["shape"] is None or left["shape"] != right["shape"]:
        reasons.append("matrix_mismatch_or_missing")
    for name, tolerance in (("orientation", 1e-4), ("spacing", 0.01),
                            ("thickness", 0.1), ("echo", 1.0), ("repetition", 10.0)):
        a, b = left[name], right[name]
        if a is None or b is None:
            reasons.append(f"{name}_missing_or_unstable")
        elif isinstance(a, tuple):
            if max(abs(x - y) for x, y in zip(a, b)) > tolerance:
                reasons.append(f"{name}_mismatch")
        elif abs(a - b) > tolerance:
            reasons.append(f"{name}_mismatch")
    max_position_difference = None
    if left["coordinates"] is not None and right["coordinates"] is not None and len(left["coordinates"]) == len(right["coordinates"]):
        max_position_difference = max(abs(a - b) for a, b in zip(left["coordinates"], right["coordinates"]))
        if max_position_difference > 0.1:
            reasons.append("slice_centers_mismatch")
    else:
        reasons.append("slice_centers_missing")
    time_difference = None
    if left["time"] is None or right["time"] is None:
        reasons.append("time_missing")
    else:
        time_difference = abs(left["time"] - right["time"])
        if time_difference < 1:
            reasons.append("series_time_not_distinct")
    return {"header_compatible": not reasons,
            "max_slice_center_difference_mm": max_position_difference,
            "series_time_difference_seconds": time_difference,
            "reasons": reasons}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    manifest = read_manifest()
    selected_ids = sorted({row["case_id"] for row in manifest
                           if "repeat" in row["series_label"].lower()})
    if len(selected_ids) != 7:
        raise ValueError("repeat-label case count changed")
    case_rows = []
    pair_rows = []
    total_files = 0
    for index, case_id in enumerate(selected_ids, start=1):
        case_dir = (DATA_ROOT / case_id).resolve()
        if case_dir.parent != DATA_ROOT or not case_dir.is_dir():
            raise ValueError("candidate directory outside expected source")
        files = sorted(case_dir.glob("*.dcm"))
        if len(files) not in (32, 48):
            raise ValueError("candidate DICOM count changed")
        total_files += len(files)
        groups = defaultdict(list)
        for path in files:
            ds = pydicom.dcmread(str(path), stop_before_pixels=True)
            uid = str(getattr(ds, "SeriesInstanceUID", ""))
            if not uid:
                raise ValueError("missing SeriesInstanceUID")
            groups[uid].append(ds)
        descriptions = [describe_series(groups[uid]) for uid in sorted(groups)]
        ordinal = f"candidate_{index:02d}"
        case_rows.append({"candidate": ordinal, "dicom_headers": len(files),
                          "series": len(groups),
                          "t2_labeled_series": sum(s["t2_label"] for s in descriptions),
                          "repeat_labeled_series": sum(s["repeat_label"] for s in descriptions),
                          "original_primary_2d_series": sum(s["original_primary_2d"] for s in descriptions)})
        for (i, left), (j, right) in itertools.combinations(enumerate(descriptions, start=1), 2):
            comparison = compare(left, right)
            pair_rows.append({"candidate": ordinal, "series_a": i, "series_b": j,
                              "both_T2_labeled": left["t2_label"] and right["t2_label"],
                              "one_repeat_labeled": left["repeat_label"] or right["repeat_label"],
                              **comparison})
    summary = {"status": "header-only technical feasibility; rights unresolved",
               "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
               "manifest_sha256": MANIFEST_SHA,
               "cases": len(case_rows), "dicom_headers_read": total_files,
               "series": sum(row["series"] for row in case_rows),
               "T2_pairs": sum(row["both_T2_labeled"] for row in pair_rows),
               "header_compatible_T2_pairs": sum(row["both_T2_labeled"] and row["header_compatible"]
                                                 for row in pair_rows),
               "case_rows": case_rows, "pair_rows": pair_rows}
    OUT.mkdir(parents=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("cases", "dicom_headers_read", "series", "T2_pairs", "header_compatible_T2_pairs")}, indent=2))


if __name__ == "__main__":
    main()
