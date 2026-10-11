"""Archive the public UCSF-PDGM descriptor and version-5 nonimage metadata."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/ucsf_pdgm_descriptor_2026-10-01"
SOURCES = {
    "pmc_article.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9748624/",
    "metadata_v5.csv": "https://www.cancerimagingarchive.net/wp-content/uploads/UCSF-PDGM-metadata_v5.csv",
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Descriptor/metadata archive exists")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    retrieved = {}
    for name, url in SOURCES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=35) as response:
            body = response.read(2_000_001)
            status, final_url = response.status, response.geturl()
        if status != 200 or final_url != url or len(body) > 2_000_000:
            raise ValueError(f"Unexpected response: {name}")
        retrieved[name] = (body, {"url": url, "http_status": status,
                                  "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
    article = BeautifulSoup(retrieved["pmc_article.html"][0], "html.parser")
    if (article.title is None or
            "The University of California San Francisco Preoperative Diffuse Glioma MRI Dataset"
            not in article.title.get_text(" ", strip=True)):
        raise ValueError("Unexpected PMC article")
    for tag in article(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = "\n".join(line.strip() for line in article.get_text("\n").splitlines() if line.strip())
    csv_bytes = retrieved["metadata_v5.csv"][0]
    decoded = csv_bytes.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(decoded)))
    if len(rows) < 490:
        raise ValueError("Unexpectedly short UCSF metadata")
    OUT.mkdir(parents=True)
    for name, (body, _) in retrieved.items():
        (OUT / name).write_bytes(body)
    (OUT / "pmc_article.txt").write_text(text + "\n", encoding="utf-8")
    index = {"sources": {name: details for name, (_, details) in retrieved.items()},
             "metadata_rows": len(rows), "metadata_columns": list(rows[0]),
             "patient_pixels_read": False}
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
