"""Archive metadata and available full-text XML for three glioma datasets."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache" / "three_glioma_descriptors_2026-10-01"
DOIS = {
    "lumiere_2022": "10.1038/s41597-022-01881-7",
    "gbm_standardized_2026": "10.1038/s41597-026-07953-2",
    "ucsd_ptgbm_2025": "10.1038/s41597-025-06499-z",
}


def fetch(opener, url: str, limit: int = 1_500_000) -> tuple[int, bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=25) as response:
        raw = response.read(limit + 1)
        if len(raw) > limit:
            raise RuntimeError("Response exceeds source cap")
        return response.status, raw, response.geturl()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {"patient_data_requested": False, "gpu_used": False, "papers": {}}
    for key, doi in DOIS.items():
        item = {"doi": doi}
        query = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({
            "query": f"DOI:{doi}", "format": "json", "pageSize": "5",
        })
        try:
            status, raw, final_url = fetch(opener, query)
            (OUT / f"{key}_search.json").write_bytes(raw)
            item["search"] = {"url": query, "status": status, "final_url": final_url,
                              "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            entries = json.loads(raw).get("resultList", {}).get("result", [])
            exact = [entry for entry in entries if entry.get("doi", "").lower() == doi.lower()]
            item["exact_records"] = len(exact)
            pmcid = exact[0].get("pmcid") if exact else None
            item["pmcid"] = pmcid
            if pmcid:
                full_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
                try:
                    status, raw, final_url = fetch(opener, full_url)
                    (OUT / f"{key}_fulltext.xml").write_bytes(raw)
                    item["fulltext"] = {"url": full_url, "status": status,
                                        "final_url": final_url, "bytes": len(raw),
                                        "sha256": hashlib.sha256(raw).hexdigest()}
                except urllib.error.HTTPError as error:
                    item["fulltext_http_status"] = error.code
        except urllib.error.HTTPError as error:
            item["search_http_status"] = error.code
        except (urllib.error.URLError, TimeoutError, RuntimeError) as error:
            item["error_type"] = type(error).__name__
        report["papers"][key] = item
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
