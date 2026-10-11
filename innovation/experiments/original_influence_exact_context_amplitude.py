"""Post-result amplitude sensitivity with exact target/context adjustment."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "design/paper/FINAL_SCIENTIFIC_STRENGTHENING/acquired_only_influence.csv"
OUT = ROOT / "innovation/experiments/original_influence_exact_context_amplitude"
EPSILONS = (.01, .005, .02, -.01)


def partial_rank(frame: pd.DataFrame) -> float:
    x = rankdata(frame.influence).reshape(-1, 4)
    y = rankdata(frame.alignment).reshape(-1, 4)
    x = x - x.mean(axis=1, keepdims=True)
    y = y - y.mean(axis=1, keepdims=True)
    x = x - x.mean(axis=0, keepdims=True)
    y = y - y.mean(axis=0, keepdims=True)
    return float(np.sum(x * y) / np.sqrt(np.sum(x * x) * np.sum(y * y)))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    data = pd.read_csv(SOURCE)
    data = data[data.overlap_count == 1]
    rows = []
    for (dataset, model, epsilon), frame in data.groupby(["dataset", "model", "epsilon"]):
        frame = frame.sort_values(["case", "z", "context"])
        cases = frame.case.nunique()
        assert epsilon in EPSILONS and len(frame) == cases * 12
        contexts = tuple(sorted(frame.context.unique()))
        assert len(contexts) == 4
        assert frame.groupby(["case", "z"]).context.apply(
            lambda x: tuple(x) == contexts).all()
        rows.append({"dataset": dataset, "model": model, "epsilon": epsilon,
                     "cases": cases, "targets": cases * 3,
                     "target_and_exact_context_partial_rank": partial_rank(frame)})
    result = {"status": "post-result amplitude/sign sensitivity; descriptive",
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "rows": rows}
    OUT.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
