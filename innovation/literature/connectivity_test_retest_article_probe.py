"""Archive bounded public HTML for the 2015 multimodal retest paper."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "CONNECTIVITY_TEST_RETEST_T2_SOURCE_GATE_PLAN_2026-10-01.md"
OUT = ROOT / "literature/source_cache/connectivity_test_retest_article_2026-10-01"
URL = "https://www.nature.com/articles/sdata201556"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of retest article cache")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=30) as response:
        raw = response.read(2_000_001)
        row = {"url": URL, "final_url": response.url, "status": response.status,
               "content_type": response.headers.get("Content-Type"),
               "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    if len(raw) > 2_000_000 or row["status"] != 200 or "html" not in (row["content_type"] or ""):
        raise ValueError(f"Unexpected article response: {row}")
    (OUT / "article.html").write_bytes(raw)
    row["plan_sha256"] = hashlib.sha256(PLAN.read_bytes()).hexdigest()
    (OUT / "index.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    main()
