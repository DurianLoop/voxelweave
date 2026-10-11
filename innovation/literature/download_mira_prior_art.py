"""Fetch two arXiv prior-art PDFs with verified byte ranges and SHA-256."""
from __future__ import annotations

import hashlib
import http.client
import json
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PAPERS = (
    ("2601.13236v3", "Pixelwise_Uncertainty_Accelerated_MRI_2026.pdf"),
    ("2605.15050v1", "Intrinsic_Ambiguity_Inverse_Problems_2026.pdf"),
)
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
BLOCK = 1024 * 1024


def exact_range(url: str, start: int, end: int, size: int) -> bytes:
    request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}",
                                                   "User-Agent": "MRI-literature-audit/1.0"})
    for attempt in range(5):
        try:
            with OPENER.open(request, timeout=45) as response:
                expected = f"bytes {start}-{end}/{size}"
                if response.status != 206 or response.headers.get("Content-Range") != expected:
                    raise IOError("arXiv did not honor exact range")
                data = response.read()
            if len(data) != end - start + 1:
                raise IOError("Short PDF range")
            return data
        except (OSError, http.client.HTTPException):
            if attempt == 4:
                raise
            time.sleep(0.5 * (attempt + 1))
    raise AssertionError("unreachable")


def main() -> None:
    records = []
    for paper_id, filename in PAPERS:
        url = f"https://export.arxiv.org/pdf/{paper_id}"
        with OPENER.open(urllib.request.Request(url, method="HEAD", headers={"User-Agent": "MRI-literature-audit/1.0"}),
                         timeout=30) as response:
            size = int(response.headers["Content-Length"])
        path = ROOT / filename
        if not path.exists():
            part = path.with_suffix(".pdf.part")
            existing = part.stat().st_size if part.exists() else 0
            if existing > size or (existing != size and existing % BLOCK != 0):
                raise IOError(f"Partial PDF has invalid boundary: {part}")
            if existing:
                with part.open("rb") as stream:
                    for start in range(0, existing, BLOCK):
                        end = min(start + BLOCK, size) - 1
                        if stream.read(end - start + 1) != exact_range(url, start, end, size):
                            raise IOError(f"Partial PDF differs from source: {part}")
            with part.open("ab") as stream:
                for start in range(existing, size, BLOCK):
                    end = min(start + BLOCK, size) - 1
                    stream.write(exact_range(url, start, end, size))
            part.replace(path)
        if path.stat().st_size != size or path.open("rb").read(4) != b"%PDF":
            raise IOError(f"Downloaded PDF invalid: {filename}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append({"arxiv_id": paper_id, "source_url": url, "local_pdf": path.name,
                        "bytes": size, "sha256": digest})
        print(records[-1], flush=True)
    (ROOT / "mira_new_pdf_manifest.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
