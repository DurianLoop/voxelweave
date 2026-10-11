"""Exercise the frozen analysis gate using synthetic values, never real cohort outputs."""
from __future__ import annotations
import json
from pathlib import Path

import vs_seg_full_volume_cohort as cohort
from vs_seg_full_volume_runtime import sha

OUT = cohort.ROOT / "experiments/vs_seg_full_volume_analysis_dryrun"


def main():
    cohort.verify_contract()
    OUT.mkdir(parents=True, exist_ok=True)
    contract = {"main_roster": [f"synthetic_{i:02d}" for i in range(45)], "secondary_roster": ["synthetic_tse"]}
    checks, errors = [], []
    real_out = cohort.OUT
    real_reader = cohort.successful_conditions
    try:
        for name, image_delta, dice_delta, missing_last, expected in (
                ("two_negative_complete", -.001, -.01, False, True),
                ("image_improves_task_improves", -.001, .01, False, False),
                ("task_declines_image_declines", .001, -.01, False, False),
                ("incomplete_primary", -.001, -.01, True, None)):
            def synthetic_reader(patient, contract_sha):
                records = {}
                for condition in cohort.CONDITIONS:
                    if missing_last and patient == "synthetic_44" and condition == "hat":
                        continue
                    dice = .8 + (dice_delta if condition == "hat" else 0)
                    image = .005 + (image_delta if condition == "hat" else 0)
                    task = {ref: {domain: {"dice": None if domain == "exclude_reference_boundary_1mm" else dice}
                                 for domain in ("full", "observed_anchor_slab", "exclude_reference_boundary_1mm")}
                            for ref in ("original_json", "rtstruct")}
                    records[condition] = {"condition": condition, "image_metrics": {"support": {"target_equal_nmse": image}}, "task_metrics": task}
                return records
            cohort.OUT = OUT / name
            cohort.successful_conditions = synthetic_reader
            result = cohort.status(contract)
            actual = result.get("fixed_primary_joint_direction_supported")
            if actual != expected:
                errors.append(name + ": primary gate differs from expected")
            if missing_last and "analysis" in result:
                errors.append("Incomplete primary denominator generated inferential results")
            if not missing_last:
                descriptions = result["analysis"]["descriptive_secondary_pairs"]
                if len(descriptions) != 8 or any(x["task_sensitivity"]["original_json/exclude_reference_boundary_1mm"]["undefined_count"] != 45 for x in descriptions):
                    errors.append("Secondary family/undefined handling incorrect")
            checks.append({"scenario": name, "expected_joint_support": expected, "actual_joint_support": actual,
                           "main_complete": result["main_complete"]})
    finally:
        cohort.OUT = real_out
        cohort.successful_conditions = real_reader
    report = {"script_sha256": sha(Path(__file__)), "cohort_script_sha256": sha(Path(cohort.__file__)),
              "synthetic_data_only": True, "actual_patient_outputs_read": False, "checks": checks, "errors": errors,
              "complete": not errors}
    cohort.write_json(OUT / "result.json", report)
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
