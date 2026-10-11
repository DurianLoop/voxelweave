"""Read-only accounting check for the post-result equal-information controls."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def close(actual: float, expected: float, where: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-7):
        raise AssertionError(f"{where}: {actual} != {expected}")


def main() -> None:
    folder = ROOT / "experiments"
    summaries = {}
    for name, plan, script in (
        ("two_source_ensemble_error", "TWO_SOURCE_ENSEMBLE_ERROR_PLAN_2026-10-01.md", "two_source_ensemble_error.py"),
        ("union_even_linear_control", "UNION_EVEN_LINEAR_CONTROL_PLAN_2026-10-01.md", "union_even_linear_control.py"),
        ("union_even_cubic_control", "UNION_EVEN_CUBIC_CONTROL_PLAN_2026-10-01.md", "union_even_cubic_control.py"),
    ):
        summary = json.loads((folder / name / "summary.json").read_text(encoding="utf-8"))
        assert summary["plan_sha256"] == digest(ROOT / plan)
        assert summary["script_sha256"] == digest(folder / script)
        assert summary["gpu_used"] is False
        summaries[name] = summary
    main_rows = {}
    for source, subfolder, expected_hash in (
        ("msvalid", "msvalid_ixi_weights_secondary", "ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4"),
        ("remind", "remind_native_t2_ixi_pair", "450def82f8f03261b55c36ffaed952ee865e7c3be83c0c5b77df1f6a8e441e1c"),
    ):
        path = folder / subfolder / "per_target.csv"
        assert digest(path) == expected_hash
        for row in read(path):
            key = (source, row["patient"], row["z"])
            assert key not in main_rows
            main_rows[key] = row
    assert len(main_rows) == 727
    mapped = {}
    for name in summaries:
        rows = read(folder / name / "per_target.csv")
        assert len(rows) == 727
        mapped[name] = {(r["source"], r["patient"], r["z"]): r for r in rows}
        assert len(mapped[name]) == 727 and set(mapped[name]) == set(main_rows)
    for key, main in main_rows.items():
        ens = mapped["two_source_ensemble_error"][key]
        linear = mapped["union_even_linear_control"][key]
        cubic = mapped["union_even_cubic_control"][key]
        es = float(main["shared_paired_mse"]) * (1 - float(main["shared_observable"]))
        ed = float(main["disjoint_paired_mse"]) * (1 - float(main["disjoint_observable"]))
        close(float(ens["shared_ensemble_mse"]), es, f"{key} shared ensemble")
        close(float(ens["disjoint_ensemble_mse"]), ed, f"{key} disjoint ensemble")
        close(float(linear["disjoint_ensemble_mse"]), ed, f"{key} linear model")
        close(float(cubic["disjoint_ensemble_mse"]), ed, f"{key} cubic model")
        close(float(cubic["linear_mse"]), float(linear["union_linear_mse"]), f"{key} repeated linear")
        for method in ("catmull", "pchip"):
            baseline = float(cubic[f"{method}_mse"])
            close(float(cubic[f"{method}_relative_ensemble_gain"]),
                  (baseline - ed) / baseline, f"{key} {method} gain")
    by_patient = defaultdict(list)
    for key, row in mapped["union_even_cubic_control"].items():
        by_patient[key[:2]].append(row)
    stored_patients = {(r["source"], r["patient"]): r
                       for r in read(folder / "union_even_cubic_control/per_patient.csv")}
    assert len(by_patient) == len(stored_patients) == 146
    for key, targets in by_patient.items():
        residues = {r: [t for t in targets if int(t["residue"]) == r] for r in (1, 3)}
        assert all(residues.values())
        record = stored_patients[key]
        assert len(targets) == int(record["targets"])
        for method in ("catmull", "pchip", "disjoint_ensemble"):
            mse = sum(sum(float(t[f"{method}_mse"]) for t in residues[r]) / len(residues[r]) for r in (1, 3)) / 2
            close(float(record[f"{method}_mse"]), mse, f"{key} {method} patient")
        model = float(record["disjoint_ensemble_mse"])
        for method in ("catmull", "pchip"):
            base = float(record[f"{method}_mse"])
            close(float(record[f"{method}_relative_ensemble_gain"]), (base - model) / base,
                  f"{key} {method} patient gain")
    summary = summaries["union_even_cubic_control"]["sources"]
    for source, n, nt, seed in (("msvalid", 84, 479, 20261001), ("remind", 62, 248, 20261002)):
        patients = [r for r in read(folder / "union_even_cubic_control/per_patient.csv") if r["source"] == source]
        assert len(patients) == n and summary[source]["patients"] == n and summary[source]["targets"] == nt
        rng = np.random.default_rng(seed)
        for method in ("catmull", "pchip"):
            values = np.array([float(r[f"{method}_relative_ensemble_gain"]) for r in patients])
            if source == "msvalid":
                draws = values[rng.integers(n, size=(5000, n))].mean(axis=1)
            else:
                draws = np.zeros(5000)
                for label, size in (("2D_AX_T2", 35), ("2D_AX_T2_BLADE", 27)):
                    stratum = np.array([float(r[f"{method}_relative_ensemble_gain"]) for r in patients if r["stratum"] == label])
                    assert len(stratum) == size
                    draws += size / n * stratum[rng.integers(size, size=(5000, size))].mean(axis=1)
            found = summary[source]["methods"][method]
            close(found["mean_patient_relative_ensemble_gain"], float(values.mean()), f"{source} {method} mean")
            for a, b in zip(found["ci95"], np.percentile(draws, [2.5, 97.5])):
                close(a, float(b), f"{source} {method} CI")
            assert found["ensemble_better_patients"] == int((values > 0).sum())
            assert found["cubic_better_patients"] == int((values < 0).sum())
    print(json.dumps({"status": "PASS", "targets": 727, "patients": 146,
                      "checked": "source algebra, three target tables, cubic patient aggregation and four bootstrap intervals",
                      "pixel_data_read": False, "gpu_used": False}, indent=2))


if __name__ == "__main__":
    main()
