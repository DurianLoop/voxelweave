"""Read-only cohort, aggregation and bootstrap audit of synthetic noise control."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

import msvalid_matched_geometry_noise_control as run


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def close(value: float, expected: float, name: str) -> None:
    if not np.isclose(value, expected, rtol=0, atol=1e-10):
        raise AssertionError(f"{name}: {value} != {expected}")


def main() -> None:
    out = run.OUT
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    targets = read_csv(out / "per_target.csv")
    patients = read_csv(out / "per_patient.csv")
    original = read_csv(run.MAIN_TARGETS)
    original_by_key = {(row["patient"], row["z"]): row for row in original}
    if (summary["plan_sha256"] != run.original.sha256(run.PLAN) or
            summary["script_sha256"] != run.original.sha256(Path(run.__file__)) or
            summary["original_per_target_sha256"] != run.MAIN_TARGETS_SHA256 or
            run.original.sha256(run.MAIN_TARGETS) != run.MAIN_TARGETS_SHA256):
        raise AssertionError("frozen input/script hash mismatch")
    if (summary["failures"] or summary["patients_complete"] != 84 or
            summary["targets_scored"] != 958 or len(targets) != 958 or len(patients) != 168):
        raise AssertionError("incomplete cohort")

    expected = set(original_by_key)
    grouped: dict[tuple[str, float], list[dict[str, str]]] = {}
    for level in run.LEVELS:
        rows = [row for row in targets if float(row["noise_fraction"]) == level]
        keys = [(row["patient"], row["z"]) for row in rows]
        if len(keys) != 479 or len(set(keys)) != 479 or set(keys) != expected:
            raise AssertionError(f"target list changed at noise level {level}")
    for row in targets:
        old = original_by_key[(row["patient"], row["z"])]
        if (int(row["support_pixels"]) != int(old["support_pixels"]) or
                row["residue"] != old["residue"] or
                not np.isfinite(float(row["delta_o"]))):
            raise AssertionError("fixed target support/residue/finite check failed")
        close(float(row["independent_o"]) - float(row["shared_o"]),
              float(row["delta_o"]), "target delta")
        grouped.setdefault((row["patient"], float(row["noise_fraction"])), []).append(row)

    patient_values = {level: [] for level in run.LEVELS}
    for patient in patients:
        pid, level = patient["patient"], float(patient["noise_fraction"])
        rows = grouped.pop((pid, level))
        if len(rows) != int(patient["targets"]):
            raise AssertionError(f"target count mismatch: {pid} {level}")
        for key in ("shared_o", "independent_o", "delta_o", "shared_b_mae",
                    "independent_b_mae", "a_mae"):
            residue_means = []
            for residue in (1, 3):
                values = [float(row[key]) for row in rows if int(row["residue"]) == residue]
                if not values:
                    raise AssertionError(f"missing residue: {pid} {level}")
                residue_means.append(float(np.mean(values)))
            close(float(patient[key]), float(np.mean(residue_means)), f"{pid} {level} {key}")
        patient_values[level].append(patient)
    if grouped:
        raise AssertionError("unmatched target patient/level rows")

    for index, level in enumerate(run.LEVELS):
        rows = patient_values[level]
        if len(rows) != 84 or sum(int(row["targets"]) for row in rows) != 479:
            raise AssertionError("patient count/targets changed")
        result = summary["levels"][str(level)]
        values = np.array([float(row["delta_o"]) for row in rows], dtype=np.float64)
        rng = np.random.default_rng(20261003 + index)
        indices = rng.integers(0, 84, (5000, 84))
        interval = np.percentile(values[indices].mean(axis=1), [2.5, 97.5])
        for name in ("shared_o", "independent_o", "delta_o", "shared_b_mae",
                     "independent_b_mae"):
            close(float(result[name]), float(np.mean([float(row[name]) for row in rows])), name)
        for actual, expected_limit in zip(result["ci95"], interval):
            close(float(actual), float(expected_limit), "bootstrap interval")
        if (result["positive_patients"] != int((values > 0).sum()) or
                result["negative_patients"] != int((values < 0).sum())):
            raise AssertionError("patient direction counts changed")
        print(f"PASS level={level:.2%}: 84 patients, 479 targets, "
              f"delta={values.mean():.6f}, CI={result['ci95']}")


if __name__ == "__main__":
    main()
