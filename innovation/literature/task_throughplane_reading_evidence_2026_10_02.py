"""Attach short method excerpts to primary XML nodes; validate them mechanically."""
from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
THROUGH = ROOT / "source_cache/task_throughplane_fulltexts_2026-10-02"
SPINAL = ROOT / "source_cache/spinal_lesion_alternates_2026-10-02"
OUT = ROOT / "source_cache/task_throughplane_reading_evidence_2026-10-02.json"
SPECS = [
    ("ciss_vs_2026", THROUGH / "ciss_vs_2026_jats.xml", [
        ("same_raw_data", "All reconstruction methods were obtained from the same raw data."),
        ("inplane_only", "SR-DLR reconstruction improves only the in-plane spatial resolution and not the through-plane resolution"),
        ("no_detection_validation", "we did not evaluate detection performance")]),
    ("brain_tumor_slice_2022", THROUGH / "brain_tumor_slice_2022_jats.xml", [
        ("bicubic_simulation", "downsampled by a scaling factor of four"),
        ("segmentation_retraining", "the UNet trained with the super"),
        ("throughplane_separate_experiment", "The smaller the distance between the slices")]),
    ("fetal_srr_bias_2025", THROUGH / "fetal_srr_bias_2025_jats.xml", [
        ("conditional_quality_selection", "If no combination resulted in a sufficiently high-quality reconstruction"),
        ("automated_volumetry", "Automated volumetric evaluation was carried out"),
        ("private_data", "The data used in this study is not open access")]),
    ("spinal_lesion_2025", SPINAL / "pmc_efetch_attempt_01.response", [
        ("fixed_lesion_tool", "Lesion segmentation was obtained for each scan using sct_deepseg_lesion."),
        ("preprocessing_exclusion", "Any scans with extensive motion artifacts"),
        ("clinical_association", "Across all types")]),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_text(node):
    return " ".join(" ".join(node.itertext()).split())


def main():
    rows = []
    for key, path, specs in SPECS:
        root = ET.parse(path).getroot()
        article = root if root.tag == "article" else root.find("article")
        title = canonical_text(article.find("front/article-meta/title-group/article-title"))
        paragraphs = list(article.iter("p"))
        evidence = []
        for claim, needle in specs:
            matches = []
            for index, node in enumerate(paragraphs):
                value = canonical_text(node)
                if needle in value:
                    matches.append({"paragraph_index_zero_based_over_article_p_nodes": index,
                                    "paragraph_canonical_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest()})
            if not matches:
                raise ValueError(key + ": primary paragraph anchor not found: " + needle)
            evidence.append({"contract_fact": claim, "short_verbatim_anchor": needle, "matching_nodes": matches})
        rows.append({"key": key, "title_from_primary_xml": title, "primary_file": path.relative_to(ROOT.parent).as_posix(),
                     "primary_sha256": sha(path), "paragraphs": len(paragraphs),
                     "table_ids": [node.get("id") for node in article.iter("table-wrap")],
                     "figure_ids": [node.get("id") for node in article.iter("fig")],
                     "reading_scope": "Body, methods/results/discussion, table text and figure captions; figures not visually inspected; supplementary files not read",
                     "evidence": evidence})
    result = {"script_sha256": sha(Path(__file__)), "papers": rows, "all_primary_anchors_verified": True,
              "source_download_is_not_replication": True, "scientific_publication_claim_confirmed": False}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"papers": len(rows), "primary_fact_anchors": sum(len(r["evidence"]) for r in rows), "errors": []}))


if __name__ == "__main__":
    main()
