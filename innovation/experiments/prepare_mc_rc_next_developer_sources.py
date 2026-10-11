"""Source-only fixed expansion preparation from authenticated stored metadata."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json"
API = ROOT / "literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response"
PLAN = ROOT / "MC_RC_NEXT_DEVELOPER_SOURCE_PREPARATION_PLAN_2026-10-02.md"
OUT = ROOT / "experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json"

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    api = {r["SeriesInstanceUID"]: r for r in json.loads(API.read_text(encoding="utf-8"))}
    candidates = sorted((r for r in source["availability"]["rows"] if r["patient"].startswith("VS-MC-RC-") and r["description"].startswith("_T2_") and r["availability"] == "available"), key=lambda r: (r["patient"], r["study"], r["uid"]))
    patient_ids = sorted({r["patient"] for r in candidates})
    previous = [f"VS-MC-RC-{i:03d}" for i in range(1, 7)]
    selected = sorted(set(patient_ids) - set(previous))[:3]
    if len(patient_ids) != 71 or len(candidates) != 159 or selected != ["VS-MC-RC-007", "VS-MC-RC-009", "VS-MC-RC-010"]:
        raise ValueError("Frozen source-only selection scope differs")
    rows = []
    for r in candidates:
        if r["patient"] not in selected:
            continue
        a = api[r["uid"]]
        if a["PatientID"] != r["patient"] or a["StudyInstanceUID"] != r["study"]:
            raise ValueError("Exact UID identity differs")
        rows.append({"availability": r, "source": a})
    result = {"status": "prepared_not_executed", "script_sha256": sha(__file__), "plan_sha256": sha(PLAN), "availability_result_sha256": sha(SOURCE), "api_sha256": sha(API),
              "scope": "stored source metadata only; all selected patients/times assigned to development", "candidate_patients": len(patient_ids), "candidate_series": len(candidates), "previous_source_or_developer_patients": previous,
              "next_batch_patient_ids": selected, "next_batch_series": rows, "next_batch_API_ImageCount": sum(r["source"]["ImageCount"] for r in rows), "next_batch_API_FileSize": sum(r["source"]["FileSize"] for r in rows),
              "selection_rule": "first three sorted labelled patients after excluding001-006, all labelled T2 series", "network_requests_made": 0, "new_MR_arrays_decoded": False, "new_label_arrays_decoded": False, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False}
    if OUT.exists():
        raise ValueError("Refuse to overwrite fixed preparation")
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "next_batch_patient_ids", "next_batch_API_ImageCount", "next_batch_API_FileSize", "network_requests_made")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
