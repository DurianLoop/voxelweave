"""Frozen geometry-vs-influence patient-heldout prediction diagnostic."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from msvalid_mira_confirmation import sha256


INNOVATION = Path(__file__).resolve().parents[1]
EXPERIMENTS = INNOVATION / "experiments"
STAGE1 = EXPERIMENTS / "msvalid_influence_stage1_analysis/per_context.csv"
STAGE2 = EXPERIMENTS / "msvalid_influence_stage2_p13_p24/per_context.csv"
PLAN = INNOVATION / "MSVALID_INFLUENCE_HELDOUT_PREDICTION_PROTOCOL_2026-09-30.md"
OUT = EXPERIMENTS / "msvalid_influence_heldout_prediction"
GEOMETRY = ("context_left_offset", "context_right_offset", "span_mm",
            "asymmetry_mm", "z_spacing_mm", "residue")
ALPHA = 1.0


def rows(path: Path, expected_patients: list[str]) -> pd.DataFrame:
    data = pd.read_csv(path)
    data = data[data.shared_anchor_count == 1].copy()
    data["target_id"] = data.patient + "/z" + data.z.astype(str)
    if (sorted(data.patient.unique(), key=lambda pid: int(pid[1:])) != expected_patients or
            len(data) != 96 or data.target_id.nunique() != 24 or
            not data.groupby("target_id").size().eq(4).all()):
        raise AssertionError(f"Sample contract mismatch: {path}")
    needed = list(GEOMETRY) + ["influence", "error_cosine", "observable"]
    if not np.isfinite(data[needed].to_numpy(dtype=float)).all():
        raise AssertionError(f"Nonfinite data: {path}")
    return data


def features(frame: pd.DataFrame, with_influence: bool) -> np.ndarray:
    names = (*GEOMETRY, "influence") if with_influence else GEOMETRY
    return frame[list(names)].to_numpy(dtype=np.float64)


def fit_predict(train: pd.DataFrame, test: pd.DataFrame, outcome: str,
                mode: str) -> np.ndarray:
    y = train[outcome].to_numpy(dtype=np.float64)
    if mode == "constant":
        return np.full(len(test), float(y.mean()))
    with_influence = mode == "geometry_plus_influence"
    x_train = features(train, with_influence)
    x_test = features(test, with_influence)
    mean = x_train.mean(axis=0)
    scale = x_train.std(axis=0)
    scale[scale == 0] = 1
    centered = (x_train - mean) / scale
    centered_test = (x_test - mean) / scale
    y_mean = float(y.mean())
    coeff = np.linalg.solve(centered.T @ centered + ALPHA * np.eye(centered.shape[1]),
                            centered.T @ (y - y_mean))
    return y_mean + centered_test @ coeff


def metrics(frame: pd.DataFrame, outcome: str) -> dict:
    comparisons = {}
    for mode in ("constant", "geometry", "geometry_plus_influence"):
        predicted = frame[f"{outcome}_{mode}_prediction"].to_numpy()
        actual = frame[outcome].to_numpy()
        frame[f"{outcome}_{mode}_absolute_error"] = np.abs(predicted - actual)
        by_patient = frame.groupby("patient")[f"{outcome}_{mode}_absolute_error"].mean()
        correlations = []
        for _, group in frame.groupby("target_id"):
            value = spearmanr(group[outcome],
                              group[f"{outcome}_{mode}_prediction"]).statistic
            correlations.append(float(value) if np.isfinite(value) else None)
        comparisons[mode] = {"patient_equal_mae": float(by_patient.mean()),
                             "target_mean_spearman": float(np.mean([x for x in correlations
                                                                    if x is not None]))
                             if any(x is not None for x in correlations) else None,
                             "finite_target_rankings": sum(x is not None for x in correlations)}
    per_patient = frame.groupby("patient").agg(
        geometry_mae=(f"{outcome}_geometry_absolute_error", "mean"),
        plus_mae=(f"{outcome}_geometry_plus_influence_absolute_error", "mean"))
    gain = (per_patient.geometry_mae - per_patient.plus_mae).to_numpy()
    rng = np.random.default_rng(20261004 if outcome == "error_cosine" else 20261005)
    draws = rng.integers(0, len(gain), (5000, len(gain)))
    ci = np.percentile(gain[draws].mean(axis=1), [2.5, 97.5]).tolist()
    return {"comparisons": comparisons,
            "geometry_minus_plus_patient_equal_mae": float(gain.mean()),
            "ci95_patient_bootstrap_exploratory": ci,
            "patients_plus_better": int((gain > 0).sum()),
            "patients_plus_worse": int((gain < 0).sum())}


def predictions(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    output = test.copy()
    for outcome in ("error_cosine", "observable"):
        for mode in ("constant", "geometry", "geometry_plus_influence"):
            output[f"{outcome}_{mode}_prediction"] = fit_predict(train, test, outcome, mode)
    return output


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite: {OUT}")
    train = rows(STAGE1, [f"P{i}" for i in range(1, 13)])
    heldout = rows(STAGE2, [f"P{i}" for i in range(13, 25)])
    lopo_frames = []
    for patient in [f"P{i}" for i in range(1, 13)]:
        lopo_frames.append(predictions(train[train.patient != patient],
                                       train[train.patient == patient]))
    lopo = pd.concat(lopo_frames, ignore_index=True)
    heldout_predictions = predictions(train, heldout)
    result = {"status": "post-result, within-MSValid heldout diagnostic; not independent cohort confirmation",
              "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
              "stage1_csv_sha256": sha256(STAGE1), "stage2_csv_sha256": sha256(STAGE2),
              "train_patients": 12, "heldout_patients": 12,
              "one_overlap_rows_each": 96, "alpha": ALPHA, "geometry_features": list(GEOMETRY),
              "lopo_train_stage": {outcome: metrics(lopo, outcome)
                                   for outcome in ("error_cosine", "observable")},
              "p13_p24_heldout": {outcome: metrics(heldout_predictions, outcome)
                                  for outcome in ("error_cosine", "observable")}}
    OUT.mkdir(parents=True)
    lopo.to_csv(OUT / "lopo_predictions.csv", index=False)
    heldout_predictions.to_csv(OUT / "heldout_predictions.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
