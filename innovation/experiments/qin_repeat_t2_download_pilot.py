"""Download only the two frozen public QIN T2 series; do not decode pixels."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INNOVATION = ROOT / "innovation"
OUT = INNOVATION / "data/qin_prostate_repeat_t2"
RAW = INNOVATION / "literature/source_cache/qin_repeat_t2_getSeries_2026-10-01.json"
MANIFEST = INNOVATION / "literature/qin_repeat_t2_pilot_download_manifest.json"
COLLECTION = "QIN-PROSTATE-Repeatability"
PATIENT = "PCAMPMRI-00001"
UIDS = (
    "1.3.6.1.4.1.14519.5.2.1.3671.4754.983460207615355998147518323000",
    "1.3.6.1.4.1.14519.5.2.1.3671.4754.609837242670719860929372097937",
)
API = "https://services.cancerimagingarchive.net/nbia-api/services/v1/"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    if OUT.exists() or RAW.exists() or MANIFEST.exists():
        raise FileExistsError("Refusing to overwrite frozen QIN pilot files")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    series_url = API + "getSeries?" + urllib.parse.urlencode({"Collection": COLLECTION})
    with opener.open(series_url, timeout=30) as response:
        raw = response.read()
    records = json.loads(raw)
    selected = sorted((row for row in records if row.get("PatientID") == PATIENT
                       and row.get("Modality") == "MR"
                       and row.get("SeriesDescription") == "T2 Weighted Axial"
                       and int(row.get("ImageCount", 0)) >= 24),
                      key=lambda row: (row.get("StudyDate", ""), row["SeriesInstanceUID"]))
    if tuple(row["SeriesInstanceUID"] for row in selected) != UIDS:
        raise ValueError("Official QIN series selection differs from frozen pilot")
    if any(row.get("LicenseURI", "").rstrip("/") != "https://creativecommons.org/licenses/by/4.0"
           for row in selected):
        raise ValueError("Official QIN license metadata changed")
    OUT.mkdir(parents=True)
    RAW.write_bytes(raw)
    downloaded = []
    for i, row in enumerate(selected, 1):
        url = API + "getImage?" + urllib.parse.urlencode(
            {"SeriesInstanceUID": row["SeriesInstanceUID"]})
        path = OUT / f"{PATIENT}_repeat_{i}.zip"
        partial = path.with_suffix(".zip.part")
        with opener.open(url, timeout=90) as response, partial.open("wb") as target:
            for block in iter(lambda: response.read(1024 * 1024), b""):
                target.write(block)
        if not zipfile.is_zipfile(partial):
            raise ValueError(f"NBIA did not return a ZIP for repeat {i}")
        partial.rename(path)
        with zipfile.ZipFile(path) as archive:
            members = [name for name in archive.namelist() if not name.endswith("/")]
        downloaded.append({"repeat": i, "patient": PATIENT,
                           "series_uid": row["SeriesInstanceUID"],
                           "study_uid": row["StudyInstanceUID"],
                           "study_date": row.get("StudyDate"),
                           "expected_images": row["ImageCount"],
                           "api_file_size": row.get("FileSize"),
                           "archive_path": path.relative_to(INNOVATION).as_posix(),
                           "zip_bytes": path.stat().st_size,
                           "zip_sha256": digest(path), "zip_members": len(members)})
        print(f"repeat {i}: {len(members)} ZIP members, {path.stat().st_size} bytes", flush=True)
    result = {"protocol_sha256": digest(INNOVATION / "QIN_REPEAT_T2_HEADER_PILOT_PLAN_2026-10-01.md"),
              "script_sha256": digest(Path(__file__)),
              "source_url": series_url, "source_sha256": hashlib.sha256(raw).hexdigest(),
              "source_series_count": len(records), "records": downloaded}
    MANIFEST.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"series": len(downloaded), "manifest": str(MANIFEST)}, indent=2))


if __name__ == "__main__":
    main()
