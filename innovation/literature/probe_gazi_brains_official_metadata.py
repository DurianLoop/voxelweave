"""Archive bounded public Kaggle metadata for the Gazi Brains dataset."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/gazi_brains_kaggle_metadata_2026-10-01"
URL = "https://www.kaggle.com/api/v1/datasets/view/gazibrains2020/gazi-brains-2020"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    record = {"url": URL, "patient_pixels_read": False}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        request = urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=30) as response:
            raw = response.read(2_000_001)
            record["status"] = response.status
            record["content_type"] = response.headers.get("Content-Type")
        if len(raw) > 2_000_000:
            raise ValueError("Response exceeded 2 MB cap")
        (OUT / "response.json").write_bytes(raw)
        data = json.loads(raw)
        record.update({"file": "response.json", "bytes": len(raw),
                       "sha256": hashlib.sha256(raw).hexdigest(),
                       "title": data.get("title"), "licenseName": data.get("licenseName"),
                       "totalBytes": data.get("totalBytes"),
                       "resources": [{k: item.get(k) for k in ("path", "name", "totalBytes", "size")}
                                     for item in data.get("resources", [])]})
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    (OUT / "index.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
