"""Recheck the stopped run's VS-SEG-010 spacing failure without pixel decoding."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/vs_seg_thin3d_model_confirmation/VS-SEG-010_t2.zip"
OUT = ROOT / "experiments/vs_seg_010_header_spacing_check_2026-10-01.json"


def main() -> None:
    with zipfile.ZipFile(SOURCE) as archive:
        members = [x for x in archive.infolist() if x.filename.lower().endswith(".dcm")]
        headers = [pydicom.dcmread(io.BytesIO(archive.read(x)), stop_before_pixels=True) for x in members]
    orientation = np.asarray(headers[0].ImageOrientationPatient, dtype=float)
    normal = np.cross(orientation[:3], orientation[3:])
    positions = sorted(float(np.dot(normal, np.asarray(x.ImagePositionPatient, dtype=float))) for x in headers)
    steps = np.diff(positions)
    result = {"patient": "VS-SEG-010", "source": SOURCE.relative_to(ROOT).as_posix(),
              "instances": len(headers), "acquisition_types": sorted({str(x.get("MRAcquisitionType", "")) for x in headers}),
              "slice_thickness_mm": sorted({float(x.SliceThickness) for x in headers}),
              "min_plane_spacing_mm": float(steps.min()), "max_plane_spacing_mm": float(steps.max()),
              "median_plane_spacing_mm": float(np.median(steps)),
              "first_three_steps_mm": steps[:3].tolist(),
              "uniform_to_0_0001_mm": bool(np.allclose(steps, steps[0], rtol=0, atol=1e-4)),
              "original_1_to_1_5_mm_gate": bool(1 <= steps[0] <= 1.5 and np.allclose(steps, steps[0], rtol=0, atol=1e-4)),
              "patient_pixels_read": False}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
