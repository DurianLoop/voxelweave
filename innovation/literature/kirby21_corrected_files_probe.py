"""Read the NITRC file group ID linked by the official Kirby21 project page."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT / "source_cache/kirby21_public_metadata_2026-10-01/index.json"
OUT = ROOT / "source_cache/kirby21_corrected_files_2026-10-01"
URL = "https://www.nitrc.org/frs/?group_id=313"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of corrected file-list probe")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(URL, headers={"User-Agent": "MRI-source-audit/1.0"})
    result = {"correction": "Official project links group_id=313; the first probe used 324",
              "previous_probe_sha256": hashlib.sha256(PREVIOUS.read_bytes()).hexdigest(),
              "url": URL}
    try:
        with opener.open(request, timeout=30) as response:
            result.update({"status": response.status, "final_url": response.url,
                           "content_type": response.headers.get("Content-Type")})
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("File-list page exceeded metadata bound")
        (OUT / "page.html").write_bytes(raw)
        result.update({"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                       "page_file": "page.html"})
    except Exception as error:
        result.update({"error_type": type(error).__name__, "error": str(error)[:200]})
    (OUT / "index.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
