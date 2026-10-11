"""Archive one frozen page of four OpenAlex novelty queries."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_snapshots/openalex_context_overlap_2026-10-01"
QUERIES = (
    "magnetic resonance image reconstruction ensemble shared measurements disagreement error",
    "MRI slice interpolation uncertainty correlated errors",
    "medical image reconstruction measurement overlap ensemble uncertainty",
    "scan rescan MRI reconstruction error correlation",
)


def abstract_text(inverted: dict | None) -> str | None:
    if not inverted:
        return None
    words = [""] * (1 + max(index for positions in inverted.values() for index in positions))
    for word, positions in inverted.items():
        for index in positions:
            words[index] = word
    return " ".join(words)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite frozen search: {OUT}")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    OUT.mkdir(parents=True)
    queries = []
    by_id = {}
    for i, query in enumerate(QUERIES, 1):
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
            {"search": query, "per-page": 25})
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"})
        with opener.open(request, timeout=30) as response:
            raw = response.read()
        path = OUT / f"query_{i}.json"
        path.write_bytes(raw)
        parsed = json.loads(raw)
        hits = parsed.get("results", [])
        queries.append({"query": query, "url": url, "file": path.name,
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "total_hits_reported": parsed.get("meta", {}).get("count"),
                        "first_page_hits": len(hits)})
        for rank, work in enumerate(hits, 1):
            ident = work["id"]
            location = work.get("primary_location") or {}
            source = location.get("source") or {}
            if ident not in by_id:
                by_id[ident] = {
                    "id": ident, "title": work.get("title"), "doi": work.get("doi"),
                    "publication_year": work.get("publication_year"),
                    "primary_source": source.get("display_name"),
                    "primary_landing_page": location.get("landing_page_url"),
                    "open_access_url": (work.get("best_oa_location") or {}).get("pdf_url"),
                    "abstract": abstract_text(work.get("abstract_inverted_index")),
                    "query_ranks": []}
            by_id[ident]["query_ranks"].append({"query": i, "rank": rank})
        print(f"query {i}: {len(hits)} works", flush=True)
    index = {"scope": "bounded first-page OpenAlex novelty check",
             "queries": queries, "unique_works": len(by_id),
             "works": sorted(by_id.values(), key=lambda work: work["id"])}
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")
    print(f"unique works: {len(by_id)}")


if __name__ == "__main__":
    main()
