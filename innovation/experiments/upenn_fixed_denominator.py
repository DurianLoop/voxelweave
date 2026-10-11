"""CPU-only fixed-denominator sensitivity from frozen UPENN target metrics."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "experiments" / "upenn_gbm_processed_t2_context"
OUTPUT = ROOT / "experiments" / "upenn_fixed_denominator"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUTPUT}")
    paths = {name: INPUT / name for name in ("per_target.csv", "per_patient.csv", "summary.json")}
    hashes = {name: sha256(path) for name, path in paths.items()}
    source_summary = json.loads(paths["summary.json"].read_text(encoding="utf-8"))
    with paths["per_target.csv"].open(newline="", encoding="utf-8") as stream:
        source_targets = list(csv.DictReader(stream))
    with paths["per_patient.csv"].open(newline="", encoding="utf-8") as stream:
        source_patients = {row["patient"]: row for row in csv.DictReader(stream)}
    if len(source_targets) != 1496 or len(source_patients) != 374:
        raise ValueError("Unexpected source cohort")
    rows = []
    grouped = defaultdict(lambda: defaultdict(list))
    for row in source_targets:
        patient, residue = row["patient"], int(row["residue"])
        ts = float(row["shared_paired_mse"])
        td = float(row["disjoint_paired_mse"])
        ds = float(row["shared_disagreement_mse"])
        dd = float(row["disjoint_disagreement_mse"])
        if not all(math.isfinite(x) and x > 0 for x in (ts, td, ds, dd)):
            raise ValueError("Invalid archived per-target metric")
        qs, qd = ds / (4 * ts), dd / (4 * ts)
        original = float(row["delta_o"])
        if (not math.isclose(qs, float(row["shared_observable"]), abs_tol=1e-12)
                or not math.isclose(dd / (4 * td), float(row["disjoint_observable"]), abs_tol=1e-12)
                or not math.isclose(dd / (4 * td) - qs, original, abs_tol=1e-12)):
            raise ValueError("Archived O formula mismatch")
        result = {"patient": patient, "z": row["z"], "residue": residue,
                  "shared_q": qs, "disjoint_q": qd, "delta_q": qd - qs,
                  "original_delta_o": original}
        rows.append(result)
        grouped[patient][residue].append(result)
    patient_rows = []
    for patient, residues in sorted(grouped.items()):
        if set(residues) != {1, 3} or any(len(items) != 2 for items in residues.values()):
            raise ValueError(f"Unexpected targets for {patient}")
        means = {}
        for key in ("shared_q", "disjoint_q", "delta_q", "original_delta_o"):
            means[key] = float(np.mean([np.mean([item[key] for item in residues[r]]) for r in (1, 3)]))
        if not math.isclose(means["original_delta_o"], float(source_patients[patient]["delta_o"]), abs_tol=1e-12):
            raise ValueError(f"Original patient delta mismatch: {patient}")
        patient_rows.append({"patient": patient, **means})
    values = np.array([row["delta_q"] for row in patient_rows])
    original_mean = float(np.mean([row["original_delta_o"] for row in patient_rows]))
    if not math.isclose(original_mean, source_summary["mean_delta_o"], abs_tol=1e-12):
        raise ValueError("Original cohort delta mismatch")
    rng = np.random.default_rng(20261001)
    boot = values[rng.integers(0, len(values), size=(5000, len(values)))].mean(axis=1)
    result = {
        "status": "post_result_algebraic_sensitivity_not_independent_confirmation",
        "input_sha256": hashes,
        "patients": len(patient_rows), "targets": len(rows),
        "shared_q": float(np.mean([row["shared_q"] for row in patient_rows])),
        "disjoint_q": float(np.mean([row["disjoint_q"] for row in patient_rows])),
        "mean_delta_q": float(values.mean()),
        "ci95_delta_q": [float(x) for x in np.quantile(boot, [0.025, 0.975])],
        "positive_patients": int(np.count_nonzero(values > 0)),
        "positive_targets": sum(row["delta_q"] > 0 for row in rows),
        "original_mean_delta_o": original_mean,
        "patient_bootstrap_draws": 5000,
        "bootstrap_seed": 20261001,
        "patient_pixels_read": False,
        "gpu_used": False,
    }
    OUTPUT.mkdir(parents=True)
    with (OUTPUT / "per_target.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (OUTPUT / "per_patient.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(patient_rows[0]))
        writer.writeheader()
        writer.writerows(patient_rows)
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
