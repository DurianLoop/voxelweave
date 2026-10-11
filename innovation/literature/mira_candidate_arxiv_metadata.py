"""Resolve selected MRI uncertainty papers against exact-title arXiv searches."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_snapshots/mira_four_seed_citations_2026-10-01/arxiv_candidates"
TITLES = {
    "mind_detail": "Mind the Detail Uncovering Clinically Relevant Image Details in Accelerated MRI",
    "structural_uncertainty": "Evaluating Structural Uncertainty in Accelerated MRI Are Voxelwise Measures Useful Surrogates",
    "unified_uncertainty": "A unified approach for maintaining MRI reconstruction quality and quantifying both aleatoric and epistemic uncertainty",
    "segmentation_guided": "Segmentation Guided MRI Reconstruction for Meaningfully Diverse Reconstructions",
}
NS = {"atom": "http://www.w3.org/2005/Atom"}


def field(entry: ET.Element, name: str) -> str:
    node = entry.find(f"atom:{name}", NS)
    return " ".join("".join(node.itertext()).split()) if node is not None else ""


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records, raw_files = [], {}
    for name, title in TITLES.items():
        params = urllib.parse.urlencode({"search_query": f'ti:"{title}"', "start": 0,
                                         "max_results": 10})
        url = "https://export.arxiv.org/api/query?" + params
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"})
        try:
            with opener.open(request, timeout=40) as response:
                raw = response.read()
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
            root = ET.fromstring(raw)
            entries = [{key: field(entry, key) for key in ("id", "title", "published", "summary")}
                       for entry in root.findall("atom:entry", NS)]
            raw_files[name + ".xml"] = raw
            records.append({"name": name, "query_title": title, "url": url,
                            "sha256": hashlib.sha256(raw).hexdigest(), "entries": entries})
        except Exception as error:
            records.append({"name": name, "query_title": title, "url": url,
                            "error": f"{type(error).__name__}: {error}"})
    OUT.mkdir(parents=True)
    for name, raw in raw_files.items():
        (OUT / name).write_bytes(raw)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{row["name"]: [entry["id"] for entry in row.get("entries", [])],
                       "error": row.get("error")} for row in records], indent=2))


if __name__ == "__main__":
    main()
