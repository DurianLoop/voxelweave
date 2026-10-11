"""Archive the public TCIA UCSF-PDGM collection page and relevant links only."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache/ucsf_pdgm_official_2026-10-01"
URL = "https://www.cancerimagingarchive.net/collection/ucsf-pdgm/"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Source gate already archived; refusing overwrite")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=35) as response:
        body = response.read(2_000_001)
        status, final_url, content_type = response.status, response.geturl(), response.headers.get("Content-Type")
    if status != 200 or final_url != URL or len(body) > 2_000_000 or b"<html" not in body[:1000].lower():
        raise ValueError("Unexpected official page response")
    soup = BeautifulSoup(body, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    links = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        label = anchor.get_text(" ", strip=True)
        if href and (label or any(word in href.lower() for word in ("download", "doi", "data"))):
            links.append({"label": label[:200], "href": href})
    OUT.mkdir(parents=True)
    (OUT / "page.html").write_bytes(body)
    (OUT / "page.txt").write_text(text + "\n", encoding="utf-8")
    index = {"url": URL, "final_url": final_url, "http_status": status,
             "content_type": content_type, "bytes": len(body),
             "sha256": hashlib.sha256(body).hexdigest(), "links": links,
             "patient_pixels_read": False}
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: index[key] for key in ("http_status", "bytes", "sha256")}, indent=2))


if __name__ == "__main__":
    main()
