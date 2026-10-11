"""Archive CrossMoDA full text for high-resolution T2 label-source qualification."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/crossmoda_descriptor_2026-10-01"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10186181/fullTextXML"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    record = {"url": URL, "patient_pixels_read": False}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"}),
                         timeout=30) as response:
            raw = response.read(3_000_001)
            record["status"] = response.status
        if len(raw) > 3_000_000:
            raise ValueError("Full text exceeded 3 MB cap")
        (OUT / "article.xml").write_bytes(raw)
        record.update({"file": "article.xml", "bytes": len(raw),
                       "sha256": hashlib.sha256(raw).hexdigest()})
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    (OUT / "index.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
