"""CPU-only SAINT response-label controls from archived acquired-only arrays."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[2]
CLOSURE = ROOT / "design/paper/ARCHITECTURE_COVERAGE_CLOSURE"
SOURCE = CLOSURE / "outputs/saint_acquired_observations.csv"
ARRAYS = CLOSURE / "outputs/acquired_responses"
OUT = ROOT / "innovation/experiments/saint_response_id_placebo"
REF = (-2, 2)
SCORES = ("influence", "placebo_a", "placebo_b")


def score_target(rows: pd.DataFrame) -> list[dict]:
    dataset, case, z = rows.iloc[0][["dataset", "case", "z"]]
    path = ARRAYS / f"{dataset}_saint_{case}_z{z}.npz"
    blob = path.read_bytes()
    if rows.source_hash.nunique() != 1 or hashlib.sha256(blob).hexdigest() != rows.source_hash.iloc[0]:
        raise AssertionError(f"NPZ hash mismatch: {path}")
    with np.load(io.BytesIO(blob)) as data:
        contexts = [tuple(pair) for pair in data["contexts"]]
        if contexts[0] != REF or len(contexts) != 9 or data["epsilons"][0] != .01:
            raise AssertionError(f"Context contract changed: {path}")
        response = data["response"][0]
    reference = response[0].astype(np.float64)
    ref_energy = float(np.sum(reference * reference))
    scored = []
    for _, row in rows.iterrows():
        context = tuple(int(value) for value in row.context.strip("()").split(","))
        if context not in contexts or len(set(context) & set(REF)) != 1:
            raise AssertionError(f"Unexpected context: {context}")
        candidate = response[contexts.index(context)].astype(np.float64)
        denominator = np.sqrt(ref_energy * float(np.sum(candidate * candidate)))
        if denominator <= 0:
            raise AssertionError(f"Zero response energy: {path}")
        shared = next(anchor for anchor in REF if anchor in context)
        ri, ci = REF.index(shared), context.index(shared)
        correct = float(np.sum(reference[ri] * candidate[ci]) / denominator)
        if abs(correct - row.influence) > 1e-7:
            raise AssertionError(f"Original influence mismatch: {path}/{context}")
        scored.append({"dataset": dataset, "model": "saint", "case": case,
                       "z": z, "context": row.context, "alignment": row.alignment,
                       "influence": row.influence, "influence_recomputed": correct,
                       "placebo_a": float(np.sum(reference[ri] * candidate[1 - ci]) / denominator),
                       "placebo_b": float(np.sum(reference[1 - ri] * candidate[ci]) / denominator)})
    return scored


def partial_rank(frame: pd.DataFrame, score: str) -> float:
    matrix = np.stack([rankdata(frame[score]), rankdata(frame.alignment)], axis=1)
    matrix = matrix.reshape(-1, 4, 2)
    residual = matrix - matrix.mean(axis=1, keepdims=True)
    residual -= residual.mean(axis=0, keepdims=True)
    x, y = residual[:, :, 0].ravel(), residual[:, :, 1].ravel()
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    raw = pd.read_csv(SOURCE)
    raw = raw[(raw.epsilon == .01) & (raw.overlap_count == 1)].sort_values(
        ["dataset", "case", "z", "context"])
    records = []
    for index, (_, group) in enumerate(raw.groupby(["dataset", "case", "z"], sort=True), 1):
        if len(group) != 4:
            raise AssertionError("Unbalanced context set")
        records.extend(score_target(group))
        if index % 30 == 0:
            print(f"verified response targets={index}", flush=True)
    data = pd.DataFrame(records).sort_values(["dataset", "case", "z", "context"])
    results = []
    for dataset, frame in data.groupby("dataset"):
        cases = sorted(frame.case.unique())
        assert len(frame) == len(cases) * 12
        contexts = tuple(sorted(frame.context.unique()))
        assert len(contexts) == 4
        assert frame.groupby(["case", "z"]).context.apply(
            lambda x: tuple(x) == contexts).all()
        points = {score: partial_rank(frame, score) for score in SCORES}
        difference = points["influence"] - .5 * (points["placebo_a"] + points["placebo_b"])
        values = frame[[*SCORES, "alignment"]].to_numpy().reshape(len(cases), 12, 4)
        rng = np.random.default_rng(20261024 if dataset == "fastmri" else 20261025)
        draws = []
        for ids in rng.integers(0, len(cases), (1000, len(cases))):
            sample = pd.DataFrame(values[ids].reshape(-1, 4), columns=[*SCORES, "alignment"])
            p = [partial_rank(sample, score) for score in SCORES]
            draws.append(p[0] - .5 * (p[1] + p[2]))
        results.append({"dataset": dataset, "cases": len(cases),
                        "targets": len(cases) * 3,
                        "partial_rank_target_and_context": points,
                        "true_minus_mean_placebo": difference,
                        "ci95_case_bootstrap_exploratory": np.percentile(draws, [2.5, 97.5]).tolist(),
                        "max_abs_original_reproduction_error": float(np.max(np.abs(
                            frame.influence - frame.influence_recomputed)))})
    OUT.mkdir(parents=True)
    data.to_csv(OUT / "per_context.csv", index=False)
    summary = {"status": "post-result SAINT response-label placebo",
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "response_files_sha256_verified": data.groupby(["dataset", "case", "z"]).ngroups,
               "results": results}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
