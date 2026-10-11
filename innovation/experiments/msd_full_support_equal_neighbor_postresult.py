"""CPU-only full-foreground replay of MSD two-neighbor linear baselines."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from msd_pipeline_linear_preflight import ROOT, score_scan


PROTOCOL = ROOT / "MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_PLAN_2026-10-01.md"
NEURAL = ROOT / "experiments/msd_task01_tumor_roi_context/cases"
OUT = ROOT / "experiments/msd_full_support_equal_neighbor_postresult"
METHODS = ("raw_linear", "pipeline_linear", "hat", "swinir")


def save_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def describe(patients: list[dict], field: str, draws: np.ndarray) -> dict:
    values = np.array([row[field] for row in patients], dtype=np.float64)
    return {"mean": float(values.mean()),
            "bootstrap_95_percentile": [float(x) for x in np.percentile(values[draws].mean(axis=1), [2.5, 97.5])],
            "positive_patients": int(np.sum(values > 0)),
            "negative_patients": int(np.sum(values < 0)),
            "tied_patients": int(np.sum(values == 0))}


def main() -> None:
    ids = sorted(path.stem for path in NEURAL.glob("BRATS_*.json"))
    if len(ids) != 484:
        raise ValueError("Expected 484 frozen MSD IDs")
    patients, targets, failures = [], [], []
    for count, scan in enumerate(ids, 1):
        neural = json.loads((NEURAL / f"{scan}.json").read_text(encoding="utf-8"))
        if not neural["complete"]:
            failures.append(scan)
            continue
        replay = score_scan(scan)
        if (replay["complete_targets"] != 4 or len(neural["rows"]) != 4 or
                replay["source_sha256"] != [entry["compressed_sha256"] for entry in neural["source_files"]]):
            raise ValueError(f"Source/target contract mismatch: {scan}")
        per_target = []
        for replay_row, neural_row in zip(replay["rows"], neural["rows"]):
            if ((replay_row["z"], replay_row["residue"]) !=
                    (neural_row["z"], neural_row["residue"]) or
                    replay_row["full_support_pixels"] != neural_row["full_support"]["pixels"]):
                raise ValueError(f"Target/support mismatch: {scan}")
            row = {"scan": scan, "z": replay_row["z"],
                   "residue": replay_row["residue"],
                   "support_pixels": replay_row["full_support_pixels"],
                   "raw_linear_mse": replay_row["full_support_raw_linear_mse"],
                   "pipeline_linear_mse": replay_row["full_support_pipeline_linear_mse"],
                   "hat_mse": neural_row["full_support"]["shared"]["a_mse"],
                   "swinir_mse": neural_row["full_support"]["shared"]["b_mse"]}
            if not all(np.isfinite(row[f"{method}_mse"]) and row[f"{method}_mse"] >= 0
                       for method in METHODS):
                raise ValueError(f"Nonfinite/negative MSE: {scan}")
            per_target.append(row)
            targets.append(row)
        patient = {"scan": scan}
        for method in METHODS:
            patient[f"{method}_mse"] = float(np.mean([
                np.mean([row[f"{method}_mse"] for row in per_target
                         if row["residue"] == residue]) for residue in (1, 3)]))
        for model in ("hat", "swinir"):
            for baseline in ("raw_linear", "pipeline_linear"):
                patient[f"{model}_minus_{baseline}"] = (
                    patient[f"{model}_mse"] - patient[f"{baseline}_mse"])
        patients.append(patient)
        if count % 25 == 0 or count == 484:
            print(f"full-support source cases {count}/484", flush=True)
    if len(patients) != 483 or len(targets) != 1932 or failures != ["BRATS_044"]:
        raise ValueError("Frozen denominator changed")
    rng = np.random.default_rng(20261011)
    draws = rng.integers(0, 483, size=(5000, 483))
    fields = [f"{method}_mse" for method in METHODS]
    fields += [f"{model}_minus_{baseline}" for model in ("hat", "swinir")
               for baseline in ("raw_linear", "pipeline_linear")]
    summary = {"status": "post-result exploratory", "cases_attempted": 484,
               "cases_complete": len(patients), "targets_complete": len(targets),
               "failures": failures, "bootstrap_seed": 20261011,
               "bootstrap_draws": 5000,
               "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
               "gpu_used": False,
               "results": {field: describe(patients, field, draws) for field in fields}}
    OUT.mkdir(parents=True, exist_ok=True)
    save_csv(OUT / "per_target.csv", targets)
    save_csv(OUT / "per_patient.csv", patients)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value["mean"] for key, value in summary["results"].items()}, indent=2))


if __name__ == "__main__":
    main()
