"""Inspect bounded official converted-label and SlicerRT/runtime source routes."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "literature/source_cache/vs_seg_original_mask_routes_2026-10-02"
PLAN = ROOT / "VS_SEG_ORIGINAL_MASK_CONVERSION_SOURCE_PLAN_2026-10-02.md"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current = None
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.current = {"href": href, "text": ""}
    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data
    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.current["text"] = " ".join(self.current["text"].split())
            self.rows.append(self.current)
            self.current = None


def fetch(name: str, url: str, cap: int) -> dict:
    path = OUT / name
    rec = {"file": name, "url": url}
    try:
        raw = path.read_bytes() if path.exists() else None
        if raw is None:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
            with opener.open(request, timeout=35) as response:
                raw = response.read(cap + 1)
                rec["final_url"] = response.url
                rec["content_type"] = response.headers.get("Content-Type")
            if len(raw) > cap:
                raise ValueError("Official source response exceeds cap")
            path.write_bytes(raw)
        rec.update({"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    except (urllib.error.URLError, ValueError) as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
    return rec


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tcia = ROOT / "literature/source_cache/vs_seg_public_sources_2026-10-01/vs_seg_tcia.html"
    parser = Links()
    parser.feed(tcia.read_text(encoding="utf-8"))
    links = [x for x in parser.rows if re.search(r"nifti|nii|contour|download|zip|mask|segment", x["text"] + " " + x["href"], re.I)]
    tree = json.loads((ROOT / "literature/source_cache/vs_seg_author_code_2026-10-01/tree.json").read_text())
    author_voxels = [x["path"] for x in tree["tree"] if re.search(r"\.nii(\.gz)?$|\.nrrd$|\.mha$", x["path"], re.I)]
    sources = [fetch("slicer_download.html", "https://download.slicer.org/", 1_000_000),
               fetch("slicerrt_repository.json", "https://api.github.com/repos/SlicerRt/SlicerRT", 200_000),
               fetch("slicer_windows_release.json", "https://slicer-packages.kitware.com/api/v1/app/5f4474d0e1d8c75dfc705482/release?os=win&arch=amd64", 1_000_000)]
    repo = OUT / "slicerrt_repository.json"
    if repo.exists():
        branch = json.loads(repo.read_text())["default_branch"]
        sources.append(fetch("slicerrt_tree.json", "https://api.github.com/repos/SlicerRt/SlicerRT/git/trees/" + branch + "?recursive=1", 3_000_000))
    rt_tree = OUT / "slicerrt_tree.json"
    conversion_paths = []
    if rt_tree.exists():
        data = json.loads(rt_tree.read_text())
        conversion_paths = [x["path"] for x in data["tree"] if re.search(r"PlanarContour|ConversionRule|BatchStructure|s4ext$", x["path"])]
    result = {"plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
              "tcia_page_sha256": hashlib.sha256(tcia.read_bytes()).hexdigest(),
              "official_tcia_relevant_links": links, "fixed_author_voxel_files": author_voxels,
              "sources": sources, "slicerrt_conversion_paths": conversion_paths,
              "packages_downloaded": False, "patient_pixels_read": False}
    (OUT / "index.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tcia_links": links, "author_voxel_files": author_voxels,
                      "sources": sources, "conversion_paths": conversion_paths}, indent=2))


if __name__ == "__main__":
    main()
