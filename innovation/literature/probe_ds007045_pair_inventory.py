"""Archive small official metadata and bounded S3 keys for one ds007045 subject."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/ds007045_pair_inventory_2026-10-01"
SUBJECT = "sub-BA2"
PREFIXES = [
    f"ds007045/{SUBJECT}/",
    f"ds007045/derivatives/processing/{SUBJECT}/",
    f"ds007045/derivatives/segmentation/{SUBJECT}/",
    "ds007045/derivatives/segmentation/",
]
TEXT_FILES = ["README.txt", "dataset_description.json", "CHANGES"]


def fetch(opener: urllib.request.OpenerDirector, url: str) -> tuple[int, bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    try:
        with opener.open(request, timeout=25) as response:
            return response.status, response.read(100_001), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(100_001), exc.headers.get("Content-Type", "")


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for name in TEXT_FILES:
        url = f"https://s3.amazonaws.com/openneuro.org/ds007045/{name}"
        status, body, content_type = fetch(opener, url)
        path = OUT / name
        if len(body) > 100_000:
            records.append({"name": name, "status": status, "error": "Too large"})
            continue
        path.write_bytes(body)
        records.append({"name": name, "url": url, "status": status,
                        "content_type": content_type, "bytes": len(body),
                        "sha256": hashlib.sha256(body).hexdigest()})
    for n, prefix in enumerate(PREFIXES):
        query = urllib.parse.urlencode({"list-type": "2", "prefix": prefix, "max-keys": "30"})
        url = f"https://s3.amazonaws.com/openneuro.org?{query}"
        status, body, content_type = fetch(opener, url)
        path = OUT / f"prefix_{n}.xml"
        if len(body) > 100_000:
            records.append({"prefix": prefix, "status": status, "error": "Too large"})
            continue
        path.write_bytes(body)
        row = {"prefix": prefix, "url": url, "status": status,
               "content_type": content_type, "bytes": len(body),
               "sha256": hashlib.sha256(body).hexdigest()}
        if status == 200:
            root = ET.fromstring(body)
            ns = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
            row["is_truncated"] = root.findtext("s:IsTruncated", namespaces=ns)
            row["keys"] = [{"key": x.findtext("s:Key", namespaces=ns),
                             "size": int(x.findtext("s:Size", namespaces=ns) or 0)}
                           for x in root.findall("s:Contents", ns)]
        records.append(row)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
