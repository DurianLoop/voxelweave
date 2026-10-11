"""Independently replay the fixed-denominator CSV analysis without model inference."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/fixed_denominator_two_source"
PLAN = ROOT / "FIXED_DENOMINATOR_TWO_SOURCE_PLAN_2026-10-01.md"
SCRIPT = ROOT / "experiments/fixed_denominator_two_source.py"
INPUTS = {
    "msvalid": ROOT / "experiments/msvalid_ixi_weights_secondary/per_target.csv",
    "remind": ROOT / "experiments/remind_native_t2_ixi_pair/per_target.csv",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def near(actual: float, expected: float, label: str) -> None:
    if not np.isclose(actual, expected, rtol=0, atol=1e-10):
        raise AssertionError(f"{label}: {actual} != {expected}")


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    if summary["plan_sha256"] != sha256(PLAN) or summary["script_sha256"] != sha256(SCRIPT):
        raise AssertionError("plan or script hash changed")
    output_targets = rows(OUT / "per_target.csv")
    output_patients = rows(OUT / "per_patient.csv")
    if len(output_targets) != 727 or len(output_patients) != 146:
        raise AssertionError("combined row count changed")

    for source, path in INPUTS.items():
        if sha256(path) != summary["source_hashes"][source]["per_target.csv"]:
            raise AssertionError(f"{source} source CSV changed")
        input_rows = {(row["patient"], row["z"]): row for row in rows(path)}
        targets = [row for row in output_targets if row["source"] == source]
        patients = [row for row in output_patients if row["source"] == source]
        result = summary["results"][source]
        if len(input_rows) != result["targets"] or len(targets) != result["targets"]:
            raise AssertionError(f"{source} target count changed")
        if len(patients) != result["patients"] or len({r["patient"] for r in patients}) != len(patients):
            raise AssertionError(f"{source} patient count changed")
        if {(r["patient"], r["z"]) for r in targets} != set(input_rows):
            raise AssertionError(f"{source} target keys changed")

        grouped = defaultdict(lambda: {1: [], 3: []})
        for row in targets:
            raw = input_rows[(row["patient"], row["z"])]
            s_t = Decimal(raw["shared_paired_mse"])
            d_t = Decimal(raw["disjoint_paired_mse"])
            s_o = Decimal(raw["shared_observable"])
            d_o = Decimal(raw["disjoint_observable"])
            expected = (d_o * d_t / s_t) - s_o
            near(float(row["delta_q"]), float(expected), "target delta Q")
            near(float(row["disjoint_d"]), float(4 * d_t * d_o), "target disjoint D")
            near(float(row["shared_d"]), float(4 * s_t * s_o), "target shared D")
            grouped[row["patient"]][int(row["residue"])].append(float(expected))

        values = []
        for row in patients:
            residue = grouped.pop(row["patient"])
            if not residue[1] or not residue[3]:
                raise AssertionError(f"{source} missing residue")
            expected = (np.mean(residue[1]) + np.mean(residue[3])) / 2
            near(float(row["delta_q"]), float(expected), "patient delta Q")
            values.append(float(expected))
        if grouped:
            raise AssertionError(f"{source} unmatched patients")
        near(float(np.mean(values)), result["mean_delta_q"], "summary delta Q")
        if (sum(value > 0 for value in values) != result["positive_patients"] or
                sum(float(row["delta_q"]) > 0 for row in targets) != result["positive_targets"]):
            raise AssertionError(f"{source} sign counts changed")

        rng = np.random.default_rng(20261001 if source == "msvalid" else 20261002)
        if source == "msvalid":
            arr = np.asarray(values)
            draws = arr[rng.integers(0, len(arr), (5000, len(arr)))].mean(axis=1)
        else:
            draws = np.zeros(5000)
            for group, count in (("2D_AX_T2", 35), ("2D_AX_T2_BLADE", 27)):
                arr = np.asarray([float(p["delta_q"]) for p in patients if p["group"] == group])
                if len(arr) != count:
                    raise AssertionError(f"{group} count changed")
                draws += count / 62 * arr[rng.integers(0, count, (5000, count))].mean(axis=1)
        for actual, expected in zip(result["ci95_delta_q"], np.percentile(draws, [2.5, 97.5])):
            near(actual, float(expected), "bootstrap interval")
        print(f"PASS {source}: {len(patients)} patients, {len(targets)} targets, "
              f"delta Q={result['mean_delta_q']:.9f}")


if __name__ == "__main__":
    main()
