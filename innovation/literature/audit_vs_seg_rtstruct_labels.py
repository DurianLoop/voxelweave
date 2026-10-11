"""Public T2 RTSTRUCT ROI-name/contour inventory with no MR pixels."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

import pydicom


ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "literature/source_cache/vs_seg_official_inventory_2026-10-01/mapping.csv"
OUT = ROOT / "literature/source_cache/vs_seg_rtstruct_labels_2026-10-01"
DATA = ROOT / "data/vs_seg_rtstruct_audit"
FIRST = ROOT / "data/vs_seg_001_header_pilot/rtstruct.zip"
PARTIAL = ROOT / "data/vs_seg_thin3d_model_confirmation"
BASE = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def source_for(patient: str, uid: str) -> Path:
    candidates = ([FIRST] if patient == "VS-SEG-001" else []) + [
        PARTIAL / f"{patient}_rtstruct.zip", DATA / f"{patient}_rtstruct.zip"]
    for path in candidates:
        if path.is_file():
            return path
    if shutil.disk_usage(DATA).free < 15_000_000_000:
        raise OSError("15 GB free-space floor reached")
    url = BASE + urllib.parse.urlencode({"SeriesInstanceUID": uid})
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=60) as response:
        raw = response.read(5_000_001)
        if response.status != 200 or len(raw) > 5_000_000:
            raise ValueError("Unexpected RTSTRUCT response size/status")
    path = DATA / f"{patient}_rtstruct.zip"
    path.write_bytes(raw)
    return path


def parse(path: Path, patient: str, uid: str) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.endswith(".dcm")]
        if len(names) != 1:
            raise ValueError("Expected one T2 RTSTRUCT DICOM")
        ds = pydicom.dcmread(io.BytesIO(archive.read(names[0])), stop_before_pixels=True)
    if str(ds.PatientID) != patient or str(ds.SeriesInstanceUID) != uid:
        raise ValueError("Patient/series UID mismatch")
    name_by_number = {int(roi.ROINumber): str(roi.ROIName) for roi in ds.StructureSetROISequence}
    observations = {int(x.ReferencedROINumber):
                    {"label": str(x.get("ROIObservationLabel", "")),
                     "interpreted_type": str(x.get("RTROIInterpretedType", ""))}
                    for x in ds.get("RTROIObservationsSequence", [])}
    contour_count = {int(x.ReferencedROINumber): len(x.get("ContourSequence", []))
                     for x in ds.get("ROIContourSequence", [])}
    rois = [{"number": number, "name": name,
             "observation": observations.get(number, {}),
             "contours": contour_count.get(number, 0)}
            for number, name in sorted(name_by_number.items())]
    return {"patient": patient, "uid": uid, "source_path": path.relative_to(ROOT).as_posix(),
            "zip_bytes": path.stat().st_size, "zip_sha256": sha256(path), "rois": rois}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    DATA.mkdir(parents=True, exist_ok=True)
    with MAPPING.open(newline="", encoding="utf-8-sig") as stream:
        mapping = {r["Descriptive Directory Name"].split("/")[0]:
                   r["Classic Directory Name"].split("/")[-1]
                   for r in csv.DictReader(stream) if r["Modality"] == "T2 RTSTRUCT"}
    if len(mapping) != 242:
        raise ValueError("Official RTSTRUCT mapping denominator differs")
    cases, failures = [], []
    for index, patient in enumerate(sorted(mapping), 1):
        path = OUT / f"{patient}.json"
        try:
            case = parse(source_for(patient, mapping[patient]), patient, mapping[patient])
            path.write_text(json.dumps(case, indent=2) + "\n", encoding="utf-8")
            cases.append(case)
        except Exception as exc:
            failures.append({"patient": patient, "type": type(exc).__name__,
                             "reason": str(exc)[:200]})
        print(f"RTSTRUCT labels {index}/242 {patient} complete={path.exists()}", flush=True)
    names = Counter(roi["name"] for case in cases for roi in case["rois"])
    summary = {"attempted": 242, "completed": len(cases), "failures": failures,
               "mapping_sha256": sha256(MAPPING), "script_sha256": sha256(Path(__file__)),
               "roi_name_counts": dict(names.most_common()),
               "patients_with_exact_tv": sum(any(r["name"] == "TV" for r in c["rois"]) for c in cases),
               "patient_pixels_read": False}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
