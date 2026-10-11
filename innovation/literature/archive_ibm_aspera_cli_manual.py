"""Archive IBM Aspera CLI manual and repository tree for bounded review."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache" / "ibm_aspera_cli_manual_2026-10-01"
URLS = {
    "README.md": "https://raw.githubusercontent.com/IBM/aspera-cli/main/docs/README.md",
    "tree.json": "https://api.github.com/repos/IBM/aspera-cli/git/trees/main?recursive=1",
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {"patient_data_requested": False, "transfer_started": False, "sources": {}}
    for name, url in URLS.items():
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=25) as response:
            raw = response.read(2_000_001)
            if response.status != 200 or len(raw) > 2_000_000:
                raise RuntimeError(f"Unexpected response for {name}")
            report["sources"][name] = {"url": url, "final_url": response.geturl(),
                                       "status": response.status, "bytes": len(raw),
                                       "sha256": hashlib.sha256(raw).hexdigest()}
            (OUT / name).write_bytes(raw)
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
