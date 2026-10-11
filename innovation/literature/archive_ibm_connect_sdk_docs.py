"""Archive bounded public IBM Connect SDK repository documentation."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache" / "ibm_connect_sdk_docs_2026-10-01"
BASE = "https://api.github.com/repos/IBM/aspera-connect-sdk-js"


def fetch(opener, url: str, limit: int = 1_000_000) -> tuple[bytes, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0",
                                                   "Accept": "application/vnd.github+json"})
    with opener.open(request, timeout=20) as response:
        raw = response.read(limit + 1)
        if response.status != 200 or len(raw) > limit:
            raise RuntimeError(f"Unexpected response for {url}")
        return raw, {"url": url, "final_url": response.geturl(), "http_status": response.status,
                     "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {"patient_data_requested": False, "transfer_started": False, "sources": {}}
    try:
        raw, record = fetch(opener, BASE)
        (OUT / "repo.json").write_bytes(raw)
        report["sources"]["repo.json"] = record
        branch = json.loads(raw)["default_branch"]
        if not isinstance(branch, str) or not branch.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Unexpected default branch")
        for name, url in {
            "README.md": f"https://raw.githubusercontent.com/IBM/aspera-connect-sdk-js/{branch}/README.md",
            "tree.json": BASE + f"/git/trees/{branch}?recursive=1",
        }.items():
            raw, record = fetch(opener, url)
            (OUT / name).write_bytes(raw)
            report["sources"][name] = record
        report["default_branch"] = branch
    except (urllib.error.URLError, TimeoutError, RuntimeError, KeyError, ValueError) as error:
        report["error_type"] = type(error).__name__
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
