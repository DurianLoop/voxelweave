"""Archive the official UPENN-GBM dataset citation metadata."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache"
SOURCES = {
    "upenn_gbm_datacite_2026-10-01.json": "https://api.datacite.org/dois/10.7937%2FTCIA.709X-DN49",
    "upenn_gbm_tcia_citation_2026-10-01.html": "https://www.cancerimagingarchive.net/collection/upenn-gbm/",
}


def main() -> None:
    if any((OUT / name).exists() for name in SOURCES):
        raise FileExistsError("Refusing to overwrite citation snapshots")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = {}
    for name, url in SOURCES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-research-citation-audit/1.0"})
        with opener.open(request, timeout=25) as response:
            data = response.read()
            if response.status != 200:
                raise RuntimeError(f"Citation source returned HTTP {response.status}")
        if name.endswith(".json"):
            attrs = json.loads(data)["data"]["attributes"]
            if attrs["doi"].lower() != "10.7937/tcia.709x-dn49":
                raise ValueError("Unexpected DataCite DOI")
        elif b"Attribution must include the following citation" not in data:
            raise ValueError("TCIA page lacks the required data-citation heading")
        records[name] = {"url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        (OUT / name).write_bytes(data)
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
