"""Archive one bounded arXiv refresh for MIRA's exact measurement context."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_snapshots/mira_targeted_arxiv_2026-10-01"
QUERIES = (
    'all:"slice interpolation" AND all:MRI',
    'all:"through-plane" AND all:uncertainty',
    'all:"MRI reconstruction" AND all:disagreement',
)
NS = {"atom": "http://www.w3.org/2005/Atom",
      "opensearch": "http://a9.com/-/spec/opensearch/1.1/"}


def field(entry: ET.Element, name: str) -> str:
    node = entry.find(f"atom:{name}", NS)
    return " ".join("".join(node.itertext()).split()) if node is not None else ""


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    responses = []
    for index, query in enumerate(QUERIES, 1):
        params = urllib.parse.urlencode({"search_query": query, "start": 0,
                                         "max_results": 100, "sortBy": "submittedDate",
                                         "sortOrder": "descending"})
        url = f"https://export.arxiv.org/api/query?{params}"
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"})
        with opener.open(request, timeout=45) as response:
            raw = response.read()
            if response.status != 200:
                raise RuntimeError(f"arXiv HTTP {response.status}")
        root = ET.fromstring(raw)
        entries = [{key: field(entry, key) for key in ("id", "title", "published", "updated", "summary")}
                   for entry in root.findall("atom:entry", NS)]
        total = root.find("opensearch:totalResults", NS)
        responses.append({"query": query, "url": url,
                          "raw_file": f"query_{index}.xml", "raw_sha256": hashlib.sha256(raw).hexdigest(),
                          "total_results": int(total.text) if total is not None else None,
                          "returned": len(entries), "entries": entries, "raw": raw})
    OUT.mkdir(parents=True)
    for record in responses:
        (OUT / record["raw_file"]).write_bytes(record.pop("raw"))
    (OUT / "index.json").write_text(json.dumps({"retrieved_date": "2026-10-01",
                                                "responses": responses}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{"query": r["query"], "total_results": r["total_results"],
                       "returned": r["returned"]} for r in responses], indent=2))


if __name__ == "__main__":
    main()
