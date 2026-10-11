"""Independently derive all eligible planes with vectorized support and patient summaries."""
from __future__ import annotations
import json
import statistics
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_cohort import CONTRACT, cases_from_sources, verify_contract, write_json
from vs_seg_full_volume_runtime import decode_source, sha

OUT = ROOT / "experiments/vs_seg_full_volume_coverage"


def main():
    verify_contract()
    import numpy as np
    source = OUT / "attempt_01.json"
    report = json.loads(source.read_text())
    by_patient = {r["patient"]: r for r in report["patients"]}
    errors, checks = [], []
    if not report["complete"] or report["errors"] or len(by_patient) != 45:
        errors.append("Source coverage result incomplete")
    for case in cases_from_sources():
        if not case["main_ciss_source_qualified"]:
            continue
        resource_gate()
        volume, affine, refs = decode_source(case)
        depth = volume.shape[2]
        targets = np.array([z for z in range(5, ((depth - 1) // 4 - 1) * 4) if z % 4 in (1, 3)])
        lower_indices = targets - targets % 4
        left, right = volume[:, :, lower_indices], volume[:, :, lower_indices + 4]
        threshold_l = np.maximum(np.abs(left).max(axis=(0, 1)).astype(np.float64), 1e-6) * .01
        threshold_r = np.maximum(np.abs(right).max(axis=(0, 1)).astype(np.float64), 1e-6) * .01
        support = (np.abs(left) > threshold_l) | (np.abs(right) > threshold_r)
        for key, label in refs.items():
            counts = (support & label[:, :, targets]).sum(axis=(0, 1))
            eligible = {str(r): targets[(targets % 4 == r) & (counts >= 64)].tolist() for r in (1, 3)}
            saved = by_patient[case["patient"]]["labels"][key]
            if eligible != saved["candidate_indices"]:
                errors.append(case["patient"] + "/" + key + " independently vectorized candidate set differs")
            qualified = min(len(v) for v in eligible.values()) >= 3
            if qualified != saved["old_target_rule_eligible"]:
                errors.append(case["patient"] + "/" + key + " eligibility differs")
            selected = sorted(v[(len(v) - 1) // 3] for v in eligible.values()) + sorted(v[2 * (len(v) - 1) // 3] for v in eligible.values()) if qualified else []
            if sorted(selected) != saved["selected_four_indices"]:
                errors.append(case["patient"] + "/" + key + " chosen four targets differ")
        checks.append(case["patient"])
    for key in ("original_json", "rtstruct"):
        rows = [r["labels"][key] for r in report["patients"]]
        for flag, summary_key in ((True, "selected_volume_mm3"), (False, "excluded_volume_mm3")):
            values = sorted(r["native_volume_mm3"] for r in rows if r["old_target_rule_eligible"] is flag)
            saved = report["summary"][key][summary_key]
            if len(values) != saved["n"] or statistics.median(values) != saved["median"] or values[0] != saved["min"] or values[-1] != saved["max"]:
                errors.append(key + " volume distribution differs")
    proof = {"source_result_sha256": sha(source), "script_sha256": sha(Path(__file__)), "contract_sha256": sha(CONTRACT),
             "checked_patients": checks, "errors": errors, "model_output_used": False,
             "method": "Independent batched support counts and sorted patient median", "complete": len(checks) == 45 and not errors}
    write_json(OUT / "independent_verification.json", proof)
    print(json.dumps({"checked_patients": len(checks), "errors": errors, "complete": proof["complete"]}))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
