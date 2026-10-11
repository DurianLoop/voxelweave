"""Read-only independent arithmetic audit of the archived PCHIP sensitivity."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "experiments/ds007045_thin3d_pchip_sensitivity"
OLD = ROOT / "experiments/ds007045_thin3d_model_pilot"


def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def verify() -> dict:
    summary = json.loads((NEW / "summary.json").read_text(encoding="utf-8"))
    targets, patients = rows(NEW / "per_target.csv"), rows(NEW / "per_patient.csv")
    old_targets = {(r["case"], r["z"]): r for r in rows(OLD / "per_target.csv")}
    old_patients = {r["case"]: r for r in rows(OLD / "per_patient.csv")}
    assert len(targets) == 132 and len(patients) == 33 and not summary["failures"]
    assert len({(r["case"], r["z"]) for r in targets}) == 132
    assert len({r["case"] for r in patients}) == 33
    grouped = defaultdict(list)
    for row in targets:
        key = (row["case"], row["z"])
        assert key in old_targets
        grouped[row["case"]].append(row)
        for roi in ("tumor", "full"):
            for model in ("hat", "swinir"):
                field = f"{roi}_{model}_normalized_mse"
                assert abs(float(row[field]) - float(old_targets[key][field])) < 1e-12
    for patient in patients:
        case = patient["case"]
        assert len(grouped[case]) == 4 and case in old_patients
        for roi in ("tumor", "full"):
            for method in ("raw_pchip", "pipeline_pchip", "hat", "swinir"):
                field = f"{roi}_{method}_normalized_mse"
                assert abs(float(patient[field]) - np.mean([float(r[field]) for r in grouped[case]])) < 1e-12
                if method in ("hat", "swinir"):
                    assert abs(float(patient[field]) - float(old_patients[case][field])) < 1e-12
            for model in ("hat", "swinir"):
                for baseline in ("raw_pchip", "pipeline_pchip"):
                    key = f"{roi}_{model}_minus_{baseline}"
                    assert abs(float(patient[key]) - (float(patient[f"{roi}_{model}_normalized_mse"]) -
                                                        float(patient[f"{roi}_{baseline}_normalized_mse"]))) < 1e-12
    draws = np.random.default_rng(summary["bootstrap_seed"]).integers(0, 33, (5000, 33))
    for field, report in summary["differences"].items():
        values = np.array([float(p[field]) for p in patients])
        assert abs(values.mean() - report["mean"]) < 1e-12
        assert int((values > 0).sum()) == report["positive_patients"]
        assert np.allclose(np.percentile(values[draws].mean(axis=1), [2.5, 97.5]),
                           report["ci95"], rtol=0, atol=1e-12)
    for key, count in summary["sign_discordance"].items():
        model, baseline = key.split("_vs_")
        assert count == sum(float(p[f"tumor_{model}_minus_{baseline}"]) > 0 and
                            float(p[f"full_{model}_minus_{baseline}"]) < 0 for p in patients)
    return {"verified": True, "cases": len(patients), "targets": len(targets),
            "sites": dict(Counter(p["site"] for p in patients)),
            "difference_intervals_checked": len(summary["differences"]),
            "sign_counts_checked": len(summary["sign_discordance"])}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
