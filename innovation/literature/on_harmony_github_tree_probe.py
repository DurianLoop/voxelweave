"""Archive the public OpenNeuro GitHub mirror tree page for metadata paths."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache/on_harmony_github_tree_2026-10-01"
URL = "https://github.com/OpenNeuroDatasets/ds004712/tree/master"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of GitHub tree snapshot")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=30) as response:
        raw = response.read(750_001)
        result = {"url": URL, "final_url": response.url, "status": response.status,
                  "content_type": response.headers.get("Content-Type"),
                  "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    if len(raw) > 750_000 or result["status"] != 200:
        raise ValueError(f"Unexpected tree page: {result}")
    (OUT / "tree.html").write_bytes(raw)
    (OUT / "index.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
