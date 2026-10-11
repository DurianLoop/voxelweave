"""Archive bounded public ON-Harmony article HTML, without imaging data."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "ON_HARMONY_REPEAT_T2_SOURCE_GATE_PLAN_2026-10-01.md"
OUT = ROOT / "literature/source_cache/on_harmony_article_2026-10-01"
URL = "https://www.nature.com/articles/s41597-025-04822-2"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite ON-Harmony source cache")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=30) as response:
        raw = response.read(2_000_001)
        info = {"url": URL, "final_url": response.url, "status": response.status,
                "content_type": response.headers.get("Content-Type"),
                "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    if len(raw) > 2_000_000 or info["status"] != 200 or "html" not in (info["content_type"] or ""):
        raise ValueError(f"Unexpected article response: {info}")
    (OUT / "article.html").write_bytes(raw)
    info["plan_sha256"] = hashlib.sha256(PLAN.read_bytes()).hexdigest()
    (OUT / "index.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
