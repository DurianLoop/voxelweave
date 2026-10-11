"""Archive three open full texts for acquisition/access qualification."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/thin3d_glioma_candidate_fulltexts_2026-10-01"
ARTICLES = {"gazi_brains_2020": "PMC12192951",
            "posttreatment_t2_lesion": "PMC11117752",
            "glioma_7t_t2": "PMC11775408"}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for name, pmcid in ARTICLES.items():
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
        item = {"name": name, "pmcid": pmcid, "url": url}
        try:
            with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"}),
                             timeout=30) as response:
                raw = response.read(3_000_001)
                item["status"] = response.status
                item["content_type"] = response.headers.get("Content-Type")
            if len(raw) > 3_000_000:
                raise ValueError("Full text exceeded 3 MB cap")
            file = f"{name}.xml"
            (OUT / file).write_bytes(raw)
            item.update({"file": file, "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest()})
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
        records.append(item)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
