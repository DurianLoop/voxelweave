"""Exploratory case-heldout prediction from archived acquired-only response rows."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "design/paper/FINAL_SCIENTIFIC_STRENGTHENING/acquired_only_influence.csv"
OUT = ROOT / "innovation/experiments/original_influence_case_heldout_prediction"


def predict(train: pd.DataFrame, test: pd.DataFrame, contexts: list[str],
            with_influence: bool) -> np.ndarray:
    def design(frame: pd.DataFrame) -> np.ndarray:
        features = [(frame.context.to_numpy() == name).astype(float)
                    for name in contexts[1:]]
        if with_influence:
            features.append(frame.influence.to_numpy(dtype=float))
        return np.column_stack(features)

    a, b = design(train), design(test)
    mean, scale = a.mean(axis=0), a.std(axis=0)
    scale[scale == 0] = 1
    a, b = (a - mean) / scale, (b - mean) / scale
    y = train.alignment.to_numpy(dtype=float)
    center = y.mean()
    coefficients = np.linalg.solve(a.T @ a + np.eye(a.shape[1]), a.T @ (y - center))
    return center + b @ coefficients


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    data = pd.read_csv(SOURCE)
    data = data[(data.epsilon == .01) & (data.overlap_count == 1)].copy()
    all_predictions, results = [], []
    for (dataset, model), group in data.groupby(["dataset", "model"]):
        group = group.copy()
        cases = sorted(group.case.unique())
        assert len(group) == len(cases) * 12
        contexts = sorted(group.context.unique())
        assert len(contexts) == 4
        rng = np.random.default_rng(20261010)
        folds = np.array_split(rng.permutation(cases), 5)
        predictions = []
        for fold, heldout_cases in enumerate(folds):
            test = group[group.case.isin(heldout_cases)].copy()
            train = group[~group.case.isin(heldout_cases)]
            test["fold"] = fold
            test["context_prediction"] = predict(train, test, contexts, False)
            test["context_plus_influence_prediction"] = predict(train, test, contexts, True)
            predictions.append(test)
        result = pd.concat(predictions, ignore_index=True)
        for mode in ("context", "context_plus_influence"):
            result[f"{mode}_absolute_error"] = np.abs(
                result.alignment - result[f"{mode}_prediction"])
        case_mae = result.groupby("case")[["context_absolute_error",
                                           "context_plus_influence_absolute_error"]].mean()
        gain = (case_mae.context_absolute_error -
                case_mae.context_plus_influence_absolute_error).to_numpy()
        draws = gain[rng.integers(0, len(gain), (5000, len(gain)))].mean(axis=1)
        target_ranks = {}
        for mode in ("context", "context_plus_influence"):
            target_ranks[mode] = float(np.mean([
                spearmanr(target.alignment, target[f"{mode}_prediction"]).statistic
                for _, target in result.groupby(["case", "z"])]))
        results.append({"dataset": dataset, "model": model,
                        "cases": len(cases), "targets": len(cases) * 3,
                        "mae": {mode: float(result[f"{mode}_absolute_error"].mean())
                                for mode in ("context", "context_plus_influence")},
                        "context_minus_plus_case_equal_mae": float(gain.mean()),
                        "ci95_case_bootstrap_exploratory": np.percentile(draws, [2.5, 97.5]).tolist(),
                        "cases_plus_better": int((gain > 0).sum()),
                        "target_mean_spearman": target_ranks})
        all_predictions.append(result)
    OUT.mkdir(parents=True)
    pd.concat(all_predictions, ignore_index=True).to_csv(OUT / "out_of_fold_predictions.csv", index=False)
    summary = {"status": "post-result case-heldout exploratory diagnostic",
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "folds": 5, "alpha": 1.0, "results": results}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
