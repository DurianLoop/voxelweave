"""Fetch the fixed arXiv version of Savant's MRI interpolation paper."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "Savant_2026_MRI_Slice_Interpolation_Problem_Formulation.pdf"
RECORD = ROOT / "source_cache/savant_formulation_pdf_source.json"
URL = "https://arxiv.org/pdf/2605.16476v1"


def main() -> None:
    if PDF.exists() or RECORD.exists():
        raise FileExistsError("Refusing to overwrite paper evidence")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "MRI-literature-audit/1.0"})
    with opener.open(request, timeout=45) as response:
        data = response.read()
        if response.status != 200 or not data.startswith(b"%PDF-"):
            raise ValueError("Expected a PDF from the fixed arXiv URL")
    record = {"url": URL, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
              "local_pdf": PDF.relative_to(ROOT).as_posix()}
    PDF.write_bytes(data)
    RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
