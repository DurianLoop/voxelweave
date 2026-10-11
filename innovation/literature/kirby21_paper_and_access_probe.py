"""Archive Kirby21 paper metadata/open text and a header-only download check."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/kirby21_paper_access_2026-10-01"
DOI = "10.1016/j.neuroimage.2010.11.047"
SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({
    "query": f"DOI:{DOI}", "format": "json"})
SESSION_URL = "https://www.nitrc.org/frs/downloadlink.php/2201"


def fetch(opener: urllib.request.OpenerDirector, url: str, name: str,
          max_bytes: int = 3_000_000) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=30) as response:
        raw = response.read(max_bytes + 1)
        result = {"status": response.status, "url": url, "final_url": response.url,
                  "content_type": response.headers.get("Content-Type")}
    if len(raw) > max_bytes:
        raise ValueError(f"Response exceeded bounded metadata/text transfer: {name}")
    (OUT / name).write_bytes(raw)
    result.update({"file": name, "bytes": len(raw),
                   "sha256": hashlib.sha256(raw).hexdigest()})
    return result


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of Kirby21 article/access probe")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    result: dict = {"doi": DOI, "article": None, "fulltext": None, "session_head": None}
    try:
        result["article"] = fetch(opener, SEARCH_URL, "europepmc_search.json")
        records = json.loads((OUT / "europepmc_search.json").read_text(encoding="utf-8"))
        matches = [row for row in records["resultList"]["result"]
                   if row.get("doi", "").lower() == DOI.lower()]
        result["exact_doi_matches"] = [{key: row.get(key) for key in
                                        ("title", "authorString", "journalTitle", "pubYear",
                                         "pmid", "pmcid", "isOpenAccess", "hasPDF")}
                                       for row in matches]
        if len(matches) == 1 and matches[0].get("pmcid"):
            pmcid = matches[0]["pmcid"]
            url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
            result["fulltext"] = fetch(opener, url, "fulltext.xml")
    except Exception as error:
        result["article_error"] = f"{type(error).__name__}: {str(error)[:180]}"
    try:
        request = urllib.request.Request(
            SESSION_URL, method="HEAD", headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=30) as response:
            result["session_head"] = {"url": SESSION_URL, "status": response.status,
                                      "final_url": response.url,
                                      "content_type": response.headers.get("Content-Type"),
                                      "content_length": response.headers.get("Content-Length"),
                                      "content_disposition": response.headers.get("Content-Disposition"),
                                      "body_bytes_read": 0}
    except Exception as error:
        result["session_head_error"] = f"{type(error).__name__}: {str(error)[:180]}"
    (OUT / "index.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
