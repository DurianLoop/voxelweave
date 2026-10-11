"""Join archived MSD case metrics for a post-result, same-neighbor baseline audit."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
NEURAL = ROOT / "experiments/msd_task01_tumor_roi_context/cases"
ANALYTIC = ROOT / "experiments/msd_task01_analytic_context_control/cases"
PROTOCOL = ROOT / "MSD_EQUAL_NEIGHBOR_LINEAR_AUDIT_PROTOCOL_2026-10-01.md"
OUT = ROOT / "experiments/msd_equal_neighbor_linear_audit"
REGIONS = ("lesion", "local_control")
MODELS = ("hat", "swinir")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def balanced(rows: list[dict], field: str) -> float:
    return float(np.mean([np.mean([row[field] for row in rows
                                   if row["residue"] == residue])
                          for residue in (1, 3)]))


def source_signature(item: dict) -> list[tuple[str, str]]:
    return [(entry["member"], entry["compressed_sha256"])
            for entry in item["source_files"]]


def case_pair(scan: str) -> tuple[dict, dict]:
    neural = json.loads((NEURAL / f"{scan}.json").read_text(encoding="utf-8"))
    analytic = json.loads((ANALYTIC / f"{scan}.json").read_text(encoding="utf-8"))
    if neural["scan"] != scan or analytic["scan"] != scan:
        raise ValueError(f"scan mismatch: {scan}")
    if neural["complete"] != analytic["complete"]:
        raise ValueError(f"completion mismatch: {scan}")
    return neural, analytic


def patient_metrics(scan: str, neural: dict, analytic: dict) -> tuple[dict, list[dict]]:
    if neural["targets"] != analytic["targets"] or source_signature(neural) != source_signature(analytic):
        raise ValueError(f"source or target contract mismatch: {scan}")
    expected = [(int(z), residue) for residue in (1, 3)
                for z in neural["targets"][str(residue)]]
    if len(expected) != 4 or [res for _, res in expected].count(1) != 2:
        raise ValueError(f"invalid target design: {scan}")
    if len(neural["rows"]) != 4 or len(analytic["rows"]) != 4:
        raise ValueError(f"missing rows: {scan}")
    per_target = []
    for (z, residue), nrow, arow in zip(expected, neural["rows"], analytic["rows"]):
        if (nrow["z"], nrow["residue"]) != (z, residue) or (arow["z"], arow["residue"]) != (z, residue):
            raise ValueError(f"target row mismatch: {scan} z{z}")
        result = {"scan": scan, "z": z, "residue": residue}
        for region in REGIONS:
            if nrow[region]["pixels"] != arow[region]["pixels"] or nrow[region]["pixels"] < 64:
                raise ValueError(f"ROI mismatch: {scan} z{z} {region}")
            result[f"{region}_pixels"] = nrow[region]["pixels"]
            result[f"{region}_linear_mse"] = arow[region]["shared"]["b_mse"]
            result[f"{region}_hat_mse"] = nrow[region]["shared"]["a_mse"]
            result[f"{region}_swinir_mse"] = nrow[region]["shared"]["b_mse"]
            for method in ("linear", *MODELS):
                value = result[f"{region}_{method}_mse"]
                if not np.isfinite(value) or value < 0:
                    raise ValueError(f"invalid MSE: {scan} z{z} {region} {method}")
            for model in MODELS:
                result[f"{region}_{model}_minus_linear"] = (
                    result[f"{region}_{model}_mse"] - result[f"{region}_linear_mse"])
        per_target.append(result)
    patient = {"scan": scan}
    for region in REGIONS:
        for method in ("linear", *MODELS):
            field = f"{region}_{method}_mse"
            patient[field] = balanced(per_target, field)
        for model in MODELS:
            field = f"{region}_{model}_minus_linear"
            patient[field] = balanced(per_target, field)
            linear = patient[f"{region}_linear_mse"]
            patient[f"{region}_{model}_ratio"] = (
                patient[f"{region}_{model}_mse"] / linear if linear > 0 else None)
    for model in MODELS:
        patient[f"{model}_lesion_minus_local_excess"] = (
            patient[f"lesion_{model}_minus_linear"] -
            patient[f"local_control_{model}_minus_linear"])
    return patient, per_target


def describe(patients: list[dict], field: str, draws: np.ndarray) -> dict:
    values = np.array([p[field] for p in patients], dtype=np.float64)
    means = values[draws].mean(axis=1)
    return {"mean": float(values.mean()),
            "bootstrap_95_percentile": [float(x) for x in np.percentile(means, [2.5, 97.5])],
            "positive_patients": int(np.sum(values > 0)),
            "negative_patients": int(np.sum(values < 0)),
            "tied_patients": int(np.sum(values == 0))}


def save_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    neural_ids = sorted(path.stem for path in NEURAL.glob("BRATS_*.json"))
    analytic_ids = sorted(path.stem for path in ANALYTIC.glob("BRATS_*.json"))
    if neural_ids != analytic_ids or len(neural_ids) != 484:
        raise ValueError("The two archives do not contain the same 484 cases")
    patients, targets, failures = [], [], []
    for scan in neural_ids:
        neural, analytic = case_pair(scan)
        if not neural["complete"]:
            failures.append({"scan": scan,
                             "neural_failure_stage": neural.get("failure_stage"),
                             "analytic_failure_stage": analytic.get("failure_stage")})
            continue
        patient, rows = patient_metrics(scan, neural, analytic)
        patients.append(patient)
        targets.extend(rows)
    if len(patients) != 483 or len(targets) != 1932 or [x["scan"] for x in failures] != ["BRATS_044"]:
        raise ValueError("Frozen attempted/complete/target denominator changed")
    rng = np.random.default_rng(20261007)
    draws = rng.integers(0, len(patients), size=(5000, len(patients)))
    results = {}
    for region in REGIONS:
        results[region] = {"linear_mse": describe(patients, f"{region}_linear_mse", draws)}
        for model in MODELS:
            ratios = np.array([p[f"{region}_{model}_ratio"] for p in patients
                               if p[f"{region}_{model}_ratio"] is not None])
            results[region][model] = {
                "mse": describe(patients, f"{region}_{model}_mse", draws),
                "minus_linear": describe(patients, f"{region}_{model}_minus_linear", draws),
                "ratio_valid_patients": len(ratios),
                "patient_ratio_median_iqr": [float(x) for x in np.percentile(ratios, [50, 25, 75])]}
    results["lesion_minus_local_excess"] = {
        model: describe(patients, f"{model}_lesion_minus_local_excess", draws)
        for model in MODELS}
    summary = {"status": "post-result exploratory", "cases_attempted": 484,
               "cases_complete": len(patients), "targets_complete": len(targets),
               "failures": failures, "bootstrap_draws": 5000, "bootstrap_seed": 20261007,
               "protocol_sha256": sha256(PROTOCOL),
               "neural_run_contract_sha256": sha256(NEURAL.parent / "run_contract.json"),
               "analytic_run_contract_sha256": sha256(ANALYTIC.parent / "run_contract.json"),
               "results": results}
    OUT.mkdir(parents=True, exist_ok=True)
    save_csv(OUT / "per_target.csv", targets)
    save_csv(OUT / "per_patient.csv", patients)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
