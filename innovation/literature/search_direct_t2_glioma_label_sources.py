"""Bounded OpenAlex metadata search for directly accessible T2 glioma labels."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache" / "direct_t2_glioma_label_search_2026-10-01"
QUERIES = (
    "LUMIERE longitudinal glioblastoma MRI tumor segmentation dataset",
    "public glioma MRI T2 tumor segmentation dataset Zenodo",
    "glioblastoma MRI T2 expert segmentation dataset download",
    "independent brain tumor T2 MRI segmentation data descriptor",
)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {"patient_data_requested": False, "gpu_used": False, "queries": []}
    for index, query in enumerate(QUERIES, start=1):
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
            "search": query, "per-page": "25", "select": "id,doi,title,publication_year,open_access,primary_location,best_oa_location,ids",
        })
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=25) as response:
            raw = response.read(2_000_001)
            if response.status != 200 or len(raw) > 2_000_000:
                raise RuntimeError("Unexpected OpenAlex response")
        path = OUT / f"query_{index}.json"
        path.write_bytes(raw)
        body = json.loads(raw)
        report["queries"].append({"query": query, "url": url, "bytes": len(raw),
                                  "sha256": hashlib.sha256(raw).hexdigest(),
                                  "returned": len(body.get("results", [])),
                                  "total_count": body.get("meta", {}).get("count")})
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
