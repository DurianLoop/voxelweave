"""Bounded read-only official/public metadata probe for Kirby21."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "literature/source_cache/kirby21_public_metadata_2026-10-01"
PLAN = ROOT / "KIRBY21_REPEAT_T2_SOURCE_GATE_PLAN_2026-10-01.md"
URLS = {
    "openalex": "https://api.openalex.org/works?" + urllib.parse.urlencode({
        "search": "Multi-Modal MRI Reproducibility Resource Landman",
        "per-page": 5,
    }),
    "nitrc_project": "https://www.nitrc.org/projects/multimodal/",
    "nitrc_files": "https://www.nitrc.org/frs/?group_id=324",
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite Kirby21 metadata probe")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    responses = []
    for name, url in URLS.items():
        row = {"name": name, "url": url}
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
            with opener.open(request, timeout=30) as response:
                row["status"] = response.status
                row["content_type"] = response.headers.get("Content-Type")
                row["final_url"] = response.url
                raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError("Metadata response exceeded two-MB bound")
            suffix = ".json" if "json" in (row["content_type"] or "") else ".html"
            filename = name + suffix
            (OUT / filename).write_bytes(raw)
            row.update({"file": filename, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
        except Exception as error:
            row.update({"error_type": type(error).__name__, "error": str(error)[:180]})
        responses.append(row)
    index = {"plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
             "responses": responses}
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(responses, indent=2))


if __name__ == "__main__":
    main()
