"""Summarize only a complete 484-case frozen MSD tumor-ROI run."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "MSD_TASK01_TUMOR_ROI_CONTEXT_PROTOCOL_2026-10-01.md"
LABELS = ROOT / "experiments/msd_task01_label_qualification.json"
RUN = ROOT / "experiments/msd_task01_tumor_roi_context"
CONTRACT = RUN / "run_contract.json"
CASES = RUN / "cases"
OUT = RUN / "summary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interval(values: np.ndarray, indices: np.ndarray) -> list[float]:
    return [float(v) for v in np.percentile(values[indices].mean(axis=1), [2.5, 97.5])]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def region_descriptive(cases: list[dict], region: str, optional: bool = False) -> dict:
    fields = {
        "shared_o": ("shared", "observable"),
        "disjoint_o": ("disjoint", "observable"),
        "delta_o": ("delta_o",),
        "fixed_denominator_delta_o": ("delta_o_fixed_shared_denominator",),
        "hat_mse": ("shared", "a_mse"),
        "hat_mae": ("shared", "a_mae"),
        "shared_companion_mse": ("shared", "b_mse"),
        "disjoint_companion_mse": ("disjoint", "b_mse"),
        "shared_companion_mae": ("shared", "b_mae"),
        "disjoint_companion_mae": ("disjoint", "b_mae"),
        "shared_disagreement_mse": ("shared", "disagreement_mse"),
        "disjoint_disagreement_mse": ("disjoint", "disagreement_mse"),
        "shared_ensemble_mse": ("shared_ensemble_mse",),
        "disjoint_ensemble_mse": ("disjoint_ensemble_mse",),
        "pchip_mse": ("pchip_mse",),
    }
    case_values = {key: [] for key in fields}
    positive_targets = undefined_targets = positive_cases = all_four_cases = 0
    for case in cases:
        valid = []
        has_pixels = False
        for row in case["rows"]:
            item = row[region]
            if item is None:
                continue
            has_pixels = True
            positive_targets += 1
            if item.get("metric_undefined"):
                undefined_targets += 1
            else:
                valid.append((row["residue"], item))
        if has_pixels:
            positive_cases += 1
        if len(valid) == 4:
            all_four_cases += 1
        if not optional and len(valid) != 4:
            raise ValueError(f"Missing required {region} ROI in {case['scan']}")
        if not valid:
            continue
        for key, path in fields.items():
            def value(item: dict) -> float:
                current = item
                for part in path:
                    current = current[part]
                return current
            if optional:
                case_values[key].append(float(np.mean([value(item) for _, item in valid])))
            else:
                case_values[key].append(float(np.mean([
                    np.mean([value(item) for residue_row, item in valid
                             if residue_row == residue]) for residue in (1, 3)])))
    return {"aggregation": "patient-equal; optional subclasses average available targets per patient"
            if optional else "patient-equal; two targets within each residue, then residues equal",
            "patients_with_defined_metrics": len(case_values["delta_o"]),
            "patients_with_any_labeled_pixels": positive_cases,
            "patients_with_zero_labeled_pixels": len(cases) - positive_cases,
            "patients_with_all_four_defined_targets": all_four_cases,
            "positive_targets": positive_targets,
            "zero_pixel_targets": 4 * len(cases) - positive_targets,
            "undefined_metric_targets": undefined_targets,
            **{key: float(np.mean(values)) if values else None
               for key, values in case_values.items()}}


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of complete summary")
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (labels["cases_attempted"] != 484 or contract["attempted_cases"] != 484 or
            contract["protocol_sha256"] != sha256(PROTOCOL) or
            contract["label_qualification_sha256"] != sha256(LABELS)):
        raise ValueError("Frozen protocol or source contract changed")
    cases = []
    for label in labels["records"]:
        path = CASES / f"{label['scan']}.json"
        if not path.exists():
            raise ValueError(f"Missing attempt record: {label['scan']}")
        case = json.loads(path.read_text(encoding="utf-8"))
        if (case["scan"] != label["scan"] or
                case["protocol_sha256"] != contract["protocol_sha256"] or
                case["run_contract_sha256"] != sha256(CONTRACT)):
            raise ValueError(f"Case contract mismatch: {label['scan']}")
        cases.append(case)
    if len(list(CASES.glob("BRATS_*.json"))) != 484:
        raise ValueError("Unexpected case record count")
    complete = [case for case in cases if case["complete"]]
    failures = [case for case in cases if not case["complete"]]
    per_patient, per_target = [], []
    for case in complete:
        rows = case["rows"]
        if len(rows) != 4 or sorted(row["residue"] for row in rows) != [1, 1, 3, 3]:
            raise ValueError(f"Target contract mismatch: {case['scan']}")
        for row in rows:
            if row["lesion"]["pixels"] != row["local_control"]["pixels"]:
                raise ValueError(f"ROI area mismatch: {case['scan']}")
        expected_lesion = float(np.mean([
            np.mean([row["lesion"]["delta_o"] for row in rows if row["residue"] == residue])
            for residue in (1, 3)]))
        expected_local = float(np.mean([
            np.mean([row["local_control"]["delta_o"] for row in rows if row["residue"] == residue])
            for residue in (1, 3)]))
        summary = case["summary"]
        if (abs(summary["delta_o_lesion"] - expected_lesion) > 1e-9 or
                abs(summary["delta_o_local_control"] - expected_local) > 1e-9 or
                abs(summary["delta_o_lesion_minus_local"] - (expected_lesion - expected_local)) > 1e-9):
            raise ValueError(f"Patient aggregation mismatch: {case['scan']}")
        per_patient.append({"scan": case["scan"], **summary})
        for row in rows:
            per_target.append({"scan": case["scan"], "z": row["z"], "residue": row["residue"],
                "lesion_pixels": row["lesion"]["pixels"],
                "local_control_pixels": row["local_control"]["pixels"],
                "delta_o_lesion": row["lesion"]["delta_o"],
                "delta_o_local_control": row["local_control"]["delta_o"],
                "delta_o_full_support": row["full_support"]["delta_o"],
                "lesion_shared_paired_mse": row["lesion"]["shared"]["paired_mse"],
                "lesion_disjoint_paired_mse": row["lesion"]["disjoint"]["paired_mse"],
                "lesion_shared_ensemble_mse": row["lesion"]["shared_ensemble_mse"],
                "lesion_disjoint_ensemble_mse": row["lesion"]["disjoint_ensemble_mse"],
                "lesion_pchip_mse": row["lesion"]["pchip_mse"],
                "edema_pixels": row["edema_pixels"],
                "tumor_core_pixels": row["tumor_core_pixels"]})
    if not complete:
        raise ValueError("No complete patient")
    lesion = np.asarray([row["delta_o_lesion"] for row in per_patient], dtype=float)
    local = np.asarray([row["delta_o_local_control"] for row in per_patient], dtype=float)
    difference = lesion - local
    rng = np.random.default_rng(20261005)
    indices = rng.integers(0, len(complete), (5000, len(complete)))
    lesion_ci = interval(lesion, indices)
    difference_ci = interval(difference, indices)
    gain = np.asarray([
        100 * (row["lesion_pchip_mse"] - row["lesion_disjoint_ensemble_mse"]) /
        row["lesion_pchip_mse"] if row["lesion_pchip_mse"] > 0 else np.nan
        for row in per_patient], dtype=float)
    result = {"protocol_sha256": sha256(PROTOCOL), "run_contract_sha256": sha256(CONTRACT),
              "label_qualification_sha256": sha256(LABELS),
              "cases_attempted": len(cases), "cases_complete": len(complete),
              "targets_complete": len(per_target),
              "failure_counts": dict(Counter(case["failure_stage"] + ":" + case["failure_type"]
                                             for case in failures)),
              "failed_case_ids": [case["scan"] for case in failures],
              "primary_lesion_delta_o": float(lesion.mean()),
              "primary_lesion_delta_o_ci95": lesion_ci,
              "primary_lesion_minus_local_delta_o": float(difference.mean()),
              "primary_lesion_minus_local_ci95": difference_ci,
              "primary_success": len(complete) >= 350 and lesion_ci[0] > 0 and difference_ci[0] > 0,
              "positive_lesion_cases": int((lesion > 0).sum()),
              "positive_specificity_cases": int((difference > 0).sum()),
              "mean_local_delta_o": float(local.mean()),
              "mean_full_support_delta_o": float(np.mean([
                  row["delta_o_full_support"] for row in per_patient])),
              "mean_lesion_fixed_denominator_delta_o": float(np.mean([
                  row["delta_o_lesion_fixed_denominator"] for row in per_patient])),
              "mean_lesion_shared_ensemble_mse": float(np.mean([
                  row["lesion_shared_ensemble_mse"] for row in per_patient])),
              "mean_lesion_disjoint_ensemble_mse": float(np.mean([
                  row["lesion_disjoint_ensemble_mse"] for row in per_patient])),
              "mean_lesion_pchip_mse": float(np.mean([
                  row["lesion_pchip_mse"] for row in per_patient])),
              "mean_patient_relative_gain_over_pchip_percent":
                  float(np.nanmean(gain)) if np.isfinite(gain).any() else None,
              "edema_target_count": sum(row["edema_pixels"] > 0 for row in per_target),
              "tumor_core_target_count": sum(row["tumor_core_pixels"] > 0 for row in per_target),
              "gpu_used": False}
    result["region_descriptive"] = {
        region: region_descriptive(complete, region, region in ("edema", "tumor_core"))
        for region in ("lesion", "local_control", "full_support", "edema", "tumor_core")}
    write_csv(RUN / "per_patient.csv", per_patient)
    write_csv(RUN / "per_target.csv", per_target)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
