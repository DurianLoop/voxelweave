"""Read-only HAT-to-SwinIR response and heldout-prediction audit on old cohorts."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "design/paper/FINAL_SCIENTIFIC_STRENGTHENING"
SOURCE = PAPER / "acquired_only_influence.csv"
MANIFEST = PAPER / "prepared_input_manifest.json"
ARRAYS = PAPER / "outputs/acquired_responses"
REF = (-2, 2)
SCORES = ("influence", "placebo_a", "placebo_b")


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def load_array(path: Path, expected: str) -> dict:
    blob = path.read_bytes()
    if sha256(blob) != expected:
        raise AssertionError(f"Hash mismatch: {path}")
    with np.load(io.BytesIO(blob)) as data:
        return {name: data[name] for name in data.files}


def score_target(dataset: str, case: str, z: int, rows: pd.DataFrame,
                 manifest: dict[str, str]) -> list[dict]:
    archives = {}
    for model in ("hat", "swinir"):
        source = rows[rows.model == model]
        if len(source) != 4 or source.source_hash.nunique() != 1:
            raise AssertionError("Missing archived model response")
        archives[model] = load_array(
            ARRAYS / f"{dataset}_{model}_{case}_z{z}.npz", source.source_hash.iloc[0])
    hat, swinir = archives["hat"], archives["swinir"]
    contexts = [tuple(pair) for pair in hat["contexts"]]
    if (contexts[0] != REF or not np.array_equal(hat["contexts"], swinir["contexts"]) or
            not np.array_equal(hat["mask"], swinir["mask"]) or
            hat["lo"] != swinir["lo"] or hat["scale"] != swinir["scale"] or
            hat["epsilons"][0] != .01 or swinir["epsilons"][0] != .01):
        raise AssertionError(f"Unequal model information contract: {dataset}/{case}/z{z}")
    target_name = f"targets/{dataset}_{case}_z{z}.npy"
    target_path = PAPER / target_name
    target_blob = target_path.read_bytes()
    if sha256(target_blob) != manifest[target_name]:
        raise AssertionError(f"Target hash mismatch: {target_path}")
    target = np.load(io.BytesIO(target_blob))
    mask = hat["mask"]
    if target.shape != mask.shape:
        raise AssertionError("Target/mask shape mismatch")
    reference_error = (hat["base"][0][mask] - target[mask]).astype(np.float64)
    ref_response = hat["response"][0, 0].astype(np.float64)
    ref_energy = float(np.sum(ref_response * ref_response))
    results = []
    for context in ((-2, 1), (-2, 3), (-1, 2), (-3, 2)):
        ci = contexts.index(context)
        candidate_error = (swinir["base"][ci][mask] - target[mask]).astype(np.float64)
        cosine = float((reference_error @ candidate_error) /
                       np.sqrt((reference_error @ reference_error) *
                               (candidate_error @ candidate_error)))
        candidate_response = swinir["response"][0, ci].astype(np.float64)
        denominator = np.sqrt(ref_energy * float(np.sum(candidate_response ** 2)))
        if denominator <= 0 or not np.isfinite(cosine):
            raise AssertionError("Nonfinite score or error cosine")
        shared = next(anchor for anchor in REF if anchor in context)
        ri, other_i = REF.index(shared), context.index(shared)
        scores = {
            "influence": float(np.sum(ref_response[ri] *
                                      candidate_response[other_i]) / denominator),
            "placebo_a": float(np.sum(ref_response[ri] *
                                      candidate_response[1 - other_i]) / denominator),
            "placebo_b": float(np.sum(ref_response[1 - ri] *
                                      candidate_response[other_i]) / denominator),
        }
        results.append({"dataset": dataset, "case": case, "z": z,
                        "context": str(context), "alignment": cosine, **scores})
    return results


def partial_rank(frame: pd.DataFrame, score: str) -> float:
    ranked = np.stack([rankdata(frame[score]), rankdata(frame.alignment)], axis=1)
    ranked = ranked.reshape(-1, 4, 2)
    residual = ranked - ranked.mean(axis=1, keepdims=True)
    residual -= residual.mean(axis=0, keepdims=True)
    x, y = residual[:, :, 0].ravel(), residual[:, :, 1].ravel()
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def features(frame: pd.DataFrame, contexts: list[str], with_influence: bool) -> np.ndarray:
    columns = [(frame.context.to_numpy() == context).astype(float)
               for context in contexts[1:]]
    if with_influence:
        columns.append(frame.influence.to_numpy(dtype=float))
    return np.column_stack(columns)


def predict(train: pd.DataFrame, test: pd.DataFrame, contexts: list[str],
            with_influence: bool) -> np.ndarray:
    a, b = features(train, contexts, with_influence), features(test, contexts, with_influence)
    mean, scale = a.mean(axis=0), a.std(axis=0)
    scale[scale == 0] = 1
    a, b = (a - mean) / scale, (b - mean) / scale
    y = train.alignment.to_numpy(dtype=float)
    center = y.mean()
    coefficient = np.linalg.solve(a.T @ a + np.eye(a.shape[1]), a.T @ (y - center))
    return center + b @ coefficient


def analyze(frame: pd.DataFrame, dataset: str) -> tuple[dict, pd.DataFrame]:
    cases = sorted(frame.case.unique())
    contexts = sorted(frame.context.unique())
    assert len(frame) == len(cases) * 12 and len(contexts) == 4
    assert frame.groupby(["case", "z"]).context.apply(
        lambda x: tuple(x) == tuple(contexts)).all()
    points = {score: partial_rank(frame, score) for score in SCORES}
    difference = points["influence"] - .5 * (points["placebo_a"] + points["placebo_b"])
    values = frame[[*SCORES, "alignment"]].to_numpy().reshape(len(cases), 12, 4)
    rng = np.random.default_rng(20261015 if dataset == "fastmri" else 20261016)
    draws = []
    for ids in rng.integers(0, len(cases), (1000, len(cases))):
        sample = pd.DataFrame(values[ids].reshape(-1, 4), columns=[*SCORES, "alignment"])
        numbers = [partial_rank(sample, score) for score in SCORES]
        draws.append(numbers[0] - .5 * (numbers[1] + numbers[2]))

    rng = np.random.default_rng(20261017)
    predictions = []
    for fold, heldout in enumerate(np.array_split(rng.permutation(cases), 5)):
        test = frame[frame.case.isin(heldout)].copy()
        train = frame[~frame.case.isin(heldout)]
        test["fold"] = fold
        test["context_prediction"] = predict(train, test, contexts, False)
        test["context_plus_influence_prediction"] = predict(train, test, contexts, True)
        predictions.append(test)
    output = pd.concat(predictions, ignore_index=True)
    for mode in ("context", "context_plus_influence"):
        output[f"{mode}_absolute_error"] = np.abs(
            output.alignment - output[f"{mode}_prediction"])
    by_case = output.groupby("case")[["context_absolute_error",
                                      "context_plus_influence_absolute_error"]].mean()
    gain = (by_case.context_absolute_error -
            by_case.context_plus_influence_absolute_error).to_numpy()
    rng = np.random.default_rng(20261018)
    gains = gain[rng.integers(0, len(gain), (5000, len(gain)))].mean(axis=1)
    rankings = {mode: float(np.mean([
        spearmanr(group.alignment, group[f"{mode}_prediction"]).statistic
        for _, group in output.groupby(["case", "z"])]))
        for mode in ("context", "context_plus_influence")}
    result = {"dataset": dataset, "cases": len(cases), "targets": len(cases) * 3,
              "partial_rank_target_and_context": points,
              "true_minus_mean_placebo": difference,
              "placebo_ci95_case_bootstrap_exploratory": np.percentile(draws, [2.5, 97.5]).tolist(),
              "heldout_mae": {mode: float(output[f"{mode}_absolute_error"].mean())
                              for mode in ("context", "context_plus_influence")},
              "heldout_case_equal_mae_gain": float(gain.mean()),
              "heldout_gain_ci95_case_bootstrap_exploratory": np.percentile(gains, [2.5, 97.5]).tolist(),
              "cases_plus_better": int((gain > 0).sum()),
              "target_mean_spearman": rankings}
    return result, output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=("fastmri", "ixi"), required=True)
    args = parser.parse_args()
    output = ROOT / "innovation/experiments" / f"cross_arch_acquired_response_{args.dataset}"
    if output.exists():
        raise FileExistsError(output)
    manifest = {item["path"].replace("\\", "/"): item["sha256"]
                for item in json.loads(MANIFEST.read_text(encoding="utf-8"))}
    raw = pd.read_csv(SOURCE)
    raw = raw[(raw.dataset == args.dataset) & (raw.epsilon == .01) &
              (raw.overlap_count == 1)].copy()
    rows = []
    for index, ((case, z), group) in enumerate(raw.groupby(["case", "z"], sort=True), 1):
        rows.extend(score_target(args.dataset, case, int(z), group, manifest))
        if index % 30 == 0:
            print(f"{args.dataset} verified targets={index}", flush=True)
    frame = pd.DataFrame(rows).sort_values(["case", "z", "context"])
    result, predictions = analyze(frame, args.dataset)
    output.mkdir(parents=True)
    frame.to_csv(output / "per_context.csv", index=False)
    predictions.to_csv(output / "out_of_fold_predictions.csv", index=False)
    summary = {"status": "post-result old-cohort cross-architecture diagnostic",
               "source_csv_sha256": sha256(SOURCE.read_bytes()),
               "prepared_manifest_sha256": sha256(MANIFEST.read_bytes()),
               "script_sha256": sha256(Path(__file__).read_bytes()),
               "response_files_sha256_verified": 2 * result["targets"],
               "target_files_sha256_verified": result["targets"], **result}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
