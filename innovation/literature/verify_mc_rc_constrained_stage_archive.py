"""Static lineage and scientific-conclusion audit for the fixed-five checkpoint."""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "literature/mc_rc_constrained_stage_archive_manifest_2026-10-02.json"
EXPECTED = "061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5"

def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as stream:
        for block in iter(lambda: stream.read(1_048_576), b""):
            h.update(block)
    return h.hexdigest()

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    errors, files = [], {Path(__file__), ROOT / "README.md"}
    def require(ok, why):
        if not ok:
            errors.append(why)
    def match(p, expected, why, original_project=False):
        p = Path(p).resolve()
        allowed = ROOT.parent if original_project else ROOT
        valid = p.is_relative_to(allowed) and p.is_file()
        require(valid, "Missing/outside authorized scope " + why)
        if valid:
            require(sha(p) == expected, "Hash differs " + why)
            if p.is_relative_to(ROOT):
                files.add(p)
    folders = [ROOT / "experiments" / name for name in ("mc_rc_001_002_raw_action_oracle", "mc_rc_five_developer_constrained_oracle", "mc_rc_constrained_constant_diagnostic")]
    raw, constrained, constant = [read(f / "attempt_01.json") for f in folders]
    for folder, result in zip(folders, (raw, constrained, constant)):
        contract = read(folder / "run_contract.json")
        match(folder / "run_contract.json", result["run_contract_sha256"], "contract " + folder.name)
        for entry in contract["files"]:
            base = ROOT.parent if entry["path"].replace("\\", "/").startswith("innovation/") else ROOT
            # Original raw contract paths are workspace-relative, including weights.
            if folder.name == "mc_rc_001_002_raw_action_oracle":
                base = ROOT.parent
            match(base / entry["path"], entry["sha256"], "frozen file " + entry["path"], original_project=True)
        require(result["complete"] and not result["publication_claim_confirmed"] and not result["gpu_used"], "Execution/publication scope changed " + folder.name)
        files.update(p for p in folder.iterdir() if p.is_file())
    raw_proof = read(folders[0] / "independent_numerical_and_forward_verification.json")
    match(ROOT / "experiments/verify_mc_rc_001_002_raw_action_oracle.py", raw_proof["verification_script_sha256"], "raw verifier")
    match(folders[0] / "attempt_01.json", raw_proof["result_sha256"], "raw proof result")
    match(folders[0] / "run_contract.json", raw_proof["run_contract_sha256"], "raw proof contract")
    require(raw_proof["errors"] == [] and raw_proof["targets"] == 45 and raw_proof["tiles"] == 14976 and raw_proof["direct_HAT_forward_planes"] == 6 and not raw_proof["full_HAT_output_regenerated"], "Raw proof scope differs")
    require(not raw["primary_fixed_action_development_gate_passed"] and not raw["all_five_raw_development_gate_passed"] and not raw["cuda_initialized"], "Original raw failure was removed")
    raw_flags = []
    for p in raw["patients"]:
        for key in ("hat", "tiles"):
            match(ROOT / p[key + "_file"], p[key + "_sha256"], "raw saved " + key)
        action = next(a for a in p["actions"] if a["base"] == "raw_pchip")
        raw_flags.append(action["development_gate_passed"])
    require(raw_flags == [False, True], "Fixed two-patient guard pattern differs")
    adaptation = read(folders[0] / "independent_verifier_source_adaptation.json")
    match(ROOT / adaptation["source_file"], adaptation["source_sha256"], "unchanged old verifier")
    match(ROOT / adaptation["target_file"], adaptation["target_sha256"], "adapted verifier")
    require(len(adaptation["replacements"]) == 5, "Verifier adaptation scope changed")
    proof = read(folders[1] / "independent_pixel_and_dual_verification.json")
    match(ROOT / "experiments/verify_mc_rc_five_developer_constrained_oracle.py", proof["verification_script_sha256"], "independent constrained verifier")
    match(folders[1] / "attempt_01.json", proof["result_sha256"], "constrained proof result")
    match(folders[1] / "run_contract.json", proof["run_contract_sha256"], "constrained proof contract")
    require(proof["errors"] == [] and proof["targets"] == 240 and proof["tiles"] == 34872 and proof["neural_networks_executed"] == 0 and not proof["full_HAT_output_regenerated"], "Constrained proof scope differs")
    require(constrained["post_result_diagnostic"] and constrained["all_five_constrained_space_gate_passed"] and not constrained["original_unconstrained_raw_gate_passed"] and constrained["scientific_independent_validation_patients"] == 0, "Constrained scientific boundary changed")
    require([p["patient"] for p in constrained["patients"]] == ["VS-MC-RC-001", "VS-MC-RC-002", "VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"], "Five-patient roster changed")
    by_proof = {p["patient"]: p for p in proof["patients"]}
    for p in constrained["patients"]:
        match(ROOT / p["coefficients_file"], p["coefficients_sha256"], "constrained coefficients")
        s = p["solution"]
        gain = 10 * math.log10(min(p["baseline_losses"][0], p["candidate_losses"][0]) / s["primal_objective"])
        require(abs(gain - p["constrained_support_gain_db_vs_better_fixed"]) <= 1e-12 and gain >= .1, "Constrained gain arithmetic differs")
        require(s["numerically_certified"] and max(s["violations"]) <= 1e-10 and -1e-10 <= s["primal_dual_gap"] <= 1e-8 and s["max_box_stationarity_residual"] <= 1e-8 and min(s["multipliers"]) >= 0, "Saved certificate failed")
        pr = by_proof[p["patient"]]
        require(pr["numerically_certified"] and not pr["patient_errors"] and pr["post_result_space_gate_passed"] and not pr["independent_confirmation"], "Independent patient certificate changed")
    require(not constant["errors"] and constant["post_result_diagnostic"] and constant["target_assisted_shared_alpha"] and not constant["original_raw_gate_passed"] and not constant["deployable_method_tested"], "Constant diagnostic boundary changed")
    require(all(p["shared_constant_feasible"] and max(p["violations"]) <= 1e-10 and p["tile_gain_over_best_feasible_shared_db"] > 0 for p in constant["patients"]), "Common-alpha diagnostic conclusion differs")
    require([p["changed_tiles"] for p in constant["patients"]] == [10, 0, 0, 0, 0], "Local conflict description differs")
    failure = read(folders[2] / "failed_attempt_01_run_contract.json")
    entry = next(e for e in failure["files"] if e["path"] == "experiments/mc_rc_constrained_constant_diagnostic.py")
    match(folders[2] / "failed_attempt_01_script.py", entry["sha256"], "retained first failing constant source")
    require((folders[1] / "independent_verifier_failed_attempt_01.json").is_file() and (folders[2] / "failed_attempt_01.json").is_file(), "Known failure record missing")
    cache = ROOT / "literature/source_cache/constrained_oracle_reading_2026-10-02"
    index = read(cache / "index.json")
    match(ROOT / "literature/prepare_constrained_oracle_reading_evidence.py", index["script_sha256"], "reading builder")
    require(index["papers_reread"] == 6 and index["new_papers_acquired"] == 0 and index["network_requests_made"] == 0 and len(index["rendered_pages"]) == 4 and index["render_error"] is None, "Reading count/render scope differs")
    for p in index["records"]:
        match(ROOT / p["source_file"], p["source_sha256"], "reread source")
        match(ROOT / p["excerpts_file"], p["excerpts_sha256"], "reading excerpt")
    for p in index["rendered_pages"]:
        match(ROOT / p["source_pdf"], p["source_sha256"], "render source")
        match(ROOT / p["png"], p["png_sha256"], "rendered page")
    files.update(p for p in cache.iterdir() if p.is_file())
    snapshot = ROOT / "literature/source_cache/mc_rc_constrained_queue_observation_2026-10-02.json"
    observation = read(snapshot)
    require(observation["unified_exec_session"] == 83910 and observation["poll_returned_live"] and observation["contract_sha256"] == EXPECTED and not observation["dynamic_subcohort_statistics_computed"] and not observation["scientific_goal_complete"], "Historical queue snapshot scope differs")
    files.add(snapshot)
    match(ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json", EXPECTED, "unchanged original queue")
    names = ["MC_RC_001_002_RAW_ACTION_EXECUTION_PLAN_2026-10-02.md", "MC_RC_001_002_RAW_ACTION_ORACLE_RESULT_2026-10-02.md", "MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_PLAN_2026-10-02.md", "MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_RESULT_2026-10-02.md", "MC_RC_CONSTRAINED_CONSTANT_DIAGNOSTIC_PLAN_2026-10-02.md", "MC_RC_JOINT_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md", "SESSION_UPDATE_MC_RC_CONSTRAINED_2026-10-02.md", "SESSION_VISIBLE_DIALOGUE_MC_RC_CONSTRAINED_2026-10-02.md", "SESSION_HANDOFF_MC_RC_CONSTRAINED_QUEUE_ACTIVE_2026-10-02.md", "USER_PROVIDED_HANDOFF_MC_RC_CONSTRAINED_2026-10-02.md", "literature/2026-10-02_constrained_oracle_prior_art_recheck.md", "experiments/prepare_mc_rc_001_002_independent_verifier.py", "literature/capture_mc_rc_constrained_queue_observation_2026_10_02.py", "literature/verify_mc_rc_constrained_all_archives_2026_10_02.py"]
    for name in names:
        p = ROOT / name
        require(p.is_file(), "Missing stage file " + name)
        if p.is_file():
            files.add(p)
    manifest = {"scope": "terminal fixed-five developer results/known failures/local reading; excludes live queue and dependency junctions", "fixed_main_contract_sha256": EXPECTED,
                "raw_development_gate_passed": False, "constrained_post_result_space_gate_passed": True, "independent_pixel_targets": 240, "independent_pixel_tiles": 34872,
                "new_papers_acquired": 0, "papers_reread": 6, "PDF_pages_rendered_and_inspected": 4, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False,
                "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(files)]}
    if "--write" in sys.argv:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        require(MANIFEST.is_file() and read(MANIFEST) == manifest, "Static constrained stage manifest differs")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"} | {"files": len(files), "errors": errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))

if __name__ == "__main__":
    raise SystemExit(main())
