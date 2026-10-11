"""Read-only target, patient, and interval audit of the linear-partner control."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from public_linear_partner_control import EXPECTED_MAIN, INNOVATION, OUT, PLAN, msvalid


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def close(actual: float, expected: float, label: str, atol: float = 1e-10) -> None:
    if not np.isclose(actual, expected, rtol=0, atol=atol):
        raise AssertionError(f"{label}: {actual} != {expected}")


def verify(source: str) -> None:
    result = OUT / source
    summary = json.loads((result / "summary.json").read_text(encoding="utf-8"))
    targets = read_csv(result / "per_target.csv")
    patients = read_csv(result / "per_patient.csv")
    original_folder = ("msvalid_ixi_weights_secondary" if source == "msvalid"
                       else "remind_native_t2_ixi_pair")
    original_path = INNOVATION / "experiments" / original_folder / "per_target.csv"
    original = read_csv(original_path)
    original_by_key = {(row["patient"], row["z"]): row for row in original}
    keys = [(row["patient"], row["z"]) for row in targets]
    if (len(keys) != len(set(keys)) or set(keys) != set(original_by_key) or
            (len(patients), len(targets)) != ((84, 479) if source == "msvalid" else (62, 248))):
        raise AssertionError(f"{source} target/patient population changed")
    if (summary["plan_sha256"] != msvalid.sha256(PLAN) or
            summary["original_per_target_sha256"] != EXPECTED_MAIN[source] or
            msvalid.sha256(original_path) != EXPECTED_MAIN[source]):
        raise AssertionError(f"{source} frozen input hash mismatch")

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in targets:
        old = original_by_key[(row["patient"], row["z"])]
        if (int(row["support_pixels"]) != int(old["support_pixels"]) or
                row["residue"] != old["residue"]):
            raise AssertionError("fixed target support/residue changed")
        close(float(row["a_mae"]), float(old["shared_a_mae"]), "HAT replay", 1e-5)
        close(float(row["disjoint_o"]) - float(row["shared_o"]),
              float(row["delta_o"]), "target contrast")
        grouped.setdefault(row["patient"], []).append(row)

    for patient in patients:
        pid = patient["patient"]
        rows = grouped.pop(pid)
        if int(patient["targets"]) != len(rows) or len({row["group"] for row in rows}) != 1:
            raise AssertionError(f"patient grouping changed: {pid}")
        for key in ("shared_o", "disjoint_o", "delta_o", "a_mae", "shared_b_mae",
                    "disjoint_b_mae", "shared_b_mse", "disjoint_b_mse"):
            residue_means = [np.mean([float(row[key]) for row in rows
                                      if int(row["residue"]) == residue])
                             for residue in (1, 3)]
            if not all(np.isfinite(residue_means)):
                raise AssertionError(f"missing residue: {pid}")
            close(float(patient[key]), float(np.mean(residue_means)), f"{pid} {key}")
    if grouped:
        raise AssertionError(f"unmatched patients: {sorted(grouped)}")

    values = np.array([float(row["delta_o"]) for row in patients])
    rng = np.random.default_rng(20261001 if source == "msvalid" else 20261002)
    if source == "msvalid":
        indices = rng.integers(0, len(values), (5000, len(values)))
        draws = values[indices].mean(axis=1)
        groups = {"MSValid": 84}
    else:
        draws = np.zeros(5000)
        groups = {}
        for name in ("2D_AX_T2", "2D_AX_T2_BLADE"):
            stratum = np.array([float(row["delta_o"]) for row in patients
                                if row["group"] == name])
            groups[name] = len(stratum)
            indices = rng.integers(0, len(stratum), (5000, len(stratum)))
            draws += stratum[indices].mean(axis=1) * len(stratum) / len(values)
        if groups != {"2D_AX_T2": 35, "2D_AX_T2_BLADE": 27}:
            raise AssertionError("ReMIND stratum count changed")

    if summary["groups"] != groups:
        raise AssertionError("group summary mismatch")
    for key in ("shared_o", "disjoint_o", "delta_o", "shared_b_mae", "disjoint_b_mae"):
        close(float(summary[key]), float(np.mean([float(row[key]) for row in patients])), key)
    for actual, expected in zip(summary["ci95"], np.percentile(draws, [2.5, 97.5])):
        close(float(actual), float(expected), "patient-bootstrap interval")
    if (summary["positive_patients"] != int((values > 0).sum()) or
            summary["negative_patients"] != int((values < 0).sum())):
        raise AssertionError("direction counts changed")
    print(f"PASS {source}: {len(patients)} patients, {len(targets)} targets; "
          f"delta={values.mean():.6f}, CI={summary['ci95']}")


if __name__ == "__main__":
    verify("msvalid")
    verify("remind")
