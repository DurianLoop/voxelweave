"""Describe the frozen UPENN context run without changing its primary endpoint."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


OUT = Path(__file__).resolve().parent / "upenn_gbm_processed_t2_context"


def read_csv(name: str) -> list[dict]:
    with (OUT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def mean(rows: list[dict], key: str) -> float | None:
    return float(np.mean([float(row[key]) for row in rows])) if rows else None


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    patients = read_csv("per_patient.csv")
    targets = read_csv("per_target.csv")
    if len(patients) != summary["patients_scored"] or len(targets) != summary["targets_scored"]:
        raise ValueError("Frozen run and CSV counts disagree")
    by_spacing = defaultdict(list)
    for row in patients:
        by_spacing[f"{float(row['z_spacing_mm']):.1f} mm"].append(row)
    columns = ("shared_observable", "disjoint_observable", "delta_o",
               "shared_a_mae", "shared_b_mae", "disjoint_b_mae",
               "shared_paired_mse", "disjoint_paired_mse",
               "residue_1_delta_o", "residue_3_delta_o")
    patient_means = {key: mean(patients, key) for key in columns}
    target_columns = ("shared_a_mse", "shared_b_mse", "disjoint_b_mse",
                      "shared_a_mae", "shared_b_mae", "disjoint_b_mae")
    target_means = {key: mean(targets, key) for key in target_columns}
    values = np.asarray([float(row["delta_o"]) for row in patients], dtype=float)
    report = {
        "status": "descriptive_postresult_not_primary",
        "attempted_patients": summary["patients_expected"],
        "complete_patients": len(patients),
        "targets": len(targets),
        "failure_stages": dict(Counter(item["stage"] for item in summary["failures"])),
        "positive_patients": int((values > 0).sum()),
        "negative_patients": int((values < 0).sum()),
        "zero_patients": int((values == 0).sum()),
        "patient_mean": patient_means,
        "target_mean": target_means,
        "patient_delta_o_quantiles": {str(q): float(np.quantile(values, q))
                                       for q in (0, .05, .25, .5, .75, .95, 1)},
        "by_physical_spacing": {
            spacing: {"patients": len(rows), "mean_delta_o": mean(rows, "delta_o"),
                      "positive_patients": sum(float(row["delta_o"]) > 0 for row in rows)}
            for spacing, rows in sorted(by_spacing.items())},
    }
    path = OUT / "descriptive_summary.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
