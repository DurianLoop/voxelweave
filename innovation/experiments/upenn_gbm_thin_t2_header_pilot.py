"""Download one frozen thin-T2 UPENN series and inspect only nonpixel headers."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "UPENN_GBM_THIN_T2_HEADER_PILOT_PLAN_2026-10-01.md"
CSV_DIR = ROOT / "literature/source_cache/upenn_gbm_label_availability_2026-10-01"
SERIES = ROOT / "literature/source_cache/upenn_gbm_getSeries_2026-10-01.json"
OUT = ROOT / "literature/upenn_gbm_thin_t2_header_pilot.json"
ZIP = ROOT / "data/upenn_gbm_t2_header_pilot/first_thin_sag_space.zip"
PATIENT = "UPENN-GBM-00001"
UID = "1.3.6.1.4.1.14519.5.2.1.179890292978753819584197741746287159209"
DESCRIPTION = "T2 SAG SPACE: Processed_CaPTk"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def field(ds: pydicom.dataset.Dataset, name: str) -> str:
    value = ds.get(name, "")
    return "/".join(map(str, value)) if name == "ImageType" else str(value)


def main() -> None:
    if OUT.exists() or ZIP.exists():
        raise FileExistsError("Refusing to overwrite thin-T2 pilot")
    availability = csv.DictReader(
        io.StringIO((CSV_DIR / "data_availability.csv").read_text(encoding="utf-8-sig")))
    acquisition = {row["ID"]: row for row in csv.DictReader(
        io.StringIO((CSV_DIR / "acquisition.csv").read_text(encoding="utf-8-sig")))}
    thin = {row["ID"].split("_", 1)[0] for row in availability
            if row["Corrected Tumor Segmentation"] == "available"
            and acquisition[row["ID"]]["T2 Slice Thickness"].startswith("0.9")}
    rows = json.loads(SERIES.read_text(encoding="utf-8"))
    candidates = sorted((row for row in rows if row.get("PatientID") in thin
                         and row.get("SeriesDescription") == DESCRIPTION),
                        key=lambda row: (row["PatientID"], row["SeriesInstanceUID"]))
    if (len(thin) != 86 or len(candidates) != 83 or
            candidates[0]["PatientID"] != PATIENT or
            candidates[0]["SeriesInstanceUID"] != UID or
            int(candidates[0]["ImageCount"]) != 192):
        raise ValueError("Frozen metadata selection changed")
    url = ("https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?"
           + urllib.parse.urlencode({"SeriesInstanceUID": UID}))
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-header-only-source-gate/1.0"})
    with opener.open(request, timeout=120) as response:
        if response.status != 200:
            raise RuntimeError(f"NBIA HTTP {response.status}")
        raw = response.read()
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("Official response is not a ZIP")
    headers = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC failed")
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".dcm"))
        if len(names) != 192:
            raise ValueError(f"Expected 192 DICOM members, received {len(names)}")
        for name in names:
            with archive.open(name) as stream:
                ds = pydicom.dcmread(stream, stop_before_pixels=True)
            if "PixelData" in ds:
                raise AssertionError("PixelData loaded")
            if field(ds, "PatientID") != PATIENT or field(ds, "SeriesInstanceUID") != UID:
                raise ValueError("DICOM identity differs from frozen metadata")
            headers.append(ds)
    if len({field(ds, "SOPInstanceUID") for ds in headers}) != 192:
        raise ValueError("Duplicate SOP UID")
    orientations = np.asarray([[float(v) for v in ds.ImageOrientationPatient] for ds in headers])
    positions = np.asarray([[float(v) for v in ds.ImagePositionPatient] for ds in headers])
    spacing = np.asarray([[float(v) for v in ds.PixelSpacing] for ds in headers])
    normal = np.cross(orientations[0, :3], orientations[0, 3:])
    normal /= np.linalg.norm(normal)
    steps = np.diff(np.sort(positions @ normal))
    fields = ("ImageType", "MRAcquisitionType", "SeriesDescription", "DerivationDescription",
              "SliceThickness", "SpacingBetweenSlices", "ScanningSequence", "SequenceName")
    result = {
        "plan_sha256": sha256(PLAN.read_bytes()),
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "availability_index_sha256": sha256((CSV_DIR / "index.json").read_bytes()),
        "series_inventory_sha256": sha256(SERIES.read_bytes()),
        "url": url, "zip_path": ZIP.relative_to(ROOT).as_posix(),
        "zip_bytes": len(raw), "zip_sha256": sha256(raw),
        "patient": PATIENT, "series_uid": UID,
        "headers": len(headers), "unique_sop_uids": 192,
        "technical_values": {name: dict(Counter(field(ds, name) for ds in headers))
                             for name in fields},
        "source_image_sequence_present": sum("SourceImageSequence" in ds for ds in headers),
        "derivation_code_sequence_present": sum("DerivationCodeSequence" in ds for ds in headers),
        "rows_columns": [int(headers[0].Rows), int(headers[0].Columns)],
        "pixel_spacing_mm": spacing[0].tolist(),
        "max_orientation_component_delta": float(np.max(np.abs(orientations - orientations[0]))),
        "max_pixel_spacing_delta_mm": float(np.max(np.abs(spacing - spacing[0]))),
        "unique_projected_positions": len(set(np.round(positions @ normal, 4))),
        "physical_step_min_mm": float(steps.min()),
        "physical_step_max_mm": float(steps.max()),
        "pixel_data_read": False,
    }
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    ZIP.write_bytes(raw)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "zip_bytes", "headers", "technical_values", "source_image_sequence_present",
        "derivation_code_sequence_present", "rows_columns", "pixel_spacing_mm",
        "physical_step_min_mm", "physical_step_max_mm", "pixel_data_read")}, indent=2))


if __name__ == "__main__":
    main()
