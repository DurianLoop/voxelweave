"""Resolve four exact DOI records and public full-text locations without credentials."""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/operator_multicontrast_candidates_2026-10-02"
DOIS = {
    "multi_contrast_tmi": "10.1109/tmi.2025.3628113",
    "knee_isotropic": "10.1016/j.compmedimag.2026.102786",
    "target_driven": "10.1016/j.mri.2026.110675",
    "kuestner": "10.1002/mrm.30030",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(item, attempt):
    key, doi, provider = item
    if provider == "europepmc":
        query = urllib.parse.urlencode({"query": "DOI:" + doi, "format": "json", "resultType": "core", "pageSize": 5})
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + query
    else:
        url = "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/")
    path = OUT / f"{key}_{provider}_attempt_{attempt:02d}.json"
    row = {"key": key, "doi": doi, "provider": provider, "url": url, "file": path.name}
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"}), timeout=25) as response:
            raw = response.read(3_000_001)
            row.update(status=response.status, content_type=response.headers.get("Content-Type"), final_url=response.url)
        if len(raw) > 3_000_000:
            raise ValueError("Metadata response exceeds size bound")
        path.write_bytes(raw)
        row.update(bytes=len(raw), sha256=sha(path))
        obj = json.loads(raw)
        if provider == "europepmc":
            row["records"] = [{k: rec.get(k) for k in ("title", "doi", "authorString", "pubYear", "id", "pmcid", "abstractText", "fullTextUrlList", "isOpenAccess", "hasPDF")}
                              for rec in obj.get("resultList", {}).get("result", [])]
        else:
            inverse = obj.get("abstract_inverted_index") or {}
            ordered = {position: word for word, positions in inverse.items() for position in positions}
            row["records"] = [{"id": obj.get("id"), "title": obj.get("title"), "doi": obj.get("doi"), "publication_date": obj.get("publication_date"),
                               "abstract": " ".join(ordered[i] for i in sorted(ordered)) if ordered else None,
                               "locations": [{k: loc.get(k) for k in ("landing_page_url", "pdf_url", "is_oa", "license", "version")} for loc in obj.get("locations", [])],
                               "authors": [rec["author"]["display_name"] for rec in obj.get("authorships", [])]}]
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    jobs = [(key, doi, provider) for key, doi in DOIS.items() for provider in ("europepmc", "openalex")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda item: fetch(item, attempt), jobs))
    result = {"attempt": attempt, "created_utc": datetime.now(timezone.utc).isoformat(), "script_sha256": sha(Path(__file__)), "responses": rows,
              "public_records_only": True, "article_bodies_read": False, "existing_cohort_contract_changed": False}
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps({k: row.get(k) for k in ("key", "provider", "status", "error", "records")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
