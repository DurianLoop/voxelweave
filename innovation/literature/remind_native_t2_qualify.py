"""Freeze ReMIND 2D T2 patient/target eligibility from DICOM headers only."""
from __future__ import annotations

import hashlib
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "literature/remind_native_t2_inventory.json"
DOWNLOADS = ROOT / "literature/remind_native_t2_download_manifest.json"
PROTOCOL = ROOT / "REMIND_NATIVE_T2_CONFIRMATION_PROTOCOL_2026-10-01.md"
OUTPUT = ROOT / "literature/remind_native_t2_qualification.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def targets_for_depth(depth: int) -> dict[str, list[int]]:
    phases = (list(range(0, depth, 4)), list(range(2, depth, 4)))
    chosen = {}
    for residue in (1, 3):
        eligible = [
            z for z in range(depth) if z % 4 == residue
            and all(sum(anchor < z for anchor in phase) >= 2
                    and sum(anchor > z for anchor in phase) >= 2 for phase in phases)
        ]
        if len(eligible) < 2:
            raise ValueError(f"fewer than two eligible residue-{residue} targets")
        lower = math.floor((len(eligible) - 1) / 3)
        upper = math.ceil(2 * (len(eligible) - 1) / 3)
        if lower == upper:
            raise ValueError(f"duplicate selected residue-{residue} targets")
        chosen[str(residue)] = [eligible[lower], eligible[upper]]
    return chosen


def qualify(item: dict, downloaded: dict) -> dict:
    path = ROOT / downloaded["path"]
    if sha256(path) != downloaded["zip_sha256"]:
        raise ValueError("ZIP SHA-256 changed")
    headers = []
    with zipfile.ZipFile(path) as archive:
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".dcm"))
        if len(names) != item["image_count"]:
            raise ValueError("DICOM count changed")
        for name in names:
            with archive.open(name) as stream:
                ds = pydicom.dcmread(stream, stop_before_pixels=True)
            if "PixelData" in ds:
                raise AssertionError("pixel data read during qualification")
            if str(ds.PatientID) != item["patient"] or str(ds.SeriesInstanceUID) != item["series_uid"]:
                raise ValueError("patient or series UID mismatch")
            if str(ds.StudyInstanceUID) != item["study_uid"]:
                raise ValueError("study UID mismatch")
            if str(ds.get("StudyDescription", "")) != "Preop":
                raise ValueError("not preoperative")
            if str(ds.get("SeriesDescription", "")) != item["series_description"]:
                raise ValueError("series description mismatch")
            if str(ds.get("PhotometricInterpretation", "")) != "MONOCHROME2" or int(ds.SamplesPerPixel) != 1:
                raise ValueError("not single-channel MONOCHROME2")
            headers.append({
                "filename": name,
                "sop_uid": str(ds.SOPInstanceUID),
                "orientation": np.asarray(ds.ImageOrientationPatient, dtype=float),
                "position": np.asarray(ds.ImagePositionPatient, dtype=float),
                "spacing": np.asarray(ds.PixelSpacing, dtype=float),
                "shape": (int(ds.Rows), int(ds.Columns)),
                "image_type": "/".join(str(value) for value in ds.get("ImageType", [])),
                "slice_thickness": float(ds.get("SliceThickness", 0)),
            })
    if len(headers) < 24 or len({header["sop_uid"] for header in headers}) != len(headers):
        raise ValueError("too few layers or duplicate SOP UID")
    if len({header["shape"] for header in headers}) != 1:
        raise ValueError("inconsistent image shape")
    orientations = np.asarray([header["orientation"] for header in headers])
    if not np.isfinite(orientations).all() or np.max(np.abs(orientations - orientations[0])) > 1e-4:
        raise ValueError("inconsistent orientation")
    normal = np.cross(orientations[0, :3], orientations[0, 3:])
    norm = float(np.linalg.norm(normal))
    if not np.isfinite(norm) or norm < 0.99:
        raise ValueError("invalid orientation normal")
    normal /= norm
    spacings = np.asarray([header["spacing"] for header in headers])
    if not np.isfinite(spacings).all() or np.any(spacings <= 0):
        raise ValueError("invalid pixel spacing")
    if np.max(np.abs(spacings / spacings[0] - 1)) > .005:
        raise ValueError("inconsistent pixel spacing")
    projections = np.asarray([header["position"] @ normal for header in headers])
    if not np.isfinite(projections).all():
        raise ValueError("nonfinite slice position")
    order = np.argsort(projections)
    steps = np.diff(projections[order])
    median = float(np.median(steps))
    if median <= 0 or np.any(steps <= 0) or np.max(np.abs(steps / median - 1)) > .02:
        raise ValueError("duplicate or nonuniform slice positions")
    chosen = targets_for_depth(len(headers))
    return {
        "eligible": True,
        "reason": "",
        "zip_sha256": downloaded["zip_sha256"],
        "path": downloaded["path"],
        "depth": len(headers),
        "shape": list(headers[0]["shape"]),
        "pixel_spacing_mm": spacings[0].tolist(),
        "z_spacing_mm": median,
        "max_step_relative_deviation": float(np.max(np.abs(steps / median - 1))),
        "image_types": sorted({header["image_type"] for header in headers}),
        "slice_thickness_mm": sorted({header["slice_thickness"] for header in headers}),
        "targets": chosen,
        "ordered_files": [headers[index]["filename"] for index in order],
    }


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    downloads = json.loads(DOWNLOADS.read_text(encoding="utf-8"))
    by_patient = {record["patient"]: record for record in downloads["records"]}
    records = []
    for item in inventory["series"]:
        base = {"patient": item["patient"], "series_uid": item["series_uid"],
                "series_description": item["series_description"]}
        if item["patient"] not in by_patient:
            result = {"eligible": False, "reason": "download_missing"}
        else:
            try:
                result = qualify(item, by_patient[item["patient"]])
            except (OSError, ValueError, KeyError, AttributeError, TypeError, zipfile.BadZipFile) as error:
                result = {"eligible": False, "reason": f"{type(error).__name__}: {error}"}
        records.append({**base, **result})
        print(f"{len(records)}/63 {item['patient']} {'ELIGIBLE' if result['eligible'] else result['reason']}", flush=True)
    counts = {name: sum(row["eligible"] and row["series_description"] == name for row in records)
              for name in inventory["protocol_counts"]}
    payload = {
        "inventory_sha256": sha256(INVENTORY),
        "download_manifest_sha256": sha256(DOWNLOADS),
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "patients_expected": 63,
        "patients_header_eligible": sum(row["eligible"] for row in records),
        "eligible_by_protocol": counts,
        "pixel_data_read": False,
        "records": records,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("patients_header_eligible", "eligible_by_protocol")}, indent=2))


if __name__ == "__main__":
    main()
