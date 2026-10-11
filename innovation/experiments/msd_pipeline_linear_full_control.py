"""CPU-only full-case replay of raw versus model-pipeline linear interpolation."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from msd_pipeline_linear_preflight import ROOT, score_scan


PROTOCOL = ROOT / "MSD_PIPELINE_LINEAR_CONTROL_PROTOCOL_2026-10-01.md"
NEURAL = ROOT / "experiments/msd_task01_tumor_roi_context/cases"
ANALYTIC = ROOT / "experiments/msd_task01_analytic_context_control/cases"
OUT = ROOT / "experiments/msd_pipeline_linear_full_control"
REGIONS = ("lesion", "local_control")
MODELS = ("hat", "swinir")


def mean_ci(patients: list[dict], field: str, draws: np.ndarray) -> dict:
    values = np.array([row[field] for row in patients], dtype=np.float64)
    bounds = np.percentile(values[draws].mean(axis=1), [2.5, 97.5])
    return {"mean": float(values.mean()),
            "bootstrap_95_percentile": [float(x) for x in bounds],
            "positive_patients": int(np.sum(values > 0)),
            "negative_patients": int(np.sum(values < 0)),
            "tied_patients": int(np.sum(values == 0))}


def save_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ids = sorted(path.stem for path in NEURAL.glob("BRATS_*.json"))
    if ids != sorted(path.stem for path in ANALYTIC.glob("BRATS_*.json")) or len(ids) != 484:
        raise ValueError("Frozen case archives differ")
    patients, targets, failures = [], [], []
    for index, scan in enumerate(ids, 1):
        neural = json.loads((NEURAL / f"{scan}.json").read_text(encoding="utf-8"))
        analytic = json.loads((ANALYTIC / f"{scan}.json").read_text(encoding="utf-8"))
        if neural["complete"] != analytic["complete"]:
            raise ValueError(f"Completion mismatch: {scan}")
        if not neural["complete"]:
            failures.append(scan)
            continue
        if (neural["targets"] != analytic["targets"] or len(neural["rows"]) != 4 or
                len(analytic["rows"]) != 4 or
                [(x["member"], x["compressed_sha256"]) for x in neural["source_files"]] !=
                [(x["member"], x["compressed_sha256"]) for x in analytic["source_files"]]):
            raise ValueError(f"Frozen source/target contract mismatch: {scan}")
        replay = score_scan(scan)
        if replay["complete_targets"] != 4 or replay["source_sha256"] != [
                x["compressed_sha256"] for x in neural["source_files"]]:
            raise ValueError(f"Replay source or target count mismatch: {scan}")
        patient = {"scan": scan}
        for region in REGIONS:
            for method in ("raw_linear", "pipeline_linear", *MODELS):
                values = []
                for replay_row, neural_row in zip(replay["rows"], neural["rows"]):
                    if (replay_row["z"], replay_row["residue"]) != (
                            neural_row["z"], neural_row["residue"]):
                        raise ValueError(f"Frozen target mismatch: {scan}")
                    if replay_row[f"{region}_pixels"] != neural_row[region]["pixels"]:
                        raise ValueError(f"Frozen ROI mismatch: {scan} {region}")
                    if method in MODELS:
                        key = "a_mse" if method == "hat" else "b_mse"
                        value = neural_row[region]["shared"][key]
                    else:
                        value = replay_row[f"{region}_{method}_mse"]
                    if not np.isfinite(value) or value < 0:
                        raise ValueError(f"Invalid MSE: {scan} {region} {method}")
                    values.append(float(value))
                    if method == "raw_linear":
                        targets.append({"scan": scan, "z": replay_row["z"],
                                        "residue": replay_row["residue"],
                                        "region": region, "raw_linear_mse": float(value),
                                        "pipeline_linear_mse": replay_row[f"{region}_pipeline_linear_mse"],
                                        "hat_mse": neural_row[region]["shared"]["a_mse"],
                                        "swinir_mse": neural_row[region]["shared"]["b_mse"]})
                patient[f"{region}_{method}_mse"] = float(np.mean(values))
            raw = patient[f"{region}_raw_linear_mse"]
            pipeline = patient[f"{region}_pipeline_linear_mse"]
            patient[f"{region}_pipeline_minus_raw"] = pipeline - raw
            for model in MODELS:
                patient[f"{region}_{model}_minus_raw"] = patient[f"{region}_{model}_mse"] - raw
                patient[f"{region}_{model}_minus_pipeline"] = patient[f"{region}_{model}_mse"] - pipeline
        patients.append(patient)
        if index % 25 == 0 or index == 484:
            print(f"pipeline-linear source cases {index}/484", flush=True)
    if len(patients) != 483 or len(targets) != 3864 or failures != ["BRATS_044"]:
        raise ValueError("Frozen 484/483/1932 denominator changed")
    rng = np.random.default_rng(20261008)
    draws = rng.integers(0, len(patients), size=(5000, len(patients)))
    result = {}
    for region in REGIONS:
        fields = [f"{region}_{method}_mse" for method in ("raw_linear", "pipeline_linear", *MODELS)]
        fields += [f"{region}_pipeline_minus_raw"]
        for model in MODELS:
            fields.extend((f"{region}_{model}_minus_raw", f"{region}_{model}_minus_pipeline"))
        result[region] = {field.removeprefix(f"{region}_"): mean_ci(patients, field, draws)
                          for field in fields}
        result[region]["pipeline_excess_over_model_excess_mean_ratio"] = {
            model: result[region]["pipeline_minus_raw"]["mean"] /
                   result[region][f"{model}_minus_raw"]["mean"]
            for model in MODELS}
    summary = {"status": "post-result, post-first-case-pilot exploratory",
               "cases_attempted": 484, "cases_complete": len(patients),
               "targets_complete": len(targets) // 2, "failures": failures,
               "bootstrap_seed": 20261008, "bootstrap_draws": 5000,
               "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
               "gpu_used": False, "results": result}
    OUT.mkdir(parents=True, exist_ok=True)
    save_csv(OUT / "per_patient.csv", patients)
    save_csv(OUT / "per_target_region.csv", targets)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({region: {key: value["mean"] for key, value in result[region].items()
                               if isinstance(value, dict) and "mean" in value}
                      for region in REGIONS}, indent=2))


if __name__ == "__main__":
    main()
