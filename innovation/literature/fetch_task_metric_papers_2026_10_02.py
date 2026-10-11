"""Bounded primary-source retrieval for three metric-validation method papers."""
from __future__ import annotations
import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/task_metric_papers_2026-10-02"
PAPERS = {
    "pitfalls": "Understanding metric-related pitfalls in image analysis validation",
    "reloaded": "Metrics Reloaded: recommendations for image analysis validation",
    "taha": "Metrics for evaluating 3D medical image segmentation: analysis, selection, and tool",
}


def fetch(name, url, cap=8_000_000):
    path = OUT / name
    rec = {"file": name, "url": url}
    try:
        if path.exists():
            raw = path.read_bytes()
            rec["cache_reused"] = True
        else:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"}), timeout=30) as response:
                raw = response.read(cap + 1)
                rec.update({"status": response.status, "final_url": response.url,
                            "content_type": response.headers.get("Content-Type")})
            if len(raw) > cap:
                raise ValueError("Response exceeds bounded size")
            path.write_bytes(raw)
        rec.update({"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    except Exception as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
    return rec


def retrieve(item):
    name, title = item
    query = urllib.parse.urlencode({"query": 'TITLE:"' + title.split(":")[0] + '"', "format": "json", "resultType": "core", "pageSize": 5})
    meta = fetch(name + "_search.json", "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + query)
    out = {"key": name, "query_title": title, "sources": [meta], "fulltext_extracted": False}
    if "error" in meta:
        return out
    items = json.loads((OUT / meta["file"]).read_text())["resultList"]["result"]
    out["candidates"] = [{k: v.get(k) for k in ("title", "doi", "pmcid", "authorString", "pubYear")} for v in items]
    match = next((v for v in items if v.get("pmcid") and v.get("title", "").lower().rstrip(".") == title.lower()), None)
    if not match:
        out["error"] = "No exact-title primary article with PMC identifier"
        return out
    out["selected"] = {k: match.get(k) for k in ("title", "doi", "pmcid", "authorString", "pubYear")}
    pmcid = match["pmcid"]
    xml = fetch(name + "_fulltext.xml", "https://www.ebi.ac.uk/europepmc/webservices/rest/" + pmcid + "/fullTextXML")
    out["sources"].append(xml)
    if "error" in xml:
        xml = fetch(name + "_bioc.xml", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/" + pmcid + "/unicode")
        out["sources"].append(xml)
    if "error" not in xml:
        tree = ET.parse(OUT / xml["file"])
        if tree.getroot().tag == "article":
            parts = [" ".join(x.itertext()) for x in tree.iter() if x.tag in ("title", "p", "table-wrap", "fig")]
        else:
            parts = [" ".join(x.itertext()) for x in tree.iter("text")]
        text = "\n\n".join(parts) + "\n"
        p = OUT / (name + "_fulltext.txt")
        p.write_text(text, encoding="utf-8")
        out.update({"fulltext_extracted": True, "extracted_file": p.name, "extracted_characters": len(text),
                    "extracted_sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(retrieve, PAPERS.items()))
    result = {"attempt": attempt, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "papers": rows}
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
