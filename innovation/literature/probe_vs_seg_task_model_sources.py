"""Fetch fixed author inference code and pretrained-release metadata, no weights."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHOR = ROOT / "literature/source_cache/vs_seg_author_code_2026-10-01"
OUT = ROOT / "literature/source_cache/vs_seg_task_model_sources_2026-10-02"
PLAN = ROOT / "VS_SEG_TASK_MODEL_SOURCE_GATE_PLAN_2026-10-02.md"


def fetch(url: str, cap: int) -> bytes:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    with opener.open(req, timeout=35) as response:
        raw = response.read(cap + 1)
        if response.status != 200 or len(raw) > cap:
            raise ValueError("Response exceeds bounded source contract")
        return raw


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tree = json.loads((AUTHOR / "tree.json").read_text(encoding="utf-8"))
    blobs = {x["path"]: x for x in tree["tree"] if x["type"] == "blob"}
    records = []
    paths = ("VS_inference.py", "params/VSparams.py", "params/split_TCIA.csv",
             "requirements.txt", "params/networks/nets/unet2d5_spvPA.py", "LICENSE")
    for path in paths:
        item = blobs[path]
        url = "https://raw.githubusercontent.com/KCL-BMEIS/VS_Seg/" + tree["sha"] + "/" + urllib.parse.quote(path)
        local = OUT / path
        local.parent.mkdir(parents=True, exist_ok=True)
        raw = local.read_bytes() if local.exists() else fetch(url, 500_000)
        git_hash = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        if git_hash != item["sha"] or len(raw) != item["size"]:
            raise ValueError("Downloaded author code differs from fixed Git tree")
        if not local.exists():
            local.write_bytes(raw)
        records.append({"file": path, "url": url, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(), "git_blob_verified": True})
    model_url = "https://zenodo.org/api/records/6323472"
    local = OUT / "zenodo_record.json"
    try:
        raw = local.read_bytes() if local.exists() else fetch(model_url, 1_000_000)
        record = json.loads(raw)
        if str(record["id"]) != "6323472":
            raise ValueError("Unexpected Zenodo record")
        if not local.exists():
            local.write_bytes(raw)
        records.append({"file": local.name, "url": model_url, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
        model = {"id": record["id"], "doi": record.get("doi"),
                 "title": record.get("metadata", {}).get("title"),
                 "license": record.get("metadata", {}).get("license"),
                 "files": [{k: f.get(k) for k in ("key", "size", "checksum", "links")} for f in record.get("files", [])]}
    except (urllib.error.URLError, ValueError, KeyError) as exc:
        model = {"error": f"{type(exc).__name__}: {exc}", "url": model_url}
    result = {"plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
              "git_tree_sha": tree["sha"], "sources": records, "model_release": model,
              "weights_downloaded": False, "patient_pixels_read": False}
    (OUT / "index.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"author_files_verified": len(paths), "model_release": model}, indent=2))


if __name__ == "__main__":
    main()
