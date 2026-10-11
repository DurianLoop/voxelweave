"""Verify this static increment while the main CPU queue continues independently."""
from __future__ import annotations

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIT = ROOT / "literature"
CACHE = LIT / "source_cache"
MANIFEST = CACHE / "task_throughplane_stage_archive_2026-10-02.json"
CONTRACT = ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json"
EXPECTED_CONTRACT = "061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    errors, files = [], set()
    for name in ("task_throughplane_collision_2026-10-02", "task_throughplane_fulltexts_2026-10-02", "spinal_lesion_alternates_2026-10-02"):
        files.update(p for p in (CACHE / name).rglob("*") if p.is_file())
    for relative in (
        "README.md", "VS_SEG_SELECTION_SENSITIVITY_PREPARATION_2026-10-02.md",
        "SESSION_UPDATE_TASK_THROUGHPLANE_COLLISIONS_2026-10-02.md",
        "SESSION_VISIBLE_DIALOGUE_TASK_THROUGHPLANE_2026-10-02.md",
        "SESSION_IMPORTED_CHECKPOINT_TASK_THROUGHPLANE_2026-10-02.md",
        "SESSION_HANDOFF_TASK_THROUGHPLANE_QUEUE_ACTIVE_2026-10-02.md",
        "literature/2026-10-02_task_throughplane_collision_search_plan.md",
        "literature/2026-10-02_task_throughplane_fulltext_collision_matrix.md",
        "literature/search_task_throughplane_collisions_2026_10_02.py",
        "literature/fetch_task_throughplane_fulltexts_2026_10_02.py",
        "literature/fetch_spinal_lesion_alternates_2026_10_02.py",
        "literature/task_throughplane_reading_evidence_2026_10_02.py",
        "literature/verify_task_throughplane_stage_archive.py",
        "literature/source_cache/task_throughplane_reading_evidence_2026-10-02.json",
        "experiments/vs_seg_selection_sensitivity.py",
        "experiments/verify_vs_seg_selection_sensitivity.py",
        "experiments/vs_seg_selection_sensitivity/development_checks.json",
        "experiments/vs_seg_selection_sensitivity/attempt_01.json",
        "experiments/vs_seg_full_volume_coverage/attempt_01.json",
        "experiments/vs_seg_full_volume_coverage/independent_verification.json",
        "experiments/vs_seg_full_volume_cohort/run_contract.json",
    ):
        files.add(ROOT / relative)
    for p in files:
        if not p.is_file():
            errors.append("Missing stage artifact: " + p.relative_to(ROOT).as_posix())
    search_path = CACHE / "task_throughplane_collision_2026-10-02/attempt_02.json"
    search = read(search_path)
    if search["script_sha256"] != sha(LIT / "search_task_throughplane_collisions_2026_10_02.py") or search["plan_sha256"] != sha(LIT / "2026-10-02_task_throughplane_collision_search_plan.md"):
        errors.append("Search plan or script digest differs")
    returned = 0
    for response in search["responses"]:
        path = search_path.parent / response["raw_file"]
        if sha(path) != response["raw_sha256"] or path.stat().st_size != response["bytes"] or len(response["items"]) != response["returned"]:
            errors.append("Raw search response/hash/count differs")
        returned += response["returned"]
    full_path = CACHE / "task_throughplane_fulltexts_2026-10-02/attempt_01.json"
    full = read(full_path)
    if full["search_index_sha256"] != sha(search_path) or full["script_sha256"] != sha(LIT / "fetch_task_throughplane_fulltexts_2026_10_02.py"):
        errors.append("Original full-text provenance differs")
    for paper in full["papers"]:
        for source in paper["sources"]:
            if "sha256" in source:
                path = full_path.parent / source["file"]
                if sha(path) != source["sha256"] or path.stat().st_size != source["bytes"]:
                    errors.append("Original full-text route response differs")
        if paper["complete_text_obtained"]:
            for field in ("fulltext", "maintext"):
                if sha(full_path.parent / paper[field + "_file"]) != paper[field + "_sha256"]:
                    errors.append("Extracted primary text differs")
    alternate_path = CACHE / "spinal_lesion_alternates_2026-10-02/attempt_01.json"
    alternate = read(alternate_path)
    if alternate["script_sha256"] != sha(LIT / "fetch_spinal_lesion_alternates_2026_10_02.py"):
        errors.append("Spinal alternate retrieval script differs")
    for response in alternate["responses"]:
        if "sha256" in response:
            path = alternate_path.parent / response["file"]
            if sha(path) != response["sha256"] or path.stat().st_size != response["bytes"]:
                errors.append("Spinal public response differs")
        if "maintext_file" in response:
            if sha(alternate_path.parent / response["maintext_file"]) != response["maintext_sha256"]:
                errors.append("Spinal maintext differs")
    ledger = read(CACHE / "task_throughplane_reading_evidence_2026-10-02.json")
    if ledger["script_sha256"] != sha(LIT / "task_throughplane_reading_evidence_2026_10_02.py"):
        errors.append("Reading anchor extraction script differs")
    anchors = 0
    for paper in ledger["papers"]:
        path = ROOT / paper["primary_file"]
        if sha(path) != paper["primary_sha256"]:
            errors.append("Reading primary XML differs")
        tree = ET.parse(path).getroot()
        article = tree if tree.tag == "article" else tree.find("article")
        nodes = list(article.iter("p"))
        for evidence in paper["evidence"]:
            for match in evidence["matching_nodes"]:
                node = nodes[match["paragraph_index_zero_based_over_article_p_nodes"]]
                value = " ".join(" ".join(node.itertext()).split())
                if hashlib.sha256(value.encode()).hexdigest() != match["paragraph_canonical_sha256"] or evidence["short_verbatim_anchor"] not in value:
                    errors.append("Original paragraph anchor differs")
            anchors += 1
    checks = read(ROOT / "experiments/vs_seg_selection_sensitivity/development_checks.json")
    if not checks["complete"] or checks["errors"] or checks["patient_effect_records_read"] or checks["simulated_outcomes_are_scientific_evidence"]:
        errors.append("Secondary development checks did not pass or scope differs")
    if checks["script_sha256"] != sha(ROOT / "experiments/verify_vs_seg_selection_sensitivity.py") or checks["analysis_script_sha256"] != sha(ROOT / "experiments/vs_seg_selection_sensitivity.py"):
        errors.append("Verified secondary implementation changed")
    incomplete = read(ROOT / "experiments/vs_seg_selection_sensitivity/attempt_01.json")
    if incomplete["complete"] or incomplete["gate"]["allowed"] or incomplete["gate"]["patient_effects_read"] or "analysis" in incomplete:
        errors.append("Historical incomplete gate generated patient analysis")
    if incomplete["script_sha256"] != checks["analysis_script_sha256"] or incomplete["plan_sha256"] != sha(ROOT / "VS_SEG_SELECTION_SENSITIVITY_PREPARATION_2026-10-02.md"):
        errors.append("Gate attempt implementation/plan differs")
    if sha(CONTRACT) != EXPECTED_CONTRACT:
        errors.append("Frozen scientific contract changed")
    contract = read(CONTRACT)
    frozen_code_checked = 0
    for item in contract["files"]:
        if Path(item["path"]).suffix in (".py", ".md"):
            path = ROOT.parent / item["path"]
            if sha(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
                errors.append("Frozen code/protocol changed: " + item["path"])
            frozen_code_checked += 1
    entries = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
               for p in sorted(files) if p.is_file()]
    result = {"scope": "Static task/through-plane literature and secondary-analysis preparation increment; active queue logs and growing outputs excluded",
              "primary_papers_read": len(ledger["papers"]), "returned_search_records_not_unique_fulltexts": returned,
              "primary_fact_anchors_verified": anchors, "secondary_development_checks": len(checks["checks"]),
              "fixed_scientific_contract_sha256": EXPECTED_CONTRACT, "frozen_code_and_protocol_files_checked": frozen_code_checked,
              "scientific_publication_goal_achieved": False, "entries": entries}
    if "--write" in sys.argv:
        if not errors:
            MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif not MANIFEST.exists() or read(MANIFEST) != result:
        errors.append("Static increment manifest missing or out of date")
    print(json.dumps({k: result[k] for k in ("primary_papers_read", "returned_search_records_not_unique_fulltexts", "primary_fact_anchors_verified",
          "secondary_development_checks", "frozen_code_and_protocol_files_checked")} | {"files": len(entries), "bytes": sum(x["bytes"] for x in entries), "errors": errors}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
