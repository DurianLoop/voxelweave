"""Archive a bounded public OpenNeuro GraphQL query-field introspection."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/openneuro_search_schema_2026-10-01"
URL = "https://openneuro.org/crn/graphql"
QUERY = {"query": "query { __schema { queryType { fields { name description args { name type { kind name ofType { kind name } } } } } } }"}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, data=json.dumps(QUERY).encode(),
                                     headers={"User-Agent": "MRI-source-audit/1.0",
                                              "Content-Type": "application/json"})
    try:
        with opener.open(request, timeout=25) as response:
            body = response.read(250_001)
            status = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read(250_001)
        status = exc.code
    if len(body) > 250_000:
        raise ValueError("Schema response exceeded 250 KB cap")
    path = OUT / "response.json"
    path.write_bytes(body)
    record = {"url": URL, "query": QUERY, "status": status,
              "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
              "file": path.name}
    (OUT / "index.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    parsed = json.loads(body)
    fields = parsed.get("data", {}).get("__schema", {}).get("queryType", {}).get("fields", [])
    print(json.dumps({"status": status, "bytes": len(body),
                      "fields": [f["name"] for f in fields]}, indent=2))


if __name__ == "__main__":
    main()
