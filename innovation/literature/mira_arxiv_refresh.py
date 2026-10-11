"""Archive a bounded arXiv search for MIRA-neighboring 2026 preprints."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_snapshots/mira_arxiv_2026-09-30.json"
QUERIES = (
    'all:MRI AND (all:uncertainty OR all:"predictive error")',
    'all:reconstruction AND (all:agreement OR all:disagreement)',
    'all:"measurement dependence" AND all:reconstruction',
)
NS = {"atom": "http://www.w3.org/2005/Atom", "opensearch": "http://a9.com/-/spec/opensearch/1.1/"}
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def entry_text(entry: ET.Element, name: str) -> str:
    node = entry.find(f"atom:{name}", NS)
    return " ".join(node.itertext()).strip() if node is not None else ""


def main() -> None:
    searches = []
    for query in QUERIES:
        params = urllib.parse.urlencode({"search_query": query, "start": 0, "max_results": 100,
                                         "sortBy": "submittedDate", "sortOrder": "descending"})
        url = f"https://export.arxiv.org/api/query?{params}"
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"})
        with OPENER.open(request, timeout=45) as response:
            raw = response.read()
        root = ET.fromstring(raw)
        total = root.find("opensearch:totalResults", NS)
        items = [{"id": entry_text(entry, "id"), "title": entry_text(entry, "title"),
                  "published": entry_text(entry, "published"),
                  "updated": entry_text(entry, "updated"),
                  "summary": entry_text(entry, "summary")}
                 for entry in root.findall("atom:entry", NS)]
        searches.append({"query": query, "url": url, "total_results": int(total.text) if total is not None else None,
                         "returned": len(items), "items": items})
        print(query, "total", searches[-1]["total_results"], "returned", len(items), flush=True)
        time.sleep(1)
    OUT.write_text(json.dumps({"retrieved_date": "2026-09-30", "scope": "three bounded arXiv queries; latest 100 per query, not exhaustive", "searches": searches},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
