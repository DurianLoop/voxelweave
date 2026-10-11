"""Post-result exact-context sensitivity of the archived acquired-only results."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "design/paper/FINAL_SCIENTIFIC_STRENGTHENING/acquired_only_influence.csv"
OUT = ROOT / "innovation/experiments/original_influence_exact_context"


def correlation(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.dot(x, y) / np.sqrt(np.dot(x, x) * np.dot(y, y)))


def estimate(values: np.ndarray, adjust_partner_error: bool = False) -> float:
    """Each examination has three targets, each with the same four context types."""
    ranked = np.stack([rankdata(values[:, i]) for i in range(values.shape[1])], axis=1)
    ranked = ranked.reshape(-1, 4, values.shape[1])
    residual = ranked - ranked.mean(axis=1, keepdims=True)
    residual -= residual.mean(axis=0, keepdims=True)
    x, y = residual[:, :, 0].ravel(), residual[:, :, 1].ravel()
    if adjust_partner_error:
        z = residual[:, :, 2].ravel()
        x -= z * (np.dot(x, z) / np.dot(z, z))
        y -= z * (np.dot(y, z) / np.dot(z, z))
    return correlation(x, y)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    import hashlib
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    data = pd.read_csv(SOURCE)
    data = data[(data.epsilon == .01) & (data.overlap_count == 1)].copy()
    results = []
    for (dataset, model), frame in data.groupby(["dataset", "model"]):
        frame = frame.sort_values(["case", "z", "context"])
        cases = frame.case.unique()
        contexts = tuple(sorted(frame.context.unique()))
        assert len(contexts) == 4
        assert len(frame) == len(cases) * 3 * 4
        assert frame.groupby(["case", "z"]).context.apply(
            lambda s: tuple(s) == contexts).all()
        values = frame[["influence", "alignment", "companion_error"]].to_numpy()
        assert np.isfinite(values).all()
        values = values.reshape(len(cases), 12, 3)
        point = estimate(values.reshape(-1, 3))
        partner_point = estimate(values.reshape(-1, 3), True)
        rng = np.random.default_rng(20261007)
        draws = np.empty((1000, 2))
        for j, ids in enumerate(rng.integers(0, len(cases), (1000, len(cases)))):
            sample = values[ids].reshape(-1, 3)
            draws[j] = estimate(sample), estimate(sample, True)
        results.append({
            "dataset": dataset, "model": model,
            "examinations": len(cases), "targets": len(cases) * 3,
            "one_overlap_rows": len(frame), "contexts": contexts,
            "target_and_exact_context_partial_rank": point,
            "ci95_case_bootstrap_exploratory": np.percentile(draws[:, 0], [2.5, 97.5]).tolist(),
            "plus_retrospective_partner_mae": partner_point,
            "partner_ci95_case_bootstrap_exploratory": np.percentile(draws[:, 1], [2.5, 97.5]).tolist(),
        })
    OUT.mkdir(parents=True)
    result = {"status": "post-result sensitivity, not a registered confirmatory test",
              "source_sha256": source_hash, "bootstrap_draws": 1000,
              "results": results}
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
