"""Download two title/abstract-screened arXiv papers for full-text review."""
from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PAPERS = {
    "2026_Measured_Subspace_Consistency_MRI.pdf": "2606.28448v1",
    "2023_Local_Lipschitz_MRI_Uncertainty.pdf": "2305.07618v3",
}
PARTIAL_FIRST_SHA = "e91098888ee19098c26bd822494e06a24b1e34a1aa3dad4653738ebf0a34aa86"


def main() -> None:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for name, arxiv_id in PAPERS.items():
        path = ROOT / name
        if path.exists():
            data = path.read_bytes()
            if name != "2026_Measured_Subspace_Consistency_MRI.pdf" or hashlib.sha256(data).hexdigest() != PARTIAL_FIRST_SHA:
                raise FileExistsError("Existing PDF differs from the verified partial download")
            records.append({"path": f"innovation/literature/{name}",
                            "source_url": f"https://arxiv.org/pdf/{arxiv_id}",
                            "bytes": len(data), "sha256": PARTIAL_FIRST_SHA})
            continue
        urls = [f"https://arxiv.org/pdf/{arxiv_id}",
                f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                f"https://export.arxiv.org/pdf/{arxiv_id}"]
        data = None
        source_url = None
        for url in urls:
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                                               "Accept": "application/pdf"})
                with opener.open(request, timeout=45) as response:
                    candidate = response.read()
                    if response.status == 200 and candidate.startswith(b"%PDF-"):
                        data, source_url = candidate, url
                        break
            except urllib.error.HTTPError as exc:
                if exc.code not in (403, 404, 406):
                    raise
        if data is None or source_url is None:
            raise RuntimeError(f"No arXiv PDF endpoint responded for {arxiv_id}")
        path.write_bytes(data)
        records.append({"path": f"innovation/literature/{name}",
                        "source_url": source_url,
                        "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest()})
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
