"""Post-result, CSV-only check of equal-weight ensemble error."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/two_source_ensemble_error"
PLAN = ROOT / "TWO_SOURCE_ENSEMBLE_ERROR_PLAN_2026-10-01.md"
SOURCES = {
    "msvalid": ("msvalid_ixi_weights_secondary", "ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4", 84, 479, 20261001),
    "remind": ("remind_native_t2_ixi_pair", "450def82f8f03261b55c36ffaed952ee865e7c3be83c0c5b77df1f6a8e441e1c", 62, 248, 20261002),
}


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def mean(items: list[float]) -> float:
    return float(np.mean(items))


def analyze(name: str, config: tuple) -> tuple[dict, list[dict], list[dict]]:
    folder, frozen_hash, expected_patients, expected_targets, seed = config
    path = ROOT / "experiments" / folder / "per_target.csv"
    if sha256(path) != frozen_hash:
        raise ValueError(f"{name} frozen target CSV changed")
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != expected_targets:
        raise ValueError(f"{name} target count changed")
    patients = defaultdict(lambda: defaultdict(list))
    target_results = []
    seen = set()
    for row in rows:
        key = (row["patient"], row["z"])
        if key in seen or int(row["residue"]) not in (1, 3):
            raise ValueError(f"{name} duplicated or unexpected target: {key}")
        seen.add(key)
        ts, td = (float(row[f"{condition}_paired_mse"]) for condition in ("shared", "disjoint"))
        os, od = (float(row[f"{condition}_observable"]) for condition in ("shared", "disjoint"))
        if not all(math.isfinite(x) for x in (ts, td, os, od)) or min(ts, td) <= 0 or not (0 <= os <= 1 and 0 <= od <= 1):
            raise ValueError(f"{name} invalid endpoint at {key}")
        if not math.isclose(float(row["shared_a_mse"]), float(row["disjoint_a_mse"]), abs_tol=1e-8):
            raise ValueError(f"{name} reference not fixed at {key}")
        es, ed = ts * (1 - os), td * (1 - od)
        stratum = row.get("series_description", "msvalid")
        patients[row["patient"]][int(row["residue"])].append((es, ed, stratum))
        target_results.append({"source": name, "patient": row["patient"], "z": row["z"],
                               "residue": row["residue"], "stratum": stratum,
                               "shared_ensemble_mse": es, "disjoint_ensemble_mse": ed,
                               "relative_reduction": (es - ed) / es})
    if len(patients) != expected_patients:
        raise ValueError(f"{name} patient count changed")
    patient_results = []
    for patient in sorted(patients):
        residues = patients[patient]
        if set(residues) != {1, 3}:
            raise ValueError(f"{name} missing residue for {patient}")
        es = mean([mean([item[0] for item in residues[r]]) for r in (1, 3)])
        ed = mean([mean([item[1] for item in residues[r]]) for r in (1, 3)])
        strata = {item[2] for values in residues.values() for item in values}
        if len(strata) != 1:
            raise ValueError(f"{name} mixed protocol for {patient}")
        patient_results.append({"source": name, "patient": patient, "stratum": strata.pop(),
                                "targets": sum(map(len, residues.values())),
                                "shared_ensemble_mse": es, "disjoint_ensemble_mse": ed,
                                "relative_reduction": (es - ed) / es})
    rng = np.random.default_rng(seed)
    values = np.array([row["relative_reduction"] for row in patient_results])
    if name == "remind":
        strata = []
        for label, expected in (("2D_AX_T2", 35), ("2D_AX_T2_BLADE", 27)):
            group = np.array([row["relative_reduction"] for row in patient_results if row["stratum"] == label])
            if len(group) != expected:
                raise ValueError(f"{name} stratum count changed: {label}")
            strata.append(group)
        draws = sum(len(group) / len(values) * group[rng.integers(0, len(group), size=(5000, len(group)))].mean(axis=1)
                    for group in strata)
    else:
        draws = values[rng.integers(0, len(values), size=(5000, len(values)))].mean(axis=1)
    summary = {"patients": len(patient_results), "targets": len(target_results),
               "mean_patient_relative_reduction": float(values.mean()),
               "ci95_patient_relative_reduction": np.percentile(draws, [2.5, 97.5]).tolist(),
               "improved_patients": int((values > 0).sum()), "worsened_patients": int((values < 0).sum()),
               "improved_targets": sum(row["relative_reduction"] > 0 for row in target_results),
               "worsened_targets": sum(row["relative_reduction"] < 0 for row in target_results),
               "mean_patient_absolute_mse_reduction": mean([row["shared_ensemble_mse"] - row["disjoint_ensemble_mse"] for row in patient_results]),
               "per_target_source_sha256": frozen_hash, "bootstrap_draws": 5000, "bootstrap_seed": seed}
    return summary, patient_results, target_results


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    summaries = {}
    all_patients, all_targets = [], []
    for name, config in SOURCES.items():
        summaries[name], patients, targets = analyze(name, config)
        all_patients.extend(patients)
        all_targets.extend(targets)
    OUT.mkdir(parents=True)
    write_csv(OUT / "per_patient.csv", all_patients)
    write_csv(OUT / "per_target.csv", all_targets)
    result = {"plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
              "sources": summaries, "target_pixels_read": False, "gpu_used": False,
              "status": "post_result_exploratory"}
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
