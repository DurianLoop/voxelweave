"""Resolve the API from the official catalog client; retain empty/failing routes."""
from __future__ import annotations

import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from probe_vs_seg_original_mask_routes import OUT, fetch


def main():
    base = "https://slicer-packages.kitware.com/api/v1/app/5f4474d0e1d8c75dfc705482"
    queries = {
        "slicerrt_win_34645_basename.json": ("extension", {"app_revision": "34645", "os": "win", "arch": "amd64", "baseName": "SlicerRT", "limit": 0}),
        "slicerrt_win_34645_noarch.json": ("extension", {"app_revision": "34645", "os": "win", "baseName": "SlicerRT", "limit": 0}),
        "slicerrt_win_revisions.json": ("extension", {"os": "win", "baseName": "SlicerRT", "limit": 20, "sort": "meta.app_revision", "sortdir": -1}),
    }
    def retrieve(item):
        name, (route, parameters) = item
        record = fetch(name, base + "/" + route + "?" + urllib.parse.urlencode(parameters), 3_000_000)
        summary = []
        if "error" not in record:
            data = json.loads((OUT / name).read_text())
            summary = [{k: row.get(k) for k in ("_id", "name", "size", "meta")} for row in data]
        return {"source": record, "items": summary}
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(retrieve, queries.items()))
    payload = {"official_client_api_evidence": "slicer_extensions_app.js: function C uses baseName, not extension_name", "queries": results}
    (OUT / "matching_catalog_index.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
