"""Archive the fixed NPB-REC arXiv PDF for a bounded prior-art check."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "NPB_REC_2022.pdf"
ARXIV = "2208.03966v1"
URL = f"https://arxiv.org/pdf/{ARXIV}"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0",
                                                 "Accept": "application/pdf"})
    with opener.open(request, timeout=60) as response:
        raw = response.read()
        if response.status != 200 or not raw.startswith(b"%PDF-"):
            raise RuntimeError("arXiv did not return a PDF")
    OUT.write_bytes(raw)
    print(json.dumps({"url": URL, "path": str(OUT), "bytes": len(raw),
                      "sha256": hashlib.sha256(raw).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
