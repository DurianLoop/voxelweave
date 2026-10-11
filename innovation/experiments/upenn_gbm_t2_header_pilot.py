"""Qualify one frozen official UPENN-GBM T2 series without reading pixels."""
from __future__ import annotations

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
PLAN = ROOT / "UPENN_GBM_T2_HEADER_PILOT_PLAN_2026-10-01.md"
SOURCE = ROOT / "literature/source_cache/upenn_gbm_getSeries_2026-10-01.json"
OUT = ROOT / "literature/upenn_gbm_t2_header_pilot.json"
ZIP = ROOT / "data/upenn_gbm_t2_header_pilot/first_axial_t2_tse.zip"
EXPECTED_SOURCE_SHA256 = "bbae9a76f75a42cc35d460448c3afa87c55119d4ee5a84b9b18179fe28908de9"
DESCRIPTION = "Axial T2 tse: Processed_CaPTk"
EXPECTED_PATIENT = "UPENN-GBM-00020"
EXPECTED_UID = "1.3.6.1.4.1.14519.5.2.1.304664131632340855252559437288625814808"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def values(ds: pydicom.dataset.Dataset, name: str) -> str:
    value = ds.get(name, "")
    if name == "ImageType":
        return "/".join(map(str, value))
    return str(value)


def main() -> None:
    if OUT.exists() or ZIP.exists():
        raise FileExistsError("Refusing to overwrite pilot evidence")
    if sha256(SOURCE.read_bytes()) != EXPECTED_SOURCE_SHA256:
        raise ValueError("Frozen official inventory changed")
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    candidates = sorted((row for row in rows if row.get("Modality") == "MR"
                         and row.get("SeriesDescription") == DESCRIPTION
                         and int(row.get("ImageCount", 0)) >= 24),
                        key=lambda row: (row["PatientID"], row.get("StudyDate", ""), row["SeriesInstanceUID"]))
    first = candidates[0]
    if (len(candidates) != 402 or len({row["PatientID"] for row in candidates}) != 374
            or first["PatientID"] != EXPECTED_PATIENT or first["SeriesInstanceUID"] != EXPECTED_UID
            or first["LicenseURI"].rstrip("/") != "https://creativecommons.org/licenses/by/4.0"):
        raise ValueError("Frozen source/pilot selection changed")
    url = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?" + urllib.parse.urlencode(
        {"SeriesInstanceUID": EXPECTED_UID})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-header-only-source-gate/1.0"})
    with opener.open(request, timeout=90) as response:
        raw = response.read()
        if response.status != 200:
            raise RuntimeError(f"Official NBIA returned HTTP {response.status}")
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("Official response was not a DICOM ZIP")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:
            raise ValueError("Downloaded ZIP CRC failed")
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".dcm"))
        if len(names) != int(first["ImageCount"]):
            raise ValueError("Official ImageCount and DICOM member count differ")
        headers = []
        for name in names:
            with archive.open(name) as stream:
                ds = pydicom.dcmread(stream, stop_before_pixels=True)
            if "PixelData" in ds:
                raise AssertionError("PixelData unexpectedly loaded")
            if (values(ds, "PatientID") != EXPECTED_PATIENT or
                    values(ds, "SeriesInstanceUID") != EXPECTED_UID or
                    values(ds, "StudyInstanceUID") != first["StudyInstanceUID"]):
                raise ValueError("DICOM identity differs from official inventory")
            headers.append(ds)
    if len({values(ds, "SOPInstanceUID") for ds in headers}) != len(headers):
        raise ValueError("Duplicate SOP Instance UID")
    orientations = np.array([[float(x) for x in ds.ImageOrientationPatient] for ds in headers])
    positions = np.array([[float(x) for x in ds.ImagePositionPatient] for ds in headers])
    spacings = np.array([[float(x) for x in ds.PixelSpacing] for ds in headers])
    normal = np.cross(orientations[0, :3], orientations[0, 3:])
    normal /= np.linalg.norm(normal)
    projections = np.sort(positions @ normal)
    steps = np.diff(projections)
    first_header = headers[0]
    fields = ("ImageType", "MRAcquisitionType", "StudyDate", "AcquisitionDate", "AcquisitionTime",
              "StudyDescription", "SeriesDescription", "DerivationDescription", "ScanningSequence",
              "SequenceName", "RepetitionTime", "EchoTime", "SliceThickness", "SpacingBetweenSlices")
    observed = {name: dict(Counter(values(ds, name) for ds in headers)) for name in fields}
    result = {"plan_sha256": sha256(PLAN.read_bytes()),
              "script_sha256": sha256(Path(__file__).read_bytes()),
              "official_source_sha256": sha256(SOURCE.read_bytes()),
              "download_url": url,
              "archive_path": ZIP.relative_to(ROOT).as_posix(),
              "zip_bytes": len(raw), "zip_sha256": sha256(raw),
              "patient": EXPECTED_PATIENT, "series_uid": EXPECTED_UID,
              "headers": len(headers), "unique_sop_uids": len(headers),
              "technical_values": observed,
              "source_image_sequence_present": sum("SourceImageSequence" in ds for ds in headers),
              "derivation_code_sequence_present": sum("DerivationCodeSequence" in ds for ds in headers),
              "rows_columns": [int(first_header.Rows), int(first_header.Columns)],
              "pixel_spacing_mm": spacings[0].tolist(),
              "max_within_series_orientation_component_difference": float(np.max(np.abs(orientations - orientations[0]))),
              "max_within_series_pixel_spacing_difference_mm": float(np.max(np.abs(spacings - spacings[0]))),
              "unique_projected_position_count": len(set(np.round(projections, 4))),
              "projected_step_min_mm": float(np.min(steps)),
              "projected_step_max_mm": float(np.max(steps)),
              "pixel_data_read": False}
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    ZIP.write_bytes(raw)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("zip_bytes", "zip_sha256", "headers", "technical_values",
                                                "source_image_sequence_present", "derivation_code_sequence_present",
                                                "rows_columns", "pixel_spacing_mm", "projected_step_min_mm",
                                                "projected_step_max_mm", "pixel_data_read")}, indent=2))


if __name__ == "__main__":
    main()
