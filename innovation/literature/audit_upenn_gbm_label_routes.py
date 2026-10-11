"""Archive UPENN-GBM NBIA series routes and compare them with the frozen MR list."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache/upenn_gbm_label_routes_2026-10-01"
FROZEN_MR = HERE / "source_cache/upenn_gbm_getSeries_2026-10-01.json"
BASE = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getSeries?"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> tuple[int, bytes]:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-qualification/1.0"})
    with opener.open(request, timeout=90) as response:
        return response.status, response.read()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    frozen = json.loads(FROZEN_MR.read_text(encoding="utf-8"))
    frozen_uids = {row["SeriesInstanceUID"] for row in frozen}
    responses = []
    for name, params in (
        ("all_series", {"Collection": "UPENN-GBM"}),
        ("seg_series", {"Collection": "UPENN-GBM", "Modality": "SEG"}),
    ):
        url = BASE + urllib.parse.urlencode(params)
        status, data = fetch(url)
        responses.append((name, url, status, data))
    all_rows = json.loads(responses[0][3])
    all_uids = {row["SeriesInstanceUID"] for row in all_rows}
    modalities = dict(Counter(row.get("Modality") for row in all_rows))
    if (len(frozen) != 3680 or len(all_rows) != 3680 or
            len(all_uids) != 3680 or all_uids != frozen_uids or
            modalities != {"MR": 3680} or responses[1][3] != b""):
        raise ValueError("Unexpected NBIA inventory/SEG route result; inspect before archiving")
    OUT.mkdir(parents=True)
    index = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_mr_sha256": sha256(FROZEN_MR.read_bytes()),
        "all_series_rows": len(all_rows),
        "all_series_uid_set_equals_frozen_mr": all_uids == frozen_uids,
        "modalities": modalities,
        "seg_route_empty_body": True,
        "pixel_data_read": False,
        "responses": [],
    }
    for name, url, status, data in responses:
        filename = name + (".json" if data else ".bin")
        (OUT / filename).write_bytes(data)
        index["responses"].append({
            "name": name, "url": url, "status": status,
            "bytes": len(data), "sha256": sha256(data), "file": filename,
        })
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: index[key] for key in (
        "all_series_rows", "all_series_uid_set_equals_frozen_mr",
        "modalities", "seg_route_empty_body", "pixel_data_read")}, indent=2))


if __name__ == "__main__":
    main()
