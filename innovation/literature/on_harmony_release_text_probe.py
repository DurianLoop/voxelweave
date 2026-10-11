"""Archive exact public ON-Harmony release text paths and S3 metadata routes."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache/on_harmony_release_text_2026-10-01"
ROUTES = (
    ("github_readme", "https://raw.githubusercontent.com/OpenNeuroDatasets/ds004712/master/README"),
    ("github_scan_delays", "https://raw.githubusercontent.com/OpenNeuroDatasets/ds004712/master/scan_delays.csv"),
    ("s3_scan_delays", "https://s3.amazonaws.com/openneuro.org/ds004712/scan_delays.csv"),
    ("s3_description", "https://s3.amazonaws.com/openneuro.org/ds004712/dataset_description.json"),
)


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of ON-Harmony release text probe")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    rows = []
    for name, url in ROUTES:
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        try:
            with opener.open(request, timeout=30) as response:
                raw = response.read(250_001)
                row = {"name": name, "url": url, "final_url": response.url,
                       "status": response.status, "content_type": response.headers.get("Content-Type")}
        except urllib.error.HTTPError as exc:
            raw = exc.read(250_001)
            row = {"name": name, "url": url, "final_url": exc.url,
                   "status": exc.code, "content_type": exc.headers.get("Content-Type")}
        except Exception as exc:
            rows.append({"name": name, "url": url, "error": f"{type(exc).__name__}: {exc}"})
            continue
        if len(raw) > 250_000:
            rows.append({**row, "error": "Response exceeded 250 KB; not retained"})
            continue
        suffix = ".csv" if "delays" in name else ".json" if "description" in name else ".txt"
        filename = name + suffix
        (OUT / filename).write_bytes(raw)
        rows.append({**row, "file": filename, "bytes": len(raw),
                     "sha256": hashlib.sha256(raw).hexdigest()})
    (OUT / "index.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
