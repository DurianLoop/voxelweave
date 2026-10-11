"""Archive a bounded OpenAlex citing-work screen for four MRI error papers."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_snapshots/mira_four_seed_citations_2026-10-01"
SEEDS = {
    "hu2021": "10.1007/978-3-030-87199-4_57",
    "kuestner2024": "10.1002/mrm.30030",
    "npb_rec2022": "10.48550/arXiv.2208.03966",
    "radmanesh2022": "10.1148/ryai.210313",
}


def fetch(opener: urllib.request.OpenerDirector, url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"})
    with opener.open(request, timeout=35) as response:
        data = response.read()
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return data


def abstract(index: dict | None) -> str | None:
    if not index:
        return None
    words = []
    for word, positions in index.items():
        words.extend((position, word) for position in positions)
    return " ".join(word for _, word in sorted(words))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    raw_files = {}
    results = []
    for name, doi in SEEDS.items():
        detail_url = "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/")
        try:
            detail_raw = fetch(opener, detail_url)
            detail = json.loads(detail_raw)
            work_id = detail["id"].rsplit("/", 1)[-1]
            query = urllib.parse.urlencode({"filter": f"cites:{work_id}",
                                            "sort": "publication_date:desc", "per-page": 100})
            citing_url = "https://api.openalex.org/works?" + query
            citing_raw = fetch(opener, citing_url)
            citing = json.loads(citing_raw)
            rows = []
            for work in citing.get("results", []):
                source = (work.get("primary_location") or {}).get("source") or {}
                rows.append({"id": work.get("id"), "doi": work.get("doi"),
                             "year": work.get("publication_year"), "title": work.get("display_name"),
                             "venue": source.get("display_name"),
                             "abstract": abstract(work.get("abstract_inverted_index"))})
            raw_files[f"{name}_seed.json"] = detail_raw
            raw_files[f"{name}_citations.json"] = citing_raw
            results.append({"name": name, "seed_doi": doi, "seed_openalex_id": work_id,
                            "seed_url": detail_url, "seed_sha256": hashlib.sha256(detail_raw).hexdigest(),
                            "citing_url": citing_url, "citing_sha256": hashlib.sha256(citing_raw).hexdigest(),
                            "total_count": citing["meta"]["count"], "returned": len(rows), "works": rows})
        except Exception as error:
            results.append({"name": name, "seed_doi": doi,
                            "error": f"{type(error).__name__}: {error}"})
    OUT.mkdir(parents=True)
    for name, data in raw_files.items():
        (OUT / name).write_bytes(data)
    (OUT / "index.json").write_text(json.dumps({"date": "2026-10-01", "seeds": results},
                                               ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{key: row.get(key) for key in ("name", "seed_openalex_id", "total_count",
                                                      "returned", "error")}
                      for row in results], indent=2))


if __name__ == "__main__":
    main()
