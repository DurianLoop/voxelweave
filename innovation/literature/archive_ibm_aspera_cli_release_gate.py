"""Archive official ascli release metadata and Faspex5 source for scope review."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache" / "ibm_aspera_cli_release_gate_2026-10-01"
URLS = {
    "latest_release.json": "https://api.github.com/repos/IBM/aspera-cli/releases/latest",
    "faspex5.rb": "https://raw.githubusercontent.com/IBM/aspera-cli/main/lib/aspera/cli/plugins/faspex5.rb",
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
    release = json.loads((OUT / "latest_release.json").read_text(encoding="utf-8"))
    report["version"] = release.get("tag_name")
    report["portable_assets"] = [
        {"name": item["name"], "size": item["size"], "digest": item.get("digest"),
         "url": item["browser_download_url"]}
        for item in release.get("assets", []) if "windows-x86_64-portable" in item["name"]
    ]
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
