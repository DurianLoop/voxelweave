"""Archive bounded Europe PMC full text for the Erasmus Glioma Database."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/egd_2021_descriptor"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8203723/fullTextXML"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=30) as response:
        body = response.read(500_001)
        status = response.status
    if len(body) > 500_000:
        raise ValueError("Full text exceeded 500 KB cap")
    path = OUT / "fulltext.xml"
    path.write_bytes(body)
    record = {"url": URL, "status": status, "bytes": len(body),
              "sha256": hashlib.sha256(body).hexdigest(), "file": path.name}
    (OUT / "index.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
