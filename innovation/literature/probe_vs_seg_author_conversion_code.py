"""Archive the author repo tree for RTSTRUCT/contour conversion semantics."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import urllib.parse
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/vs_seg_author_code_2026-10-01"
BASE = "https://api.github.com/repos/KCL-BMEIS/VS_Seg"


def fetch(url: str, cap: int) -> bytes:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0",
                                               "Accept": "application/vnd.github+json"})
    with opener.open(req, timeout=30) as response:
        raw = response.read(cap + 1)
        if response.status != 200 or len(raw) > cap:
            raise ValueError("Unexpected GitHub response")
    return raw


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url, cap in (("repository", BASE, 200_000),):
        path = OUT / f"{name}.json"
        raw = path.read_bytes() if path.exists() else fetch(url, cap)
        if len(raw) > cap:
            raise ValueError("Cached GitHub response exceeds cap")
        if not path.exists():
            path.write_bytes(raw)
        records.append({"name": name, "url": url, "file": f"{name}.json",
                        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    repository = json.loads((OUT / "repository.json").read_bytes())
    branch = repository["default_branch"]
    url = BASE + "/git/trees/" + branch + "?recursive=1"
    tree_path = OUT / "tree.json"
    raw = tree_path.read_bytes() if tree_path.exists() else fetch(url, 10_000_000)
    if len(raw) > 10_000_000:
        raise ValueError("Cached GitHub tree exceeds cap")
    if not tree_path.exists():
        tree_path.write_bytes(raw)
    tree = json.loads(raw)
    records.append({"name": "tree", "url": url, "file": "tree.json",
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "tree_sha": tree.get("sha"), "truncated": tree.get("truncated")})
    cases = ("001", "004", "063", "073", "010", "133")
    contour_files = tuple("preprocessing/createBIDSdataset/VS-SEG-BIDS-nonifti/sourcedata/contours/"
                          f"sub-{case}/anat/sub-{case}_contours_space-individual_T2w.json"
                          for case in cases)
    wanted = ("README.md", "preprocessing/README.md",
              "preprocessing/createBIDSdataset/README.md",
              "preprocessing/TCIA_data_convert_into_convenient_folder_structure.py",
              "preprocessing/data_conversion.py",
              "preprocessing/createBIDSdataset/data_conversion_BIDS.py") + contour_files
    blobs = {x["path"]: x for x in tree.get("tree", []) if x.get("type") == "blob"}
    for path in wanted:
        item = blobs[path]
        if item["size"] > 1_000_000:
            raise ValueError("Unexpected author code file size")
        url = "https://raw.githubusercontent.com/KCL-BMEIS/VS_Seg/" + tree["sha"] + "/" + urllib.parse.quote(path)
        local = OUT / path
        local.parent.mkdir(parents=True, exist_ok=True)
        raw = local.read_bytes() if local.exists() else fetch(url, 1_000_000)
        if not local.exists():
            local.write_bytes(raw)
        records.append({"name": "author_file", "url": url, "file": path,
                        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                        "git_blob_sha": item["sha"]})
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"branch": branch, "tree_sha": tree.get("sha"),
                      "files": list(wanted)},
                     indent=2))


if __name__ == "__main__":
    main()
