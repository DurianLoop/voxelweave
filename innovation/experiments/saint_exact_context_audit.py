"""Post-result exact-context and case-heldout audit of archived SAINT responses."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "design/paper/ARCHITECTURE_COVERAGE_CLOSURE/outputs/saint_acquired_observations.csv"
OUT = ROOT / "innovation/experiments/saint_exact_context_audit"


def partial_rank(frame: pd.DataFrame) -> float:
    x = rankdata(frame.influence).reshape(-1, 4)
    y = rankdata(frame.alignment).reshape(-1, 4)
    x = x - x.mean(axis=1, keepdims=True)
    y = y - y.mean(axis=1, keepdims=True)
    x = x - x.mean(axis=0, keepdims=True)
    y = y - y.mean(axis=0, keepdims=True)
    return float(np.sum(x * y) / np.sqrt(np.sum(x * x) * np.sum(y * y)))


def design(frame: pd.DataFrame, contexts: list[str], influence: bool) -> np.ndarray:
    cols = [(frame.context.to_numpy() == context).astype(float) for context in contexts[1:]]
    if influence:
        cols.append(frame.influence.to_numpy(dtype=float))
    return np.column_stack(cols)


def predict(train: pd.DataFrame, test: pd.DataFrame, contexts: list[str],
            influence: bool) -> np.ndarray:
    a, b = design(train, contexts, influence), design(test, contexts, influence)
    mean, scale = a.mean(axis=0), a.std(axis=0)
    scale[scale == 0] = 1
    a, b = (a - mean) / scale, (b - mean) / scale
    y = train.alignment.to_numpy(dtype=float)
    center = y.mean()
    coefficient = np.linalg.solve(a.T @ a + np.eye(a.shape[1]), a.T @ (y - center))
    return center + b @ coefficient


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    raw = pd.read_csv(SOURCE)
    rows, predictions = [], []
    for dataset, all_rows in raw[raw.overlap_count == 1].groupby("dataset"):
        points = {}
        for epsilon, group in all_rows.groupby("epsilon"):
            group = group.sort_values(["case", "z", "context"])
            cases = sorted(group.case.unique())
            contexts = tuple(sorted(group.context.unique()))
            assert len(contexts) == 4 and len(group) == len(cases) * 12
            assert group.groupby(["case", "z"]).context.apply(
                lambda x: tuple(x) == contexts).all()
            points[str(epsilon)] = partial_rank(group)
        main_rows = all_rows[all_rows.epsilon == .01].sort_values(
            ["case", "z", "context"]).copy()
        cases = sorted(main_rows.case.unique())
        values = main_rows[["influence", "alignment"]].to_numpy().reshape(len(cases), 12, 2)
        rng = np.random.default_rng(20261021 if dataset == "fastmri" else 20261022)
        draws = []
        for ids in rng.integers(0, len(cases), (1000, len(cases))):
            sample = pd.DataFrame(values[ids].reshape(-1, 2), columns=["influence", "alignment"])
            draws.append(partial_rank(sample))
        rng = np.random.default_rng(20261023)
        folds = np.array_split(rng.permutation(cases), 5)
        predicted = []
        for fold, heldout in enumerate(folds):
            test = main_rows[main_rows.case.isin(heldout)].copy()
            train = main_rows[~main_rows.case.isin(heldout)]
            test["fold"] = fold
            test["context_prediction"] = predict(train, test, list(contexts), False)
            test["context_plus_influence_prediction"] = predict(train, test, list(contexts), True)
            predicted.append(test)
        result = pd.concat(predicted, ignore_index=True)
        for mode in ("context", "context_plus_influence"):
            result[f"{mode}_absolute_error"] = np.abs(
                result.alignment - result[f"{mode}_prediction"])
        case_mae = result.groupby("case")[["context_absolute_error",
                                           "context_plus_influence_absolute_error"]].mean()
        gain = (case_mae.context_absolute_error -
                case_mae.context_plus_influence_absolute_error).to_numpy()
        ci = gain[rng.integers(0, len(gain), (5000, len(gain)))].mean(axis=1)
        ranks = {mode: float(np.mean([
            spearmanr(target.alignment, target[f"{mode}_prediction"]).statistic
            for _, target in result.groupby(["case", "z"])]))
            for mode in ("context", "context_plus_influence")}
        rows.append({"dataset": dataset, "model": "saint", "cases": len(cases),
                     "targets": len(cases) * 3,
                     "partial_rank_by_epsilon": points,
                     "main_partial_rank_ci95_exploratory": np.percentile(draws, [2.5, 97.5]).tolist(),
                     "heldout_mae": {mode: float(result[f"{mode}_absolute_error"].mean())
                                     for mode in ("context", "context_plus_influence")},
                     "heldout_case_equal_mae_gain": float(gain.mean()),
                     "heldout_gain_ci95_exploratory": np.percentile(ci, [2.5, 97.5]).tolist(),
                     "cases_plus_better": int((gain > 0).sum()),
                     "target_mean_spearman": ranks})
        predictions.append(result)
    OUT.mkdir(parents=True)
    pd.concat(predictions, ignore_index=True).to_csv(OUT / "out_of_fold_predictions.csv", index=False)
    summary = {"status": "post-result SAINT exact-context sensitivity",
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "rows": rows}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
