"""Verify static native-header/label provenance while retaining all failed gates."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "literature/source_cache/mc_rc_three_patient_headers_2026-10-02"
GATE = ROOT / "experiments/mc_rc_native_t2_label_gate"
MANIFEST = ROOT / "literature/mc_rc_native_stage_archive_manifest_2026-10-02.json"
EXPECTED = "061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    errors = []
    files = {Path(__file__), ROOT / "README.md"}

    def require(condition, message):
        if not condition:
            errors.append(message)

    def match(path, expected, message, archived_input=True):
        path = Path(path).resolve()
        allowed_root = ROOT if archived_input else ROOT.parent
        require(path.is_relative_to(allowed_root) and path.is_file(), "File outside allowed root or missing: " + message)
        if path.is_file() and path.is_relative_to(allowed_root):
            if path.is_relative_to(ROOT):
                files.add(path)
            require(sha(path) == expected, "Hash differs: " + message)

    ledger = read(B / "attempt_01.json")
    first = read(GATE / "label_grid_attempt_01.json")
    refined = read(GATE / "geometry_availability_attempt_01.json")
    proof = read(GATE / "independent_raw_geometry_grid_verification.json")
    reader = read(GATE / "official_pathnames_artifact_read.json")
    preparation = read(GATE / "labelled_native_expansion_preparation.json")
    match(ROOT / "literature/download_mc_rc_three_patient_headers_2026_10_02.py", ledger["script_sha256"], "download script")
    match(ROOT / "MC_RC_THREE_PATIENT_NATIVE_HEADER_PLAN_2026-10-02.md", ledger["plan_sha256"], "header plan")
    match(ROOT / "experiments/mc_rc_v2_nonpixel_identity/native_header_followup_selection.json", ledger["selection_sha256"], "prior frozen selection")
    require(ledger["complete"] and len(ledger["series"]) == 9 and ledger["header_qualified_series"] == 5, "Original header scope differs")
    require(not ledger["MR_pixel_array_decoded"] and not ledger["patient_performance_statistics_computed"], "MR/performance scope differs")
    total_transfer = 0
    header_objects = 0
    patients = set()
    header_by_uid = {}
    for r in ledger["series"]:
        uid = r["source"]["SeriesInstanceUID"]
        patients.add(r["source"]["PatientID"])
        t = r["transfer"]
        require(t["complete"] and t["http_status"] == 200 and r["headers_complete"], "Incomplete source request " + uid)
        path = ROOT / t["file"]
        match(path, t["sha256"], "MR ZIP " + uid)
        require(path.stat().st_size == t["bytes"] and t["bytes"] <= t["cap_bytes"], "MR transfer size differs " + uid)
        total_transfer += t["bytes"]
        match(B / r["header_file"], r["header_sha256"], "header extraction " + uid)
        header = read(B / r["header_file"])
        header_by_uid[uid] = header
        require(not header["MR_pixel_array_decoded"] and header["summary"] == r["summary"], "Header scope/summary differs " + uid)
        records = header["records"]
        header_objects += len(records)
        require(len(records) == r["source"]["ImageCount"] and len({v["sop_uid"] for v in records}) == len(records), "Header object count differs " + uid)
        require(all(v["patient"] == r["source"]["PatientID"] and v["series_uid"] == uid and v["study_uid"] == r["source"]["StudyInstanceUID"] for v in records), "Header identity differs " + uid)
    require(patients == {"VS-MC-RC-001", "VS-MC-RC-002", "VS-MC-RC-003"} and header_objects == 473, "Fixed source roster/count differs")
    labels = ledger["labels"]
    t = labels["transfer"]
    label_zip = ROOT / t["file"]
    match(label_zip, t["sha256"], "official label ZIP")
    require(t["complete"] and t["http_status"] == 200 and labels["directory_complete"] and label_zip.stat().st_size == t["bytes"], "Label ZIP transfer differs")
    total_transfer += t["bytes"]
    require(total_transfer == ledger["total_transfer_bytes"] == 79_554_134 and total_transfer < 300_000_000, "Total source transfer differs")
    for r in labels["metadata"]:
        match(B / r["file"], r["sha256"], "label metadata " + r["file"])
    csv_path = B / "official_label_metadata_00_attempt_01.csv"
    match(csv_path, reader["source_sha256"], "CSV artifact source")
    match(ROOT / "tools/mc_rc_pathname_read_2026-10-02/read_official_mc_rc_pathnames.mjs", reader["script_sha256"], "artifact reader")
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        cells = list(csv.reader(f))
    require(cells == reader["values"] and len(cells) == 488 and all(len(r) == 15 for r in cells), "Artifact/Python all-cell equivalence differs")
    require(reader["sheet"] == "Official pathnames" and reader["range"] == "A1:O488" and "matched 0 entries" in reader["error_scan_ndjson"], "CSV read-only scope differs")
    mapping = [dict(zip(cells[0], values)) for values in cells[1:]]
    api_path = ROOT / "literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response"
    files.add(api_path)
    api = {r["SeriesInstanceUID"]: r for r in read(api_path)}
    require(len(api) == len(mapping) == len({r["series_instance_uid"] for r in mapping}) == 487, "Full metadata uniqueness/count differs")
    require(set(api) == {r["series_instance_uid"] for r in mapping}, "Full CSV/API UID universe differs")
    prefix = "VS-MC-RC-Segmentations_with_pathname_spreadsheet-Release2023/VS-MC-RC segmentations-NIfTI-Release 2023/"
    with zipfile.ZipFile(label_zip) as z:
        actual_inventory = [{"path": m.filename, "compressed_bytes": m.compress_size, "uncompressed_bytes": m.file_size, "crc32": f"{m.CRC:08x}"} for m in z.infolist() if not m.is_dir()]
        require(actual_inventory == labels["members"], "Official full ZIP directory differs")
        nifti_paths = {m.filename[len(prefix):] for m in z.infolist() if not m.is_dir() and m.filename.startswith(prefix) and m.filename.endswith(".nii.gz")}
    require(len(nifti_paths) == 301 and len({p.split("/", 1)[0] for p in nifti_paths}) == 124, "Actual label files/patients differ")
    available_rows = []
    for m in mapping:
        a = api[m["series_instance_uid"]]
        require(a["PatientID"] == m["patient_id"] and a["StudyInstanceUID"] == m["study_instance_uid"] and a["ImageCount"] == int(m["num_files"]), "Full metadata identity differs " + m["series_instance_uid"])
        path = m["SegmentationPath"]
        status = "blank_path" if path == "" else "available" if path in nifti_paths else "specified_path_absent"
        available_rows.append({"uid": m["series_instance_uid"], "patient": a["PatientID"], "study": a["StudyInstanceUID"], "description": a["SeriesDescription"], "release": a["DateReleased"], "segmentation_path": path, "availability": status})
    available_rows.sort(key=lambda r: (r["patient"], r["study"], r["uid"]))
    require(available_rows == refined["availability"]["rows"], "Independent CSV/ZIP/API availability rows differ")
    counts = dict(Counter(r["availability"] for r in available_rows))
    require(counts == {"available": 301, "blank_path": 60, "specified_path_absent": 126}, "Availability categories differ")
    missing = [r for r in available_rows if r["availability"] == "specified_path_absent"]
    require(all(r["description"].startswith("_T2_") and r["release"].startswith("2026-06-04") for r in missing), "Missing 2026 T2 identity differs")
    blank_counts = Counter((r["description"][:4], r["release"][:10]) for r in available_rows if r["availability"] == "blank_path")
    require(dict(blank_counts) == {("_T1_", "2023-08-23"): 53, ("_T1_", "2026-06-04"): 7}, "Blank T1 path categories differ")
    labelled_candidates = [r for r in available_rows if r["patient"].startswith("VS-MC-RC-") and r["description"].startswith("_T2_") and r["availability"] == "available"]
    require(len(labelled_candidates) == 159 and len({r["patient"] for r in labelled_candidates}) == 71, "Labelled nonoverlap candidate counts differ")
    require(len({r["patient"] for r in available_rows if r["patient"].startswith("VS-SEG-")}) == 58, "Shared-patient exclusion scope differs")
    match(ROOT / "experiments/audit_mc_rc_three_patient_label_grid.py", first["script_sha256"], "first label script")
    match(ROOT / "MC_RC_THREE_PATIENT_LABEL_GRID_PLAN_2026-10-02.md", first["plan_sha256"], "first label plan")
    match(B / "attempt_01.json", first["source_header_attempt_sha256"], "first label header source")
    match(label_zip, first["official_label_zip_sha256"], "first label ZIP source")
    match(GATE / "official_pathnames_artifact_read.json", first["full_metadata_audit"]["artifact_read_sha256"], "first label artifact source")
    require(not first["complete"] and len(first["full_metadata_audit"]["errors"]) == 186 and first["source_preflight_series_passed"] == 3, "Original full label failure was lost")
    require(first["label_arrays_decoded"] and not first["MR_pixel_arrays_decoded"] and first["scientific_independent_validation_patients"] == 0, "First label/performance scope differs")
    inspected = [r for r in first["series"] if r.get("label_inspection_complete")]
    require(len(inspected) == 6, "Original label-read scope differs")
    with zipfile.ZipFile(label_zip) as z:
        for r in inspected:
            match(ROOT / r["label_file"], r["label_sha256"], "extracted label " + r["series_uid"])
            require(hashlib.sha256(z.read(r["label_zip_member"])).hexdigest() == r["label_sha256"], "ZIP/extracted label bytes differ " + r["series_uid"])
    for script, data in [("refine_mc_rc_geometry_and_label_availability.py", refined)]:
        match(ROOT / "experiments" / script, data["script_sha256"], script)
        match(ROOT / "experiments/audit_mc_rc_three_patient_label_grid.py", data["grid_helper_sha256"], "refined grid helper")
        match(ROOT / "MC_RC_GEOMETRY_AND_LABEL_AVAILABILITY_FOLLOWUP_PLAN_2026-10-02.md", data["plan_sha256"], "refinement plan")
        match(B / "attempt_01.json", data["header_attempt_sha256"], "refinement original headers")
        match(GATE / "label_grid_attempt_01.json", data["first_label_grid_attempt_sha256"], "retained original label failure")
    match(ROOT / "experiments/verify_mc_rc_native_t2_label_preflight.py", proof["verification_script_sha256"], "independent raw verifier")
    match(ROOT / "MC_RC_GEOMETRY_AND_LABEL_AVAILABILITY_FOLLOWUP_PLAN_2026-10-02.md", proof["plan_sha256"], "independent follow-up plan")
    match(B / "attempt_01.json", proof["header_result_sha256"], "proof headers")
    match(GATE / "label_grid_attempt_01.json", proof["first_label_result_sha256"], "proof original label failure")
    match(GATE / "geometry_availability_attempt_01.json", proof["refined_result_sha256"], "proof refined result")
    require(proof["errors"] == [] and proof["counts"] == {"raw_DICOM_objects_checked": 473, "series": 9, "label_arrays_checked": 6, "header_qualified_series": 6, "source_preflight_series": 4, "source_preflight_patients": 2}, "Raw independent proof differs")
    require(not proof["original_full_label_gate_complete"] and not proof["full_public_label_coverage_certified"] and not proof["MR_pixel_arrays_decoded"] and proof["scientific_independent_validation_patients"] == 0, "Raw proof certified an incomplete/performance gate")
    require(refined["refined_header_qualified_series"] == 6 and refined["refined_source_preflight_series"] == 4 and refined["refined_source_preflight_patients"] == 2 and not refined["full_public_label_coverage_certified"], "Refined preflight scope differs")
    changed = [r for r in refined["series"] if r["first_run_header_qualified"] != r["refined_header_qualified"]]
    require(len(changed) == 1 and changed[0]["uid"] == "1.3.6.1.4.1.14519.5.2.1.213711595575218613093188251544325434833" and changed[0]["first_run_max_affine_residual_mm"] > .02 and changed[0]["max_fitted_position_residual_mm"] < .02, "Post-result estimator correction differs")
    third = [r for r in refined["series"] if r["patient"] == "VS-MC-RC-003"]
    require(len(third) == 3 and all(not r["prior_label_inspection_complete"] and not r["refined_header_and_label_grid_passed"] for r in third), "Missing third-patient labels incorrectly passed")
    require(sum(r["missing_acquisition_type_pending"] for r in refined["series"]) == 1, "Missing acquisition type status differs")
    match(ROOT / "experiments/prepare_mc_rc_labelled_native_expansion.py", preparation["script_sha256"], "preparation script")
    match(ROOT / "MC_RC_LABELLED_NATIVE_EXPANSION_PREPARATION_2026-10-02.md", preparation["plan_sha256"], "preparation plan")
    match(GATE / "geometry_availability_attempt_01.json", preparation["availability_result_sha256"], "preparation source")
    match(api_path, preparation["api_sha256"], "preparation API")
    require(preparation["status"] == "prepared_not_executed" and preparation["network_requests_made"] == 0 and not preparation["MR_pixel_arrays_decoded"] and not preparation["new_label_arrays_decoded"], "Future batch incorrectly marked executed")
    require(preparation["candidate_series"] == labelled_candidates and preparation["candidate_patients"] == sorted({r["patient"] for r in labelled_candidates}), "Future candidate universe differs")
    selected_patients = sorted({r["patient"] for r in labelled_candidates} - {"VS-MC-RC-001", "VS-MC-RC-002", "VS-MC-RC-003"})[:3]
    selected_rows = [r for r in labelled_candidates if r["patient"] in selected_patients]
    expected_batch = [{"availability": r, "source": api[r["uid"]]} for r in selected_rows]
    require(preparation["next_batch_patient_ids"] == selected_patients == ["VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"] and preparation["next_batch_series"] == expected_batch and len(expected_batch) == 8, "Future fixed batch differs")
    require(preparation["next_batch_API_ImageCount"] == sum(r["source"]["ImageCount"] for r in expected_batch) == 701 and preparation["next_batch_API_FileSize"] == sum(r["source"]["FileSize"] for r in expected_batch) == 385_990_404, "Future API resource estimate differs")
    match(ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json", EXPECTED, "frozen main cohort contract")
    frozen = 0
    for r in read(ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json")["files"]:
        if Path(r["path"]).suffix in (".md", ".py"):
            match(ROOT.parent / r["path"], r["sha256"], "frozen protocol/code " + r["path"], archived_input=False)
            frozen += 1
    # Include static new products only. Never walk the tools dependency junction or live cohort outputs.
    files.update(p for p in B.iterdir() if p.is_file())
    files.update(p for p in GATE.iterdir() if p.is_file())
    files.update(ROOT / name for name in [
        "MC_RC_NATIVE_T2_LABEL_PREFLIGHT_RESULT_2026-10-02.md",
        "INNOVATION_DECISION_AFTER_MC_RC_PREFLIGHT_2026-10-02.md",
        "MC_RC_LABELLED_NATIVE_EXPANSION_PREPARATION_2026-10-02.md",
        "USER_PROVIDED_HANDOFF_MC_RC_NATIVE_2026-10-02.md",
        "SESSION_UPDATE_MC_RC_NATIVE_2026-10-02.md",
        "SESSION_VISIBLE_DIALOGUE_MC_RC_NATIVE_2026-10-02.md",
        "SESSION_HANDOFF_MC_RC_NATIVE_QUEUE_ACTIVE_2026-10-02.md",
        "literature/verify_mc_rc_native_all_archives_2026_10_02.py",
        "literature/capture_mc_rc_native_queue_observation_2026_10_02.py",
        "literature/source_cache/mc_rc_native_queue_observation_2026-10-02.json",
    ])
    observation = read(ROOT / "literature/source_cache/mc_rc_native_queue_observation_2026-10-02.json")
    require(observation["unified_exec_session"] == 83910 and observation["poll_returned_live"] and observation["contract_sha256"] == EXPECTED and not observation["scientific_goal_complete"], "Queue historical observation differs")
    entries = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(files)]
    manifest = {
        "scope": "static source/native-header/label-grid archive; includes original failures and post-result estimator correction; excludes live inference and bundled dependency junction",
        "source_requests": 10, "total_transfer_bytes": total_transfer,
        "raw_header_objects_independently_verified": 473, "original_header_qualified_series": 5,
        "refined_header_qualified_series": 6, "label_arrays_independently_verified": 6,
        "source_preflight_series": 4, "source_preflight_patients": 2,
        "original_full_label_gate_complete": False, "original_full_label_gate_errors": 186,
        "full_public_label_coverage_certified": False, "geometry_estimator_correction_post_result": True,
        "label_available_rows": 301, "blank_label_paths": 60, "specified_T2_paths_absent": 126,
        "official_nonoverlap_labelled_T2_candidates": 71, "labelled_T2_candidate_series": 159,
        "next_batch_status": "prepared_not_executed", "next_batch_series": 8,
        "MR_pixel_arrays_decoded": False, "scientific_independent_validation_patients": 0,
        "main_contract_sha256": EXPECTED, "frozen_code_and_protocol_files_checked": frozen,
        "files": entries,
    }
    if "--write" in sys.argv:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        require(MANIFEST.is_file() and read(MANIFEST) == manifest, "Static native stage manifest differs")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"} | {"files": len(entries), "errors": errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
