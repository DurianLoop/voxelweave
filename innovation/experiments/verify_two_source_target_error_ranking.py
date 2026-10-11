"""Independent read-only replay of target score ranking and patient bootstrap."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/two_source_target_error_ranking"
PLAN = ROOT / "TWO_SOURCE_TARGET_ERROR_RANKING_PLAN_2026-10-01.md"
SCRIPT = ROOT / "experiments/two_source_target_error_ranking.py"
SOURCES = {
    "msvalid": (ROOT / "experiments/msvalid_ixi_weights_secondary/per_target.csv",
                ROOT / "experiments/public_linear_partner_control/msvalid/per_target.csv", 20261004),
    "remind": (ROOT / "experiments/remind_native_t2_ixi_pair/per_target.csv",
               ROOT / "experiments/public_linear_partner_control/remind/per_target.csv", 20261005),
}
SCORES = ("s_shared", "s_disjoint", "l_shared", "l_disjoint")
DIFFS = {"s_disjoint_minus_shared": ("s_disjoint", "s_shared"),
         "l_disjoint_minus_shared": ("l_disjoint", "l_shared"),
         "disjoint_s_minus_l": ("s_disjoint", "l_disjoint")}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def close(actual: float, expected: float, label: str) -> None:
    if not np.isclose(actual, expected, rtol=0, atol=1e-9):
        raise AssertionError(f"{label}: {actual} != {expected}")


def concordance(rows: list[dict], score: str) -> float:
    points = []
    for a, b in itertools.combinations(rows, 2):
        x = float(a[score]) - float(b[score])
        y = float(a["hat_mae"]) - float(b["hat_mae"])
        points.append(1.0 if x * y > 0 else 0.0 if x * y < 0 else 0.5)
    if not points:
        raise AssertionError("empty residue pair list")
    return float(np.mean(points))


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    if summary["plan_sha256"] != sha256(PLAN) or summary["script_sha256"] != sha256(SCRIPT):
        raise AssertionError("frozen rule or script hash changed")
    scored = read_csv(OUT / "per_target.csv")
    patients = read_csv(OUT / "per_patient.csv")
    if len(scored) != 727 or len(patients) != 146:
        raise AssertionError("combined output row count changed")

    for source, (main_path, linear_path, seed) in SOURCES.items():
        if (summary["source_hashes"][source]["main"] != sha256(main_path) or
                summary["source_hashes"][source]["linear"] != sha256(linear_path)):
            raise AssertionError(f"{source}: source hash changed")
        main = {(r["patient"], r["z"]): r for r in read_csv(main_path)}
        linear = {(r["patient"], r["z"]): r for r in read_csv(linear_path)}
        output = {(r["patient"], r["z"]): r for r in scored if r["source"] == source}
        if set(main) != set(linear) or set(main) != set(output):
            raise AssertionError(f"{source}: exact target list changed")
        by_patient = defaultdict(lambda: {1: [], 3: []})
        for key, row in output.items():
            m, l = main[key], linear[key]
            a_mse = Decimal(m["shared_a_mse"])
            for condition, prefix in (("shared", "shared"), ("disjoint", "disjoint")):
                model_d = Decimal(4) * Decimal(m[f"{condition}_paired_mse"]) * Decimal(m[f"{condition}_observable"])
                linear_t = (a_mse + Decimal(l[f"{condition}_b_mse"])) / 2
                linear_d = Decimal(4) * linear_t * Decimal(l[f"{condition}_o"])
                close(float(row[f"s_{prefix}"]) ** 2, float(model_d), "model score square")
                close(float(row[f"l_{prefix}"]) ** 2, float(linear_d), "linear score square")
            close(float(row["hat_mae"]), float(m["shared_a_mae"]), "HAT outcome")
            by_patient[row["patient"]][int(row["residue"])].append(row)

        source_patients = [p for p in patients if p["source"] == source]
        report = summary["results"][source]
        if len(source_patients) != report["patients"] or len(output) != report["targets"]:
            raise AssertionError(f"{source}: cohort changed")
        for patient in source_patients:
            residue = by_patient.pop(patient["patient"])
            for score in SCORES:
                value = (concordance(residue[1], score) + concordance(residue[3], score)) / 2
                close(float(patient[score]), value, "patient concordance")
            for name, (left, right) in DIFFS.items():
                close(float(patient[name]), float(patient[left]) - float(patient[right]), "patient difference")
        if by_patient:
            raise AssertionError(f"{source}: unmatched patients")
        for score in SCORES:
            close(report["scores"][score], float(np.mean([float(p[score]) for p in source_patients])),
                  "score mean")

        groups = ({"MSValid": source_patients} if source == "msvalid" else
                  {g: [p for p in source_patients if p["group"] == g]
                   for g in ("2D_AX_T2", "2D_AX_T2_BLADE")})
        rng = np.random.default_rng(seed)
        draws = {g: rng.integers(0, len(rows), (5000, len(rows))) for g, rows in groups.items()}
        for name in DIFFS:
            pooled = np.zeros(5000)
            for group, rows in groups.items():
                values = np.array([float(p[name]) for p in rows])
                pooled += len(rows) / len(source_patients) * values[draws[group]].mean(axis=1)
            actual = report["differences"][name]
            close(actual["mean"], float(np.mean([float(p[name]) for p in source_patients])), "mean difference")
            for got, expected in zip(actual["ci95"], np.percentile(pooled, [2.5, 97.5])):
                close(got, float(expected), "bootstrap limit")
        print(f"PASS {source}: {len(source_patients)} patients, {len(output)} targets, "
              f"S shared/disjoint={report['scores']['s_shared']:.6f}/"
              f"{report['scores']['s_disjoint']:.6f}")


if __name__ == "__main__":
    main()
