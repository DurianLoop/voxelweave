"""Post-result descriptive fixed-mixture arithmetic and stored-source-only preparation."""
from __future__ import annotations

import json
import math
from pathlib import Path
from vs_seg_full_volume_runtime import ROOT, sha

OUT = ROOT / "experiments/mc_rc_three_development_action_oracle"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    result = read(OUT / "attempt_01.json")
    proof = read(OUT / "independent_numerical_and_forward_verification.json")
    if not result["complete"] or proof["errors"] or proof["result_sha256"] != sha(OUT / "attempt_01.json"):
        raise ValueError("Complete independently checked developer result required")
    rows = []
    for p in result["patients"]:
        for a in p["actions"]:
            summaries = a["summaries"]
            fixed = {name: value["support"]["target_equal_nmse"] for name, value in summaries.items() if name.startswith("fixed_")}
            name = min(fixed, key=fixed.get)
            rows.append({"patient": p["patient"], "base": a["base"], "endpoint_oracle_gain_db": a["support_gain_db_vs_better_fixed"],
                         "best_prespecified_constant_name_using_reference": name, "best_constant_support_nmse": fixed[name],
                         "tile_oracle_support_nmse": summaries["tile_32_oracle"]["support"]["target_equal_nmse"],
                         "oracle_gain_over_best_prespecified_constant_db": 10 * math.log10(fixed[name] / summaries["tile_32_oracle"]["support"]["target_equal_nmse"]),
                         "lesion_relative_change_percent_vs_endpointwise_best": {key: (summaries["tile_32_oracle"]["lesion"][key] / min(summaries["fixed_0"]["lesion"][key], summaries["fixed_1"]["lesion"][key]) - 1) * 100 for key in ("target_equal_nmse", "pixel_weighted_nmse")}})
    write(OUT / "fixed_mixture_comparison.json", {"script_sha256": sha(__file__), "result_sha256": sha(OUT / "attempt_01.json"), "scope": "post-result descriptive arithmetic; both per-patient best constant and tile oracle use hidden reference; no gate changes", "rows": rows})
    first = ROOT / "literature/source_cache/mc_rc_three_patient_headers_2026-10-02/attempt_01.json"
    refined_path = ROOT / "experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json"
    first_proof_path = refined_path.with_name("independent_raw_geometry_grid_verification.json")
    first_labels_path = refined_path.with_name("label_grid_attempt_01.json")
    source, refined, source_proof, labels = read(first), read(refined_path), read(first_proof_path), read(first_labels_path)
    if source_proof["errors"] or source_proof["refined_result_sha256"] != sha(refined_path):
        raise ValueError("Existing first-batch source proof differs")
    eligible = {r["uid"]: r for r in refined["series"] if r["refined_header_and_label_grid_passed"]}
    by_label = {r["series_uid"]: r for r in labels["series"]}
    selected = []
    for patient in ("VS-MC-RC-001", "VS-MC-RC-002"):
        candidates = [r for r in source["series"] if r["source"]["PatientID"] == patient and r["source"]["SeriesInstanceUID"] in eligible]
        chosen = sorted(candidates, key=lambda r: (r["source"]["StudyDate"], r["source"]["SeriesInstanceUID"]))[0]
        uid = chosen["source"]["SeriesInstanceUID"]
        selected.append({"patient": patient, "role": "previously declared preflight/development; not new-method confirmation", "header_row": chosen,
                         "refined_source_geometry": eligible[uid], "label_row": by_label[uid]})
    plan = ROOT / "MC_RC_RAW_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md"
    write(OUT / "next_development_followup_preparation.json", {
        "status": "prepared_not_executed", "script_sha256": sha(__file__), "plan_sha256": sha(plan),
        "scope": "post-result raw-branch development selection; stored exact-UID sources only; no new MR decoding or model run",
        "selection_rule": "earliest StudyDate/UID among already header+grid qualified series for each predeclared developer001/002",
        "selected": selected, "source_header_sha256": sha(first), "source_refined_sha256": sha(refined_path),
        "source_label_result_sha256": sha(first_labels_path), "source_proof_sha256": sha(first_proof_path),
        "three_patient_action_result_sha256": sha(OUT / "attempt_01.json"),
        "original_pipeline_primary_gate_passed": False, "network_requests_made": 0, "new_MR_arrays_decoded": False,
        "scientific_independent_validation_patients": 0,
    })
    print(json.dumps({"complete": True, "rows": len(rows), "next_development_patients": [r["patient"] for r in selected], "status": "prepared_not_executed", "original_pipeline_primary_gate_passed": False}))


if __name__ == "__main__":
    main()
