"""Download the frozen processed-UPENN series from official NBIA without decoding pixels."""
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
INVENTORY = ROOT / "literature/upenn_gbm_processed_t2_inventory.json"
PROTOCOL = ROOT / "UPENN_GBM_PROCESSED_T2_CONTEXT_PROTOCOL_2026-10-01.md"
PILOT_RESULT = ROOT / "literature/upenn_gbm_t2_header_pilot.json"
DIRECTORY = ROOT / "data/upenn_gbm_processed_t2_audit/zips"
MANIFEST = ROOT / "literature/upenn_gbm_processed_t2_download_manifest.json"
BASE_URL = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(path: Path, expected_count: int) -> int:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".dcm")]
        if len(names) != expected_count:
            raise ValueError(f"DICOM member count {len(names)} != {expected_count}")
        bad = archive.testzip()
        if bad is not None:
            raise ValueError(f"ZIP CRC failed: {bad}")
    return len(names)


def fetch(item: dict, pilot: dict) -> dict:
    patient = item["patient"]
    path = DIRECTORY / f"{patient}.zip"
    started = time.monotonic()
    status = "reused"
    if not path.exists():
        pilot_path = ROOT / pilot["archive_path"]
        if (patient == pilot["patient"] and item["series_uid"] == pilot["series_uid"]
                and pilot_path.is_file() and sha256(pilot_path) == pilot["zip_sha256"]):
            shutil.copyfile(pilot_path, path)
            status = "pilot_copy"
        else:
            url = BASE_URL + urllib.parse.urlencode({"SeriesInstanceUID": item["series_uid"]})
            part = path.with_suffix(".part")
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            for attempt in range(1, 4):
                try:
                    request = urllib.request.Request(url, headers={"User-Agent": "MRI-processed-source-audit/1.0"})
                    with opener.open(request, timeout=180) as source, part.open("wb") as dest:
                        if source.status != 200:
                            raise RuntimeError(f"NBIA HTTP {source.status}")
                        shutil.copyfileobj(source, dest, length=1024 * 1024)
                    validate(part, item["image_count"])
                    part.replace(path)
                    status = "downloaded"
                    break
                except (OSError, ValueError, RuntimeError, zipfile.BadZipFile):
                    part.unlink(missing_ok=True)
                    if attempt == 3:
                        raise
                    time.sleep(2 * attempt)
    count = validate(path, item["image_count"])
    return {"patient": patient, "series_uid": item["series_uid"],
            "path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "zip_sha256": sha256(path), "dicom_files": count,
            "status": status, "elapsed_seconds": round(time.monotonic() - started, 3)}


def main() -> None:
    if MANIFEST.exists():
        raise FileExistsError(MANIFEST)
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if len(inventory["series"]) != 374 or inventory["protocol_sha256"] != sha256(PROTOCOL):
        raise ValueError("Frozen inventory or protocol changed")
    pilot = json.loads(PILOT_RESULT.read_text(encoding="utf-8"))
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    results, failures = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(fetch, item, pilot): item for item in inventory["series"]}
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                record = future.result()
                results.append(record)
                print(f"{len(results) + len(failures)}/374 {item['patient']} {record['status']}", flush=True)
            except Exception as error:
                failures.append({"patient": item["patient"], "series_uid": item["series_uid"],
                                 "error": f"{type(error).__name__}: {error}"})
                print(f"{len(results) + len(failures)}/374 {item['patient']} FAIL {error}", flush=True)
    results.sort(key=lambda row: row["patient"])
    failures.sort(key=lambda row: row["patient"])
    payload = {"inventory_sha256": sha256(INVENTORY),
               "protocol_sha256": sha256(PROTOCOL),
               "script_sha256": sha256(Path(__file__)),
               "downloaded_or_reused": len(results), "failures": failures,
               "total_zip_bytes": sum(row["bytes"] for row in results),
               "records": results}
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in (
        "downloaded_or_reused", "failures", "total_zip_bytes")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
