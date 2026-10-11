"""Archive a bounded metadata search for native repeated 2D brain T2 data."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
PLAN = HERE / "2026-10-01_native_2d_t2_retest_targeted_search_plan.md"
OUT = HERE / "search_snapshots/native_2d_t2_retest_targeted_2026-10-01"
QUERIES = (
    "2D T2 weighted brain MRI scan rescan dataset",
    "test retest T2 weighted fast spin echo brain MRI data",
    "repeat acquisition T2 brain MRI DICOM open dataset",
)


def abstract(inverted: dict | None) -> str | None:
    if not inverted:
        return None
    words = [None] * (1 + max(i for positions in inverted.values() for i in positions))
    for word, positions in inverted.items():
        for index in positions:
            words[index] = word
    return " ".join(word or "" for word in words)


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite frozen targeted search")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    responses = []
    works = {}
    for number, query in enumerate(QUERIES, 1):
        params = urllib.parse.urlencode({
            "search": query,
            "per-page": 50,
            "select": "id,display_name,publication_year,doi,primary_location,best_oa_location,abstract_inverted_index,cited_by_count",
        })
        url = f"https://api.openalex.org/works?{params}"
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=30) as response:
            if response.status != 200:
                raise ValueError(f"Query {number}: HTTP {response.status}")
            raw = response.read(5_000_001)
        if len(raw) > 5_000_000:
            raise ValueError("Metadata response exceeded 5 MB")
        payload = json.loads(raw)
        rows = payload["results"]
        if len(rows) > 50:
            raise ValueError("Query cap exceeded")
        name = f"query_{number}.json"
        (OUT / name).write_bytes(raw)
        responses.append({"query": query, "url": url, "file": name,
                          "sha256": hashlib.sha256(raw).hexdigest(),
                          "returned": len(rows), "indexed_count": payload["meta"]["count"]})
        for row in rows:
            key = row["id"]
            if key in works:
                works[key]["matched_queries"].append(number)
                continue
            primary = row.get("primary_location") or {}
            oa = row.get("best_oa_location") or {}
            works[key] = {
                "id": key, "title": row["display_name"],
                "year": row.get("publication_year"), "doi": row.get("doi"),
                "venue": (primary.get("source") or {}).get("display_name"),
                "landing_page_url": primary.get("landing_page_url"),
                "open_pdf_url": oa.get("pdf_url"),
                "abstract": abstract(row.get("abstract_inverted_index")),
                "cited_by_count": row.get("cited_by_count"),
                "matched_queries": [number],
            }
    index = {
        "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        "queries": responses, "distinct_works": len(works),
        "works": sorted(works.values(), key=lambda work: work["id"]),
    }
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"returned": [x["returned"] for x in responses],
                      "distinct_works": len(works)}, indent=2))


if __name__ == "__main__":
    main()
