"""Bounded TCIA exact-two-series transfer and DICOM header/RT reference audit."""

from __future__ import annotations

import hashlib
import io
import json
import os
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/vs_seg_001_header_pilot"
REPORT = ROOT / "literature/source_cache/vs_seg_001_two_series_headers_2026-10-01"
BASE = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?"
PATIENT = "VS-SEG-001"
SERIES = {
    "t2": ("1.3.6.1.4.1.14519.5.2.1.97824612055862366318560427964793890998", 35_000_000),
    "rtstruct": ("1.3.6.1.4.1.14519.5.2.1.100364245183930759730290495595573094436", 5_000_000),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_zip(name: str, path: Path, uid: str) -> dict:
    records, objects, sidecars = [], [], []
    with zipfile.ZipFile(path) as archive:
        members = [x for x in archive.infolist() if not x.is_dir()]
        for member in members:
            parts = Path(member.filename).parts
            if (member.filename.startswith(("/", "\\")) or ".." in parts or
                    any(":" in part for part in parts)):
                raise ValueError("Unsafe ZIP member path")
            if member.filename == "LICENSE":
                raw = archive.read(member)
                sidecars.append({"zip_member": member.filename, "bytes": len(raw),
                                 "sha256": sha256(raw)})
                continue
            if not member.filename.lower().endswith(".dcm"):
                raise ValueError("Unexpected non-DICOM ZIP member")
            limit = 2_000_000 if name == "rtstruct" else 10_000_000
            if member.file_size > limit:
                raise ValueError("Unexpected large DICOM member")
            raw = archive.read(member)
            ds = pydicom.dcmread(io.BytesIO(raw), stop_before_pixels=True, force=False)
            if str(ds.get("PatientID", "")) != PATIENT or str(ds.get("SeriesInstanceUID", "")) != uid:
                raise ValueError("Patient or series UID differs")
            records.append({"zip_member": member.filename, "bytes": len(raw),
                            "sha256": sha256(raw), "sop_instance_uid": str(ds.SOPInstanceUID)})
            objects.append(ds)
    if not objects or len({r["sop_instance_uid"] for r in records}) != len(objects):
        raise ValueError("Empty series or duplicate SOP UID")
    result = {"members": records, "sidecars": sidecars, "count": len(objects)}
    if name == "t2":
        geometry = []
        for ds in objects:
            geometry.append({
                "sop_instance_uid": str(ds.SOPInstanceUID),
                "rows": int(ds.Rows), "columns": int(ds.Columns),
                "pixel_spacing": [float(x) for x in ds.PixelSpacing],
                "slice_thickness": float(ds.SliceThickness),
                "image_position_patient": [float(x) for x in ds.ImagePositionPatient],
                "image_orientation_patient": [float(x) for x in ds.ImageOrientationPatient],
                "frame_of_reference_uid": str(ds.get("FrameOfReferenceUID", "")),
                "image_type": [str(x) for x in ds.get("ImageType", [])],
                "mr_acquisition_type": str(ds.get("MRAcquisitionType", "")),
                "scanning_sequence": [str(x) for x in ds.get("ScanningSequence", [])],
                "sequence_variant": [str(x) for x in ds.get("SequenceVariant", [])],
            })
        orientations = {tuple(x["image_orientation_patient"]) for x in geometry}
        normals = np.cross(np.array(geometry[0]["image_orientation_patient"][:3]),
                           np.array(geometry[0]["image_orientation_patient"][3:]))
        projections = sorted(float(np.dot(normals, x["image_position_patient"])) for x in geometry)
        spacings = np.diff(projections)
        result["geometry"] = geometry
        result["summary"] = {
            "rows": sorted({x["rows"] for x in geometry}),
            "columns": sorted({x["columns"] for x in geometry}),
            "pixel_spacing": sorted({tuple(x["pixel_spacing"]) for x in geometry}),
            "slice_thickness": sorted({x["slice_thickness"] for x in geometry}),
            "mr_acquisition_type": sorted({x["mr_acquisition_type"] for x in geometry}),
            "frame_of_reference_uids": sorted({x["frame_of_reference_uid"] for x in geometry}),
            "orientation_count": len(orientations),
            "unique_plane_count": len(set(round(x, 5) for x in projections)),
            "spacing_min_max": [float(spacings.min()), float(spacings.max())],
        }
    else:
        result["rtstruct"] = [{
            "sop_instance_uid": str(ds.SOPInstanceUID),
            "frame_of_reference_uid": str(ds.get("FrameOfReferenceUID", "")),
            "roi_names": [str(x.ROIName) for x in ds.get("StructureSetROISequence", [])],
            "contour_counts": [len(x.get("ContourSequence", [])) for x in ds.get("ROIContourSequence", [])],
        } for ds in objects]
    return result


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("Refusing to overwrite exact-two-series pilot")
    OUT.mkdir(parents=True)
    REPORT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for name, (uid, cap) in SERIES.items():
        url = BASE + urllib.parse.urlencode({"SeriesInstanceUID": uid})
        item = {"name": name, "url": url, "series_instance_uid": uid,
                "patient_id": PATIENT, "pixel_array_decoded": False}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
            with opener.open(req, timeout=120) as response:
                raw = response.read(cap + 1)
                item["status"] = response.status
                item["content_type"] = response.headers.get("Content-Type")
            if len(raw) > cap:
                raise ValueError("ZIP exceeded fixed size cap")
            path = OUT / f"{name}.zip"
            path.write_bytes(raw)
            item.update({"file": path.relative_to(ROOT).as_posix(),
                         "bytes": len(raw), "sha256": sha256(raw)})
            header = inspect_zip(name, path, uid)
            header_path = REPORT / f"{name}_headers.json"
            header_path.write_text(json.dumps(header, indent=2) + "\n", encoding="utf-8")
            item["header_file"] = header_path.relative_to(ROOT).as_posix()
            item["header_sha256"] = hashlib.sha256(header_path.read_bytes()).hexdigest()
            item["summary"] = header.get("summary", header.get("rtstruct"))
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
        records.append(item)
    (REPORT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
