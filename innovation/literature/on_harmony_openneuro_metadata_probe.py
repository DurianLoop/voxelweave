"""Archive bounded ON-Harmony OpenNeuro pages/API metadata only."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache/on_harmony_openneuro_metadata_2026-10-01"
URLS = (
    ("dataset_page", "https://openneuro.org/datasets/ds004712/versions/2.0.1"),
    ("snapshot_files", "https://openneuro.org/crn/datasets/ds004712/snapshots/2.0.1/files?prefix="),
    ("github_root", "https://api.github.com/repos/OpenNeuroDatasets/ds004712/contents?ref=master"),
)


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of ON-Harmony metadata probe")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    rows = []
    for name, url in URLS:
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        try:
            with opener.open(request, timeout=30) as response:
                raw = response.read(1_000_001)
                row = {"name": name, "url": url, "final_url": response.url,
                       "status": response.status, "content_type": response.headers.get("Content-Type")}
        except urllib.error.HTTPError as exc:
            raw = exc.read(1_000_001)
            row = {"name": name, "url": url, "final_url": exc.url,
                   "status": exc.code, "content_type": exc.headers.get("Content-Type")}
        except Exception as exc:
            rows.append({"name": name, "url": url, "error": f"{type(exc).__name__}: {exc}"})
            continue
        if len(raw) > 1_000_000:
            rows.append({**row, "error": "Response exceeded 1 MB; no body retained"})
            continue
        suffix = ".json" if "json" in (row["content_type"] or "") else ".html"
        filename = name + suffix
        (OUT / filename).write_bytes(raw)
        rows.append({**row, "file": filename, "bytes": len(raw),
                     "sha256": hashlib.sha256(raw).hexdigest()})
    (OUT / "index.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
