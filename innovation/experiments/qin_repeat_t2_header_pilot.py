"""Read only the two frozen QIN series' public DICOM technical headers."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[2] / "innovation"
PLAN = ROOT / "QIN_REPEAT_T2_HEADER_PILOT_PLAN_2026-10-01.md"
DOWNLOADS = ROOT / "literature/qin_repeat_t2_pilot_download_manifest.json"
OUT = ROOT / "literature/qin_repeat_t2_header_pilot.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def numeric(ds: pydicom.dataset.Dataset, name: str) -> float | None:
    value = ds.get(name)
    return float(value) if value is not None else None


def read_series(record: dict) -> tuple[dict, np.ndarray, np.ndarray]:
    path = ROOT / record["archive_path"]
    if sha256(path) != record["zip_sha256"]:
        raise ValueError("ZIP hash changed")
    datasets = []
    with zipfile.ZipFile(path) as archive:
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".dcm"))
        if len(names) != record["expected_images"]:
            raise ValueError(f"DICOM count {len(names)} != {record['expected_images']}")
        for name in names:
            with archive.open(name) as stream:
                ds = pydicom.dcmread(stream, stop_before_pixels=True)
            if "PixelData" in ds:
                raise AssertionError("PixelData unexpectedly decoded")
            datasets.append(ds)
    if len({str(ds.SOPInstanceUID) for ds in datasets}) != len(datasets):
        raise ValueError("duplicate SOPInstanceUID")
    if any(str(ds.get("PatientID", "")) != record["patient"] or
           str(ds.get("StudyInstanceUID", "")) != record["study_uid"] or
           str(ds.get("SeriesInstanceUID", "")) != record["series_uid"]
           for ds in datasets):
        raise ValueError("DICOM identity does not match official inventory")
    orientation = np.array([list(map(float, ds.ImageOrientationPatient)) for ds in datasets])
    position = np.array([list(map(float, ds.ImagePositionPatient)) for ds in datasets])
    spacing = np.array([list(map(float, ds.PixelSpacing)) for ds in datasets])
    row, col = orientation[0, :3], orientation[0, 3:]
    normal = np.cross(row, col)
    normal /= np.linalg.norm(normal)
    projected = position @ normal
    if len(np.unique(np.round(projected, 4))) != len(projected):
        raise ValueError("duplicate physical plane centers")
    if np.max(np.abs(orientation - orientation[0])) > 1e-4:
        raise ValueError("orientation varies within series")
    if np.max(np.abs(spacing - spacing[0])) > 1e-3:
        raise ValueError("pixel spacing varies within series")
    order = np.argsort(projected)
    ordered = position[order]
    steps = np.diff(np.sort(projected))
    first = datasets[0]
    info = {
        "repeat": record["repeat"], "dicom_headers": len(datasets),
        "image_types": sorted({"/".join(map(str, ds.get("ImageType", []))) for ds in datasets}),
        "acquisition_types": sorted({str(ds.get("MRAcquisitionType", "")) for ds in datasets}),
        "study_dates": sorted({str(ds.get("StudyDate", "")) for ds in datasets}),
        "acquisition_dates": sorted({str(ds.get("AcquisitionDate", "")) for ds in datasets}),
        "acquisition_times_present": sum(bool(ds.get("AcquisitionTime")) for ds in datasets),
        "rows": int(first.Rows), "columns": int(first.Columns),
        "pixel_spacing_mm": spacing[0].tolist(),
        "slice_thickness_mm": numeric(first, "SliceThickness"),
        "spacing_between_slices_mm": numeric(first, "SpacingBetweenSlices"),
        "orientation": orientation[0].tolist(), "normal": normal.tolist(),
        "projected_step_min_mm": float(np.min(steps)),
        "projected_step_max_mm": float(np.max(steps)),
        "repetition_time_ms": numeric(first, "RepetitionTime"),
        "echo_time_ms": numeric(first, "EchoTime"),
        "scanning_sequence": str(first.get("ScanningSequence", "")),
    }
    return info, ordered, orientation[0]


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    downloads = json.loads(DOWNLOADS.read_text(encoding="utf-8"))
    records = downloads["records"]
    if len(records) != 2 or [r["patient"] for r in records] != ["PCAMPMRI-00001"] * 2:
        raise ValueError("frozen pilot selection changed")
    first, centers1, orientation1 = read_series(records[0])
    second, centers2, orientation2 = read_series(records[1])
    normal1 = np.array(first["normal"])
    normal2 = np.array(second["normal"])
    normal_angle = float(np.degrees(np.arccos(np.clip(np.dot(normal1, normal2), -1, 1))))
    center_distances = np.linalg.norm(centers1 - centers2, axis=1)
    orientation_diff = float(np.max(np.abs(orientation1 - orientation2)))
    spacing_diff = float(np.max(np.abs(np.array(first["pixel_spacing_mm"]) -
                                       np.array(second["pixel_spacing_mm"]))))
    tr1, tr2 = first["repetition_time_ms"], second["repetition_time_ms"]
    te1, te2 = first["echo_time_ms"], second["echo_time_ms"]
    tr_relative = abs(tr1 - tr2) / max(tr1, tr2) if tr1 and tr2 else None
    te_relative = abs(te1 - te2) / max(te1, te2) if te1 and te2 else None
    failures = []
    if first["study_dates"] == second["study_dates"] or first["acquisition_dates"] == second["acquisition_dates"]:
        failures.append("no_distinct_study_and_acquisition_dates")
    if not first["acquisition_times_present"] or not second["acquisition_times_present"]:
        failures.append("missing_acquisition_time")
    if any(info["acquisition_types"] != ["2D"] or
           not all(t.startswith("ORIGINAL/PRIMARY") for t in info["image_types"])
           for info in (first, second)):
        failures.append("not_original_primary_2d")
    if (first["rows"], first["columns"]) != (second["rows"], second["columns"]):
        failures.append("matrix_mismatch")
    if spacing_diff > 1e-3:
        failures.append("pixel_spacing_mismatch")
    if orientation_diff > 1e-4:
        failures.append("orientation_mismatch")
    if tr_relative is None or tr_relative > 0.05:
        failures.append("TR_mismatch")
    if te_relative is None or te_relative > 0.05:
        failures.append("TE_mismatch")
    if np.max(center_distances) > 0.5:
        failures.append("center_grid_mismatch")
    result = {
        "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
        "download_manifest_sha256": sha256(DOWNLOADS), "series": [first, second],
        "comparison": {
            "normal_angle_degrees": normal_angle,
            "max_abs_orientation_component_difference": orientation_diff,
            "max_pixel_spacing_difference_mm": spacing_diff,
            "relative_TR_difference": tr_relative,
            "relative_TE_difference": te_relative,
            "max_matched_center_distance_mm": float(np.max(center_distances)),
            "median_matched_center_distance_mm": float(np.median(center_distances))},
        "strict_header_eligible": not failures, "failed_conditions": failures,
        "pixel_data_read": False}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
