"""Bounded non-image source search across alternative public metadata APIs."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache" / "direct_t2_glioma_alt_search_2026-10-01"
TARGETS = {
    "datacite_lumiere": "https://api.datacite.org/dois?" + urllib.parse.urlencode({
        "query": "LUMIERE glioblastoma MRI", "page[size]": "10"}),
    "crossref_lumiere": "https://api.crossref.org/works?" + urllib.parse.urlencode({
        "query.title": "LUMIERE glioblastoma MRI dataset", "rows": "10"}),
    "zenodo_lumiere": "https://zenodo.org/api/records?" + urllib.parse.urlencode({
        "q": "LUMIERE glioblastoma MRI", "size": "10"}),
    "github_lumiere": "https://api.github.com/search/repositories?" + urllib.parse.urlencode({
        "q": "LUMIERE glioblastoma MRI", "per_page": "10"}),
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {"patient_data_requested": False, "gpu_used": False, "sources": {}}
    for name, url in TARGETS.items():
        item = {"url": url}
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0",
                                                           "Accept": "application/json"})
            with opener.open(request, timeout=18) as response:
                raw = response.read(1_000_001)
                item.update({"http_status": response.status, "bytes": len(raw),
                             "truncated": len(raw) > 1_000_000,
                             "sha256": hashlib.sha256(raw).hexdigest()})
                if response.status == 200 and len(raw) <= 1_000_000:
                    (OUT / f"{name}.json").write_bytes(raw)
        except urllib.error.HTTPError as error:
            item["http_status"] = error.code
        except (urllib.error.URLError, TimeoutError) as error:
            item["error_type"] = type(error).__name__
        report["sources"][name] = item
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
