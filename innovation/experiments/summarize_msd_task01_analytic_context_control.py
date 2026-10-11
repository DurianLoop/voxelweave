"""Summarize the complete post-result analytic control and paired neural contrast."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np

from msd_task01_source import ROOT, sha256


PROTOCOL = ROOT / "MSD_TASK01_ANALYTIC_CONTEXT_CONTROL_PROTOCOL_2026-10-01.md"
LABELS = ROOT / "experiments/msd_task01_label_qualification.json"
NEURAL = ROOT / "experiments/msd_task01_tumor_roi_context"
RUN = ROOT / "experiments/msd_task01_analytic_context_control"
OUT = RUN / "summary.json"


def interval(values: np.ndarray, indices: np.ndarray) -> list[float]:
    return [float(v) for v in np.percentile(values[indices].mean(axis=1), [2.5, 97.5])]


def check_region(region: dict) -> None:
    if region["pixels"] < 1:
        raise ValueError("Empty ROI")
    for condition in ("shared", "disjoint"):
        item = region[condition]
        if not np.isclose(item["paired_mse"], (item["a_mse"] + item["b_mse"]) / 2):
            raise ValueError("Paired MSE identity failed")
        if not np.isclose(item["observable"],
                          item["disagreement_mse"] / (4 * item["paired_mse"])):
            raise ValueError("Observable identity failed")
    if not np.isclose(region["shared"]["a_mse"], region["disjoint"]["a_mse"]):
        raise ValueError("Fixed reference changed")
    if not np.isclose(region["delta_o"],
                      region["disjoint"]["observable"] - region["shared"]["observable"]):
        raise ValueError("Delta O identity failed")


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite analytic control summary")
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    contract_path = RUN / "run_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if (labels["cases_attempted"] != 484 or contract["attempted_cases"] != 484 or
            contract["protocol_sha256"] != sha256(PROTOCOL) or
            contract["label_qualification_sha256"] != sha256(LABELS) or
            contract["neural_summary_sha256"] != sha256(NEURAL / "summary.json")):
        raise ValueError("Frozen control contract changed")
    if len(list((RUN / "cases").glob("BRATS_*.json"))) != 484:
        raise ValueError("Analytic control does not have 484 attempt records")
    complete, failed, paired = [], [], []
    for label in labels["records"]:
        scan = label["scan"]
        case = json.loads((RUN / "cases" / f"{scan}.json").read_text(encoding="utf-8"))
        if case["scan"] != scan or case["run_contract_sha256"] != sha256(contract_path):
            raise ValueError(f"Case contract mismatch: {scan}")
        if not case["complete"]:
            failed.append(case)
            continue
        rows = case["rows"]
        neural = json.loads((NEURAL / "cases" / f"{scan}.json").read_text(encoding="utf-8"))
        if not neural["complete"] or case["targets"] != neural["targets"] or len(rows) != 4:
            raise ValueError(f"Analytic/neural target mismatch: {scan}")
        for row, neural_row in zip(rows, neural["rows"]):
            if (row["z"] != neural_row["z"] or row["residue"] != neural_row["residue"] or
                    row["lesion"]["pixels"] != neural_row["lesion"]["pixels"] or
                    row["local_control"]["pixels"] != neural_row["local_control"]["pixels"] or
                    row["full_support_pixels"] != neural_row["full_support"]["pixels"]):
                raise ValueError(f"Analytic/neural ROI mismatch: {scan}")
            for region in ("lesion", "local_control"):
                check_region(row[region])
        entry = case["summary"]
        if not np.isclose(entry["lesion_minus_local_delta_o"],
                          entry["lesion_delta_o"] - entry["local_delta_o"]):
            raise ValueError(f"Patient contrast mismatch: {scan}")
        complete.append(entry)
        paired.append(neural["summary"]["delta_o_lesion_minus_local"])
    if not complete:
        raise ValueError("No complete control cases")
    lesion = np.asarray([row["lesion_delta_o"] for row in complete])
    local = np.asarray([row["local_delta_o"] for row in complete])
    contrast = lesion - local
    neural_contrast = np.asarray(paired)
    rng = np.random.default_rng(20261006)
    indices = rng.integers(0, len(complete), size=(5000, len(complete)))
    result = {"classification": "post-result exploratory falsification control",
              "protocol_sha256": sha256(PROTOCOL), "run_contract_sha256": sha256(contract_path),
              "cases_attempted": 484, "cases_complete": len(complete),
              "targets_complete": 4 * len(complete),
              "failed_case_ids": [case["scan"] for case in failed],
              "failure_counts": dict(Counter(case["failure_stage"] + ":" + case["failure_type"]
                                             for case in failed)),
              "analytic_lesion_delta_o": float(lesion.mean()),
              "analytic_lesion_delta_o_ci95": interval(lesion, indices),
              "analytic_local_delta_o": float(local.mean()),
              "analytic_local_delta_o_ci95": interval(local, indices),
              "analytic_lesion_minus_local_delta_o": float(contrast.mean()),
              "analytic_lesion_minus_local_ci95": interval(contrast, indices),
              "analytic_positive_lesion_cases": int((lesion > 0).sum()),
              "analytic_positive_specificity_cases": int((contrast > 0).sum()),
              "analytic_fixed_denominator_lesion_delta_o": float(np.mean([
                  row["fixed_denominator_lesion_delta_o"] for row in complete])),
              "analytic_fixed_denominator_local_delta_o": float(np.mean([
                  row["fixed_denominator_local_delta_o"] for row in complete])),
              "neural_contrast_on_same_complete_cases": float(neural_contrast.mean()),
              "neural_minus_analytic_contrast": float((neural_contrast - contrast).mean()),
              "neural_minus_analytic_contrast_ci95":
                  interval(neural_contrast - contrast, indices),
              "gpu_used": False}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
