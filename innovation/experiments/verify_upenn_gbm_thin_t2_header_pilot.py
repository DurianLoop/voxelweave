"""Independent read-only check of the UPENN thin-T2 header pilot."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "literature/upenn_gbm_thin_t2_header_pilot.json"
PLAN = ROOT / "UPENN_GBM_THIN_T2_HEADER_PILOT_PLAN_2026-10-01.md"
RUNNER = ROOT / "experiments/upenn_gbm_thin_t2_header_pilot.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    archive_path = ROOT / result["zip_path"]
    assert result["plan_sha256"] == sha256(PLAN)
    assert result["script_sha256"] == sha256(RUNNER)
    assert result["zip_sha256"] == sha256(archive_path)
    assert result["zip_bytes"] == archive_path.stat().st_size
    assert result["headers"] == result["unique_sop_uids"] == 192
    assert result["pixel_data_read"] is False
    positions = []
    orientations = []
    sop_uids = set()
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        names = [name for name in archive.namelist() if name.lower().endswith(".dcm")]
        assert len(names) == 192
        for name in names:
            with archive.open(name) as stream:
                ds = pydicom.dcmread(stream, stop_before_pixels=True)
            assert "PixelData" not in ds
            assert str(ds.PatientID) == result["patient"]
            assert str(ds.SeriesInstanceUID) == result["series_uid"]
            assert list(map(str, ds.ImageType)) == ["DERIVED", "SECONDARY", "OTHER"]
            assert str(ds.MRAcquisitionType) == "3D"
            assert np.isclose(float(ds.SliceThickness), .9, atol=1e-6)
            sop_uids.add(str(ds.SOPInstanceUID))
            orientations.append([float(value) for value in ds.ImageOrientationPatient])
            positions.append([float(value) for value in ds.ImagePositionPatient])
    assert len(sop_uids) == 192
    orientations = np.asarray(orientations)
    positions = np.asarray(positions)
    assert np.max(np.abs(orientations - orientations[0])) < 1e-6
    normal = np.cross(orientations[0, :3], orientations[0, 3:])
    normal /= np.linalg.norm(normal)
    projected = np.sort(positions @ normal)
    steps = np.diff(projected)
    assert np.all(steps > 0)
    assert np.isclose(steps.min(), result["physical_step_min_mm"], atol=1e-6)
    assert np.isclose(steps.max(), result["physical_step_max_mm"], atol=1e-6)
    assert np.allclose(steps, .9, atol=1e-5)
    print("PASS: 192 CRC-valid, uniquely identified nonpixel headers; "
          "3D derived/secondary, physical step 0.9 mm")


if __name__ == "__main__":
    main()
