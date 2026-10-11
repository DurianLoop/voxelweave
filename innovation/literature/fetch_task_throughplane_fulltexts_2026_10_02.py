"""Fetch selected primary PMC bodies, preserving metadata and every failed route."""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEARCH = ROOT / "source_cache/task_throughplane_collision_2026-10-02/attempt_02.json"
OUT = ROOT / "source_cache/task_throughplane_fulltexts_2026-10-02"
SELECT = {"ciss_vs_2026": "PMC13546317", "spinal_lesion_2025": "PMC13130011", "brain_tumor_slice_2022": "PMC9680577", "fetal_srr_bias_2025": "PMC12513972"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(name, url):
    path = OUT / name
    row = {"file": name, "url": url}
    try:
        if not path.exists():
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"}), timeout=30) as response:
                raw = response.read(8_000_001)
                row.update({"status": response.status, "final_url": response.url, "content_type": response.headers.get("Content-Type")})
            if len(raw) > 8_000_000:
                raise ValueError("Primary text exceeds bounded response size")
            path.write_bytes(raw)
        row.update({"sha256": sha(path), "bytes": path.stat().st_size})
        xml_root = ET.parse(path).getroot()
        if xml_root.tag not in ("article", "collection"):
            raise ValueError("Response is not a primary article/BioC collection")
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


def retrieve(item, lookup):
    name, pmcid = item
    metadata = lookup[pmcid]
    xml = fetch(name + "_jats.xml", "https://www.ebi.ac.uk/europepmc/webservices/rest/" + pmcid + "/fullTextXML")
    record = {"key": name, "pmcid": pmcid, "metadata": metadata, "sources": [xml], "complete_text_obtained": False}
    if "error" in xml:
        xml = fetch(name + "_bioc.xml", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/" + pmcid + "/unicode")
        record["sources"].append(xml)
    if "error" not in xml:
        root = ET.parse(OUT / xml["file"]).getroot()
        if root.tag == "article":
            chunks = [(x.tag, " ".join(x.itertext())) for x in root.iter() if x.tag in ("article-title", "abstract", "title", "p", "table-wrap", "fig")]
            # Main body, once, with section titles and complete table/figure text.
            body = root.find("body")
            main_parts = [(x.tag, " ".join(x.itertext())) for x in body.iter() if x.tag in ("title", "p", "table-wrap", "fig")] if body is not None else chunks
        else:
            chunks, main_parts = [], []
            for passage in root.iter("passage"):
                tags = {x.get("key"): x.text for x in passage.findall("infon")}
                value = passage.findtext("text")
                if value:
                    section = tags.get("section_type") or tags.get("type") or "unknown"
                    chunks.append((section, value))
                    if section.upper() not in ("REF", "REF_LIST", "REFERENCES") and "reference" not in section.lower():
                        main_parts.append((section, value))
        text = "\n\n".join(s for _, s in chunks) + "\n"
        main = "\n\n".join("[" + tag + "] " + s for tag, s in main_parts) + "\n"
        full_file, main_file = OUT / (name + "_fulltext.txt"), OUT / (name + "_maintext.txt")
        full_file.write_text(text, encoding="utf-8")
        main_file.write_text(main, encoding="utf-8")
        record.update({"complete_text_obtained": True, "fulltext_file": full_file.name, "fulltext_sha256": sha(full_file),
                       "maintext_file": main_file.name, "maintext_sha256": sha(main_file), "maintext_characters": len(main)})
    return record


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    search = json.loads(SEARCH.read_text(encoding="utf-8"))
    lookup = {x["pmcid"]: x for response in search["responses"] for x in response.get("items", []) if x.get("pmcid")}
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda item: retrieve(item, lookup), SELECT.items()))
    result = {"attempt": attempt, "search_index_sha256": sha(SEARCH), "script_sha256": sha(Path(__file__)),
              "cohort_protocol_or_code_changed": False, "papers": rows}
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps({k: row.get(k) for k in ("key", "pmcid", "complete_text_obtained", "maintext_characters", "sources")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
