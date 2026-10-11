"""Bounded direct reads of public IBM Connect documentation routes."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache" / "ibm_connect_docs_probe_2026-10-01"
URLS = {
    "ibm_connect_docs": "https://www.ibm.com/docs/en/aspera-connect",
    "ibm_connect_help": "https://ibmaspera.com/help",
    "ibm_connect_sdk_repo": "https://github.com/IBM/aspera-connect-sdk-js",
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {"patient_data_requested": False, "transfer_started": False, "responses": {}}
    for name, url in URLS.items():
        item = {"url": url}
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
            with opener.open(request, timeout=18) as response:
                raw = response.read(1_000_001)
                item.update({"status": response.status, "final_url": response.geturl(),
                             "content_type": response.headers.get("Content-Type"),
                             "bytes_read": len(raw), "truncated": len(raw) > 1_000_000,
                             "sha256": hashlib.sha256(raw).hexdigest()})
                if response.status == 200 and len(raw) <= 1_000_000:
                    (OUT / f"{name}.html").write_bytes(raw)
        except urllib.error.HTTPError as error:
            item["status"] = error.code
        except (urllib.error.URLError, TimeoutError) as error:
            item["error_type"] = type(error).__name__
        report["responses"][name] = item
    (OUT / "index.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
