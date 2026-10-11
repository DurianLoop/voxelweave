"""Archive bounded public Faspex client assets for supported-access inspection."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache" / "upenn_gbm_public_package_page_2026-10-01"
BASE = "https://faspex.cancerimagingarchive.net"
ASSETS = {
    "config.js": "/aspera/faspex/config.js",
    "app.js": "/aspera/faspex/assets/index-BRokjhaK.js",
}


def main() -> None:
    if not OUT.is_dir() or (OUT / "assets.json").exists():
        raise FileExistsError("Expected fresh landing archive and no prior asset manifest")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    fetched = []
    for name, path in ASSETS.items():
        request = urllib.request.Request(BASE + path, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=60) as response:
            raw = response.read(8_000_001)
            declared = response.headers.get("Content-Length")
            if (response.status != 200 or len(raw) > 8_000_000
                    or (declared and len(raw) != int(declared))):
                raise RuntimeError(f"Incomplete or oversize public asset: {name}")
        fetched.append((name, path, raw))
    manifest = []
    for name, path, raw in fetched:
        (OUT / name).write_bytes(raw)
        manifest.append({"file": name, "url": BASE + path, "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest()})
    (OUT / "assets.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
