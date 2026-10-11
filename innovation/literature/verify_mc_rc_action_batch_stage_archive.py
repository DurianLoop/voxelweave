"""Static integrity and conclusion checks for eight sources and three developer oracles."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "literature/source_cache/mc_rc_004_006_native_headers_2026-10-02"
G = ROOT / "experiments/mc_rc_004_006_native_label_gate"
A = ROOT / "experiments/mc_rc_three_development_action_oracle"
MANIFEST = ROOT / "literature/mc_rc_action_batch_stage_archive_manifest_2026-10-02.json"
EXPECTED = "061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1_048_576), b""):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    errors, files = [], {Path(__file__), ROOT / "README.md"}
    def require(condition, message):
        if not condition:
            errors.append(message)
    def match(path, expected, message, project_input=False):
        path = Path(path).resolve()
        allowed = ROOT.parent if project_input else ROOT
        require(path.is_relative_to(allowed) and path.is_file(), "Missing/outside authorized input: " + message)
        if path.is_file() and path.is_relative_to(allowed):
            require(sha(path) == expected, "Hash differs: " + message)
            if path.is_relative_to(ROOT):
                files.add(path)
    ledger, first, followup, source_proof = read(B / "attempt_01.json"), read(G / "attempt_01.json"), read(G / "resource_followup_attempt_01.json"), read(G / "independent_raw_geometry_grid_verification.json")
    match(ROOT / "literature/download_mc_rc_004_006_native_headers_2026_10_02.py", ledger["script_sha256"], "download code")
    match(ROOT / "MC_RC_004_006_NATIVE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md", ledger["plan_sha256"], "source plan")
    match(ROOT / "experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json", ledger["selection_sha256"], "historical frozen preparation")
    match(ROOT / "literature/download_mc_rc_three_patient_headers_2026_10_02.py", ledger["header_helper_sha256"], "unchanged first-batch header helper")
    match(ROOT / "experiments/mc_rc_native_header_geometry_v2.py", ledger["geometry_v2_sha256"], "prespecified geometry v2")
    match(ROOT / "experiments/vs_seg_task_cpu_support.py", ledger["resource_gate_sha256"], "resource gate")
    require(ledger["complete"] and len(ledger["series"]) == 8 and ledger["header_qualified_series"] == 6 and ledger["max_connections"] == 1 and ledger["total_cap_bytes"] == 500_000_000, "Fixed source scope/caps differ")
    require(not ledger["MR_pixel_array_decoded"] and not ledger["label_arrays_decoded"] and not ledger["patient_performance_statistics_computed"], "Header-only stage scope differs")
    objects, byte_total = 0, 0
    for row in ledger["series"]:
        t, s = row["transfer"], row["source"]
        require(t["complete"] and t["http_status"] == 200 and row["headers_complete"], "Source request incomplete " + s["SeriesInstanceUID"])
        match(ROOT / t["file"], t["sha256"], "raw MR ZIP")
        match(B / row["header_file"], row["header_sha256"], "header extraction")
        require((ROOT / t["file"]).stat().st_size == t["bytes"] and t["bytes"] <= t["cap_bytes"], "Transfer byte scope differs")
        header = read(B / row["header_file"])
        require(header["summary"] == row["summary"] and not header["MR_pixel_array_decoded"] and len(header["records"]) == s["ImageCount"], "Saved header record scope differs")
        objects += len(header["records"])
        byte_total += t["bytes"]
    require(objects == 701 and byte_total == ledger["total_transfer_bytes"] == 133_512_951, "Eight-source actual counts/bytes differ")
    match(ROOT / "experiments/audit_mc_rc_004_006_label_grid.py", first["script_sha256"], "original label code")
    match(ROOT / "MC_RC_004_006_NATIVE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md", first["plan_sha256"], "original label plan")
    match(ROOT / "experiments/audit_mc_rc_three_patient_label_grid.py", first["grid_helper_sha256"], "unchanged grid helper")
    match(B / "attempt_01.json", first["source_header_attempt_sha256"], "label source ledger")
    match(ROOT / "experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json", first["selection_sha256"], "label fixed roster")
    prior = read(ROOT / "literature/source_cache/mc_rc_three_patient_headers_2026-10-02/attempt_01.json")
    match(ROOT / prior["labels"]["transfer"]["file"], first["official_label_zip_sha256"], "authenticated label ZIP")
    match(ROOT / "literature/source_cache/mc_rc_three_patient_headers_2026-10-02/official_label_metadata_00_attempt_01.csv", first["source_csv_sha256"], "authenticated CSV")
    match(ROOT / "experiments/mc_rc_native_t2_label_gate/official_pathnames_artifact_read.json", first["artifact_read_sha256"], "prior read-only all-cell CSV proof")
    require(not first["complete"] and len(first["series"]) == 8 and sum(r["label_inspection_complete"] for r in first["series"]) == 3, "Original resource failure was not retained")
    require(all("budget exceeded before decoding" in r["error"] for r in first["series"] if not r["label_inspection_complete"]), "Original label failure categories differ")
    for row in first["series"]:
        match(ROOT / row["label_file"], row["label_sha256"], "all eight extracted labels")
    match(ROOT / "experiments/complete_mc_rc_004_006_label_resource_followup.py", followup["script_sha256"], "resource follow-up code")
    match(ROOT / "MC_RC_004_006_LABEL_RESOURCE_FOLLOWUP_PLAN_2026-10-02.md", followup["plan_sha256"], "post-result resource plan")
    match(G / "attempt_01.json", followup["first_attempt_sha256"], "retained resource-limited first result")
    match(B / "attempt_01.json", followup["header_attempt_sha256"], "follow-up header input")
    require(followup["complete"] and not followup["original_label_attempt_complete"] and followup["prior_arrays_reused"] == 3 and followup["new_label_arrays_requested"] == 5 and followup["array_nominal_total_bytes"] == 1_366_927_360, "Resource follow-up scope differs")
    require(followup["max_label_nominal_bytes"] == 400_000_000 and followup["max_total_nominal_bytes"] == 2_000_000_000 and followup["max_block_bytes"] == 32_000_000, "Revised fixed resource contract differs")
    require(followup["source_preflight_series_passed"] == 6 and followup["source_preflight_patients_with_a_passing_series"] == 3 and not followup["full_public_label_coverage_certified"] and followup["scientific_independent_validation_patients"] == 0, "Source preflight incorrectly certified performance/full coverage")
    match(ROOT / "experiments/verify_mc_rc_004_006_native_label_preflight.py", source_proof["verification_script_sha256"], "independent source verifier")
    for key, path in [("header_result_sha256", B / "attempt_01.json"), ("first_label_result_sha256", G / "attempt_01.json"), ("resource_followup_result_sha256", G / "resource_followup_attempt_01.json")]:
        match(path, source_proof[key], "source proof lineage " + key)
    require(source_proof["errors"] == [] and source_proof["counts"] == {"raw_DICOM_objects_checked": 701, "series": 8, "label_arrays_checked": 8, "header_qualified_series": 6, "source_preflight_series": 6, "source_preflight_patients": 3}, "Independent source proof scope differs")
    result, contract, proof = read(A / "attempt_01.json"), read(A / "run_contract.json"), read(A / "independent_numerical_and_forward_verification.json")
    match(A / "run_contract.json", result["run_contract_sha256"], "development contract")
    for entry in contract["files"]:
        match(ROOT.parent / entry["path"], entry["sha256"], "frozen development input/code/weight " + entry["path"], project_input=True)
    require(result["complete"] and len(result["patients"]) == 3 and not result["failures"] and not result["gpu_used"] and not result["cuda_initialized"] and not result["publication_claim_confirmed"], "Development execution/claim scope differs")
    require(contract["primary_action"] == ["pipeline_pchip", "hat"] and contract["secondary_action"] == ["raw_pchip", "hat"] and contract["tile_size"] == 32 and not contract["independent_confirmation"], "Fixed action scope changed")
    require([p["patient"] for p in result["patients"]] == ["VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"] and sum(len(p["targets"]) for p in result["patients"]) == 195, "Fixed developer/target roster differs")
    primary_flags, raw_flags = [], []
    for p in result["patients"]:
        match(ROOT / p["hat_file"], p["hat_sha256"], "saved full HAT output")
        match(ROOT / p["tiles_file"], p["tiles_sha256"], "saved tile moments")
        require(not p["task_fidelity_evaluated"] and not p["independent_confirmation"], "Developer was incorrectly counted as task/confirmation")
        for action in p["actions"]:
            sm = action["summaries"]
            best = min(sm["fixed_0"]["support"]["target_equal_nmse"], sm["fixed_1"]["support"]["target_equal_nmse"])
            gain = 10 * math.log10(best / sm["tile_32_oracle"]["support"]["target_equal_nmse"])
            guard = {field: sm["tile_32_oracle"]["lesion"][field] <= min(sm["fixed_0"]["lesion"][field], sm["fixed_1"]["lesion"][field]) for field in ("target_equal_nmse", "pixel_weighted_nmse")}
            gate = gain >= .1 and all(guard.values())
            require(abs(gain - action["support_gain_db_vs_better_fixed"]) <= 1e-12 and guard == action["lesion_guard"] and gate == action["development_gate_passed"], "Oracle arithmetic/gate differs")
            (primary_flags if action["base"] == "pipeline_pchip" else raw_flags).append(gate)
    require(primary_flags == [False, True, False] and raw_flags == [True, True, True] and not result["primary_fixed_action_development_gate_passed"], "Primary failure/secondary candidate was changed")
    match(ROOT / "experiments/verify_mc_rc_three_development_action_oracle.py", proof["verification_script_sha256"], "independent action verifier")
    match(A / "attempt_01.json", proof["result_sha256"], "action proof result")
    match(A / "run_contract.json", proof["run_contract_sha256"], "action proof contract")
    require(proof["errors"] == [] and proof["targets"] == 195 and proof["tiles"] == 54_768 and proof["direct_HAT_forward_planes"] == 9 and not proof["full_HAT_output_regenerated"], "Independent development numerical/forward proof scope differs")
    require(all(r["bitwise_equal"] for p in proof["patients"] for r in p["direct_HAT_forward_checks"]) and proof["scientific_independent_validation_patients"] == 0 and not proof["publication_claim_confirmed"], "Forward sampling or scientific limit differs")
    mixtures, next_batch = read(A / "fixed_mixture_comparison.json"), read(A / "next_development_followup_preparation.json")
    match(ROOT / "experiments/summarize_mc_rc_action_oracle_followup.py", mixtures["script_sha256"], "descriptive follow-up arithmetic code")
    match(A / "attempt_01.json", mixtures["result_sha256"], "descriptive arithmetic source")
    require(len(mixtures["rows"]) == 6, "Fixed-mixture description scope differs")
    by_patient = {p["patient"]: p for p in result["patients"]}
    for row in mixtures["rows"]:
        sm = next(a for a in by_patient[row["patient"]]["actions"] if a["base"] == row["base"])["summaries"]
        best_fixed = min(v["support"]["target_equal_nmse"] for name, v in sm.items() if name.startswith("fixed_"))
        expected_gain = 10 * math.log10(best_fixed / sm["tile_32_oracle"]["support"]["target_equal_nmse"])
        require(abs(row["oracle_gain_over_best_prespecified_constant_db"] - expected_gain) <= 1e-12, "Fixed-mixture increment differs")
    match(ROOT / "experiments/summarize_mc_rc_action_oracle_followup.py", next_batch["script_sha256"], "next source preparation code")
    match(ROOT / "MC_RC_RAW_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md", next_batch["plan_sha256"], "post-result raw follow-up preparation")
    match(A / "attempt_01.json", next_batch["three_patient_action_result_sha256"], "next branch original failed primary")
    for key, name in [("source_header_sha256", "literature/source_cache/mc_rc_three_patient_headers_2026-10-02/attempt_01.json"), ("source_refined_sha256", "experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json"), ("source_label_result_sha256", "experiments/mc_rc_native_t2_label_gate/label_grid_attempt_01.json"), ("source_proof_sha256", "experiments/mc_rc_native_t2_label_gate/independent_raw_geometry_grid_verification.json")]:
        match(ROOT / name, next_batch[key], "next fixed source " + key)
    require(next_batch["status"] == "prepared_not_executed" and not next_batch["new_MR_arrays_decoded"] and next_batch["network_requests_made"] == 0 and not next_batch["original_pipeline_primary_gate_passed"] and [r["patient"] for r in next_batch["selected"]] == ["VS-MC-RC-001", "VS-MC-RC-002"], "Next developer preparation incorrectly marked executed/confirmation")
    match(ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json", EXPECTED, "unchanged main cohort contract")
    # All these folders are terminal and local; never traverse a tool dependency junction/live queue.
    for folder in (B, G, A, ROOT / "data/mc_rc_004_006_native_header_gate", ROOT / "data/mc_rc_004_006_label_grid"):
        files.update(p for p in folder.iterdir() if p.is_file())
    files.update(ROOT / name for name in ["MC_RC_004_006_NATIVE_LABEL_RESULT_2026-10-02.md", "MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_RESULT_2026-10-02.md", "MC_RC_RAW_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md", "SESSION_UPDATE_MC_RC_ACTION_BATCH_2026-10-02.md", "SESSION_VISIBLE_DIALOGUE_MC_RC_ACTION_BATCH_2026-10-02.md", "SESSION_HANDOFF_MC_RC_ACTION_BATCH_QUEUE_ACTIVE_2026-10-02.md", "literature/capture_mc_rc_action_batch_queue_observation_2026_10_02.py", "literature/verify_mc_rc_action_batch_all_archives_2026_10_02.py", "literature/source_cache/mc_rc_action_batch_queue_observation_2026-10-02.json"])
    observation = read(ROOT / "literature/source_cache/mc_rc_action_batch_queue_observation_2026-10-02.json")
    require(observation["unified_exec_session"] == 83910 and observation["poll_returned_live"] and observation["contract_sha256"] == EXPECTED and not observation["scientific_goal_complete"] and not observation["dynamic_subcohort_statistics_computed"], "Historical queue snapshot scope differs")
    entries = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(files)]
    manifest = {"scope": "terminal source/development integrity; original resource failure and primary oracle failure retained; excludes live inference and bundled junction",
                "source_requests": 8, "source_transfer_bytes": byte_total, "raw_header_objects_independently_verified": 701,
                "label_arrays_independently_checked": 8, "native_header_label_preflight_series": 6, "native_header_label_preflight_patients": 3,
                "original_resource_gate_complete": False, "resource_revision_post_result": True, "full_public_label_coverage_certified": False,
                "development_MR_series_decoded": 3, "development_targets": 195, "development_tiles_independently_checked": 54_768,
                "HAT_direct_forward_planes_checked": 9, "all_HAT_planes_regenerated": False,
                "primary_fixed_action_development_gate_passed": False, "raw_secondary_patient_gates": raw_flags,
                "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False,
                "next_development_status": "prepared_not_executed", "main_contract_sha256": EXPECTED, "files": entries}
    if "--write" in sys.argv:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        require(MANIFEST.is_file() and read(MANIFEST) == manifest, "Static action-batch manifest differs")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"} | {"files": len(entries), "errors": errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
