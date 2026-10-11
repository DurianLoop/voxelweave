"""Read-only independent aggregation audit of the known-profile pilot."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "innovation/experiments/known_profile_holdout_pilot"
PLAN = ROOT / "innovation/KNOWN_PROFILE_HOLDOUT_PILOT_PLAN_2026-10-01.md"
SCRIPT = ROOT / "innovation/experiments/known_profile_holdout_pilot.py"
EXPECTED_PATIENTS = ("IXI013", "IXI015", "IXI017")


def read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def near(a: float, b: float) -> None:
    if not np.isclose(a, b, rtol=0, atol=1e-10):
        raise AssertionError(f"{a} != {b}")


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    conditions = read(OUT / "per_condition.csv")
    candidates = read(OUT / "per_candidate.csv")
    assert summary["plan_sha256"] == sha256(PLAN)
    assert summary["script_sha256"] == sha256(SCRIPT)
    assert not summary["failures"] and len(conditions) == 12 and len(candidates) == 36
    splits = ROOT / "dataset/IXI/splits/seed3407"
    train = (splits / "train_cases.txt").read_text(encoding="utf-8").splitlines()
    val = (splits / "val_cases.txt").read_text(encoding="utf-8").splitlines()
    test = (splits / "test_cases.txt").read_text(encoding="utf-8").splitlines()
    assert tuple(train[:3]) == EXPECTED_PATIENTS
    assert not set(EXPECTED_PATIENTS) & (set(val) | set(test))
    for split in ("train", "val", "test"):
        assert summary["split_sha256"][split] == sha256(splits / f"{split}_cases.txt")
    for patient in EXPECTED_PATIENTS:
        matches = list((ROOT / "dataset/IXI/raw/T2").glob(f"{patient}-*-T2.nii.gz"))
        assert len(matches) == 1 and summary["source_sha256"][patient] == sha256(matches[0])
    by_key = {}
    for row in candidates:
        key = (row["patient"], float(row["true_sigma"]), int(row["stride"]))
        by_key.setdefault(key, []).append(row)
    assert len(by_key) == 12
    assert set(by_key) == {(p, t, s) for p in EXPECTED_PATIENTS
                           for t in (0.0, 1.5) for s in (4, 6)}
    match = improve = harm = 0
    for row in conditions:
        key = (row["patient"], float(row["true_sigma"]), int(row["stride"]))
        group = by_key[key]
        assert sorted(float(x["candidate_sigma"]) for x in group) == [0.0, 1.5, 3.0]
        chosen = min(group, key=lambda x: (float(x["heldout_mse"]), float(x["candidate_sigma"])))
        oracle = min(group, key=lambda x: (float(x["target_mse"]), float(x["candidate_sigma"])))
        fixed = next(x for x in group if float(x["candidate_sigma"]) == 0)
        true = next(x for x in group if float(x["candidate_sigma"]) == key[1])
        assert float(row["chosen_sigma"]) == float(chosen["candidate_sigma"])
        assert float(row["oracle_sigma"]) == float(oracle["candidate_sigma"])
        for field, item in (("selected_target_mse", chosen), ("oracle_target_mse", oracle),
                            ("fixed_target_mse", fixed), ("true_profile_target_mse", true)):
            near(float(row[field]), float(item["target_mse"]))
        delta = float(chosen["target_mse"]) - float(fixed["target_mse"])
        near(float(row["selected_minus_fixed_mse"]), delta)
        match += float(chosen["candidate_sigma"]) == key[1]
        improve += delta < 0
        harm += delta > 0
    assert (match, improve, harm) == (summary["selection_matches_true"],
                                      summary["selected_improves_fixed"],
                                      summary["selected_harms_fixed"])
    print("PASS: train-only sources, 12 conditions, 36 candidates and all selections")


if __name__ == "__main__":
    main()
