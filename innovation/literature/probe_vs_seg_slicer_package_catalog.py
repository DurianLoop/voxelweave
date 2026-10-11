"""Archive official matching-runtime metadata and frozen conversion source."""

from __future__ import annotations

import hashlib
import json
import urllib.parse

from probe_vs_seg_original_mask_routes import OUT, fetch


def main() -> None:
    tree = json.loads((OUT / "slicerrt_tree.json").read_text())
    blobs = {x["path"]: x for x in tree["tree"] if x["type"] == "blob"}
    records = []
    paths = ("DicomRtImportExport/ConversionRules/vtkPlanarContourToClosedSurfaceConversionRule.cxx",
             "DicomRtImportExport/ConversionRules/vtkPlanarContourToClosedSurfaceConversionRule.h",
             "DicomRtImportExport/CMakeLists.txt", "BatchProcessing/BatchStructureSetConversion.py")
    for path in paths:
        local = "slicerrt_" + path.rsplit("/", 1)[-1]
        rec = fetch(local, "https://raw.githubusercontent.com/SlicerRt/SlicerRT/" + tree["sha"] + "/" + path, 500_000)
        if "error" not in rec:
            raw = (OUT / local).read_bytes()
            rec["git_blob_verified"] = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == blobs[path]["sha"]
        records.append(rec)
    base = "https://slicer-packages.kitware.com/api/v1"
    records.append(fetch("slicer_win_stable_item.json", base + "/item/6aa1db04ce9de556d30112bb", 200_000))
    records.append(fetch("slicer_win_stable_files.json", base + "/item/6aa1db04ce9de556d30112bb/files", 200_000))
    query = urllib.parse.urlencode({"app_revision": "34645", "os": "win", "arch": "amd64", "extension_name": "SlicerRT"})
    records.append(fetch("slicerrt_win_34645_catalog.json", base + "/app/5f4474d0e1d8c75dfc705482/extension?" + query, 3_000_000))
    records.append(fetch("slicer_extensions_catalog.html", "https://extensions.slicer.org/catalog/All/34645/win", 1_000_000))
    (OUT / "catalog_index.json").write_text(json.dumps({"source_tree_sha": tree["sha"], "sources": records}, indent=2) + "\n", encoding="utf-8")
    summaries = []
    for name in ("slicer_win_stable_item.json", "slicer_win_stable_files.json", "slicerrt_win_34645_catalog.json"):
        path = OUT / name
        if path.exists():
            data = json.loads(path.read_text())
            items = data if isinstance(data, list) else [data]
            summaries.append({"file": name, "count": len(items),
                              "items": [{k: r.get(k) for k in ("_id", "name", "size", "sha512", "meta")} for r in items[:3]]})
    print(json.dumps({"fetches": records, "metadata": summaries}, indent=2))


if __name__ == "__main__":
    main()
