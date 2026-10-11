"""Read-only integrity check for the bounded OpenAlex and PMC evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SEARCH = ROOT / "search_snapshots/mira_citation_neighbours_2026-10-01"
PLAN = ROOT / "2026-10-01_mira_citation_neighbour_plan.md"
SCRIPT = ROOT / "search_mira_citation_neighbours.py"
PMC = ROOT / "source_cache/rsna_acceleration_limits_2022_pmc.html"
TEXT = ROOT / "extracted/rsna_acceleration_limits_2022_pmc.txt"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    index = json.loads((SEARCH / "index.json").read_text(encoding="utf-8"))
    assert index["plan_sha256"] == sha256(PLAN)
    assert index["script_sha256"] == sha256(SCRIPT)
    assert len(index["queries"]) == 4
    works = {}
    for query_number, info in enumerate(index["queries"], 1):
        path = SEARCH / info["file"]
        assert sha256(path) == info["sha256"]
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload["results"]
        assert len(rows) == info["returned"] <= 50
        assert payload["meta"]["count"] == info["total_hits_reported"]
        for rank, row in enumerate(rows, 1):
            works.setdefault(row["id"], []).append({"query": query_number, "rank": rank})
    assert len(works) == index["unique_works"] == 157
    indexed = {row["id"]: row["query_ranks"] for row in index["works"]}
    assert indexed == works
    assert index["queries"][0]["returned"] == index["queries"][0]["total_hits_reported"] == 11
    assert sha256(PMC) == "dc32255a60d4f35d3b7a97fb2729f522ca304e28f3ecc5f7ad0b49fa94ebf5de"
    assert sha256(TEXT) == "b7aa92e48bc0fa84c9df282e73ae7d78ce889cf86a0b4c2469c7adb2d92aa4b1"
    article = TEXT.read_text(encoding="utf-8")
    assert "Monte Carlo Metric Estimation" in article
    assert "Exploring the Acceleration Limits" in article
    print(json.dumps({"status": "PASS", "queries": 4, "unique_titles": 157,
                      "Hu_citing_works": 11, "PMC_full_text_sha256_verified": True,
                      "patient_pixels_read": False, "gpu_used": False}, indent=2))


if __name__ == "__main__":
    main()
