"""Independent case/ROI/statistical check of the analytic context control."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments/msd_task01_analytic_context_control"
NEURAL = ROOT / "experiments/msd_task01_tumor_roi_context"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual: float, expected: float) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10):
        raise AssertionError((actual, expected))


def balanced(rows: list[dict], region: str, field: str) -> float:
    return float(np.mean([np.mean([row[region][field] for row in rows
                                   if row["residue"] == residue])
                          for residue in (1, 3)]))


def check_region(item: dict) -> None:
    assert item["pixels"] >= 64
    shared, disjoint = item["shared"], item["disjoint"]
    for condition in (shared, disjoint):
        close(condition["paired_mse"], (condition["a_mse"] + condition["b_mse"]) / 2)
        close(condition["observable"],
              condition["disagreement_mse"] / (4 * condition["paired_mse"]))
    close(shared["a_mse"], disjoint["a_mse"])
    close(item["delta_o"], disjoint["observable"] - shared["observable"])
    close(item["fixed_denominator_delta_o"],
          (disjoint["disagreement_mse"] - shared["disagreement_mse"]) /
          (4 * shared["paired_mse"]))


def main() -> None:
    labels = read(ROOT / "experiments/msd_task01_label_qualification.json")
    contract = read(RUN / "run_contract.json")
    summary = read(RUN / "summary.json")
    assert labels["cases_attempted"] == contract["attempted_cases"] == summary["cases_attempted"] == 484
    assert contract["protocol_sha256"] == sha256(
        ROOT / "MSD_TASK01_ANALYTIC_CONTEXT_CONTROL_PROTOCOL_2026-10-01.md")
    assert contract["label_qualification_sha256"] == sha256(
        ROOT / "experiments/msd_task01_label_qualification.json")
    assert contract["neural_summary_sha256"] == sha256(NEURAL / "summary.json")
    assert summary["run_contract_sha256"] == sha256(RUN / "run_contract.json")
    assert len(list((RUN / "cases").glob("BRATS_*.json"))) == 484
    analytic_lesion, analytic_local, neural_contrast, failures = [], [], [], []
    for record in labels["records"]:
        scan = record["scan"]
        case = read(RUN / "cases" / f"{scan}.json")
        assert case["scan"] == scan
        assert case["run_contract_sha256"] == summary["run_contract_sha256"]
        if not case["complete"]:
            failures.append(scan)
            assert not record["eligible"] or case["failure_stage"] == "source_or_analytic_prediction"
            continue
        assert record["eligible"] and case["targets"] == record["targets"]
        assert case["source_files"][1]["compressed_sha256"] == record["source"]["compressed_sha256"]
        neural = read(NEURAL / "cases" / f"{scan}.json")
        assert neural["complete"] and neural["targets"] == case["targets"]
        rows = case["rows"]
        assert len(rows) == len(neural["rows"]) == 4
        assert sorted((row["residue"], row["z"]) for row in rows) == sorted(
            (int(residue), z) for residue, zs in record["targets"].items() for z in zs)
        for row, original in zip(rows, neural["rows"]):
            assert row["z"] == original["z"] and row["residue"] == original["residue"]
            assert row["full_support_pixels"] == original["full_support"]["pixels"]
            assert row["lesion"]["pixels"] == original["lesion"]["pixels"]
            assert row["local_control"]["pixels"] == original["local_control"]["pixels"]
            assert row["lesion"]["pixels"] == row["local_control"]["pixels"]
            check_region(row["lesion"])
            check_region(row["local_control"])
        values = case["summary"]
        for name, region, field in (
            ("lesion_delta_o", "lesion", "delta_o"),
            ("local_delta_o", "local_control", "delta_o"),
            ("fixed_denominator_lesion_delta_o", "lesion", "fixed_denominator_delta_o"),
            ("fixed_denominator_local_delta_o", "local_control", "fixed_denominator_delta_o"),
        ):
            close(values[name], balanced(rows, region, field))
        close(values["lesion_minus_local_delta_o"],
              values["lesion_delta_o"] - values["local_delta_o"])
        analytic_lesion.append(values["lesion_delta_o"])
        analytic_local.append(values["local_delta_o"])
        neural_contrast.append(neural["summary"]["delta_o_lesion_minus_local"])
    assert failures == summary["failed_case_ids"]
    assert len(analytic_lesion) == summary["cases_complete"]
    assert 4 * len(analytic_lesion) == summary["targets_complete"]
    lesion, local, neural_values = map(np.asarray,
                                       (analytic_lesion, analytic_local, neural_contrast))
    contrast = lesion - local
    indices = np.random.default_rng(20261006).integers(
        0, len(lesion), size=(5000, len(lesion)))
    for data, mean_name, ci_name in (
        (lesion, "analytic_lesion_delta_o", "analytic_lesion_delta_o_ci95"),
        (local, "analytic_local_delta_o", "analytic_local_delta_o_ci95"),
        (contrast, "analytic_lesion_minus_local_delta_o", "analytic_lesion_minus_local_ci95"),
        (neural_values - contrast, "neural_minus_analytic_contrast",
         "neural_minus_analytic_contrast_ci95"),
    ):
        close(summary[mean_name], float(data.mean()))
        for actual, expected in zip(summary[ci_name],
                                    np.percentile(data[indices].mean(axis=1), [2.5, 97.5])):
            close(actual, float(expected))
    assert summary["analytic_positive_lesion_cases"] == int((lesion > 0).sum())
    assert summary["analytic_positive_specificity_cases"] == int((contrast > 0).sum())
    print(json.dumps({"verified": True, "attempted": 484,
                      "complete": len(lesion), "failed": failures,
                      "targets": 4 * len(lesion)}, indent=2))


if __name__ == "__main__":
    main()
