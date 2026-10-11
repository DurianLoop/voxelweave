"""Read-only source-CSV analysis of the shared-denominator disagreement contrast."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "FIXED_DENOMINATOR_TWO_SOURCE_PLAN_2026-10-01.md"
OUT = ROOT / "experiments/fixed_denominator_two_source"
SOURCES = {
    "msvalid": {
        "folder": ROOT / "experiments/msvalid_ixi_weights_secondary",
        "hashes": {
            "per_target.csv": "ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4",
            "per_patient.csv": "c70ae51db2e212a353ef651bf1a581104db4dc70c4d467035357260f68711659",
            "summary.json": "d36cde42258600c71fb48f5eff0a8cf8424a414ae5fbbbb69c3bae81e97e1023",
        },
        "patients": 84, "targets": 479, "seed": 20261001,
    },
    "remind": {
        "folder": ROOT / "experiments/remind_native_t2_ixi_pair",
        "hashes": {
            "per_target.csv": "450def82f8f03261b55c36ffaed952ee865e7c3be83c0c5b77df1f6a8e441e1c",
            "per_patient.csv": "1227664c0b2fb4a96092300d61daea67855161f6c00d4ccccc9d05bcb42eceb2",
            "summary.json": "e755ef75d3a20daF4db560426145d56f8356c69b2c8c7108c9b9e2ec9abaf071".lower(),
        },
        "patients": 62, "targets": 248, "seed": 20261002,
    },
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


def close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-10):
        raise ValueError(f"{label}: {actual} != {expected}")


def interval(values: np.ndarray, rng: np.random.Generator) -> list[float]:
    draws = rng.integers(0, len(values), size=(5000, len(values)))
    return [float(x) for x in np.percentile(values[draws].mean(axis=1), [2.5, 97.5])]


def analyze(source: str, config: dict) -> tuple[dict, list[dict], list[dict]]:
    folder = config["folder"]
    for name, expected_hash in config["hashes"].items():
        if sha256(folder / name) != expected_hash:
            raise ValueError(f"{source}/{name} hash changed")
    original_summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    targets = read_csv(folder / "per_target.csv")
    original_patients = {row["patient"]: row for row in read_csv(folder / "per_patient.csv")}
    if (len(targets) != config["targets"] or len(original_patients) != config["patients"] or
            original_summary["targets_scored"] != config["targets"] or
            original_summary["patients_scored"] != config["patients"]):
        raise ValueError(f"{source}: incomplete original cohort")

    seen = set()
    by_patient = defaultdict(list)
    target_rows = []
    for row in targets:
        key = (row["patient"], row["z"])
        if key in seen or row["patient"] not in original_patients:
            raise ValueError(f"{source}: duplicate/unknown target {key}")
        seen.add(key)
        ts = float(row["shared_paired_mse"])
        td = float(row["disjoint_paired_mse"])
        os = float(row["shared_observable"])
        od = float(row["disjoint_observable"])
        if not all(map(math.isfinite, (ts, td, os, od))) or min(ts, td) <= 0:
            raise ValueError(f"{source}: invalid MSE/O at {key}")
        ds = 4 * ts * os
        dd = 4 * td * od
        if source == "remind":
            close(ds, float(row["shared_disagreement_mse"]), "shared D")
            close(dd, float(row["disjoint_disagreement_mse"]), "disjoint D")
        qd = dd / (4 * ts)
        delta_q = qd - os
        delta_o = od - os
        close(delta_o, float(row["delta_o"]), "original target delta O")
        item = {
            "source": source, "patient": row["patient"], "z": row["z"],
            "residue": int(row["residue"]),
            "group": row["series_description"] if source == "remind" else "MSValid",
            "shared_o": os, "disjoint_o": od, "delta_o": delta_o,
            "shared_t": ts, "disjoint_t": td, "shared_d": ds, "disjoint_d": dd,
            "shared_q": os, "disjoint_q": qd, "delta_q": delta_q,
        }
        target_rows.append(item)
        by_patient[row["patient"]].append(item)

    patient_rows = []
    for patient, rows in sorted(by_patient.items()):
        if len(rows) != int(original_patients[patient]["targets"]):
            raise ValueError(f"{source}/{patient}: target count differs")
        groups = {r["group"] for r in rows}
        if len(groups) != 1:
            raise ValueError(f"{source}/{patient}: mixed groups")
        item = {"source": source, "patient": patient, "group": groups.pop(), "targets": len(rows)}
        for metric in ("shared_o", "disjoint_o", "delta_o", "shared_q", "disjoint_q", "delta_q"):
            residue_means = []
            for residue in (1, 3):
                values = [r[metric] for r in rows if r["residue"] == residue]
                if not values:
                    raise ValueError(f"{source}/{patient}: missing residue {residue}")
                residue_means.append(float(np.mean(values)))
            item[metric] = float(np.mean(residue_means))
        close(item["delta_o"], float(original_patients[patient]["delta_o"]), "original patient delta O")
        patient_rows.append(item)

    original_o = float(np.mean([row["delta_o"] for row in patient_rows]))
    close(original_o, original_summary["mean_delta_o"], "original source delta O")
    q_values = np.array([row["delta_q"] for row in patient_rows], dtype=float)
    if source == "msvalid":
        ci = interval(q_values, np.random.default_rng(config["seed"]))
        strata = {}
    else:
        grouped = {group: np.array([r["delta_q"] for r in patient_rows if r["group"] == group])
                   for group in ("2D_AX_T2", "2D_AX_T2_BLADE")}
        if len(grouped["2D_AX_T2"]) != 35 or len(grouped["2D_AX_T2_BLADE"]) != 27:
            raise ValueError("ReMIND stratum counts changed")
        rng = np.random.default_rng(config["seed"])
        draws = np.zeros(5000)
        for values in grouped.values():
            indexes = rng.integers(0, len(values), size=(5000, len(values)))
            draws += len(values) / len(patient_rows) * values[indexes].mean(axis=1)
        ci = [float(x) for x in np.percentile(draws, [2.5, 97.5])]
        strata = {group: {"patients": len(values), "mean_delta_q": float(values.mean()),
                          "positive_patients": int((values > 0).sum())}
                  for group, values in grouped.items()}
    result = {
        "patients": len(patient_rows), "targets": len(target_rows),
        "mean_shared_q": float(np.mean([row["shared_q"] for row in patient_rows])),
        "mean_disjoint_q": float(np.mean([row["disjoint_q"] for row in patient_rows])),
        "mean_delta_q": float(q_values.mean()), "ci95_delta_q": ci,
        "mean_delta_o": original_o, "mean_delta_q_minus_delta_o": float(q_values.mean() - original_o),
        "positive_patients": int((q_values > 0).sum()),
        "negative_patients": int((q_values < 0).sum()),
        "positive_targets": sum(row["delta_q"] > 0 for row in target_rows),
        "negative_targets": sum(row["delta_q"] < 0 for row in target_rows),
        "strata": strata,
    }
    return result, target_rows, patient_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    results = {}
    all_targets = []
    all_patients = []
    for source, config in SOURCES.items():
        result, targets, patients = analyze(source, config)
        results[source] = result
        all_targets.extend(targets)
        all_patients.extend(patients)
    OUT.mkdir(parents=True)
    write_csv(OUT / "per_target.csv", all_targets)
    write_csv(OUT / "per_patient.csv", all_patients)
    summary = {"status": "post-result fixed-denominator sensitivity",
               "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
               "source_hashes": {name: config["hashes"] for name, config in SOURCES.items()},
               "results": results}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
