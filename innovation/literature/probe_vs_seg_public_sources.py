"""Archive VS-SEG full text and official Zenodo/TCIA metadata only."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/vs_seg_public_sources_2026-10-01"
SOURCES = {
    "vs_seg_paper": ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8553833/fullTextXML", 3_000_000),
    "crossmoda_zenodo": ("https://zenodo.org/api/records/4662239", 300_000),
    "vs_seg_tcia": ("https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/", 700_000),
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for name, (url, cap) in SOURCES.items():
        item = {"name": name, "url": url, "patient_pixels_read": False}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
            with opener.open(req, timeout=30) as response:
                raw = response.read(cap + 1)
                item["status"] = response.status
                item["final_url"] = response.url
                item["content_type"] = response.headers.get("Content-Type")
            if len(raw) > cap:
                raise ValueError("Response exceeded cap")
            extension = "xml" if name == "vs_seg_paper" else "json" if name == "crossmoda_zenodo" else "html"
            file = f"{name}.{extension}"
            (OUT / file).write_bytes(raw)
            item.update({"file": file, "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest()})
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
        records.append(item)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
