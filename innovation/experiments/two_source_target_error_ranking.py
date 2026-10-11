"""Retrospective within-patient target-error ranking from existing output disagreements."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "TWO_SOURCE_TARGET_ERROR_RANKING_PLAN_2026-10-01.md"
OUT = ROOT / "experiments/two_source_target_error_ranking"
FILES = {
    "msvalid": {
        "main": (ROOT / "experiments/msvalid_ixi_weights_secondary/per_target.csv",
                 "ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4"),
        "linear": (ROOT / "experiments/public_linear_partner_control/msvalid/per_target.csv",
                   "7c50260886e4564e9be2583985379692101e447ba03b8c964518bf8e12402d96"),
        "patients": 84, "targets": 479, "seed": 20261004,
    },
    "remind": {
        "main": (ROOT / "experiments/remind_native_t2_ixi_pair/per_target.csv",
                 "450def82f8f03261b55c36ffaed952ee865e7c3be83c0c5b77df1f6a8e441e1c"),
        "linear": (ROOT / "experiments/public_linear_partner_control/remind/per_target.csv",
                   "368197fbd3a5a1dece41546cfed0bdea9c480c36ecb49d0acd1ef74b08af77b6"),
        "patients": 62, "targets": 248, "seed": 20261005,
    },
}
SCORES = ("s_shared", "s_disjoint", "l_shared", "l_disjoint")
DIFFERENCES = {
    "s_disjoint_minus_shared": ("s_disjoint", "s_shared"),
    "l_disjoint_minus_shared": ("l_disjoint", "l_shared"),
    "disjoint_s_minus_l": ("s_disjoint", "l_disjoint"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def close(value: float, expected: float, label: str) -> None:
    if not math.isclose(value, expected, rel_tol=0, abs_tol=1e-8):
        raise ValueError(f"{label}: {value} != {expected}")


def score_from_o(o: float, pair_mse: float) -> float:
    d = 4 * o * pair_mse
    if not np.isfinite(d) or d < 0:
        raise ValueError("nonfinite or negative output disagreement")
    return float(np.sqrt(d))


def target_rows(source: str, config: dict) -> list[dict]:
    for path, expected in (config["main"], config["linear"]):
        if sha256(path) != expected:
            raise ValueError(f"{source} source hash changed: {path}")
    main = read_csv(config["main"][0])
    linear = read_csv(config["linear"][0])
    if len(main) != config["targets"] or len(linear) != config["targets"]:
        raise ValueError(f"{source} target count changed")
    linear_by_key = {(r["patient"], r["z"]): r for r in linear}
    if len(linear_by_key) != len(linear):
        raise ValueError(f"{source} duplicate linear target")
    result = []
    seen = set()
    for row in main:
        key = (row["patient"], row["z"])
        if key in seen or key not in linear_by_key:
            raise ValueError(f"{source} duplicate or missing target {key}")
        seen.add(key)
        partner = linear_by_key[key]
        if (row["residue"] != partner["residue"] or
                row["support_pixels"] != partner["support_pixels"]):
            raise ValueError(f"{source} target contract mismatch {key}")
        a_mae = float(row["shared_a_mae"])
        a_mse = float(row["shared_a_mse"])
        close(a_mae, float(row["disjoint_a_mae"]), "fixed HAT MAE")
        close(a_mse, float(row["disjoint_a_mse"]), "fixed HAT MSE")
        close(a_mae, float(partner["a_mae"]), "linear fixed HAT MAE")
        if not np.isfinite(a_mae) or a_mae < 0 or a_mse <= 0:
            raise ValueError(f"{source} invalid HAT error {key}")
        scores = {}
        for condition, short in (("shared", "s_shared"), ("disjoint", "s_disjoint")):
            o = float(row[f"{condition}_observable"])
            t = float(row[f"{condition}_paired_mse"])
            if t <= 0:
                raise ValueError(f"{source} invalid paired MSE {key}")
            scores[short] = score_from_o(o, t)
            if source == "remind":
                close(scores[short] ** 2, float(row[f"{condition}_disagreement_mse"]),
                      "stored model disagreement MSE")
            b_mse = float(partner[f"{condition}_b_mse"])
            linear_t = (a_mse + b_mse) / 2
            if linear_t <= 0:
                raise ValueError(f"{source} invalid linear paired MSE {key}")
            scores["l_" + condition] = score_from_o(float(partner[f"{condition}_o"]), linear_t)
        result.append({"source": source, "patient": row["patient"], "z": row["z"],
                       "residue": int(row["residue"]),
                       "group": row["series_description"] if source == "remind" else "MSValid",
                       "hat_mae": a_mae, **scores})
    if set(linear_by_key) != seen:
        raise ValueError(f"{source} linear/main keys differ")
    return result


def concordance(rows: list[dict], score: str) -> tuple[float, int]:
    values = []
    for left, right in itertools.combinations(rows, 2):
        product = (left[score] - right[score]) * (left["hat_mae"] - right["hat_mae"])
        values.append(1.0 if product > 0 else 0.0 if product < 0 else 0.5)
    if not values:
        raise ValueError("residue has fewer than two targets")
    return float(np.mean(values)), len(values)


def patient_rows(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["patient"]].append(row)
    output = []
    for patient, patient_targets in sorted(grouped.items()):
        groups = {r["group"] for r in patient_targets}
        if len(groups) != 1:
            raise ValueError(f"mixed groups for {patient}")
        record = {"source": patient_targets[0]["source"], "patient": patient,
                  "group": groups.pop(), "targets": len(patient_targets)}
        pairs = 0
        for metric in SCORES:
            residue_values = []
            for residue in (1, 3):
                sub = [r for r in patient_targets if r["residue"] == residue]
                value, n_pairs = concordance(sub, metric)
                residue_values.append(value)
                if metric == SCORES[0]:
                    pairs += n_pairs
            record[metric] = float(np.mean(residue_values))
        record["pairs"] = pairs
        for name, (left, right) in DIFFERENCES.items():
            record[name] = record[left] - record[right]
        output.append(record)
    return output


def summary(source: str, config: dict, targets: list[dict], patients: list[dict]) -> dict:
    if len(patients) != config["patients"] or len(targets) != config["targets"]:
        raise ValueError(f"{source} incomplete patients/targets")
    if source == "remind":
        strata = {group: [row for row in patients if row["group"] == group]
                  for group in ("2D_AX_T2", "2D_AX_T2_BLADE")}
        if len(strata["2D_AX_T2"]) != 35 or len(strata["2D_AX_T2_BLADE"]) != 27:
            raise ValueError("ReMIND stratum counts changed")
    else:
        strata = {"MSValid": patients}
    rng = np.random.default_rng(config["seed"])
    boot = {}
    for group, group_rows in strata.items():
        indexes = rng.integers(0, len(group_rows), (5000, len(group_rows)))
        boot[group] = indexes
    results = {"patients": len(patients), "targets": len(targets),
               "within_residue_pairs": sum(int(row["pairs"]) for row in patients),
               "strata": {group: len(group_rows) for group, group_rows in strata.items()},
               "scores": {}, "differences": {}}
    for score in SCORES:
        results["scores"][score] = float(np.mean([row[score] for row in patients]))
    for name in DIFFERENCES:
        values = np.array([row[name] for row in patients])
        draws = np.zeros(5000)
        for group, group_rows in strata.items():
            group_values = np.array([row[name] for row in group_rows])
            draws += len(group_rows) / len(patients) * group_values[boot[group]].mean(axis=1)
        results["differences"][name] = {
            "mean": float(values.mean()),
            "ci95": [float(x) for x in np.percentile(draws, [2.5, 97.5])],
            "positive_patients": int((values > 0).sum()),
            "negative_patients": int((values < 0).sum()),
            "tied_patients": int((values == 0).sum()),
        }
    return results


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    all_targets = []
    all_patients = []
    results = {}
    for source, config in FILES.items():
        targets = target_rows(source, config)
        patients = patient_rows(targets)
        results[source] = summary(source, config, targets, patients)
        all_targets.extend(targets)
        all_patients.extend(patients)
    OUT.mkdir(parents=True)
    write_csv(OUT / "per_target.csv", all_targets)
    write_csv(OUT / "per_patient.csv", all_patients)
    metadata = {"status": "post-result retrospective ranking analysis",
                "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
                "source_hashes": {source: {name: config[name][1] for name in ("main", "linear")}
                                  for source, config in FILES.items()},
                "results": results}
    (OUT / "summary.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
