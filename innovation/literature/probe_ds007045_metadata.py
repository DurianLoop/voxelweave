"""Archive bounded, non-pixel metadata responses for OpenNeuro ds007045."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/ds007045_metadata_2026-10-01"
REQUESTS = [
    ("openneuro_page", "https://openneuro.org/datasets/ds007045/versions/1.0.1", None),
    ("datacite", "https://api.datacite.org/dois/10.18112/openneuro.ds007045.v1.0.1", None),
    ("s3_listing", "https://s3.amazonaws.com/openneuro.org?list-type=2&prefix=ds007045/&max-keys=20", None),
    ("github_readme", "https://raw.githubusercontent.com/OpenNeuroDatasets/ds007045/master/README", None),
    ("graphql_dataset", "https://openneuro.org/crn/graphql", {
        "query": "query { dataset(id: \"ds007045\") { id latestSnapshot { tag } } }"
    }),
]


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    results = []
    for name, url, payload in REQUESTS:
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"User-Agent": "MRI-source-audit/1.0"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers)
        try:
            with opener.open(request, timeout=25) as response:
                raw = response.read(1_000_001)
                status = response.status
                content_type = response.headers.get("Content-Type", "")
                final_url = response.url
        except urllib.error.HTTPError as exc:
            raw = exc.read(1_000_001)
            status = exc.code
            content_type = exc.headers.get("Content-Type", "")
            final_url = exc.url
        except Exception as exc:
            results.append({"name": name, "url": url, "error": f"{type(exc).__name__}: {exc}"})
            continue
        row = {"name": name, "url": url, "status": status,
               "content_type": content_type, "final_url": final_url}
        if len(raw) > 1_000_000:
            row["error"] = "Body exceeded 1 MB; discarded"
        else:
            suffix = ".json" if "json" in content_type else ".xml" if "xml" in content_type else ".html"
            path = OUT / f"{name}{suffix}"
            path.write_bytes(raw)
            row.update(file=path.name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        results.append(row)
    (OUT / "index.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
