"""Check public IBM Aspera SDK/CLI repository guidance without transfer."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache" / "ibm_aspera_alternatives_2026-10-01"
REPOS = ("IBM/aspera-sdk-js", "IBM/aspera-cli")


def read(opener, url: str, limit: int = 1_000_000) -> tuple[bytes, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=18) as response:
        raw = response.read(limit + 1)
        if response.status != 200 or len(raw) > limit:
            raise RuntimeError("Unexpected response")
        return raw, {"url": url, "final_url": response.geturl(), "status": response.status,
                     "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {"patient_data_requested": False, "transfer_started": False, "repos": {}}
    for repo in REPOS:
        key = repo.replace("/", "_")
        record = {}
        try:
            raw, meta = read(opener, f"https://api.github.com/repos/{repo}")
            record["repository"] = meta
            data = json.loads(raw)
            branch = data["default_branch"]
            record["description"] = data.get("description")
            record["default_branch"] = branch
            (OUT / f"{key}_repo.json").write_bytes(raw)
            raw, meta = read(opener, f"https://raw.githubusercontent.com/{repo}/{branch}/README.md")
            record["readme"] = meta
            (OUT / f"{key}_README.md").write_bytes(raw)
        except urllib.error.HTTPError as error:
            record["http_error"] = error.code
        except (urllib.error.URLError, TimeoutError, RuntimeError, KeyError) as error:
            record["error_type"] = type(error).__name__
        report["repos"][repo] = record
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
