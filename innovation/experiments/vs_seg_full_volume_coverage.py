"""Post-freeze, model-independent actual support coverage of the old four-target rule."""
from __future__ import annotations
import json
import time
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_cohort import CONTRACT, cases_from_sources, verify_contract, write_json
from vs_seg_full_volume_runtime import decode_source, sha

OUT = ROOT / "experiments/vs_seg_full_volume_coverage"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    contract = verify_contract()
    import numpy as np
    rows, errors = [], []
    start = time.perf_counter()
    for case in cases_from_sources():
        if not case["main_ciss_source_qualified"]:
            continue
        try:
            resource_gate()
            volume, affine, refs = decode_source(case)
            last = (volume.shape[2] - 1) // 4 * 4
            anchors = list(range(0, volume.shape[2], 4))
            support = {}
            for z in range(1, last):
                if not z % 4:
                    continue
                left, right = volume[:, :, z - z % 4], volume[:, :, z - z % 4 + 4]
                support[z] = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
            kinds = {}
            for key, mask in refs.items():
                candidates = {r: [z for z in support if z % 4 == r and z // 4 >= 1 and z // 4 + 2 < len(anchors)
                                  and int((mask[:, :, z] & support[z]).sum()) >= 64] for r in (1, 3)}
                picks = {}
                for r, values in candidates.items():
                    first, second = (len(values) - 1) // 3, 2 * (len(values) - 1) // 3
                    picks[str(r)] = [values[first], values[second]] if values and first != second else []
                eligible = all(len(picks[str(r)]) == 2 for r in (1, 3))
                selected = sorted(z for values in picks.values() for z in values) if eligible else []
                internal = [z for z in support if mask[:, :, z].any()]
                supported_lesion = sum(int((mask[:, :, z] & support[z]).sum()) for z in support)
                selected_lesion = sum(int((mask[:, :, z] & support[z]).sum()) for z in selected)
                kinds[key] = {"old_target_rule_eligible": eligible, "literal_old_tv_name_and_target_rule_eligible": eligible and case["first_structure"] == "TV",
                              "candidate_indices": {str(r): v for r, v in candidates.items()}, "selected_four_indices": selected,
                              "native_lesion_voxels": int(mask.sum()), "native_volume_mm3": float(mask.sum() * abs(np.linalg.det(affine[:3, :3]))),
                              "positive_native_planes": int(np.count_nonzero(mask.sum(axis=(0, 1)))),
                              "positive_internal_missing_planes": len(internal), "supported_internal_lesion_voxels": supported_lesion,
                              "selected_supported_lesion_voxels": selected_lesion,
                              "selected_fraction_of_supported_internal_lesion_voxels": selected_lesion / supported_lesion if supported_lesion else None}
            rows.append({"patient": case["patient"], "first_structure": case["first_structure"], "reference_masks_sha256": case["masks_sha256"], "labels": kinds})
            print(json.dumps({"patient": case["patient"], "eligible": {k: v["old_target_rule_eligible"] for k, v in kinds.items()}}), flush=True)
        except Exception as exc:
            errors.append({"patient": case["patient"], "error": f"{type(exc).__name__}: {exc}"})
    summaries = {}
    if len(rows) == 45 and not errors:
        for kind in ("original_json", "rtstruct"):
            selected = [r for r in rows if r["labels"][kind]["old_target_rule_eligible"]]
            excluded = [r for r in rows if not r["labels"][kind]["old_target_rule_eligible"]]
            def distribution(values):
                return {"n": len(values), "median": float(np.median(values)) if values else None,
                        "min": float(min(values)) if values else None, "max": float(max(values)) if values else None}
            summaries[kind] = {"eligible": len(selected), "excluded": len(excluded), "coverage_fraction": len(selected) / 45,
                               "literal_old_tv_name_and_target_rule_eligible": sum(r["labels"][kind]["literal_old_tv_name_and_target_rule_eligible"] for r in rows),
                               "selected_volume_mm3": distribution([r["labels"][kind]["native_volume_mm3"] for r in selected]),
                               "excluded_volume_mm3": distribution([r["labels"][kind]["native_volume_mm3"] for r in excluded]),
                               "selected_positive_planes": distribution([r["labels"][kind]["positive_native_planes"] for r in selected]),
                               "excluded_positive_planes": distribution([r["labels"][kind]["positive_native_planes"] for r in excluded]),
                               "eligible_ids": [r["patient"] for r in selected]}
    report = {"attempt": attempt, "script_sha256": sha(Path(__file__)), "contract_sha256": sha(CONTRACT),
              "fixed_main_roster": contract["main_roster"], "complete": len(rows) == 45 and not errors, "patients": rows,
              "summary": summaries, "errors": errors, "elapsed_seconds": time.perf_counter() - start,
              "model_output_used": False, "method_ranking_evaluated": False, "publication_claim": False,
              "qualification_convention": "First author-order tumor label; separately count the literal former TV name gate"}
    write_json(OUT / f"attempt_{attempt:02d}.json", report)
    print(json.dumps({"complete": report["complete"], "summary": summaries, "errors": errors}), flush=True)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
