"""Archive a fixed OpenAlex metadata search for repeat-acquired brain T2 MRI."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "2026-10-01_native_repeat_t2_source_search_plan.md"
OUT = ROOT / "search_snapshots/native_repeat_t2_2026-10-01"
QUERIES = (
    "test retest T2 weighted MRI dataset brain",
    "scan rescan T2 MRI open dataset",
    "repeated acquisition T2 weighted brain MRI public data",
)


def abstract(inverted: dict | None) -> str | None:
    if not inverted:
        return None
    words = [None] * (1 + max(index for positions in inverted.values() for index in positions))
    for word, positions in inverted.items():
        for index in positions:
            words[index] = word
    return " ".join(word or "" for word in words)


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of frozen source search")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records, responses = {}, []
    for number, query in enumerate(QUERIES, 1):
        params = urllib.parse.urlencode({
            "search": query,
            "filter": "from_publication_date:2015-01-01",
            "per-page": 25,
            "select": "id,display_name,publication_year,doi,primary_location,best_oa_location,abstract_inverted_index,cited_by_count",
        })
        url = f"https://api.openalex.org/works?{params}"
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=30) as response:
            if response.status != 200:
                raise ValueError(f"OpenAlex query {number} returned {response.status}")
            raw = response.read(5_000_001)
        if len(raw) > 5_000_000:
            raise ValueError("Unbounded metadata response")
        data = json.loads(raw)
        if len(data["results"]) > 25:
            raise ValueError("Search cap exceeded")
        name = f"query_{number}.json"
        (OUT / name).write_bytes(raw)
        responses.append({"query": query, "url": url, "file": name,
                          "sha256": hashlib.sha256(raw).hexdigest(),
                          "returned": len(data["results"]),
                          "indexed_count": data["meta"]["count"]})
        for work in data["results"]:
            identifier = work["id"]
            if identifier in records:
                records[identifier]["matched_queries"].append(number)
                continue
            primary = work.get("primary_location") or {}
            oa = work.get("best_oa_location") or {}
            records[identifier] = {
                "id": identifier, "title": work["display_name"],
                "year": work["publication_year"], "doi": work.get("doi"),
                "venue": (primary.get("source") or {}).get("display_name"),
                "landing_page_url": primary.get("landing_page_url"),
                "open_pdf_url": oa.get("pdf_url"),
                "abstract": abstract(work.get("abstract_inverted_index")),
                "cited_by_count": work.get("cited_by_count"),
                "matched_queries": [number],
            }
    index = {"plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
             "queries": responses, "distinct_works": len(records),
             "works": sorted(records.values(), key=lambda work: work["id"])}
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")
    print(json.dumps({"queries": [row["returned"] for row in responses],
                      "indexed_counts": [row["indexed_count"] for row in responses],
                      "distinct_works": len(records)}, indent=2))


if __name__ == "__main__":
    main()
