"""Bounded public full-text retrieval; save responses even if they are not articles."""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "source_cache/spinal_lesion_alternates_2026-10-02"
ROUTES = {
    "pmc_html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC13130011/",
    "pmc_efetch": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=13130011",
    "europepmc_html": "https://europepmc.org/articles/PMC13130011",
}


def get(item, attempt):
    key, url = item
    path = OUT / f"{key}_attempt_{attempt:02d}.response"
    row = {"key": key, "url": url, "file": path.name}
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-literature-audit/1.0"}), timeout=30) as response:
            raw = response.read(4_000_001)
            row.update(status=response.status, final_url=response.url, content_type=response.headers.get("Content-Type"))
        if len(raw) > 4_000_000:
            raise ValueError("Public response exceeds 4 MB bound")
        path.write_bytes(raw)
        row.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        text = raw.decode("utf-8", errors="replace")
        row["article_title_present"] = "MEASURING IMPACT OF SUPER-RESOLUTION" in text.upper()
        row["article_methods_text_present"] = "lesion" in text.lower() and "METHOD" in text.upper() and len(text) > 15000
        row["challenge_or_error_present"] = any(x in text.lower() for x in ("checking your browser", "[error]", "recaptcha", "robot check"))
        try:
            root = ET.fromstring(raw)
            row["xml_root"] = root.tag
            if root.tag in ("article", "pmc-articleset"):
                body = root.find("body") if root.tag == "article" else root.find("article/body")
                if body is not None:
                    chunks = [(x.tag, " ".join(x.itertext())) for x in body.iter() if x.tag in ("title", "p", "table-wrap", "fig")]
                    main = "\n\n".join("[" + tag + "] " + s for tag, s in chunks) + "\n"
                    mainpath = OUT / f"{key}_attempt_{attempt:02d}_maintext.txt"
                    mainpath.write_text(main, encoding="utf-8")
                    row.update(maintext_file=mainpath.name, maintext_characters=len(main), maintext_sha256=hashlib.sha256(mainpath.read_bytes()).hexdigest())
        except ET.ParseError:
            row["xml_root"] = None
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(lambda item: get(item, attempt), ROUTES.items()))
    index = {"attempt": attempt, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
             "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "responses": rows,
             "cohort_contract_changed": False, "fulltext_read": False}
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
