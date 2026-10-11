"""Download the frozen official ReMIND 2D T2 series without decoding pixels."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import shutil
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "literature/remind_native_t2_inventory.json"
PROTOCOL = ROOT / "REMIND_NATIVE_T2_CONFIRMATION_PROTOCOL_2026-10-01.md"
DIRECTORY = ROOT / "data/remind_native_t2/zips"
MANIFEST = ROOT / "literature/remind_native_t2_download_manifest.json"
PILOTS = {
    "ReMIND-003": ROOT / "data/remind_native_t2/header_pilot/ReMIND-003_blade.zip",
    "ReMIND-007": ROOT / "data/remind_native_t2/header_pilot/ReMIND-007_plain.zip",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(path: Path, expected_count: int) -> int:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        dicoms = [name for name in names if name.lower().endswith(".dcm")]
        if len(dicoms) != expected_count or "LICENSE" not in names:
            raise ValueError(f"ZIP count/license mismatch: {len(dicoms)} vs {expected_count}")
        bad = archive.testzip()
        if bad is not None:
            raise ValueError(f"ZIP CRC failed: {bad}")
        return len(dicoms)


def download(item: dict) -> dict:
    patient = item["patient"]
    path = DIRECTORY / f"{patient}_{item['series_description']}.zip"
    start = time.monotonic()
    status = "reused"
    if not path.exists():
        if patient in PILOTS and PILOTS[patient].is_file():
            shutil.copyfile(PILOTS[patient], path)
            status = "pilot_copy"
        else:
            url = ("https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?"
                   + urllib.parse.urlencode({"SeriesInstanceUID": item["series_uid"]}))
            part = path.with_suffix(".part")
            for attempt in range(1, 4):
                try:
                    with urllib.request.urlopen(url, timeout=180) as source, part.open("wb") as dest:
                        shutil.copyfileobj(source, dest, length=1024 * 1024)
                    validate(part, item["image_count"])
                    part.replace(path)
                    status = "downloaded"
                    break
                except (OSError, ValueError, zipfile.BadZipFile):
                    part.unlink(missing_ok=True)
                    if attempt == 3:
                        raise
                    time.sleep(2 * attempt)
    count = validate(path, item["image_count"])
    return {
        "patient": patient,
        "series_description": item["series_description"],
        "series_uid": item["series_uid"],
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "zip_sha256": sha256(path),
        "dicom_files": count,
        "status": status,
        "elapsed_seconds": round(time.monotonic() - start, 3),
    }


def main() -> None:
    if MANIFEST.exists():
        raise FileExistsError(MANIFEST)
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if len(inventory["series"]) != 63 or inventory["distinct_patients"] != 63:
        raise ValueError("frozen inventory changed")
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    results, failures = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(download, item): item for item in inventory["series"]}
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"{len(results) + len(failures)}/63 {item['patient']} {result['status']} "
                      f"dicom={result['dicom_files']}", flush=True)
            except Exception as error:
                failures.append({"patient": item["patient"], "series_uid": item["series_uid"],
                                 "error": f"{type(error).__name__}: {error}"})
                print(f"{len(results) + len(failures)}/63 {item['patient']} FAIL {error}", flush=True)
    results.sort(key=lambda row: row["patient"])
    failures.sort(key=lambda row: row["patient"])
    payload = {
        "inventory_sha256": sha256(INVENTORY),
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "downloaded_or_reused": len(results),
        "failures": failures,
        "total_zip_bytes": sum(row["bytes"] for row in results),
        "records": results,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("downloaded_or_reused", "failures", "total_zip_bytes")}, indent=2))


if __name__ == "__main__":
    main()
