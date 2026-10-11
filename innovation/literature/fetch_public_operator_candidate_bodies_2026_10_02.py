"""Bounded anonymous publisher/arXiv routes; distinguish body from metadata or error."""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/public_operator_candidate_bodies_2026-10-02"
ITEMS = {
    "multi_contrast_tmi": ("10.1109/tmi.2025.3628113", "Multi-Contrast MRI Super-Resolution in Brain Tumors"),
    "knee_isotropic": ("10.1016/j.compmedimag.2026.102786", "Self-supervised isotropic reconstruction for abnormality detection"),
    "target_driven": ("10.1016/j.mri.2026.110675", "Target-driven acquisition and super-resolution reconstruction"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get(key, route, url, attempt):
    path = OUT / f"{key}_{route}_attempt_{attempt:02d}.response"
    row = {"key": key, "route": route, "url": url, "file": path.name}
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"}), timeout=25) as response:
            raw = response.read(5_000_001)
            row.update(status=response.status, content_type=response.headers.get("Content-Type"), final_url=response.url)
        if len(raw) > 5_000_000:
            raise ValueError("Response exceeds bound")
        path.write_bytes(raw)
        row.update(bytes=len(raw), sha256=sha(path))
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


def retrieve(item, attempt):
    key, (doi, phrase) = item
    routes = []
    crossref = get(key, "crossref", "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"), attempt)
    routes.append(crossref)
    if "error" not in crossref:
        message = json.loads((OUT / crossref["file"]).read_bytes())["message"]
        links = [x["URL"] for x in message.get("link", []) if x.get("content-type") == "text/xml"]
        primary = message.get("resource", {}).get("primary", {}).get("URL")
        if links:
            routes.append(get(key, "publisher_xml", links[0], attempt))
        elif primary:
            routes.append(get(key, "publisher_primary", primary, attempt))
    arxiv_url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": 'ti:"' + phrase + '"', "start": 0, "max_results": 5})
    routes.append(get(key, "arxiv_title_query", arxiv_url, attempt))
    entries, bodies = [], []
    for route in routes:
        if "error" in route or route["route"] == "crossref":
            continue
        path = OUT / route["file"]
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            route["parsed_xml"] = False
            continue
        route["parsed_xml"] = True
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("a:entry", ns):
            entries.append({"title": entry.findtext("a:title", namespaces=ns), "id": entry.findtext("a:id", namespaces=ns),
                            "summary": entry.findtext("a:summary", namespaces=ns)})
        body_nodes = [n for n in root.iter() if n.tag.rsplit("}", 1)[-1] == "body"]
        for index, node in enumerate(body_nodes):
            main = " ".join(node.itertext())
            if len(main) < 10000:
                continue
            main_path = OUT / f"{key}_{route['route']}_attempt_{attempt:02d}_body_{index}.txt"
            main_path.write_text(main, encoding="utf-8")
            bodies.append({"file": main_path.name, "sha256": sha(main_path), "characters": len(main), "source_response": route["file"],
                           "primary_identity_and_completeness_need_manual_check": True})
    return {"key": key, "doi": doi, "routes": routes, "arxiv_title_candidates": entries, "potential_bodies": bodies, "fulltext_read": False}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(lambda item: retrieve(item, attempt), ITEMS.items()))
    result = {"attempt": attempt, "created_utc": datetime.now(timezone.utc).isoformat(), "script_sha256": sha(Path(__file__)),
              "papers": rows, "anonymous_public_routes_only": True}
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
