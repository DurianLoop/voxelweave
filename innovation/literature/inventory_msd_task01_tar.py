"""Index the official MSD BrainTumour tar by HTTP Range without reading images."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache" / "msd_task01_official_2026-10-01"
REGISTRY = "https://registry.opendata.aws/msd/"
BUCKET = "https://msd-for-monai.s3.us-west-2.amazonaws.com/"
KEY = "Task01_BrainTumour.tar"
TAR_URL = BUCKET + KEY
EXPECTED_SIZE = 7_608_266_240


def get_range(session: requests.Session, first: int, last: int) -> bytes:
    response = session.get(TAR_URL, headers={"Range": f"bytes={first}-{last}"}, timeout=40)
    expected = f"bytes {first}-{last}/{EXPECTED_SIZE}"
    if response.status_code != 206 or response.headers.get("Content-Range") != expected:
        raise ValueError("S3 did not honor the bounded Range request")
    if len(response.content) != last - first + 1:
        raise ValueError("S3 returned an unexpected number of bytes")
    return response.content


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    if limit < 1 or limit > 3000:
        raise ValueError("Entry limit outside 1..3000")
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / ("tar_index_full.json" if limit == 3000 else f"tar_index_first_{limit}.json")
    if report_path.exists():
        raise FileExistsError("Refusing to overwrite a prior inventory")
    session = requests.Session()
    session.trust_env = False
    registry = session.get(REGISTRY, timeout=35)
    registry.raise_for_status()
    bucket = session.get(BUCKET, params={"list-type": "2", "max-keys": "100"}, timeout=35)
    bucket.raise_for_status()
    root = ET.fromstring(bucket.content)
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    matches = [item for item in root.findall("s3:Contents", ns)
               if item.findtext("s3:Key", namespaces=ns) == KEY]
    if len(matches) != 1 or int(matches[0].findtext("s3:Size", namespaces=ns)) != EXPECTED_SIZE:
        raise ValueError("Official S3 object inventory changed")
    if not (OUT / "registry.html").exists():
        (OUT / "registry.html").write_bytes(registry.content)
    if not (OUT / "bucket.xml").exists():
        (OUT / "bucket.xml").write_bytes(bucket.content)
    entries: list[dict] = []
    offset = 0
    stopped = "entry_limit"
    dataset_data: bytes | None = None
    for _ in range(limit):
        block = get_range(session, offset, offset + 511)
        if block == bytes(512):
            stopped = "tar_end_block"
            break
        info = tarfile.TarInfo.frombuf(block, encoding="utf-8", errors="surrogateescape")
        if info.size < 0 or info.size > EXPECTED_SIZE or offset + 512 + info.size > EXPECTED_SIZE:
            raise ValueError("Invalid tar entry size")
        record = {"name": info.name, "header_offset": offset,
                  "data_offset": offset + 512, "size": info.size,
                  "type": info.type.decode("ascii", "replace")}
        entries.append(record)
        if info.name == "Task01_BrainTumour/dataset.json" and info.size <= 100_000:
            dataset_data = get_range(session, offset + 512, offset + 511 + info.size)
        offset += 512 + math.ceil(info.size / 512) * 512
    report = {"registry_url": REGISTRY, "registry_sha256": hashlib.sha256(registry.content).hexdigest(),
              "bucket_url": BUCKET, "bucket_listing_sha256": hashlib.sha256(bucket.content).hexdigest(),
              "tar_url": TAR_URL, "tar_bytes": EXPECTED_SIZE,
              "tar_etag": matches[0].findtext("s3:ETag", namespaces=ns),
              "range_requests_only": True, "patient_pixels_read": False,
              "entries_indexed": len(entries), "next_offset": offset,
              "stop_reason": stopped, "entries": entries}
    if dataset_data is not None:
        parsed = json.loads(dataset_data)
        report["dataset_json_sha256"] = hashlib.sha256(dataset_data).hexdigest()
        report["dataset_json_bytes"] = len(dataset_data)
        report["dataset_json_keys"] = sorted(parsed)
        if not (OUT / "dataset.json").exists():
            (OUT / "dataset.json").write_bytes(dataset_data)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "entries"}, indent=2))


if __name__ == "__main__":
    main()
