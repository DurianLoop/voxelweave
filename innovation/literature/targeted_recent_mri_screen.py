"""Archive a bounded, metadata-only OpenAlex prior-art search."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_snapshots" / "targeted_recent_mri_2026-10-01"
QUERIES = [
    "MRI reconstruction uncertainty ensemble pathology",
    "MRI reconstruction shared measurements correlated errors",
    "MRI slice interpolation uncertainty context",
    "MRI reconstruction lesion segmentation uncertainty",
]


def abstract(work: dict) -> str:
    inverted = work.get("abstract_inverted_index") or {}
    words = [""] * (max((max(v) for v in inverted.values()), default=-1) + 1)
    for word, positions in inverted.items():
        for position in positions:
            words[position] = word
    return " ".join(words)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    responses = []
    for query in QUERIES:
        params = urllib.parse.urlencode({
            "search": query,
            "filter": "from_publication_date:2024-01-01,to_publication_date:2026-10-01",
            "sort": "publication_date:desc",
            "per-page": 50,
        })
        url = f"https://api.openalex.org/works?{params}"
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-prior-art-audit/1.0"})
        with opener.open(request, timeout=45) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}: {url}")
            raw = response.read()
        parsed = json.loads(raw)
        responses.append((query, url, raw, parsed))
    OUT.mkdir(parents=True)
    sources = []
    works = {}
    for index, (query, url, raw, parsed) in enumerate(responses, start=1):
        name = f"query_{index}.json"
        (OUT / name).write_bytes(raw)
        sources.append({
            "query": query, "url": url, "file": name,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "total_count": parsed["meta"]["count"],
            "returned": len(parsed["results"]),
        })
        for work in parsed["results"]:
            record = works.setdefault(work["id"], {
                "id": work["id"], "doi": work.get("doi"),
                "title": work.get("display_name"),
                "year": work.get("publication_year"),
                "date": work.get("publication_date"),
                "venue": ((work.get("primary_location") or {}).get("source") or {}).get("display_name"),
                "abstract": abstract(work),
                "locations": [
                    {"landing_page_url": loc.get("landing_page_url"),
                     "pdf_url": loc.get("pdf_url"),
                     "source": (loc.get("source") or {}).get("display_name")}
                    for loc in work.get("locations", [])
                ],
                "queries": [],
            })
            record["queries"].append(index)
    index = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "unique_works": len(works),
        "works": sorted(works.values(), key=lambda w: (w["date"] or "", w["id"]), reverse=True),
    }
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"returned": sum(s["returned"] for s in sources),
                      "unique_works": len(works),
                      "totals": [s["total_count"] for s in sources]}))


if __name__ == "__main__":
    main()
