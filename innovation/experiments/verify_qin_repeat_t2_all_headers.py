"""Independent, header-only audit of the frozen QIN repeat-T2 screen."""
from __future__ import annotations

import hashlib
import json
import math
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "literature/source_cache/qin_repeat_t2_getSeries_2026-10-01.json"
RESULT = ROOT / "literature/qin_repeat_t2_all_header_screen.json"
EXPECTED_SOURCE_HASH = "2aa9a41cd2871ac16f1cea588cf2970c32cd8152aab7e3bfd465cd0d5f2f88b5"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_headers(record: dict) -> dict:
    path = ROOT / record["archive_path"]
    assert path.is_file() and path.stat().st_size == record["zip_bytes"]
    assert digest(path) == record["zip_sha256"]
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        names = [name for name in archive.namelist() if name.lower().endswith(".dcm")]
        assert len(names) == record["expected_images"] == record["dicom_members"]
        headers = []
        for name in names:
            with archive.open(name) as stream:
                ds = pydicom.dcmread(stream, stop_before_pixels=True)
            assert "PixelData" not in ds
            assert str(ds.PatientID) == record["patient"]
            assert str(ds.StudyInstanceUID) == record["study_uid"]
            assert str(ds.SeriesInstanceUID) == record["series_uid"]
            headers.append(ds)
    assert len({str(ds.SOPInstanceUID) for ds in headers}) == len(headers)
    assert all(ds.get("AcquisitionTime") and ds.get("AcquisitionDate") for ds in headers)
    assert all(str(ds.MRAcquisitionType) == "2D" for ds in headers)
    assert all("/".join(map(str, ds.ImageType)).startswith("ORIGINAL/PRIMARY") for ds in headers)
    assert len({str(ds.StudyDate) for ds in headers}) == 1
    assert len({str(ds.AcquisitionDate) for ds in headers}) == 1
    assert len({(int(ds.Rows), int(ds.Columns)) for ds in headers}) == 1
    assert len({(float(ds.RepetitionTime), float(ds.EchoTime)) for ds in headers}) == 1
    directions = np.array([[float(v) for v in ds.ImageOrientationPatient] for ds in headers])
    spacing = np.array([[float(v) for v in ds.PixelSpacing] for ds in headers])
    assert np.max(np.abs(directions - directions[0])) <= 1e-4
    assert np.max(np.abs(spacing - spacing[0])) <= 1e-3
    position = np.array([[float(v) for v in ds.ImagePositionPatient] for ds in headers])
    normal = np.cross(directions[0, :3], directions[0, 3:])
    normal /= np.linalg.norm(normal)
    projection = position @ normal
    assert len(set(np.round(projection, 4))) == len(headers)
    order = np.argsort(projection)
    first = headers[0]
    # IPP denotes the first voxel center; the FOV center also depends on orientation and matrix.
    fov_center = (position + (int(first.Columns) - 1) * spacing[:, 1:] * directions[:, :3] / 2
                  + (int(first.Rows) - 1) * spacing[:, :1] * directions[:, 3:] / 2)
    return {
        "patient": record["patient"], "repeat": record["repeat"],
        "count": len(headers), "study_date": str(first.StudyDate),
        "acquisition_date": str(first.AcquisitionDate),
        "matrix": (int(first.Rows), int(first.Columns)),
        "orientation": directions[0], "spacing": spacing[0],
        "tr": float(first.RepetitionTime), "te": float(first.EchoTime),
        "normal": normal, "ipp": position[order], "fov_center": fov_center[order],
    }


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert digest(SOURCE) == result["official_source_sha256"] == EXPECTED_SOURCE_HASH
    assert digest(ROOT / "QIN_REPEAT_T2_ALL_HEADER_PLAN_2026-10-01.md") == result["plan_sha256"]
    assert digest(ROOT / "experiments/qin_repeat_t2_all_header_screen.py") == result["script_sha256"]
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    selected = defaultdict(list)
    for row in source:
        if row.get("Modality") == "MR" and row.get("SeriesDescription") == "T2 Weighted Axial" and int(row.get("ImageCount", 0)) >= 24:
            assert row["LicenseURI"].rstrip("/") == "https://creativecommons.org/licenses/by/4.0"
            selected[row["PatientID"]].append(row)
    assert len(selected) == 15 and all(len(rows) == 2 for rows in selected.values())
    assert len(result["downloads"]) == 30 and len(result["pairs"]) == 15
    assert result["download_or_parse_failures"] == [] and result["pixel_data_read"] is False
    by_uid = {row["series_uid"]: row for row in result["downloads"]}
    assert len(by_uid) == 30
    data = {}
    for patient, rows in selected.items():
        rows.sort(key=lambda row: (row.get("StudyDate", ""), row["SeriesInstanceUID"]))
        for repeat, row in enumerate(rows, 1):
            archive = by_uid[row["SeriesInstanceUID"]]
            assert (archive["patient"], archive["repeat"], archive["expected_images"], archive["study_uid"]) == (
                patient, repeat, int(row["ImageCount"]), row["StudyInstanceUID"])
            data[(patient, repeat)] = read_headers(archive)
    counts = Counter()
    differences = []
    for archived in result["pairs"]:
        patient = archived["patient"]
        a, b = data[(patient, 1)], data[(patient, 2)]
        assert a["study_date"] != b["study_date"] and a["acquisition_date"] != b["acquisition_date"]
        angle = math.degrees(math.acos(float(np.clip(a["normal"] @ b["normal"], -1, 1))))
        orientation = float(np.max(np.abs(a["orientation"] - b["orientation"])))
        spacing = float(np.max(np.abs(a["spacing"] - b["spacing"])))
        tr = abs(a["tr"] - b["tr"]) / max(a["tr"], b["tr"])
        te = abs(a["te"] - b["te"]) / max(a["te"], b["te"])
        reasons = []
        if a["matrix"] != b["matrix"]:
            reasons.append("matrix_mismatch")
        if spacing > .001:
            reasons.append("pixel_spacing_mismatch")
        if orientation > .0001:
            reasons.append("orientation_mismatch")
        if tr > .05:
            reasons.append("TR_mismatch")
        if te > .05:
            reasons.append("TE_mismatch")
        if a["count"] != b["count"] or np.max(np.linalg.norm(a["ipp"] - b["ipp"], axis=1)) > .5:
            reasons.append("center_grid_mismatch")
        assert set(reasons) == set(archived["failed_conditions"])
        for key, value in (("normal_angle_degrees", angle),
                           ("max_abs_orientation_component_difference", orientation),
                           ("max_pixel_spacing_difference_mm", spacing),
                           ("relative_TR_difference", tr), ("relative_TE_difference", te)):
            assert math.isclose(value, archived[key], abs_tol=1e-7)
        if a["count"] == b["count"]:
            ipp_distance = float(np.max(np.linalg.norm(a["ipp"] - b["ipp"], axis=1)))
            true_center_distance = float(np.max(np.linalg.norm(a["fov_center"] - b["fov_center"], axis=1)))
            assert math.isclose(ipp_distance, archived["max_matched_center_distance_mm"], abs_tol=1e-6)
        else:
            true_center_distance = None
        counts.update(reasons)
        differences.append({"patient": patient, "normal_angle_degrees": angle,
                            "orientation_threshold_failed": orientation > .0001,
                            "max_ipp_distance_mm": archived["max_matched_center_distance_mm"],
                            "max_fov_center_distance_mm": true_center_distance,
                            "fov_center_within_0_5_mm": true_center_distance is not None and true_center_distance <= .5})
    assert dict(counts) == result["failure_condition_counts"]
    assert result["pairs_strict_eligible"] == 0
    summary = {"status": "PASS", "official_series": 30, "patients": 15,
               "zip_sha256_verified": 30, "pixel_data_read": False,
               "strict_eligible": 0, "all_orientation_fail": all(p["orientation_threshold_failed"] for p in differences),
               "fov_center_within_0_5_mm": sum(p["fov_center_within_0_5_mm"] for p in differences),
               "pairs": differences}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
