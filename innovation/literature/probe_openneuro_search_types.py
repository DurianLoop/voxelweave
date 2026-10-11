"""Archive bounded OpenNeuro GraphQL search result and node type metadata."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/openneuro_search_types_2026-10-01"
URL = "https://openneuro.org/crn/graphql"
QUERY = "query { __schema { queryType { name fields { name type { kind name ofType { kind name ofType { kind name } } } } } } }"


def request(opener: urllib.request.OpenerDirector, query: str) -> bytes:
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"User-Agent": "MRI-source-audit/1.0",
                                          "Content-Type": "application/json"})
    with opener.open(req, timeout=25) as response:
        raw = response.read(100_001)
        if response.status != 200 or len(raw) > 100_000:
            raise ValueError("Unexpected GraphQL metadata response")
        return raw


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    first = request(opener, QUERY)
    (OUT / "query_fields.json").write_bytes(first)
    root = json.loads(first)["data"]["__schema"]["queryType"]
    search = next(x for x in root["fields"] if x["name"] == "search")
    t = search["type"]
    while t.get("ofType"):
        t = t["ofType"]
    name = t["name"]
    second_query = ('query { __type(name: ' + json.dumps(name) +
                    ') { name kind fields { name type { kind name ofType { kind name } } } } }')
    second = request(opener, second_query)
    (OUT / "search_type.json").write_bytes(second)
    records = [
        {"query": QUERY, "file": "query_fields.json", "bytes": len(first),
         "sha256": hashlib.sha256(first).hexdigest()},
        {"query": second_query, "file": "search_type.json", "bytes": len(second),
         "sha256": hashlib.sha256(second).hexdigest()},
    ]
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    parsed = json.loads(second)["data"]["__type"]
    print(json.dumps({"search_return_type": name,
                      "fields": [x["name"] for x in parsed["fields"]]}, indent=2))


if __name__ == "__main__":
    main()
