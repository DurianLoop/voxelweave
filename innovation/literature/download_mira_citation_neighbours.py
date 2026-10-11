"""Fetch three fixed arXiv versions selected by the citation-chain audit."""
from __future__ import annotations

import hashlib
from http.client import IncompleteRead
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RECORD = ROOT / "source_cache/mira_four_seed_new_pdf_sources.json"
SOURCES = {
    "Mind_the_Detail_MRI_2025.pdf": "https://arxiv.org/pdf/2507.00670v1",
    "Structural_Uncertainty_MRI_2026.pdf": "https://arxiv.org/pdf/2503.10527v2",
    "Segmentation_Guided_Diverse_MRI_2024.pdf": "https://arxiv.org/pdf/2407.18026v1",
}


def download(opener: urllib.request.OpenerDirector, url: str) -> bytes:
    chunks, expected = [], None
    for _ in range(12):
        offset = sum(map(len, chunks))
        headers = {"User-Agent": "MRI-literature-audit/1.0"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        request = urllib.request.Request(url, headers=headers)
        with opener.open(request, timeout=55) as response:
            if offset:
                content_range = response.headers.get("Content-Range", "")
                if response.status != 206 or not content_range.startswith(f"bytes {offset}-"):
                    raise ValueError(f"Server did not honor byte range {offset}: {content_range}")
                total = int(content_range.rsplit("/", 1)[-1])
            else:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                total = int(response.headers["Content-Length"])
            if expected is not None and total != expected:
                raise ValueError("PDF total size changed between range requests")
            expected = total
            try:
                block = response.read()
            except IncompleteRead as error:
                block = error.partial
        if not block:
            raise ValueError("No bytes returned while resuming PDF")
        chunks.append(block)
        if sum(map(len, chunks)) == expected:
            raw = b"".join(chunks)
            if not raw.startswith(b"%PDF-"):
                raise ValueError(f"Expected fixed-version PDF: {url}")
            return raw
        if sum(map(len, chunks)) > expected:
            raise ValueError("PDF response exceeded advertised length")
    raise RuntimeError(f"Too many incomplete range responses: {url}")


def main() -> None:
    if RECORD.exists() or any((ROOT / name).exists() for name in SOURCES):
        raise FileExistsError("Refusing to overwrite paper evidence")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    fetched = {}
    for name, url in SOURCES.items():
        raw = download(opener, url)
        fetched[name] = {"url": url, "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest(), "raw": raw}
    for name, item in fetched.items():
        (ROOT / name).write_bytes(item.pop("raw"))
    RECORD.write_text(json.dumps(fetched, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(fetched, indent=2))


if __name__ == "__main__":
    main()
