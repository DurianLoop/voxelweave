"""Independent read-only case, aggregation and bootstrap check for IXI validation."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import nibabel as nib
import numpy as np


PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT / "innovation"
OUT = ROOT / "experiments/ixi_validation_equal_neighbor_diagnostic"
SPLIT = PROJECT / "dataset/IXI/splits/seed3407/val_cases.txt"
METADATA = PROJECT / "dataset/IXI/metadata/ixi_cases.csv"
REGISTRY = {row["case_id"]: row for row in csv.DictReader(METADATA.open(newline="", encoding="utf-8"))}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def targets(depth: int) -> dict[str, list[int]]:
    result = {}
    for residue in (1, 3):
        eligible = []
        for z in range(residue, depth, 4):
            if all(len([a for a in range(phase, depth, 4) if a < z]) >= 2 and
                   len([a for a in range(phase, depth, 4) if a > z]) >= 2
                   for phase in (0, 2)):
                eligible.append(z)
        result[str(residue)] = [eligible[math.floor((len(eligible) - 1) / 3)],
                                eligible[math.ceil(2 * (len(eligible) - 1) / 3)]]
    return result


def close(a: float, b: float, tolerance: float = 1e-8) -> bool:
    return abs(a - b) <= tolerance * max(1.0, abs(a), abs(b))


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    contract_path = OUT / "run_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if (contract["protocol_sha256"] != sha256(ROOT / "IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_PROTOCOL_2026-10-01.md") or
            contract["validation_split_sha256"] != sha256(SPLIT) or
            contract["metadata_sha256"] != sha256(METADATA) or
            contract["gpu_used"] is not False or
            summary["run_contract_sha256"] != sha256(contract_path)):
        raise ValueError("Run contract changed")
    ids = [line.strip() for line in SPLIT.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(ids) != 58 or len(set(ids)) != 58:
        raise ValueError("Validation source count changed")
    cases = []
    for case in ids:
        item = json.loads((OUT / "cases" / f"{case}.json").read_text(encoding="utf-8"))
        if item["case"] != case or not item["complete"] or item["run_contract_sha256"] != sha256(contract_path):
            raise ValueError(f"Case incomplete/contract mismatch: {case}")
        path = Path(REGISTRY[case]["T2_path"])
        if sha256(path) != item["source_sha256"]:
            raise ValueError(f"Validation source bytes changed: {case}")
        depth = int(REGISTRY[case]["T2_shape"].split("x")[2])
        if item["targets"] != targets(depth):
            raise ValueError(f"Frozen targets changed: {case}")
        expected_rows = [(int(z), residue) for residue in (1, 3)
                         for z in item["targets"][str(residue)]]
        if len(item["rows"]) != 4:
            raise ValueError(f"Missing targets: {case}")
        for row, (z, residue) in zip(item["rows"], expected_rows):
            if (row["z"], row["residue"]) != (z, residue) or row["support_pixels"] <= 0:
                raise ValueError(f"Target/support mismatch: {case}")
            for method in ("raw_linear", "pipeline_linear", "hat", "swinir"):
                if not np.isfinite(row[f"{method}_mse"]) or row[f"{method}_mse"] < 0:
                    raise ValueError(f"Invalid target metric: {case} z{z}")
        cases.append(item)
    with (OUT / "per_patient.csv").open(newline="", encoding="utf-8") as stream:
        stored = {row["case"]: row for row in csv.DictReader(stream)}
    if len(stored) != 58:
        raise ValueError("Patient CSV length changed")
    reconstructed = []
    for item in cases:
        result = {"case": item["case"]}
        for method in ("raw_linear", "pipeline_linear", "hat", "swinir"):
            for metric in ("mse", "mae"):
                field = f"{method}_{metric}"
                result[field] = float(np.mean([
                    np.mean([row[field] for row in item["rows"] if row["residue"] == residue])
                    for residue in (1, 3)]))
                if not close(result[field], float(stored[item["case"]][field])):
                    raise ValueError(f"Patient aggregation mismatch: {item['case']} {field}")
        for model in ("hat", "swinir"):
            for baseline in ("raw_linear", "pipeline_linear"):
                field = f"{model}_minus_{baseline}_mse"
                result[field] = result[f"{model}_mse"] - result[f"{baseline}_mse"]
                if not close(result[field], float(stored[item["case"]][field])):
                    raise ValueError(f"Patient contrast mismatch: {item['case']} {field}")
        reconstructed.append(result)
    if summary["attempted_cases"] != 58 or summary["completed_targets"] != 232 or summary["failures"]:
        raise ValueError("Summary denominator changed")
    draws = np.random.default_rng(20261012).integers(0, 58, size=(5000, 58))
    for field, expected in summary["results"].items():
        values = np.array([row[field] for row in reconstructed])
        bounds = np.percentile(values[draws].mean(axis=1), [2.5, 97.5])
        if (not close(float(values.mean()), expected["mean"]) or
                not all(close(float(a), float(b)) for a, b in zip(bounds, expected["bootstrap_95_percentile"])) or
                int(np.sum(values > 0)) != expected["positive_patients"] or
                int(np.sum(values < 0)) != expected["negative_patients"]):
            raise ValueError(f"Summary/bootstrap mismatch: {field}")
    first = cases[0]
    image = nib.load(REGISTRY[first["case"]]["T2_path"]).get_fdata(dtype=np.float32)
    for row in first["rows"]:
        z = row["z"]
        i = z // 4
        left, right = image[:, :, 4 * i], image[:, :, 4 * (i + 1)]
        support = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                   (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
        raw = (1 - (z % 4) / 4) * left.astype(np.float64) + (z % 4) / 4 * right.astype(np.float64)
        error = (raw - image[:, :, z])[support]
        if (int(support.sum()) != row["support_pixels"] or
                not close(float(np.mean(error * error)), row["raw_linear_mse"])):
            raise ValueError(f"First-case pixel replay mismatch: z{z}")
    print("PASS: 58 cases, 232 targets, source hashes, patient means, bootstrap, first-case raw pixels")


if __name__ == "__main__":
    main()
