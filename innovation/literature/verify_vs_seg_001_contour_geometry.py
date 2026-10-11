"""Independently verify T2 RTSTRUCT contours in original DICOM geometry."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data/vs_seg_001_header_pilot"
SOURCE = ROOT / "literature/source_cache/vs_seg_001_two_series_headers_2026-10-01/index.json"
OUT = ROOT / "literature/source_cache/vs_seg_001_contour_geometry_2026-10-01.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_dicom(zip_path: Path) -> list:
    with zipfile.ZipFile(zip_path) as archive:
        return [pydicom.dcmread(io.BytesIO(archive.read(name)), stop_before_pixels=True)
                for name in archive.namelist() if name.endswith(".dcm")]


def verify() -> dict:
    if OUT.exists():
        raise FileExistsError(OUT)
    index = json.loads(SOURCE.read_text(encoding="utf-8"))
    for item in index:
        if sha256(ROOT / item["file"]) != item["sha256"]:
            raise ValueError("Official ZIP hash changed")
    images = read_dicom(PILOT / "t2.zip")
    structure, = read_dicom(PILOT / "rtstruct.zip")
    image_by_uid = {str(ds.SOPInstanceUID): ds for ds in images}
    if len(images) != 80 or len(image_by_uid) != 80:
        raise ValueError("Expected 80 distinct T2 images")
    names = {int(x.ROINumber): str(x.ROIName) for x in structure.StructureSetROISequence}
    rois = []
    for roi in structure.ROIContourSequence:
        name = names[int(roi.ReferencedROINumber)]
        distances, rows, columns, referenced = [], [], [], []
        for contour in roi.ContourSequence:
            if str(contour.ContourGeometricType) != "CLOSED_PLANAR":
                raise ValueError("Nonplanar contour")
            refs = contour.get("ContourImageSequence", [])
            if len(refs) != 1 or str(refs[0].ReferencedSOPInstanceUID) not in image_by_uid:
                raise ValueError("Contour does not reference one T2 SOP")
            ds = image_by_uid[str(refs[0].ReferencedSOPInstanceUID)]
            reference = np.asarray(ds.ImagePositionPatient, dtype=np.float64)
            orientation = np.asarray(ds.ImageOrientationPatient, dtype=np.float64)
            column_direction, row_direction = orientation[:3], orientation[3:]
            normal = np.cross(column_direction, row_direction)
            points = np.asarray(contour.ContourData, dtype=np.float64).reshape(-1, 3)
            if len(points) != int(contour.NumberOfContourPoints):
                raise ValueError("Contour point count differs")
            delta = points - reference
            distances.extend(np.abs(delta @ normal).tolist())
            rows.extend((delta @ row_direction / float(ds.PixelSpacing[0])).tolist())
            columns.extend((delta @ column_direction / float(ds.PixelSpacing[1])).tolist())
            referenced.append(str(ds.SOPInstanceUID))
        result = {"roi": name, "contours": len(roi.ContourSequence),
                  "unique_t2_slices": len(set(referenced)),
                  "points": len(distances),
                  "max_plane_distance_mm": max(distances),
                  "row_coordinate_range": [min(rows), max(rows)],
                  "column_coordinate_range": [min(columns), max(columns)],
                  "all_points_in_pixel_fov": min(rows) >= -.5 and max(rows) <= int(images[0].Rows) - .5 and
                                            min(columns) >= -.5 and max(columns) <= int(images[0].Columns) - .5}
        if result["max_plane_distance_mm"] > 1e-3 or (name == "TV" and not result["all_points_in_pixel_fov"]):
            raise ValueError(f"ROI contour geometry invalid: {name}")
        rois.append(result)
    if not any(x["roi"] == "TV" and x["contours"] >= 4 for x in rois):
        raise ValueError("No usable tumor contour")
    return {"patient": "VS-SEG-001", "source_index_sha256": sha256(SOURCE),
            "image_sops": len(images), "rois": rois, "t2_tumor_contour_gate": True,
            "patient_pixels_read": False}


if __name__ == "__main__":
    result = verify()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
