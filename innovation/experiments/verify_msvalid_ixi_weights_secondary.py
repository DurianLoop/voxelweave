"""Independent read-only reconciliation of the IXI-weight MSValid result."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "experiments/msvalid_ixi_weights_secondary"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def close(actual: float, expected: float, label: str) -> None:
    if not np.isclose(actual, expected, rtol=0, atol=1e-10):
        raise AssertionError(f"{label}: {actual} != {expected}")


def main() -> None:
    summary = json.loads((RESULT / "summary.json").read_text(encoding="utf-8"))
    qualification = json.loads((ROOT / "literature/msvalid_geometry_qualification.json").read_text(encoding="utf-8"))
    targets = rows(RESULT / "per_target.csv")
    patients = rows(RESULT / "per_patient.csv")
    assert summary["protocol_sha256"] == sha256(ROOT / "MSVALID_IXI_WEIGHTS_SECONDARY_PROTOCOL_2026-10-01.md")
    assert summary["script_sha256"] == sha256(ROOT / "experiments/msvalid_ixi_weights_secondary.py")
    assert summary["qualification_sha256"] == sha256(ROOT / "literature/msvalid_geometry_qualification.json")
    assert summary["source_manifest_sha256"] == sha256(ROOT / "literature/msvalid_extraction_manifest.json")
    checkpoints = {
        "hat": ROOT / "../baseline/ixi_hat_2p5d/runs/full_test115/checkpoints/hat_epoch_best.pth",
        "swinir": ROOT / "../baseline/ixi_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth",
    }
    for name, path in checkpoints.items():
        assert summary["checkpoint_sha256"][name] == sha256(path)
    assert len(patients) == summary["patients_scored"] == 84
    assert len(targets) == summary["targets_scored"] == 479
    assert not summary["failures"]
    eligible = {(p["patient"], z)
                for p in qualification["patients"] for positions in p["eligible_targets"].values()
                for z in positions}
    actual = [(r["patient"], int(r["z"])) for r in targets]
    assert set(actual) == eligible and len(set(actual)) == len(actual)
    grouped: dict[str, dict[int, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in targets:
        pid, residue = row["patient"], int(row["residue"])
        z = int(row["z"])
        assert residue == z % 4 and residue in (1, 3)
        close(float(row["delta_o"]), float(row["disjoint_observable"])
              - float(row["shared_observable"]), f"{pid} z{z} delta")
        close(float(row["shared_a_mae"]), float(row["disjoint_a_mae"]), f"{pid} z{z} fixed A")
        for condition in ("shared", "disjoint"):
            value = float(row[f"{condition}_observable"])
            assert np.isfinite(value) and 0 <= value <= 1
        grouped[pid][residue].append(row)
    by_patient = {row["patient"]: row for row in patients}
    assert len(by_patient) == len(patients) == len(grouped)
    for pid, classes in grouped.items():
        assert set(classes) == {1, 3}
        row = by_patient[pid]
        assert int(row["targets"]) == sum(len(v) for v in classes.values())
        for residue in (1, 3):
            mean = np.mean([float(v["delta_o"]) for v in classes[residue]])
            close(float(row[f"residue_{residue}_delta_o"]), mean, f"{pid} residue {residue}")
        for key in ("delta_o", "shared_observable", "disjoint_observable",
                    "shared_a_mae", "shared_b_mae", "disjoint_b_mae",
                    "shared_paired_mse", "disjoint_paired_mse"):
            mean = np.mean([np.mean([float(v[key]) for v in classes[r]]) for r in (1, 3)])
            close(float(row[key]), mean, f"{pid} {key}")
    values = np.array([float(row["delta_o"]) for row in patients])
    rng = np.random.default_rng(20261001)
    draws = values[rng.integers(0, len(values), (5000, len(values)))].mean(axis=1)
    ci = np.percentile(draws, [2.5, 97.5])
    close(summary["mean_delta_o"], float(values.mean()), "main effect")
    close(summary["ci95_delta_o"][0], float(ci[0]), "ci lower")
    close(summary["ci95_delta_o"][1], float(ci[1]), "ci upper")
    for result_key, patient_key in (("mean_shared_o", "shared_observable"),
                                    ("mean_disjoint_o", "disjoint_observable"),
                                    ("mean_residue_1_delta_o", "residue_1_delta_o"),
                                    ("mean_residue_3_delta_o", "residue_3_delta_o")):
        close(summary[result_key], np.mean([float(r[patient_key]) for r in patients]), result_key)
    assert summary["positive_patients"] == int((values > 0).sum())
    assert summary["negative_patients"] == int((values < 0).sum())
    assert summary["secondary_positive"] == (len(values) >= 70 and ci[0] > 0)
    print(json.dumps({"verified": True, "patients": len(patients), "targets": len(targets),
                      "delta_o": float(values.mean()), "ci95": ci.tolist(),
                      "output_sha256": {name: sha256(RESULT / name)
                                        for name in ("summary.json", "per_patient.csv", "per_target.csv")}},
                     indent=2))


if __name__ == "__main__":
    main()
