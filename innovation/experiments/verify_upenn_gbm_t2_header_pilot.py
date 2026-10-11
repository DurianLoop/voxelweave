"""Read-only ZIP and DICOM-header verification for UPENN-GBM pilot."""
from __future__ import annotations

import hashlib
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "literature/upenn_gbm_t2_header_pilot.json"
SOURCE = ROOT / "literature/source_cache/upenn_gbm_getSeries_2026-10-01.json"
PLAN = ROOT / "UPENN_GBM_T2_HEADER_PILOT_PLAN_2026-10-01.md"
SCRIPT = ROOT / "experiments/upenn_gbm_t2_header_pilot.py"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["plan_sha256"] == digest(PLAN)
    assert result["script_sha256"] == digest(SCRIPT)
    assert result["official_source_sha256"] == digest(SOURCE)
    archive_path = ROOT / result["archive_path"]
    assert archive_path.stat().st_size == result["zip_bytes"]
    assert digest(archive_path) == result["zip_sha256"]
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    source = next(row for row in rows if row["SeriesInstanceUID"] == result["series_uid"])
    assert source["PatientID"] == result["patient"] and int(source["ImageCount"]) == 64
    orientation, position, types, acquisition_types = [], [], [], []
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        names = [name for name in archive.namelist() if name.lower().endswith(".dcm")]
        assert len(names) == 64
        sop = set()
        for name in names:
            with archive.open(name) as stream:
                ds = pydicom.dcmread(stream, stop_before_pixels=True)
            assert "PixelData" not in ds
            assert str(ds.PatientID) == result["patient"]
            assert str(ds.SeriesInstanceUID) == result["series_uid"]
            assert str(ds.StudyInstanceUID) == source["StudyInstanceUID"]
            sop.add(str(ds.SOPInstanceUID))
            types.append("/".join(map(str, ds.ImageType)))
            acquisition_types.append(str(ds.MRAcquisitionType))
            orientation.append([float(v) for v in ds.ImageOrientationPatient])
            position.append([float(v) for v in ds.ImagePositionPatient])
            assert (int(ds.Rows), int(ds.Columns)) == tuple(result["rows_columns"])
            assert [float(v) for v in ds.PixelSpacing] == result["pixel_spacing_mm"]
            assert math.isclose(float(ds.SliceThickness), 3, abs_tol=1e-6)
            assert math.isclose(float(ds.SpacingBetweenSlices), 1, abs_tol=1e-6)
    assert len(sop) == 64
    assert set(types) == {"DERIVED/SECONDARY/OTHER"}
    assert set(acquisition_types) == {"2D"}
    direction = np.array(orientation)
    ipp = np.array(position)
    assert np.max(np.abs(direction - direction[0])) <= 1e-4
    normal = np.cross(direction[0, :3], direction[0, 3:])
    normal /= np.linalg.norm(normal)
    centers = np.sort(ipp @ normal)
    steps = np.diff(centers)
    assert len(set(np.round(centers, 4))) == 64
    assert math.isclose(float(np.min(steps)), result["projected_step_min_mm"], abs_tol=1e-5)
    assert math.isclose(float(np.max(steps)), result["projected_step_max_mm"], abs_tol=1e-5)
    assert np.max(np.abs(steps - 3)) < 1e-3
    print(json.dumps({"status": "PASS", "zip_sha256_verified": True,
                      "dicom_headers": 64, "derived_secondary": 64,
                      "projected_spacing_mm": 3,
                      "tag_spacing_between_slices_mm": 1,
                      "pixel_data_read": False}, indent=2))


if __name__ == "__main__":
    main()
