"""Static fixed-five learning/failure/lineage audit; no live queue statistics."""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/mc_rc_visible_joint_development_diagnostic"
FAILED = ROOT / "experiments/mc_rc_visible_joint_development_diagnostic_failed_attempt_01"
MANIFEST = ROOT / "literature/mc_rc_visible_stage_archive_manifest_2026-10-02.json"
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
    def require(ok, message):
        if not ok:
            errors.append(message)
    def match(p, expected, why):
        p = Path(p).resolve()
        valid = p.is_relative_to(ROOT) and p.is_file()
        require(valid, "Missing/outside stage scope " + why)
        if valid:
            require(sha(p) == expected, "Hash differs " + why)
            files.add(p)
    result, contract, proof = read(OUT / "attempt_01.json"), read(OUT / "run_contract.json"), read(OUT / "independent_refit_and_pixel_verification.json")
    match(OUT / "run_contract.json", result["run_contract_sha256"], "current contract")
    for entry in contract["files"]:
        match(ROOT / entry["path"], entry["sha256"], "frozen input " + entry["path"])
    require(contract["ridge"] == .01 and len(contract["features"]) == 30 and contract["alpha_grid"] == [0., .25, .5, .75, 1.], "Fixed design changed")
    roster = [f"VS-MC-RC-{i:03d}" for i in (1, 2, 4, 5, 6)]
    require([p["patient"] for p in result["patients"]] == roster and [p["patient"] for p in contract["roles"]] == roster, "Developer roster changed")
    require(result["complete"] and not result["errors"] and result["post_result_development_diagnostic"] and not result["gpu_used"] and result["neural_networks_executed"] == 0 and result["scientific_independent_validation_patients"] == 0 and not result["publication_claim_confirmed"], "Execution/claim scope differs")
    require(not result["fixed_visible_joint_diagnostic_gate_passed"] and not result["all_five_joint_patient_gates_passed"] and not result["original_raw_development_gate_passed"], "Failed scientific gates removed")
    gates, equivalences = [], []
    for p in result["patients"]:
        require(p["training_patients"] == [k for k in roster if k != p["patient"]] and p["development_only"], "Whole-patient LOPO roles differ")
        for prefix in ("visible", "supervision", "model", "policies"):
            match(ROOT / p[prefix + "_file"], p[prefix + "_sha256"], prefix + " artifact")
        with np.load(ROOT / p["policies_file"]) as pack:
            for suffix in ("support", "joint"):
                require(np.array_equal(pack["alpha_full_errors_" + suffix], pack["alpha_full_gains_" + suffix]), "Equivalent coordinate policies differ")
            require(np.count_nonzero(pack["alpha_full_gains_joint"]) == np.count_nonzero(pack["alpha_random_matched_joint"]), "Matched count differs")
        with np.load(ROOT / p["supervision_file"]) as pack:
            coef = pack["coefficients"]
        with np.load(ROOT / p["policies_file"]) as pack:
            for policy, row in p["policies"].items():
                alpha = pack["alpha_" + policy]
                computed = [float(np.sum(coef[:, k] - 2 * coef[:, k + 1] * alpha + coef[:, k + 2] * alpha ** 2)) for k in (0, 3, 6)]
                actual = [row["support_target_equal_nmse"], row["lesion_target_equal_nmse"], row["lesion_pixel_weighted_nmse"]]
                require(np.allclose(computed, actual, rtol=0, atol=1e-12), "Stored policy coefficient arithmetic differs")
                raw = p["policies"]["fixed_0"]
                candidate = p["policies"]["fixed_1"]
                expected_gain = 10 * math.log10(min(raw["support_target_equal_nmse"], candidate["support_target_equal_nmse"]) / actual[0])
                require(abs(expected_gain - row["gain_db_vs_better_fixed"]) <= 1e-12, "Stored gain arithmetic differs")
        gates.append(p["policies"]["full_gains_joint"]["strict_development_gate_passed"])
        equivalences.append(p["maximum_linear_coordinate_prediction_difference"])
    require(gates == [False, False, True, False, True] and max(equivalences) <= 1e-10, "Joint failure / linear equivalence differs")
    require(result["patient_equal_mean_support_nmse"]["full_gains_joint"] > result["patient_equal_mean_support_nmse"]["fixed_0.5"], "Strong constant counterevidence lost")
    match(ROOT / "experiments/verify_mc_rc_visible_joint_development_diagnostic.py", proof["verification_script_sha256"], "current independent verifier")
    match(OUT / "attempt_01.json", proof["result_sha256"], "independent result lineage")
    match(OUT / "run_contract.json", proof["run_contract_sha256"], "independent contract lineage")
    require(proof["errors"] == [] and proof["targets"] == 240 and proof["tiles"] == 34872 and proof["supervised_scalar_targets_independently_recomputed"] == 348720 and proof["sampled_native_feature_rows"] == 25 and not proof["fixed_visible_joint_diagnostic_gate_passed"], "Independent audit scope differs")
    require(all(p["policies"] == 13 and not p["errors"] and p["independent_ridge_prediction_max_difference"] <= 1e-10 for p in proof["patients"]), "Independent fold checks differ")
    failed_contract = read(FAILED / "run_contract.json")
    producer_entry = next(e for e in failed_contract["files"] if e["path"] == "experiments/mc_rc_visible_joint_development_diagnostic.py")
    match(FAILED / "failed_script.py", producer_entry["sha256"], "first failed producer code")
    old_source = (FAILED / "failed_script.py").read_text(encoding="utf-8")
    expected_source = old_source.replace("guards = [losses[j + 1] <= limits[j] for j in range(2)]", "guards = [bool(losses[j + 1] <= limits[j]) for j in range(2)]")
    require(expected_source == (ROOT / "experiments/mc_rc_visible_joint_development_diagnostic.py").read_text(encoding="utf-8"), "Producer changed beyond recorded serialization fix")
    # The failed execution exported all arrays; require the serialization-only
    # rerun to reproduce them exactly and keep the first saved policy/model.
    for p in FAILED.glob("*.npz"):
        with np.load(p) as before, np.load(OUT / p.name) as after:
            require(set(before.files) == set(after.files) and all(np.array_equal(before[k], after[k]) for k in before.files), "Failed-attempt arrays changed on rerun " + p.name)
    first_proof = read(OUT / "independent_refit_and_pixel_verification_failed_attempt_01.json")
    require(first_proof["errors"] == ["Matched random control differs"] * 5, "First verifier failure missing/changed")
    match(OUT / "independent_verifier_failed_attempt_01.py", first_proof["verification_script_sha256"], "failed independent source")
    previous_proof = read(OUT / "independent_refit_and_pixel_verification_before_supervision_audit.json")
    match(OUT / "independent_verifier_before_supervision_audit.py", previous_proof["verification_script_sha256"], "pre-supervision audit source")
    require(previous_proof["errors"] == [] and not previous_proof["fixed_visible_joint_diagnostic_gate_passed"], "Pre-supervision successful audit changed")
    preparation = read(OUT / "next_developer_source_preparation.json")
    for key, path in [("script_sha256", "experiments/prepare_mc_rc_next_developer_sources.py"), ("plan_sha256", "MC_RC_NEXT_DEVELOPER_SOURCE_PREPARATION_PLAN_2026-10-02.md"), ("availability_result_sha256", "experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json"), ("api_sha256", "literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response")]:
        match(ROOT / path, preparation[key], "next source preparation " + key)
    require(preparation["status"] == "prepared_not_executed" and preparation["network_requests_made"] == 0 and not preparation["new_MR_arrays_decoded"] and not preparation["new_label_arrays_decoded"] and preparation["scientific_independent_validation_patients"] == 0, "Next-source preparation was incorrectly counted as execution/confirmation")
    availability = read(ROOT / "experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json")
    api = {r["SeriesInstanceUID"]: r for r in read(ROOT / "literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response")}
    candidates = [r for r in availability["availability"]["rows"] if r["patient"].startswith("VS-MC-RC-") and r["description"].startswith("_T2_") and r["availability"] == "available"]
    next_patients = sorted({r["patient"] for r in candidates} - {f"VS-MC-RC-{i:03d}" for i in range(1, 7)})[:3]
    selected = sorted([r for r in candidates if r["patient"] in next_patients], key=lambda r: (r["patient"], r["study"], r["uid"]))
    require(preparation["next_batch_patient_ids"] == next_patients == ["VS-MC-RC-007", "VS-MC-RC-009", "VS-MC-RC-010"] and [r["availability"] for r in preparation["next_batch_series"]] == selected, "Next fixed source roster differs")
    require(len(selected) == 7 and sum(api[r["uid"]]["ImageCount"] for r in selected) == preparation["next_batch_API_ImageCount"] == 527 and sum(api[r["uid"]]["FileSize"] for r in selected) == preparation["next_batch_API_FileSize"] == 261941288, "Next-source metadata counts differ")
    for r in preparation["next_batch_series"]:
        require(r["source"] == api[r["availability"]["uid"]], "Next source exact UID linkage differs")
    observation_path = ROOT / "literature/source_cache/mc_rc_visible_queue_observation_2026-10-02.json"
    observation = read(observation_path)
    require(observation["unified_exec_session"] == 83910 and observation["poll_returned_live"] and observation["contract_sha256"] == EXPECTED and not observation["dynamic_subcohort_statistics_computed"] and not observation["scientific_goal_complete"], "Progress-only snapshot changed")
    files.add(observation_path)
    match(ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json", EXPECTED, "unchanged original cohort")
    files.update(p for folder in (OUT, FAILED) for p in folder.iterdir() if p.is_file())
    names = ["MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_PLAN_2026-10-02.md", "MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_RESULT_2026-10-02.md", "MC_RC_NEXT_DEVELOPER_SOURCE_PREPARATION_PLAN_2026-10-02.md", "INNOVATION_DECISION_AFTER_VISIBLE_JOINT_2026-10-02.md", "SESSION_UPDATE_MC_RC_VISIBLE_2026-10-02.md", "SESSION_VISIBLE_DIALOGUE_MC_RC_VISIBLE_2026-10-02.md", "SESSION_HANDOFF_MC_RC_VISIBLE_QUEUE_ACTIVE_2026-10-02.md", "literature/capture_mc_rc_visible_queue_observation_2026_10_02.py", "literature/verify_mc_rc_visible_all_archives_2026_10_02.py"]
    for name in names:
        p = ROOT / name
        require(p.is_file(), "Missing stage document " + name)
        if p.is_file():
            files.add(p)
    manifest = {"scope": "terminal fixed-five visible learning, failures and source-only preparation; excludes live queue/dependency junctions", "targets": 240, "tiles": 34872, "policies_per_patient": 13, "supervised_scalars_independently_checked": 348720, "sampled_native_feature_rows": 25, "original_raw_development_gate_passed": False, "fixed_visible_joint_diagnostic_gate_passed": False, "linear_gain_error_coordinates_identical_policies": True, "next_source_status": "prepared_not_executed", "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False,
                "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(files)]}
    if "--write" in sys.argv:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        require(MANIFEST.is_file() and read(MANIFEST) == manifest, "Visible stage manifest out of date")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"} | {"files": len(files), "errors": errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))

if __name__ == "__main__":
    raise SystemExit(main())
