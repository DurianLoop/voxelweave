"""Bounded Europe PMC metadata screen for an independent thin-3D T2 cohort."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "search_snapshots/thin3d_glioma_refresh_2026-10-01"
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
QUERIES = (
    '(glioma OR glioblastoma) AND ("3D T2" OR "T2 SPACE") AND (dataset OR database) AND (segmentation OR annotation)',
    '(glioma OR glioblastoma) AND "isotropic T2" AND (dataset OR cohort)',
    '("brain tumor" OR glioma) AND "high resolution T2" AND (segmentation OR annotation)',
)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for number, query in enumerate(QUERIES):
        url = BASE + "?" + urllib.parse.urlencode({
            "query": query, "format": "json", "resultType": "lite", "pageSize": 20})
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        item = {"query": query, "url": url}
        try:
            with opener.open(request, timeout=30) as response:
                raw = response.read(400_001)
                item["status"] = response.status
            if len(raw) > 400_000:
                raise ValueError("Response exceeded 400 kB cap")
            parsed = json.loads(raw)
            file = f"query_{number}.json"
            (OUT / file).write_bytes(raw)
            item.update({"file": file, "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest(),
                         "hitCount": parsed.get("hitCount"),
                         "titles": [{k: work.get(k) for k in ("title", "authorString", "pubYear", "doi", "pmcid", "id")}
                                    for work in parsed.get("resultList", {}).get("result", [])]})
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
        records.append(item)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{k: r.get(k) for k in ("hitCount", "error", "titles")} for r in records], indent=2))


if __name__ == "__main__":
    main()
