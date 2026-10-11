"""Bounded, read-only official EGD XNAT metadata availability probe."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/egd_official_metadata_2026-10-01"
URLS = [
    ("project", "https://xnat.bmia.nl/data/archive/projects/egd?format=json"),
    ("subjects", "https://xnat.bmia.nl/data/archive/projects/egd/subjects?format=json&limit=5"),
]


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for name, url in URLS:
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        try:
            with opener.open(request, timeout=25) as response:
                body = response.read(100_001)
                status = response.status
                content_type = response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            body = exc.read(100_001)
            status = exc.code
            content_type = exc.headers.get("Content-Type", "")
        except Exception as exc:
            records.append({"name": name, "url": url, "error": f"{type(exc).__name__}: {exc}"})
            continue
        row = {"name": name, "url": url, "status": status,
               "content_type": content_type}
        if len(body) <= 100_000:
            path = OUT / (name + (".json" if "json" in content_type else ".html"))
            path.write_bytes(body)
            row.update(file=path.name, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
        else:
            row["error"] = "Response exceeded 100 KB cap"
        records.append(row)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
