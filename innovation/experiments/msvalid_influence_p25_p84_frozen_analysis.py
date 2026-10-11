"""Frozen P1-P24 to P25-P84 exact-context influence prediction analysis."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
TRAIN_FILES = (EXPERIMENTS / "msvalid_influence_stage1_analysis/per_context.csv",
               EXPERIMENTS / "msvalid_influence_stage2_p13_p24/per_context.csv")
BATCH_STARTS = (25, 37, 49, 61, 73)
TEST_FILES = tuple(EXPERIMENTS /
                   f"msvalid_influence_remaining_p{start}_p{start + 11}/per_context.csv"
                   for start in BATCH_STARTS)
PLAN = ROOT / "MSVALID_INFLUENCE_P25_P84_FROZEN_ANALYSIS_2026-09-30.md"
OUT = EXPERIMENTS / "msvalid_influence_p25_p84_frozen_analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame[frame.shared_anchor_count == 1].copy()
    frame["target_id"] = frame.patient + "/z" + frame.z.astype(str)
    frame["context_type"] = (frame.residue.astype(str) + ":" +
                             frame.context_left_offset.astype(str) + "," +
                             frame.context_right_offset.astype(str))
    if not frame.groupby("target_id").size().eq(4).all():
        raise AssertionError("A target lacks four one-overlap contexts")
    needed = ["z_spacing_mm", "influence", "error_cosine", "observable"]
    if not np.isfinite(frame[needed].to_numpy(dtype=float)).all():
        raise AssertionError("Nonfinite input")
    return frame


def design(frame: pd.DataFrame, categories: list[str], with_influence: bool) -> np.ndarray:
    columns = [(frame.context_type.to_numpy() == category).astype(float)
               for category in categories[1:]]
    columns.append(frame.z_spacing_mm.to_numpy(dtype=float))
    if with_influence:
        columns.append(frame.influence.to_numpy(dtype=float))
    return np.column_stack(columns)


def predict(train: pd.DataFrame, test: pd.DataFrame, outcome: str,
            categories: list[str], with_influence: bool) -> np.ndarray:
    x, z = design(train, categories, with_influence), design(test, categories, with_influence)
    mean, scale = x.mean(axis=0), x.std(axis=0)
    scale[scale == 0] = 1
    x, z = (x - mean) / scale, (z - mean) / scale
    y = train[outcome].to_numpy(dtype=float)
    center = y.mean()
    coefficient = np.linalg.solve(x.T @ x + np.eye(x.shape[1]), x.T @ (y - center))
    return center + z @ coefficient


def partial_rank(frame: pd.DataFrame) -> float:
    x = rankdata(frame.influence).astype(float)
    y = rankdata(frame.error_cosine).astype(float)
    target = pd.get_dummies(frame.target_id, drop_first=True, dtype=float).to_numpy()
    context = pd.get_dummies(frame.context_type, drop_first=True, dtype=float).to_numpy()
    matrix = np.column_stack([np.ones(len(frame)), target, context])
    x -= matrix @ np.linalg.lstsq(matrix, x, rcond=None)[0]
    y -= matrix @ np.linalg.lstsq(matrix, y, rcond=None)[0]
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def outcomes(frame: pd.DataFrame, outcome: str, seed: int) -> tuple[dict, pd.DataFrame]:
    modes = ("context", "context_plus_influence")
    for mode in modes:
        frame[f"{outcome}_{mode}_absolute_error"] = np.abs(
            frame[outcome] - frame[f"{outcome}_{mode}_prediction"])
    by_patient = frame.groupby("patient")[[f"{outcome}_{mode}_absolute_error"
                                           for mode in modes]].mean()
    gain = (by_patient[f"{outcome}_context_absolute_error"] -
            by_patient[f"{outcome}_context_plus_influence_absolute_error"]).to_numpy()
    rng = np.random.default_rng(seed)
    draws = gain[rng.integers(0, len(gain), (5000, len(gain)))].mean(axis=1)
    ranks = {}
    for mode in modes:
        values = [spearmanr(group[outcome],
                            group[f"{outcome}_{mode}_prediction"]).statistic
                  for _, group in frame.groupby("target_id")]
        ranks[mode] = float(np.mean(values))
    result = {"patient_equal_mae": {mode: float(by_patient[
        f"{outcome}_{mode}_absolute_error"].mean()) for mode in modes},
              "context_minus_plus_mae": float(gain.mean()),
              "ci95_patient_bootstrap_exploratory": np.percentile(draws, [2.5, 97.5]).tolist(),
              "patients_plus_better": int((gain > 0).sum()),
              "patients_plus_worse": int((gain < 0).sum()),
              "target_mean_spearman": ranks}
    return result, by_patient


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    for path in (*TRAIN_FILES, *TEST_FILES):
        if not path.exists():
            raise FileNotFoundError(path)
    train = prepare(pd.concat([pd.read_csv(path) for path in TRAIN_FILES], ignore_index=True))
    test = prepare(pd.concat([pd.read_csv(path) for path in TEST_FILES], ignore_index=True))
    expected_train = {f"P{i}" for i in range(1, 25)}
    expected_test = {f"P{i}" for i in range(25, 85)}
    if (set(train.patient) != expected_train or set(test.patient) != expected_test or
            len(train) != 192 or len(test) != 480 or
            train.target_id.nunique() != 48 or test.target_id.nunique() != 120):
        raise AssertionError("Frozen train/test sample contract mismatch")
    categories = sorted(train.context_type.unique())
    if len(categories) != 8 or categories != sorted(test.context_type.unique()):
        raise AssertionError("Exact context categories changed")
    for outcome in ("error_cosine", "observable"):
        for mode, with_influence in (("context", False),
                                     ("context_plus_influence", True)):
            test[f"{outcome}_{mode}_prediction"] = predict(
                train, test, outcome, categories, with_influence)
    scores = {}
    per_patient = pd.DataFrame(index=sorted(expected_test, key=lambda pid: int(pid[1:])))
    for outcome, seed in (("error_cosine", 20261019), ("observable", 20261020)):
        scores[outcome], patient = outcomes(test, outcome, seed)
        per_patient = per_patient.join(patient)
    result = {"status": "post-result within-source remaining-patient diagnostic",
              "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
              "train_csv_sha256": {path.name + ":" + path.parent.name: sha256(path)
                                    for path in TRAIN_FILES},
              "test_csv_sha256": {path.parent.name: sha256(path) for path in TEST_FILES},
              "train_patients": 24, "test_patients": 60,
              "train_targets": 48, "test_targets": 120,
              "one_overlap_train_rows": len(train), "one_overlap_test_rows": len(test),
              "categories": categories, "alpha": 1.0,
              "test_partial_rank_target_and_exact_context": partial_rank(test),
              "heldout_prediction": scores}
    OUT.mkdir(parents=True)
    test.to_csv(OUT / "per_context_predictions.csv", index=False)
    per_patient.to_csv(OUT / "per_patient_errors.csv", index_label="patient")
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
