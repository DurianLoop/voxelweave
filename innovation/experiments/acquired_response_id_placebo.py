"""CPU-only physical-anchor response mismatch controls from archived NPZ arrays."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "design/paper/FINAL_SCIENTIFIC_STRENGTHENING"
SOURCE = PAPER / "acquired_only_influence.csv"
ARRAYS = PAPER / "outputs/acquired_responses"
REF = (-2, 2)
SCORES = ("influence", "placebo_a", "placebo_b")


def partial_rank(frame: pd.DataFrame, score: str) -> float:
    ranked = np.stack([rankdata(frame[score]), rankdata(frame.alignment)], axis=1)
    ranked = ranked.reshape(-1, 4, 2)
    residual = ranked - ranked.mean(axis=1, keepdims=True)
    residual -= residual.mean(axis=0, keepdims=True)
    x, y = residual[:, :, 0].ravel(), residual[:, :, 1].ravel()
    return float((x @ y) / np.sqrt((x @ x) * (y @ y)))


def score_target(rows: pd.DataFrame) -> list[dict]:
    dataset, model, case, z = rows.iloc[0][["dataset", "model", "case", "z"]]
    path = ARRAYS / f"{dataset}_{model}_{case}_z{z}.npz"
    blob = path.read_bytes()
    actual_hash = hashlib.sha256(blob).hexdigest()
    if rows.source_hash.nunique() != 1 or actual_hash != rows.source_hash.iloc[0]:
        raise AssertionError(f"Response source hash mismatch: {path}")
    with np.load(io.BytesIO(blob)) as arrays:
        contexts = [tuple(pair) for pair in arrays["contexts"]]
        if contexts[0] != REF or len(contexts) != 9 or arrays["epsilons"][0] != .01:
            raise AssertionError(f"Context or epsilon mismatch: {path}")
        response = arrays["response"][0]
    ref = response[0].astype(np.float64)
    ref_energy = float(np.sum(ref * ref))
    result = []
    for _, row in rows.iterrows():
        context = tuple(int(value) for value in row.context.strip("()").split(","))
        if context not in contexts or len(set(context) & set(REF)) != 1:
            raise AssertionError(f"Unexpected one-overlap context: {context}")
        candidate = response[contexts.index(context)].astype(np.float64)
        denominator = np.sqrt(ref_energy * float(np.sum(candidate * candidate)))
        if denominator <= 0:
            raise AssertionError(f"Zero response energy: {path}")
        shared = next(anchor for anchor in REF if anchor in context)
        ri, ci = REF.index(shared), context.index(shared)
        scores = {
            "influence_recomputed": float(np.sum(ref[ri] * candidate[ci]) / denominator),
            "placebo_a": float(np.sum(ref[ri] * candidate[1 - ci]) / denominator),
            "placebo_b": float(np.sum(ref[1 - ri] * candidate[ci]) / denominator),
        }
        if abs(scores["influence_recomputed"] - row.influence) > 1e-7:
            raise AssertionError(f"Original influence not reproduced: {path}/{context}")
        result.append({"dataset": dataset, "model": model, "case": case, "z": z,
                       "context": row.context, "alignment": row.alignment,
                       "influence": row.influence, **scores})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=("fastmri", "ixi"), required=True)
    args = parser.parse_args()
    output = ROOT / "innovation/experiments" / f"acquired_response_id_placebo_{args.dataset}"
    if output.exists():
        raise FileExistsError(output)
    raw = pd.read_csv(SOURCE)
    raw = raw[(raw.dataset == args.dataset) & (raw.epsilon == .01) &
              (raw.overlap_count == 1)].copy()
    raw = raw.sort_values(["model", "case", "z", "context"])
    records = []
    for (model, case, z), group in raw.groupby(["model", "case", "z"], sort=True):
        if len(group) != 4:
            raise AssertionError("Unbalanced context set")
        records.extend(score_target(group))
        if len(records) % 120 == 0:
            print(f"{args.dataset} {model} verified targets={len(records) // 4}", flush=True)
    data = pd.DataFrame(records).sort_values(["model", "case", "z", "context"])
    results = []
    for model, frame in data.groupby("model"):
        cases = sorted(frame.case.unique())
        assert len(frame) == len(cases) * 12
        expected_contexts = tuple(sorted(frame.context.unique()))
        assert len(expected_contexts) == 4
        assert frame.groupby(["case", "z"]).context.apply(
            lambda x: tuple(x) == expected_contexts).all()
        values = frame[[*SCORES, "alignment"]].to_numpy().reshape(len(cases), 12, 4)
        points = {score: partial_rank(frame, score) for score in SCORES}
        point_difference = points["influence"] - .5 * (
            points["placebo_a"] + points["placebo_b"])
        rng = np.random.default_rng(20261012 if model == "hat" else 20261013)
        draws = []
        for ids in rng.integers(0, len(cases), (1000, len(cases))):
            sample = pd.DataFrame(values[ids].reshape(-1, 4), columns=[*SCORES, "alignment"])
            numbers = [partial_rank(sample, score) for score in SCORES]
            draws.append(numbers[0] - .5 * (numbers[1] + numbers[2]))
        results.append({"dataset": args.dataset, "model": model,
                        "cases": len(cases), "targets": len(cases) * 3,
                        "scores_partial_rank": points,
                        "true_minus_mean_placebo": point_difference,
                        "ci95_case_bootstrap_exploratory": np.percentile(draws, [2.5, 97.5]).tolist(),
                        "max_abs_original_reproduction_error": float(np.max(np.abs(
                            frame.influence - frame.influence_recomputed)))})
    output.mkdir(parents=True)
    data.to_csv(output / "per_context.csv", index=False)
    summary = {"status": "post-result response-label placebo; not physical causal randomization",
               "source_csv_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "array_files_sha256_verified": data.groupby(["model", "case", "z"]).ngroups,
               "results": results}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
