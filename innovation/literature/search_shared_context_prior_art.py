"""Archive a bounded arXiv novelty search for shared-context error audits."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_snapshots" / "shared_context_2026-10-01"
QUERIES = [
    'all:"MRI reconstruction" AND all:disagreement',
    'all:MRI AND all:"correlated errors" AND all:ensemble',
    'all:"MRI reconstruction" AND all:uncertainty AND all:ensemble',
    'all:"slice interpolation" AND all:uncertainty',
    'all:"complementary sampling" AND all:MRI',
]
ATOM = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/"}


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite the frozen search snapshot")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    response_rows = []
    for index, query in enumerate(QUERIES, 1):
        params = urllib.parse.urlencode({"search_query": query, "start": 0,
                                         "max_results": 30, "sortBy": "relevance"})
        url = "https://export.arxiv.org/api/query?" + params
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-prior-art-audit/1.0"}),
                         timeout=30) as response:
            data = response.read()
            if response.status != 200:
                raise RuntimeError("arXiv did not return HTTP 200")
        root = ET.fromstring(data)
        filename = f"query_{index}.xml"
        (OUT / filename).write_bytes(data)
        items = []
        for entry in root.findall("a:entry", ATOM):
            identifier = entry.findtext("a:id", default="", namespaces=ATOM)
            items.append({
                "id": identifier,
                "base_id": identifier.rsplit("/", 1)[-1].split("v", 1)[0],
                "title": " ".join(entry.findtext("a:title", default="", namespaces=ATOM).split()),
                "abstract": " ".join(entry.findtext("a:summary", default="", namespaces=ATOM).split()),
                "published": entry.findtext("a:published", default="", namespaces=ATOM),
            })
        response_rows.append({
            "query": query,
            "url": url,
            "raw_file": filename,
            "raw_sha256": hashlib.sha256(data).hexdigest(),
            "reported_total": int(root.findtext("o:totalResults", default="0", namespaces=ATOM)),
            "returned": len(items),
            "items": items,
        })
    unique = sorted({item["base_id"] for row in response_rows for item in row["items"]})
    summary = {"scope": "bounded arXiv title/abstract screen, not systematic review",
               "query_count": len(QUERIES), "unique_base_ids": len(unique),
               "responses": response_rows}
    (OUT / "index.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")
    print(json.dumps({"query_count": len(QUERIES), "returned": [r["returned"] for r in response_rows],
                      "reported_total": [r["reported_total"] for r in response_rows],
                      "unique_base_ids": len(unique)}, indent=2))


if __name__ == "__main__":
    main()
