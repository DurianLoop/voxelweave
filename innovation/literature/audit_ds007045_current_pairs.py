"""Count current public processed T2 / mask pairs from bounded S3 listings."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "literature/source_cache/ds007045_current_pair_audit_2026-10-01"
PREFIXES = ("ds007045/derivatives/processing/", "ds007045/derivatives/segmentation/")
NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}


def pages(prefix: str, group: str) -> list[str]:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    token = None
    keys: list[str] = []
    for page_no in range(1, 6):
        query = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            query["continuation-token"] = token
        url = "https://s3.amazonaws.com/openneuro.org?" + urllib.parse.urlencode(query)
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=30) as response:
            if response.status != 200:
                raise ValueError(f"S3 listing HTTP {response.status}")
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("Listing exceeded 1 MB cap")
        path = OUT / f"{group}_page_{page_no}.xml"
        path.write_bytes(raw)
        root = ET.fromstring(raw)
        keys.extend(x.findtext("s:Key", namespaces=NS) or "" for x in root.findall("s:Contents", NS))
        record = {"url": url, "file": path.name, "bytes": len(raw),
                  "sha256": hashlib.sha256(raw).hexdigest(),
                  "key_count": len(root.findall("s:Contents", NS)),
                  "truncated": root.findtext("s:IsTruncated", namespaces=NS)}
        (OUT / f"{group}_page_{page_no}.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if record["truncated"] == "false":
            return keys
        token = root.findtext("s:NextContinuationToken", namespaces=NS)
        if not token:
            raise ValueError("Truncated listing has no continuation token")
    raise ValueError("Exceeded five-page cap")


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    processing = pages(PREFIXES[0], "processing")
    segmentation = pages(PREFIXES[1], "segmentation")
    t2_by_subject = {}
    mask_by_subject = {}
    for key in processing:
        parts = key.split("/")
        if len(parts) == 5 and parts[3].startswith("sub-") and parts[4] == f"{parts[3]}_t2_MNI152_brain.nii.gz":
            t2_by_subject.setdefault(parts[3], []).append(key)
    for key in segmentation:
        parts = key.split("/")
        if len(parts) == 5 and parts[3].startswith("sub-") and parts[4] == f"{parts[3]}_MNI152_tumor-mask.nii.gz":
            mask_by_subject.setdefault(parts[3], []).append(key)
    t2 = set(t2_by_subject)
    masks = set(mask_by_subject)
    paired = sorted(t2 & masks)
    result = {
        "scope": "current unversioned S3 keys; dataset_description identifies v2.0.1",
        "processing_keys": len(processing), "segmentation_keys": len(segmentation),
        "t2_subjects": len(t2), "mask_subjects": len(masks), "paired_subjects": len(paired),
        "t2_only": sorted(t2 - masks), "mask_only": sorted(masks - t2),
        "duplicate_t2_subjects": sorted(k for k, v in t2_by_subject.items() if len(v) != 1),
        "duplicate_mask_subjects": sorted(k for k, v in mask_by_subject.items() if len(v) != 1),
        "paired_site_prefix_counts": dict(sorted(Counter(s.split("-")[1].rstrip("0123456789") for s in paired).items())),
        "paired_subjects_list": paired,
        "no_pixels": True,
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "paired_subjects_list"}, indent=2))


if __name__ == "__main__":
    main()
