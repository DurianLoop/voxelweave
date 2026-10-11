"""Download and verify the primary arXiv PDF for the Tweedie-target audit."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
URL = "https://export.arxiv.org/pdf/2609.33786v1"
DEST = ROOT / "Tweedie_Uncertainty_Target_Diagnostics_2026.pdf"
RECORD = ROOT / "tweedie_pdf_source.json"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def main() -> None:
    if DEST.exists() or RECORD.exists():
        raise FileExistsError("Refusing to overwrite source evidence")
    request = urllib.request.Request(URL, method="HEAD",
                                     headers={"User-Agent": "MRI-literature-audit/1.0"})
    with OPENER.open(request, timeout=30) as response:
        size = int(response.headers["Content-Length"])
    with OPENER.open(urllib.request.Request(URL,
                                            headers={"User-Agent": "MRI-literature-audit/1.0"}),
                     timeout=60) as response:
        content = response.read()
    if len(content) != size or not content.startswith(b"%PDF"):
        raise IOError("PDF download size or header mismatch")
    DEST.write_bytes(content)
    record = {"source_url": URL, "arxiv_id": "2609.33786v1",
              "local_pdf": DEST.name, "bytes": size,
              "sha256": hashlib.sha256(content).hexdigest()}
    RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
