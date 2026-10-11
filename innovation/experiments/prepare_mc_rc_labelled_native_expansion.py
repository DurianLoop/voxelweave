"""Freeze a labelled source follow-up list from stored evidence only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json"
API = ROOT / "literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response"
PLAN = ROOT / "MC_RC_LABELLED_NATIVE_EXPANSION_PREPARATION_2026-10-02.md"
OUT = SOURCE.with_name("labelled_native_expansion_preparation.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    api = {r["SeriesInstanceUID"]: r for r in json.loads(API.read_text(encoding="utf-8"))}
    candidates = sorted(
        (r for r in source["availability"]["rows"] if r["patient"].startswith("VS-MC-RC-")
         and r["description"].startswith("_T2_") and r["availability"] == "available"),
        key=lambda r: (r["patient"], r["study"], r["uid"]),
    )
    preflight = ["VS-MC-RC-001", "VS-MC-RC-002", "VS-MC-RC-003"]
    patients = sorted({r["patient"] for r in candidates})
    selected_patients = sorted(set(patients) - set(preflight))[:3]
    selected = [r for r in candidates if r["patient"] in selected_patients]
    assert len(candidates) == 159 and len(patients) == 71
    assert selected_patients == ["VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"] and len(selected) == 8
    for r in candidates:
        a = api[r["uid"]]
        assert a["PatientID"] == r["patient"] and a["StudyInstanceUID"] == r["study"]
    result = {
        "status": "prepared_not_executed",
        "script_sha256": sha(__file__), "plan_sha256": sha(PLAN),
        "availability_result_sha256": sha(SOURCE), "api_sha256": sha(API),
        "scope": "stored exact-UID labelled-source preparation; no network or pixel decoding",
        "candidate_patients": patients, "candidate_series": candidates,
        "preflight_or_development_patients_not_new_method_confirmation": preflight,
        "selection_rule": "first three sorted labelled candidate patient IDs after excluding prior preflight patients; all labelled T2 series",
        "next_batch_patient_ids": selected_patients,
        "next_batch_series": [{"availability": r, "source": api[r["uid"]]} for r in selected],
        "next_batch_API_ImageCount": sum(api[r["uid"]]["ImageCount"] for r in selected),
        "next_batch_API_FileSize": sum(api[r["uid"]]["FileSize"] for r in selected),
        "network_requests_made": 0, "MR_pixel_arrays_decoded": False,
        "new_label_arrays_decoded": False, "scientific_independent_validation_patients": 0,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "candidate_patients": len(patients),
                      "candidate_series": len(candidates), "next_batch_patients": selected_patients,
                      "next_batch_series": len(selected), "network_requests_made": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
