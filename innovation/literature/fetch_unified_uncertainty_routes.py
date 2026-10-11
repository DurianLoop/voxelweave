"""Archive official metadata and a repository page for a 2026 MRI UQ article."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/unified_mri_uncertainty_2026"
DOI = "10.1016/j.mri.2026.110680"
SOURCES = {
    "europepmc.json": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
                     + urllib.parse.urlencode({"query": f"DOI:{DOI}", "format": "json", "resultType": "core"}),
    "repository.html": "https://tsukuba.repo.nii.ac.jp/records/2025078",
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records, files = [], {}
    for name, url in SOURCES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"})
        try:
            with opener.open(request, timeout=30) as response:
                data = response.read()
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
            if name.endswith(".json"):
                payload = json.loads(data)
                matches = payload.get("resultList", {}).get("result", [])
                if not matches or matches[0].get("doi", "").lower() != DOI:
                    raise ValueError("Europe PMC DOI mismatch")
            elif b"<html" not in data[:1000].lower():
                raise ValueError("Expected repository HTML")
            files[name] = data
            records.append({"name": name, "url": url, "bytes": len(data),
                            "sha256": hashlib.sha256(data).hexdigest()})
        except Exception as error:
            records.append({"name": name, "url": url,
                            "error": f"{type(error).__name__}: {error}"})
    OUT.mkdir(parents=True)
    for name, data in files.items():
        (OUT / name).write_bytes(data)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
