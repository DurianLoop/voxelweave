"""Static oracle/operator increment; do not snapshot the live primary queue."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "literature/source_cache"
ORACLE = ROOT / "experiments/vs_seg_001_local_action_oracle"
MANIFEST = CACHE / "local_action_and_operator_stage_archive_2026-10-02.json"
MASTER = ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json"
EXPECTED_MASTER = "061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    errors, files = [], set()
    for name in ("operator_multicontrast_candidates_2026-10-02", "public_operator_candidate_bodies_2026-10-02"):
        files.update(p for p in (CACHE / name).rglob("*") if p.is_file())
    files.update(p for p in ORACLE.glob("*") if p.is_file())
    for pattern in ("VS_SEG_001_LOCAL_ACTION_ORACLE*", "plot_vs_seg_001_local_action_oracle*.py"):
        files.update((ROOT / "figures").glob(pattern))
    for relative in (
        "README.md", "GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md",
        "VS_SEG_001_LOCAL_ACTION_ORACLE_PLAN_2026-10-02.md", "VS_SEG_001_LOCAL_ACTION_ORACLE_RESULT_2026-10-02.md",
        "SESSION_UPDATE_LOCAL_ACTION_AND_OPERATOR_2026-10-02.md",
        "SESSION_VISIBLE_DIALOGUE_LOCAL_ACTION_AND_OPERATOR_2026-10-02.md",
        "SESSION_HANDOFF_LOCAL_ACTION_QUEUE_ACTIVE_2026-10-02.md",
        "literature/2026-10-02_operator_multicontrast_abstract_access_result.md",
        "literature/fetch_operator_multicontrast_candidates_2026_10_02.py",
        "literature/fetch_public_operator_candidate_bodies_2026_10_02.py",
        "literature/verify_local_action_and_operator_archive.py",
        "experiments/vs_seg_001_local_action_oracle.py",
        "experiments/verify_vs_seg_001_local_action_oracle.py",
        "experiments/vs_seg_001_action_energy_diagnostic.py",
        "experiments/verify_vs_seg_001_action_energy.py",
    ):
        files.add(ROOT / relative)
    for path in files:
        if not path.is_file():
            errors.append("Missing static stage artifact: " + str(path))
    metadata_path = CACHE / "operator_multicontrast_candidates_2026-10-02/attempt_01.json"
    metadata = read(metadata_path)
    if metadata["script_sha256"] != sha(ROOT / "literature/fetch_operator_multicontrast_candidates_2026_10_02.py"):
        errors.append("Metadata fetch script differs")
    verified_responses = 0
    for row in metadata["responses"]:
        if "sha256" in row:
            path = metadata_path.parent / row["file"]
            if sha(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
                errors.append("Exact DOI raw response changed")
            for record in row["records"]:
                identity = (record.get("doi") or "").lower().replace("https://doi.org/", "")
                if identity != row["doi"].lower():
                    errors.append("Returned DOI identity differs")
            verified_responses += 1
    bodies_path = CACHE / "public_operator_candidate_bodies_2026-10-02/attempt_01.json"
    bodies = read(bodies_path)
    if bodies["script_sha256"] != sha(ROOT / "literature/fetch_public_operator_candidate_bodies_2026_10_02.py"):
        errors.append("Public-body attempt script differs")
    potential_bodies = 0
    for paper in bodies["papers"]:
        potential_bodies += len(paper["potential_bodies"])
        if paper["fulltext_read"]:
            errors.append("Abstract-only attempt misstates reading depth")
        for route in paper["routes"]:
            if "sha256" in route:
                path = bodies_path.parent / route["file"]
                if sha(path) != route["sha256"] or path.stat().st_size != route["bytes"]:
                    errors.append("Public-body response changed")
    if potential_bodies:
        errors.append("Expected zero newly obtained article bodies for this snapshot")
    result_path, contract_path = ORACLE / "attempt_01.json", ORACLE / "run_contract_attempt_01.json"
    result, contract = read(result_path), read(contract_path)
    if not result["complete"] or result["independent_confirmation"] or result["run_contract_sha256"] != sha(contract_path):
        errors.append("Development result scope/contract differs")
    for item in contract["files"]:
        path = ROOT / item["path"]
        files.add(path)
        if path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
            errors.append("Development frozen source changed: " + item["path"])
    proof = read(ORACLE / "independent_verification.json")
    if not proof["complete"] or proof["errors"] or proof["result_sha256"] != sha(result_path) or proof["run_contract_sha256"] != sha(contract_path):
        errors.append("Independent oracle proof no longer matches")
    if proof["script_sha256"] != sha(ROOT / "experiments/verify_vs_seg_001_local_action_oracle.py"):
        errors.append("Independent oracle verifier code changed")
    diagnostic_path = ORACLE / "observable_energy_diagnostic.json"
    diagnostic = read(diagnostic_path)
    if diagnostic["script_sha256"] != sha(ROOT / "experiments/vs_seg_001_action_energy_diagnostic.py") or diagnostic["oracle_result_sha256"] != sha(result_path) or diagnostic["oracle_proof_sha256"] != sha(ORACLE / "independent_verification.json"):
        errors.append("Action energy lineage changed")
    energy_proof = read(ORACLE / "observable_energy_independent_rank_verification_v2.json")
    if not energy_proof["complete"] or energy_proof["errors"] or energy_proof["script_sha256"] != sha(ROOT / "experiments/verify_vs_seg_001_action_energy.py") or energy_proof["diagnostic_sha256"] != sha(diagnostic_path):
        errors.append("Rank AUC proof/code changed")
    if sha(ROOT / result["tile_stats_file"]) != result["tile_stats_sha256"] or energy_proof["tile_stats_sha256"] != result["tile_stats_sha256"]:
        errors.append("Complete tile table hash changed")
    fig_path = ROOT / "figures/VS_SEG_001_LOCAL_ACTION_ORACLE_FIGURE_2026-10-02.json"
    fig = read(fig_path)
    if fig["script_sha256"] != sha(ROOT / "figures/plot_vs_seg_001_local_action_oracle.py") or fig["source_sha256"] != sha(result_path):
        errors.append("Latest figure source or code changed")
    for item in fig["files"]:
        if sha(ROOT / item["path"]) != item["sha256"]:
            errors.append("Latest plotted figure changed")
    if sha(MASTER) != EXPECTED_MASTER:
        errors.append("Primary cohort contract changed")
    frozen_code_checked = 0
    for item in read(MASTER)["files"]:
        if Path(item["path"]).suffix in (".py", ".md"):
            path = ROOT.parent / item["path"]
            if path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
                errors.append("Primary frozen code or protocol changed: " + item["path"])
            frozen_code_checked += 1
    entries = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
               for p in sorted(files) if p.is_file()]
    snapshot = {"scope": "Static one-seen-patient oracle, observable diagnostic, figures and exact-DOI abstract/access increment; active queue logs excluded",
                "exact_doi_metadata_responses_verified": verified_responses, "new_article_bodies_obtained": potential_bodies,
                "oracle_tiles_independently_checked": proof["checked_tiles"], "oracle_strategy_endpoints_independently_checked": proof["checked_strategy_endpoints"],
                "auc_entries_independently_checked": len(energy_proof["checked"]), "primary_frozen_code_and_protocol_files_checked": frozen_code_checked,
                "primary_contract_sha256": EXPECTED_MASTER, "scientific_independent_patients": 0,
                "scientific_publication_goal_achieved": False, "entries": entries}
    if "--write" in sys.argv:
        if not errors:
            MANIFEST.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    elif not MANIFEST.is_file() or read(MANIFEST) != snapshot:
        errors.append("Static oracle/operator manifest missing or out of date")
    print(json.dumps({k: v for k, v in snapshot.items() if k not in ("entries", "scope")} |
                     {"files": len(entries), "bytes": sum(row["bytes"] for row in entries), "errors": errors}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
