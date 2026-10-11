"""Independent arithmetic and denominator audit of the frozen MSD run."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments/msd_task01_tumor_roi_context"
LABELS = ROOT / "experiments/msd_task01_label_qualification.json"
PROTOCOL = ROOT / "MSD_TASK01_TUMOR_ROI_CONTEXT_PROTOCOL_2026-10-01.md"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual: float, expected: float) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9):
        raise AssertionError((actual, expected))


def mean_by_residue(rows: list[dict], key: str, metric: str) -> float:
    return float(np.mean([np.mean([row[key][metric] for row in rows
                                   if row["residue"] == residue])
                          for residue in (1, 3)]))


def check_region(region: dict) -> None:
    assert region["pixels"] > 0
    for condition in ("shared", "disjoint"):
        item = region[condition]
        close(item["paired_mse"], (item["a_mse"] + item["b_mse"]) / 2)
        close(item["observable"], item["disagreement_mse"] / (4 * item["paired_mse"]))
        # The saved ensemble MSE uses a float32 pixel average before squaring.
        ensemble_identity = item["paired_mse"] - item["disagreement_mse"] / 4
        if not math.isclose(region[f"{condition}_ensemble_mse"], ensemble_identity,
                            rel_tol=1e-5, abs_tol=1e-3):
            raise AssertionError((region[f"{condition}_ensemble_mse"], ensemble_identity))
    shared, disjoint = region["shared"], region["disjoint"]
    close(shared["a_mse"], disjoint["a_mse"])
    close(shared["a_mae"], disjoint["a_mae"])
    close(region["delta_o"], disjoint["observable"] - shared["observable"])
    close(region["delta_o_fixed_shared_denominator"],
          (disjoint["disagreement_mse"] - shared["disagreement_mse"]) /
          (4 * shared["paired_mse"]))
    assert math.isfinite(region["pchip_mse"]) and region["pchip_mse"] >= 0


def main() -> None:
    labels, contract, summary = read(LABELS), read(RUN / "run_contract.json"), read(RUN / "summary.json")
    assert labels["cases_attempted"] == contract["attempted_cases"] == summary["cases_attempted"] == 484
    assert contract["protocol_sha256"] == summary["protocol_sha256"] == digest(PROTOCOL)
    assert contract["label_qualification_sha256"] == digest(LABELS)
    assert summary["run_contract_sha256"] == digest(RUN / "run_contract.json")
    assert len(list((RUN / "cases").glob("BRATS_*.json"))) == 484
    patients, failures, target_count = [], [], 0
    for label in labels["records"]:
        case = read(RUN / "cases" / f"{label['scan']}.json")
        assert case["scan"] == label["scan"]
        assert case["protocol_sha256"] == contract["protocol_sha256"]
        assert case["run_contract_sha256"] == summary["run_contract_sha256"]
        if not case["complete"]:
            failures.append(case)
            if not label["eligible"]:
                assert case["failure_stage"] == "label_qualification"
            continue
        assert label["eligible"] and case["targets"] == label["targets"]
        assert case["source_files"][1]["compressed_sha256"] == label["source"]["compressed_sha256"]
        rows = case["rows"]
        assert len(rows) == 4
        assert sorted((row["residue"], row["z"]) for row in rows) == sorted(
            (int(residue), z) for residue, zs in label["targets"].items() for z in zs)
        for row in rows:
            target_count += 1
            assert row["lesion"]["pixels"] == row["local_control"]["pixels"] >= 64
            assert row["lesion"]["pixels"] <= row["full_support"]["pixels"]
            for key in ("lesion", "local_control", "full_support"):
                check_region(row[key])
            assert row["edema_pixels"] + row["tumor_core_pixels"] == row["lesion"]["pixels"]
            for key, count_key in (("edema", "edema_pixels"), ("tumor_core", "tumor_core_pixels")):
                if row[key] is not None and "metric_undefined" not in row[key]:
                    assert row[key]["pixels"] == row[count_key]
                    check_region(row[key])
        entry = case["summary"]
        for field, region, metric in (
            ("delta_o_lesion", "lesion", "delta_o"),
            ("delta_o_local_control", "local_control", "delta_o"),
            ("delta_o_full_support", "full_support", "delta_o"),
            ("delta_o_lesion_fixed_denominator", "lesion", "delta_o_fixed_shared_denominator"),
            ("lesion_shared_ensemble_mse", "lesion", "shared_ensemble_mse"),
            ("lesion_disjoint_ensemble_mse", "lesion", "disjoint_ensemble_mse"),
            ("lesion_pchip_mse", "lesion", "pchip_mse"),
        ):
            close(entry[field], mean_by_residue(rows, region, metric))
        close(entry["delta_o_lesion_minus_local"],
              entry["delta_o_lesion"] - entry["delta_o_local_control"])
        patients.append(entry)
    assert len(patients) == summary["cases_complete"]
    assert target_count == summary["targets_complete"]
    assert [case["scan"] for case in failures] == summary["failed_case_ids"]
    assert dict(Counter(case["failure_stage"] + ":" + case["failure_type"]
                        for case in failures)) == summary["failure_counts"]
    assert len(list(csv.DictReader((RUN / "per_patient.csv").open(encoding="utf-8")))) == len(patients)
    assert len(list(csv.DictReader((RUN / "per_target.csv").open(encoding="utf-8")))) == target_count
    lesion = np.asarray([entry["delta_o_lesion"] for entry in patients])
    local = np.asarray([entry["delta_o_local_control"] for entry in patients])
    draws = np.random.default_rng(20261005).integers(0, len(patients), (5000, len(patients)))
    for values, mean_key, ci_key in (
        (lesion, "primary_lesion_delta_o", "primary_lesion_delta_o_ci95"),
        (lesion - local, "primary_lesion_minus_local_delta_o", "primary_lesion_minus_local_ci95"),
    ):
        close(summary[mean_key], float(values.mean()))
        for actual, expected in zip(summary[ci_key], np.percentile(values[draws].mean(axis=1), [2.5, 97.5])):
            close(actual, float(expected))
    for region in ("lesion", "local_control", "full_support", "edema", "tumor_core"):
        reported = summary["region_descriptive"][region]
        optional = region in ("edema", "tumor_core")
        values = {"shared_o": [], "disjoint_o": [], "pchip_mse": []}
        positive_cases = positive_targets = undefined_targets = all_four = 0
        for label in labels["records"]:
            path = RUN / "cases" / f"{label['scan']}.json"
            case = read(path)
            if not case["complete"]:
                continue
            rows = case["rows"]
            items = [(row["residue"], row[region]) for row in rows if row[region] is not None]
            positive_targets += len(items)
            positive_cases += bool(items)
            undefined_targets += sum(bool(item.get("metric_undefined")) for _, item in items)
            valid = [(residue, item) for residue, item in items if not item.get("metric_undefined")]
            all_four += len(valid) == 4
            if not valid:
                continue
            for name, keys in (("shared_o", ("shared", "observable")),
                               ("disjoint_o", ("disjoint", "observable")),
                               ("pchip_mse", ("pchip_mse",))):
                def extract(item: dict) -> float:
                    for key in keys:
                        item = item[key]
                    return item
                if optional:
                    values[name].append(float(np.mean([extract(item) for _, item in valid])))
                else:
                    values[name].append(float(np.mean([
                        np.mean([extract(item) for residue_row, item in valid
                                 if residue_row == residue]) for residue in (1, 3)])))
        assert reported["positive_targets"] == positive_targets
        assert reported["zero_pixel_targets"] == 4 * len(patients) - positive_targets
        assert reported["patients_with_any_labeled_pixels"] == positive_cases
        assert reported["patients_with_zero_labeled_pixels"] == len(patients) - positive_cases
        assert reported["patients_with_all_four_defined_targets"] == all_four
        assert reported["undefined_metric_targets"] == undefined_targets
        assert reported["patients_with_defined_metrics"] == len(values["shared_o"])
        for name, patient_values in values.items():
            if patient_values:
                close(reported[name], float(np.mean(patient_values)))
            else:
                assert reported[name] is None
    assert summary["primary_success"] == (
        len(patients) >= 350 and summary["primary_lesion_delta_o_ci95"][0] > 0 and
        summary["primary_lesion_minus_local_ci95"][0] > 0)
    print(json.dumps({"verified": True, "attempted": 484, "complete": len(patients),
                      "failed": len(failures), "targets": target_count,
                      "primary_success": summary["primary_success"]}, indent=2))


if __name__ == "__main__":
    main()
