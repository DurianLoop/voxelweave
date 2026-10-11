"""Archive accessible full-text routes for three selected MRI papers."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/mira_four_seed_fulltext_routes_2026-10-01"
ROUTES = {
    "mind_detail_arxiv_html": "https://arxiv.org/html/2507.00670v1",
    "structural_uncertainty_arxiv_html": "https://arxiv.org/html/2503.10527v2",
    "segmentation_guided_arxiv_html": "https://arxiv.org/html/2407.18026v1",
    "mind_detail_springer_pdf": "https://link.springer.com/content/pdf/10.1007/978-3-032-04937-7_34.pdf",
    "structural_uncertainty_springer_pdf": "https://link.springer.com/content/pdf/10.1007/978-3-032-09513-8_49.pdf",
    "segmentation_guided_springer_pdf": "https://link.springer.com/content/pdf/10.1007/978-3-031-72744-3_18.pdf",
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records, files = [], {}
    for name, url in ROUTES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"})
        try:
            with opener.open(request, timeout=35) as response:
                raw = response.read()
                status = response.status
                content_type = response.headers.get("Content-Type", "")
            expected_pdf = name.endswith("_pdf")
            valid = raw.startswith(b"%PDF-") if expected_pdf else b"<html" in raw[:1000].lower()
            if status != 200 or not valid:
                raise ValueError(f"unexpected response: HTTP {status}, type {content_type}, bytes {len(raw)}")
            suffix = ".pdf" if expected_pdf else ".html"
            files[name + suffix] = raw
            records.append({"name": name, "url": url, "status": status, "bytes": len(raw),
                            "sha256": hashlib.sha256(raw).hexdigest(),
                            "content_type": content_type, "saved_as": name + suffix})
        except Exception as error:
            records.append({"name": name, "url": url,
                            "error": f"{type(error).__name__}: {error}"})
    OUT.mkdir(parents=True)
    for name, raw in files.items():
        (OUT / name).write_bytes(raw)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{key: row.get(key) for key in ("name", "status", "bytes", "error")}
                      for row in records], indent=2))


if __name__ == "__main__":
    main()
