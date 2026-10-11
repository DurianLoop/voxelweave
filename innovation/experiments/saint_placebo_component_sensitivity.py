"""Post-result component check for the mixed SAINT placebo outcomes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[1] / "experiments"
SOURCE = ROOT / "saint_response_id_placebo/per_context.csv"
OUT = ROOT / "saint_placebo_component_sensitivity"
SCORES = ("influence", "placebo_a", "placebo_b")


def partial(data: pd.DataFrame, score: str) -> float:
    ranked = np.stack([rankdata(data[score]), rankdata(data.alignment)], axis=1)
    ranked = ranked.reshape(-1, 4, 2)
    residual = ranked - ranked.mean(axis=1, keepdims=True)
    residual -= residual.mean(axis=0, keepdims=True)
    x, y = residual[:, :, 0].ravel(), residual[:, :, 1].ravel()
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    raw = pd.read_csv(SOURCE).sort_values(["dataset", "case", "z", "context"])
    results = []
    for dataset, frame in raw.groupby("dataset"):
        cases = sorted(frame.case.unique())
        assert len(frame) == len(cases) * 12
        values = frame[[*SCORES, "alignment"]].to_numpy().reshape(len(cases), 12, 4)
        point = np.array([partial(frame, score) for score in SCORES])
        rng = np.random.default_rng(20261026 if dataset == "fastmri" else 20261027)
        draws = []
        for ids in rng.integers(0, len(cases), (2000, len(cases))):
            sample = pd.DataFrame(values[ids].reshape(-1, 4), columns=[*SCORES, "alignment"])
            estimates = np.array([partial(sample, score) for score in SCORES])
            draws.append([estimates[0] - estimates[1], estimates[0] - estimates[2]])
        draws = np.asarray(draws)
        results.append({"dataset": dataset, "cases": len(cases),
                        "true_minus_placebo_a": float(point[0] - point[1]),
                        "true_minus_placebo_b": float(point[0] - point[2]),
                        "ci95_case_bootstrap_exploratory": {
                            "true_minus_placebo_a": np.percentile(draws[:, 0], [2.5, 97.5]).tolist(),
                            "true_minus_placebo_b": np.percentile(draws[:, 1], [2.5, 97.5]).tolist()}})
    OUT.mkdir(parents=True)
    result = {"status": "post-result component sensitivity; not prespecified primary contrast",
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "results": results}
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
