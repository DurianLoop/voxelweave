"""Post-result exact-context baseline and stage-2 association sensitivity."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr


ROOT = Path(__file__).resolve().parents[1] / "experiments"
TRAIN = ROOT / "msvalid_influence_stage1_analysis/per_context.csv"
TEST = ROOT / "msvalid_influence_stage2_p13_p24/per_context.csv"
OUT = ROOT / "msvalid_exact_context_heldout_sensitivity"


def load(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    data = data[data.shared_anchor_count == 1].copy()
    data["target_id"] = data.patient + "/z" + data.z.astype(str)
    data["context_type"] = (data.residue.astype(str) + ":" +
                            data.context_left_offset.astype(str) + "," +
                            data.context_right_offset.astype(str))
    assert len(data) == 96 and data.patient.nunique() == 12
    assert data.target_id.nunique() == 24 and data.groupby("target_id").size().eq(4).all()
    return data


def design(data: pd.DataFrame, categories: list[str], influence: bool) -> np.ndarray:
    matrix = [(data.context_type.to_numpy() == name).astype(float)
              for name in categories[1:]]
    matrix.append(data.z_spacing_mm.to_numpy(dtype=float))
    if influence:
        matrix.append(data.influence.to_numpy(dtype=float))
    return np.column_stack(matrix)


def predict(train: pd.DataFrame, test: pd.DataFrame, outcome: str,
            categories: list[str], influence: bool) -> np.ndarray:
    a, b = design(train, categories, influence), design(test, categories, influence)
    mean, scale = a.mean(axis=0), a.std(axis=0)
    scale[scale == 0] = 1
    a, b = (a - mean) / scale, (b - mean) / scale
    y = train[outcome].to_numpy(dtype=float)
    y_mean = y.mean()
    coef = np.linalg.solve(a.T @ a + np.eye(a.shape[1]), a.T @ (y - y_mean))
    return y_mean + b @ coef


def partial_rank(data: pd.DataFrame) -> float:
    x, y = rankdata(data.influence).astype(float), rankdata(data.error_cosine).astype(float)
    target = pd.get_dummies(data.target_id, drop_first=True, dtype=float).to_numpy()
    context = pd.get_dummies(data.context_type, drop_first=True, dtype=float).to_numpy()
    design_matrix = np.column_stack([np.ones(len(data)), target, context])
    x -= design_matrix @ np.linalg.lstsq(design_matrix, x, rcond=None)[0]
    y -= design_matrix @ np.linalg.lstsq(design_matrix, y, rcond=None)[0]
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    train, test = load(TRAIN), load(TEST)
    categories = sorted(train.context_type.unique())
    assert categories == sorted(test.context_type.unique())
    test = test.copy()
    for outcome in ("error_cosine", "observable"):
        for mode in ("exact_context", "exact_context_plus_influence"):
            test[f"{outcome}_{mode}_prediction"] = predict(
                train, test, outcome, categories, mode.endswith("plus_influence"))
    results = {}
    for outcome in ("error_cosine", "observable"):
        modes = ("exact_context", "exact_context_plus_influence")
        for mode in modes:
            test[f"{outcome}_{mode}_absolute_error"] = np.abs(
                test[outcome] - test[f"{outcome}_{mode}_prediction"])
        grouped = test.groupby("patient")
        gains = (grouped[f"{outcome}_{modes[0]}_absolute_error"].mean() -
                 grouped[f"{outcome}_{modes[1]}_absolute_error"].mean()).to_numpy()
        rng = np.random.default_rng(20261008 if outcome == "error_cosine" else 20261009)
        draws = gains[rng.integers(0, len(gains), (5000, len(gains)))].mean(axis=1)
        ranks = {}
        for mode in modes:
            ranks[mode] = float(np.mean([
                spearmanr(group[outcome], group[f"{outcome}_{mode}_prediction"]).statistic
                for _, group in test.groupby("target_id")]))
        results[outcome] = {
            "mae": {mode: float(test[f"{outcome}_{mode}_absolute_error"].mean())
                    for mode in modes},
            "target_mean_spearman": ranks,
            "geometry_minus_plus_mae": float(gains.mean()),
            "ci95_patient_bootstrap_exploratory": np.percentile(draws, [2.5, 97.5]).tolist(),
            "patients_plus_better": int((gains > 0).sum()),
        }
    result = {"status": "post-result sensitivity; same MSValid source and sample",
              "train_patients": 12, "test_patients": 12,
              "exact_context_categories": categories,
              "stage1_partial_rank_target_and_exact_context": partial_rank(train),
              "stage2_partial_rank_target_and_exact_context": partial_rank(test),
              "heldout": results}
    OUT.mkdir(parents=True)
    test.to_csv(OUT / "heldout_predictions.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
