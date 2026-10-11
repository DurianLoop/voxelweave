"""Read-only, post-result algebraic audit of MSValid observable-fraction changes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/msvalid_mira_confirmation/per_target.csv"
MAIN = ROOT / "experiments/msvalid_mira_confirmation/summary.json"
PLAN = ROOT / "MSVALID_ERROR_ALIGNMENT_DECOMPOSITION_PLAN_2026-09-30.md"
OUT = ROOT / "experiments/msvalid_error_alignment_decomposition"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observable(rho: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return .5 - rho * np.sqrt(a * b) / (a + b)


def mean_patient_residue(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    by_residue = frame.groupby(["patient", "residue"])[columns].mean()
    if not by_residue.groupby(level="patient").size().eq(2).all():
        raise AssertionError("Missing a residue for a patient")
    return by_residue.groupby(level="patient").mean().sort_index()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    frame = pd.read_csv(SOURCE)
    if len(frame) != 479 or frame.patient.nunique() != 84:
        raise AssertionError("Main sample contract mismatch")
    a = frame.shared_a_mse.to_numpy(dtype=float)
    if not np.allclose(a, frame.disjoint_a_mse, rtol=0, atol=1e-8):
        raise AssertionError("Fixed reference MSE changed")
    bs = frame.shared_b_mse.to_numpy(dtype=float)
    bd = frame.disjoint_b_mse.to_numpy(dtype=float)
    os = frame.shared_observable.to_numpy(dtype=float)
    od = frame.disjoint_observable.to_numpy(dtype=float)
    if not np.isfinite(np.column_stack([a, bs, bd, os, od])).all() or min(
            a.min(), bs.min(), bd.min()) <= 0:
        raise AssertionError("Nonfinite or nonpositive input")
    rs = (.5 - os) * (a + bs) / np.sqrt(a * bs)
    rd = (.5 - od) * (a + bd) / np.sqrt(a * bd)
    if (np.max(np.abs(rs)) > 1 + 1e-8 or np.max(np.abs(rd)) > 1 + 1e-8 or
            np.max(np.abs(observable(rs, a, bs) - os)) > 1e-8 or
            np.max(np.abs(observable(rd, a, bd) - od)) > 1e-8):
        raise AssertionError("Error cosine or identity invalid")
    fss = observable(rs, a, bs)
    fsd = observable(rs, a, bd)
    fds = observable(rd, a, bs)
    fdd = observable(rd, a, bd)
    quality = .5 * ((fsd - fss) + (fdd - fds))
    alignment = .5 * ((fds - fss) + (fdd - fsd))
    if np.max(np.abs(quality + alignment - frame.delta_o.to_numpy())) > 1e-8:
        raise AssertionError("Contributions do not sum to Delta O")
    frame["shared_error_cosine"] = rs
    frame["disjoint_error_cosine"] = rd
    frame["quality_imbalance_contribution"] = quality
    frame["alignment_contribution"] = alignment
    columns = ["delta_o", "shared_error_cosine", "disjoint_error_cosine",
               "quality_imbalance_contribution", "alignment_contribution"]
    patients = mean_patient_residue(frame, columns)
    point = patients.mean().to_dict()
    expected = json.loads(MAIN.read_text(encoding="utf-8"))["mean_delta_o"]
    if abs(point["delta_o"] - expected) > 1e-12:
        raise AssertionError("Primary estimate mismatch")
    rng = np.random.default_rng(20261011)
    values = patients.to_numpy()
    draws = values[rng.integers(0, len(patients), (5000, len(patients)))].mean(axis=1)
    intervals = {column: np.percentile(draws[:, i], [2.5, 97.5]).tolist()
                 for i, column in enumerate(columns)}
    matched = []
    ratio = bd / bs
    for tolerance in (.05, .10, .20):
        subset = frame[(ratio >= 1 / (1 + tolerance)) &
                       (ratio <= 1 + tolerance)]
        matched.append({"mse_ratio_tolerance": tolerance,
                        "targets": len(subset), "patients": subset.patient.nunique(),
                        "target_equal_mean_delta_o": float(subset.delta_o.mean()),
                        "positive_targets": int((subset.delta_o > 0).sum())})
    result = {"status": "post-result algebraic and outcome-matched sensitivity; not causal",
              "source_sha256": sha256(SOURCE), "main_summary_sha256": sha256(MAIN),
              "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
              "patients": len(patients), "targets": len(frame),
              "patient_residue_equal_points": point,
              "ci95_patient_bootstrap_exploratory": intervals,
              "matched_target_descriptive": matched,
              "max_abs_component_identity_error": float(np.max(np.abs(quality + alignment - frame.delta_o)))}
    OUT.mkdir(parents=True)
    frame.to_csv(OUT / "per_target.csv", index=False)
    patients.to_csv(OUT / "per_patient.csv")
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
