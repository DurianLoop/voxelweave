"""Read only Kaggle's public file-list endpoint for a named dataset."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/gazi_brains_kaggle_files_2026-10-01"
URL = "https://www.kaggle.com/api/v1/datasets/listFiles/gazibrains2020/gazi-brains-2020?pageSize=100"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    record = {"url": URL, "patient_pixels_read": False}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        request = urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=30) as response:
            raw = response.read(500_001)
            record["status"] = response.status
        if len(raw) > 500_000:
            raise ValueError("Response exceeded 500 kB cap")
        (OUT / "response.json").write_bytes(raw)
        data = json.loads(raw)
        record.update({"file": "response.json", "bytes": len(raw),
                       "sha256": hashlib.sha256(raw).hexdigest(),
                       "response_keys": list(data) if isinstance(data, dict) else None,
                       "files": [{k: item.get(k) for k in ("name", "totalBytes", "size")}
                                 for item in data.get("files", [])] if isinstance(data, dict) else []})
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    (OUT / "index.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
