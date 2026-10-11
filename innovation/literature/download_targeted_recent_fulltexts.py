"""Fetch two bounded open-access PDFs for prior-art method review."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache" / "targeted_recent_fulltexts_2026-10-01"
SOURCES = {
    "glioma_task_aware_uq_2026.pdf": "https://www.melba-journal.org/pdf/2026:033.pdf",
    "slicebridge_2026.pdf": "https://arxiv.org/pdf/2609.01827",
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    fetched = []
    for name, url in SOURCES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-prior-art-audit/1.0"})
        with opener.open(request, timeout=60) as response:
            raw = response.read(10_000_001)
            declared = response.headers.get("Content-Length")
            if (response.status != 200 or not raw.startswith(b"%PDF-")
                    or len(raw) > 10_000_000 or (declared and len(raw) != int(declared))
                    or b"%%EOF" not in raw[-2048:]):
                raise ValueError(f"Incomplete or non-PDF response: {name}")
        fetched.append((name, url, raw))
    OUT.mkdir(parents=True)
    manifest = []
    for name, url, raw in fetched:
        (OUT / name).write_bytes(raw)
        manifest.append({"file": name, "url": url, "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest()})
    (OUT / "index.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
