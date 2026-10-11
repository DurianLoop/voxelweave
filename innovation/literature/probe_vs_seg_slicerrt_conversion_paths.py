"""Archive all competing official planar-contour conversion routes."""
from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

from probe_vs_seg_original_mask_routes import OUT, fetch


def main():
    tree = json.loads((OUT / "slicerrt_tree.json").read_text())
    blobs = {row["path"]: row for row in tree["tree"] if row["type"] == "blob"}
    paths = [p for p in blobs if p.startswith("DicomRtImportExport/ConversionRules/") and (p.endswith(".cxx") or p.endswith("CMakeLists.txt"))]
    def retrieve(path):
        name = "slicerrt_rules_" + path.rsplit("/", 1)[-1]
        rec = fetch(name, "https://raw.githubusercontent.com/SlicerRt/SlicerRT/" + tree["sha"] + "/" + path, 500_000)
        rec.update({"source_path": path, "git_blob_sha": blobs[path]["sha"]})
        if "error" not in rec:
            raw = (OUT / name).read_bytes()
            rec["git_blob_verified"] = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == blobs[path]["sha"]
        return rec
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(retrieve, paths))
    (OUT / "conversion_paths_index.json").write_text(json.dumps({"git_tree": tree["sha"], "sources": results}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
