"""Bounded metadata search for a second high-resolution T2 tumor-label source."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/highres_t2_tumor_source_search_2026-10-01"
QUERIES = [
    ("europepmc_3d_t2", "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
     {"query": "glioblastoma MRI dataset 3D T2 segmentation", "format": "json", "pageSize": "25"}),
    ("europepmc_t2_space", "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
     {"query": "glioma T2 SPACE MRI segmentation dataset", "format": "json", "pageSize": "25"}),
    ("datacite_3d_t2", "https://api.datacite.org/dois",
     {"query": "brain tumor MRI 3D T2 segmentation", "page[size]": "25"}),
    ("crossref_3d_t2", "https://api.crossref.org/works",
     {"query.title": "brain tumor MRI dataset 3D T2 segmentation", "rows": "20"}),
]


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for name, base, query in QUERIES:
        url = base + "?" + urllib.parse.urlencode(query)
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        try:
            with opener.open(request, timeout=30) as response:
                body = response.read(1_000_001)
                status = response.status
        except Exception as exc:
            records.append({"name": name, "url": url, "error": f"{type(exc).__name__}: {exc}"})
            continue
        if len(body) > 1_000_000:
            records.append({"name": name, "url": url, "status": status,
                            "error": "Response exceeded 1 MB cap"})
            continue
        path = OUT / f"{name}.json"
        path.write_bytes(body)
        records.append({"name": name, "url": url, "status": status,
                        "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                        "file": path.name})
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
