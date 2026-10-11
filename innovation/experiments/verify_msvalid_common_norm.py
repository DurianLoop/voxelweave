"""Read-only reconstruction of the exploratory common-normalization summary."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from msvalid_mira_confirmation import sha256


ROOT = Path(__file__).resolve().parents[2] / "innovation"
OUT = ROOT / "experiments/msvalid_common_norm"
PLAN = ROOT / "MSVALID_COMMON_NORM_PLAN_2026-09-30.md"
SCRIPT = ROOT / "experiments/msvalid_common_norm.py"
ORIGINAL = ROOT / "experiments/msvalid_mira_confirmation/per_patient.csv"


def close(actual: float, expected: float, label: str) -> None:
    if not np.isclose(actual, expected, atol=1e-10, rtol=0):
        raise AssertionError(f"{label}: {actual} != {expected}")


def main() -> None:
    result = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    if result["plan_sha256"] != sha256(PLAN) or result["script_sha256"] != sha256(SCRIPT):
        raise AssertionError("Plan or script hash changed")
    if result["original_per_patient_sha256"] != sha256(ORIGINAL):
        raise AssertionError("Original results changed")
    with (OUT / "per_target.csv").open(newline="", encoding="utf-8") as stream:
        targets = list(csv.DictReader(stream))
    with (OUT / "per_patient.csv").open(newline="", encoding="utf-8") as stream:
        patients = list(csv.DictReader(stream))
    if len(targets) != result["targets"] != 479 or len(patients) != result["patients"] != 84:
        raise AssertionError("Patient/target count mismatch")
    by_patient = defaultdict(list)
    for row in targets:
        by_patient[row["patient"]].append(row)
        close(float(row["delta_o"]), float(row["disjoint_o"]) - float(row["shared_o"]),
              "target delta")
    keys = ("shared_o", "disjoint_o", "delta_o", "shared_b_mae", "disjoint_b_mae")
    for patient in patients:
        rows = by_patient[patient["patient"]]
        if len(rows) != int(patient["targets"]):
            raise AssertionError("Patient target count mismatch")
        for key in keys:
            actual = np.mean([np.mean([float(row[key]) for row in rows
                                       if int(row["residue"]) == residue])
                              for residue in (1, 3)])
            close(float(actual), float(patient[key]), f"{patient['patient']} {key}")
    for key in keys:
        close(float(np.mean([float(p[key]) for p in patients])), float(result[f"mean_{key}"]),
              f"result mean {key}")
    values = np.array([float(p["delta_o"]) for p in patients])
    ci = np.percentile(values[np.random.default_rng(20261002).integers(0, 84, (5000, 84))]
                       .mean(axis=1), [2.5, 97.5])
    for i in (0, 1):
        close(float(ci[i]), float(result["ci95_exploratory"][i]), f"CI {i}")
    if int((values > 0).sum()) != result["positive_patients"] or int((values < 0).sum()) != result["negative_patients"]:
        raise AssertionError("Patient signs mismatch")
    print(json.dumps({"patients": len(patients), "targets": len(targets),
                      "mean_delta_o": float(values.mean()), "ci95_exploratory": ci.tolist(),
                      "status": "read-only recomputation passed"}, indent=2))


if __name__ == "__main__":
    main()
