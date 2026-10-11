"""Archive a bounded OpenAlex citation and recent-work screen for MIRA."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "2026-10-01_mira_citation_neighbour_plan.md"
OUT = ROOT / "search_snapshots/mira_citation_neighbours_2026-10-01"
DATE_FILTER = "from_publication_date:2022-01-01,to_publication_date:2026-10-01"
QUERIES = [
    {"filter": "cites:W3204136415"},
    {"search": "MRI reconstruction error correlation ensemble", "filter": DATE_FILTER},
    {"search": "MRI through-plane interpolation uncertainty", "filter": DATE_FILTER},
    {"search": "magnetic resonance reconstruction shared measurement disagreement", "filter": DATE_FILTER},
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def abstract_text(inverted: dict | None) -> str | None:
    if not inverted:
        return None
    words = [""] * (max(index for offsets in inverted.values() for index in offsets) + 1)
    for word, offsets in inverted.items():
        for offset in offsets:
            words[offset] = word
    return " ".join(words)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    raw_responses = []
    by_id = {}
    for index, query in enumerate(QUERIES, 1):
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({**query, "per-page": 50})
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-MIRA-prior-art-screen/1.0"})
        with opener.open(request, timeout=40) as response:
            raw = response.read()
            if response.status != 200:
                raise RuntimeError(f"OpenAlex query {index} returned HTTP {response.status}")
        parsed = json.loads(raw)
        works = parsed.get("results", [])
        raw_responses.append((raw, {"query": query, "url": url,
                                    "file": f"query_{index}.json", "sha256": sha256(raw),
                                    "total_hits_reported": parsed.get("meta", {}).get("count"),
                                    "returned": len(works)}))
        for rank, work in enumerate(works, 1):
            work_id = work["id"]
            location = work.get("primary_location") or {}
            source = location.get("source") or {}
            if work_id not in by_id:
                by_id[work_id] = {"id": work_id, "title": work.get("title"),
                                  "doi": work.get("doi"), "year": work.get("publication_year"),
                                  "publication_date": work.get("publication_date"),
                                  "primary_source": source.get("display_name"),
                                  "cited_by_count": work.get("cited_by_count"),
                                  "open_pdf_url": (work.get("best_oa_location") or {}).get("pdf_url"),
                                  "abstract": abstract_text(work.get("abstract_inverted_index")),
                                  "query_ranks": []}
            by_id[work_id]["query_ranks"].append({"query": index, "rank": rank})
        print(f"{index}/4: {len(works)} works, total {parsed.get('meta', {}).get('count')}", flush=True)
    OUT.mkdir(parents=True)
    for raw, info in raw_responses:
        (OUT / info["file"]).write_bytes(raw)
    index = {"scope": "bounded citation-neighbour and recent-title/abstract collision screen",
             "plan_sha256": sha256(PLAN.read_bytes()),
             "script_sha256": sha256(Path(__file__).read_bytes()),
             "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
             "queries": [info for _, info in raw_responses],
             "unique_works": len(by_id), "works": sorted(by_id.values(), key=lambda row: row["id"])}
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"queries": len(QUERIES), "unique_works": len(by_id)}))


if __name__ == "__main__":
    main()
