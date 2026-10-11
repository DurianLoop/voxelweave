"""Audit a TCIA ReMIND DICOM ZIP without decoding pixel data."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pydicom


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    records = []
    with zipfile.ZipFile(source) as archive:
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".dcm"))
        if not names:
            raise ValueError("no DICOM files")
        for name in names:
            with archive.open(name) as stream:
                dataset = pydicom.dcmread(stream, stop_before_pixels=True)
            if "PixelData" in dataset:
                raise AssertionError("pixel data was read")
            orientation = np.asarray(dataset.ImageOrientationPatient, dtype=float)
            position = np.asarray(dataset.ImagePositionPatient, dtype=float)
            records.append({
                "patient": str(dataset.PatientID),
                "series_uid": str(dataset.SeriesInstanceUID),
                "study_description": str(dataset.get("StudyDescription", "")),
                "series_description": str(dataset.get("SeriesDescription", "")),
                "image_type": [str(value) for value in dataset.get("ImageType", [])],
                "rows": int(dataset.Rows),
                "columns": int(dataset.Columns),
                "pixel_spacing": [float(value) for value in dataset.PixelSpacing],
                "slice_thickness": float(dataset.get("SliceThickness", 0)),
                "orientation": orientation.tolist(),
                "position": position.tolist(),
                "instance_number": int(dataset.get("InstanceNumber", -1)),
                "sop_uid": str(dataset.SOPInstanceUID),
                "burned_in_annotation": str(dataset.get("BurnedInAnnotation", "UNKNOWN")),
            })

    orientations = np.asarray([record["orientation"] for record in records])
    reference = orientations[0]
    normal = np.cross(reference[:3], reference[3:])
    normal /= np.linalg.norm(normal)
    positions = np.asarray([record["position"] for record in records])
    projected = np.sort(positions @ normal)
    steps = np.diff(projected)
    unique_positions = len(np.unique(np.round(projected, 5)))
    payload = {
        "source": "TCIA ReMIND getImage; official SeriesInstanceUID in source audit",
        "zip_sha256": digest,
        "dicom_files": len(records),
        "unique_sop_uids": len({record["sop_uid"] for record in records}),
        "patients": sorted({record["patient"] for record in records}),
        "series_uids": sorted({record["series_uid"] for record in records}),
        "study_descriptions": sorted({record["study_description"] for record in records}),
        "series_descriptions": sorted({record["series_description"] for record in records}),
        "image_types": sorted({"/".join(record["image_type"]) for record in records}),
        "image_shapes": sorted({(record["rows"], record["columns"]) for record in records}),
        "pixel_spacings_mm": sorted({tuple(record["pixel_spacing"]) for record in records}),
        "slice_thickness_mm": sorted({record["slice_thickness"] for record in records}),
        "max_orientation_deviation": float(np.max(np.abs(orientations - reference))),
        "unique_slice_positions": unique_positions,
        "projected_step_mm": {
            "min": float(np.min(steps)),
            "median": float(np.median(steps)),
            "max": float(np.max(steps)),
            "std": float(np.std(steps)),
        },
        "instance_numbers_unique": len({record["instance_number"] for record in records}),
        "burned_in_annotation": sorted({record["burned_in_annotation"] for record in records}),
        "pixel_data_read": False,
    }
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
