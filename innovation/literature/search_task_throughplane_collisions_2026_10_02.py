"""Bounded primary-index discovery for MRI SR/through-plane downstream methods."""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/task_throughplane_collision_2026-10-02"
PLAN = ROOT / "2026-10-02_task_throughplane_collision_search_plan.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(item):
    name, provider, query, cap = item
    if provider == "europepmc":
        params = {"query": query + " AND FIRST_PDATE:[2015-01-01 TO 2026-10-02]", "format": "json", "resultType": "core", "pageSize": cap}
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(params)
    else:
        params = {"query": query, "rows": cap, "filter": "from-pub-date:2015-01-01,until-pub-date:2026-10-02"}
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    path = OUT / (name + ".json")
    result = {"query": query, "provider": provider, "url": url, "raw_file": path.name, "requested_cap": cap}
    try:
        if not path.exists():
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"}), timeout=35) as response:
                raw = response.read(5_000_001)
                result.update({"http_status": response.status, "final_url": response.url})
            if len(raw) > 5_000_000:
                raise ValueError("Discovery response exceeds 5 MB cap")
            path.write_bytes(raw)
        data = json.loads(path.read_text(encoding="utf-8"))
        if provider == "europepmc":
            items = data["resultList"]["result"]
            result["reported_total"] = data["hitCount"]
            result["items"] = [{"title": x.get("title"), "doi": x.get("doi"), "pmid": x.get("id"), "pmcid": x.get("pmcid"),
                                "year": x.get("pubYear"), "abstract": x.get("abstractText"), "authors": x.get("authorString"),
                                "fulltext_urls": x.get("fullTextUrlList"), "oa": x.get("isOpenAccess")} for x in items]
        else:
            items = data["message"]["items"]
            result["reported_total"] = data["message"]["total-results"]
            result["items"] = [{"title": x.get("title", [None])[0], "doi": x.get("DOI"), "type": x.get("type"),
                                "published": x.get("published"), "abstract": x.get("abstract"), "url": x.get("URL"),
                                "fulltext_urls": x.get("link"), "licenses": x.get("license")} for x in items]
        result.update({"raw_sha256": sha(path), "bytes": path.stat().st_size, "returned": len(items)})
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    attempts = len(list(OUT.glob("attempt_*.json"))) + 1
    searches = [
        ("epmc_sr_task", "europepmc", '(TITLE_ABS:"super resolution" OR TITLE_ABS:"super-resolution") AND (TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:segmentation OR TITLE_ABS:lesion OR TITLE_ABS:tumor)', 25),
        ("epmc_slice_task", "europepmc", 'TITLE_ABS:"slice interpolation" AND (TITLE_ABS:segmentation OR TITLE_ABS:tumor OR TITLE_ABS:lesion)', 20),
        ("crossref_sr_task", "crossref", "magnetic resonance super resolution brain lesion segmentation", 10),
        ("crossref_task_driven", "crossref", "task driven MRI super resolution segmentation", 10),
    ]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, searches))
    result = {"attempt": attempts, "script_sha256": sha(Path(__file__)), "plan_sha256": sha(PLAN),
              "scope": "bounded discovery, title/abstract indexing only", "responses": results}
    (OUT / f"attempt_{attempts:02d}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in results:
        print(json.dumps({k: row.get(k) for k in ("provider", "query", "returned", "reported_total", "error")}, ensure_ascii=False))
        for x in row.get("items", []):
            print(json.dumps({k: x.get(k) for k in ("title", "doi", "pmcid", "year")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
