"""Resolve the author's two earlier method papers without guessing identifiers."""
from __future__ import annotations

import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from probe_vs_seg_original_mask_routes import OUT, fetch


def main():
    titles = {
        "wang2019": "Automatic Segmentation of Vestibular Schwannoma from T2-Weighted MRI by Deep Spatial Attention with Hardness-Weighted Loss",
        "shapey2020": "An artificial intelligence framework for automatic segmentation and volumetry of vestibular schwannomas from contrast-enhanced T1-weighted and high-resolution T2-weighted MRI",
    }
    routes = [(name + "_crossref.json", "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.title": title, "rows": 2})) for name, title in titles.items()]
    routes.append(("shapey_method_europepmc.json", "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": 'TITLE:"artificial intelligence framework" AND TITLE:"vestibular"', "format": "json", "resultType": "core"})))
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(lambda row: fetch(row[0], row[1], 2_000_000), routes))
    (OUT / "method_paper_metadata_index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    for row in records:
        print(json.dumps(row))
        if "error" not in row:
            data = json.loads((OUT / row["file"]).read_text())
            items = data.get("message", {}).get("items", []) or data.get("resultList", {}).get("result", [])
            print(json.dumps([{key: x.get(key) for key in ("title", "DOI", "doi", "id", "pmcid", "URL", "link", "fullTextUrlList")} for x in items], indent=2))


if __name__ == "__main__":
    main()
