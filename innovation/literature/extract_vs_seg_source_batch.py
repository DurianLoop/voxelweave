"""Re-extract five archived XML full texts for source and endpoint review."""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_cache/vs_seg_source_batch_recheck_2026-10-02"
PATHS = {
    "vs_seg": "source_cache/vs_seg_public_sources_2026-10-01/vs_seg_paper.xml",
    "crossmoda": "source_cache/crossmoda_descriptor_2026-10-01/article.xml",
    "gazi_brains": "source_cache/thin3d_glioma_candidate_fulltexts_2026-10-01/gazi_brains_2020.xml",
    "posttreatment": "source_cache/thin3d_glioma_candidate_fulltexts_2026-10-01/posttreatment_t2_lesion.xml",
    "glioma_7t": "source_cache/thin3d_glioma_candidate_fulltexts_2026-10-01/glioma_7t_t2.xml",
}


def flatten(node):
    return " ".join("".join(node.itertext()).split())


def main() -> None:
    OUT.mkdir(exist_ok=True)
    index = []
    for name, relative in PATHS.items():
        source = ROOT / relative
        raw = source.read_bytes()
        article = ET.fromstring(raw)
        title = flatten(article.find(".//article-meta/title-group/article-title"))
        doi_node = article.find(".//article-meta/article-id[@pub-id-type='doi']")
        doi = flatten(doi_node) if doi_node is not None else None
        body = article.find("body")
        if body is None:
            raise ValueError("XML has no full-text body")
        sections = [flatten(node) for node in body.iter() if node.tag in ("title", "p", "table")]
        for extra in (article.find("front/article-meta/abstract"), article.find("back")):
            if extra is not None:
                sections.extend(flatten(node) for node in extra.iter() if node.tag in ("title", "p", "table"))
        text = title + "\nDOI: " + str(doi) + "\n\n" + "\n\n".join(sections) + "\n"
        target = OUT / f"{name}.txt"
        target.write_text(text, encoding="utf-8")
        index.append({"name": name, "title": title, "doi": doi, "source": relative,
                      "source_sha256": hashlib.sha256(raw).hexdigest(),
                      "extracted_file": target.name, "extracted_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                      "fulltext_recheck_not_newly_discovered_paper": True})
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{k: r[k] for k in ("name", "title", "doi")} for r in index], indent=2))


if __name__ == "__main__":
    main()
