"""Independent read-only recomputation of the processed-UPENN context endpoint."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/upenn_gbm_processed_t2_context"
QUALIFIED = ROOT / "literature/upenn_gbm_processed_t2_qualification.json"
INVENTORY = ROOT / "literature/upenn_gbm_processed_t2_inventory.json"
DOWNLOADS = ROOT / "literature/upenn_gbm_processed_t2_download_manifest.json"
PROTOCOL = ROOT / "UPENN_GBM_PROCESSED_T2_CONTEXT_PROTOCOL_2026-10-01.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-8)


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    qualification = json.loads(QUALIFIED.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    downloads = json.loads(DOWNLOADS.read_text(encoding="utf-8"))
    for name, path in (("protocol_sha256", PROTOCOL), ("qualification_sha256", QUALIFIED),
                       ("inventory_sha256", INVENTORY), ("download_manifest_sha256", DOWNLOADS)):
        assert summary[name] == sha256(path), name
    assert len(inventory["series"]) == 374
    assert len(qualification["records"]) == 374
    assert len({row["patient"] for row in qualification["records"]}) == 374
    assert len(downloads["records"]) + len(downloads["failures"]) == 374
    with (OUT / "per_target.csv").open(newline="", encoding="utf-8") as stream:
        targets = list(csv.DictReader(stream))
    with (OUT / "per_patient.csv").open(newline="", encoding="utf-8") as stream:
        patients = list(csv.DictReader(stream))
    by_patient = defaultdict(list)
    eligible = {row["patient"]: row for row in qualification["records"] if row["eligible"]}
    for row in targets:
        patient = row["patient"]
        assert patient in eligible
        assert int(row["z"]) in eligible[patient]["targets"][row["residue"]]
        shared = float(row["shared_observable"])
        disjoint = float(row["disjoint_observable"])
        assert close(float(row["delta_o"]), disjoint - shared)
        for prefix in ("shared", "disjoint"):
            a = float(row[f"{prefix}_a_mse"])
            b = float(row[f"{prefix}_b_mse"])
            disagreement = float(row[f"{prefix}_disagreement_mse"])
            assert close(float(row[f"{prefix}_paired_mse"]), (a + b) / 2)
            assert close(float(row[f"{prefix}_observable"]), disagreement / (4 * ((a + b) / 2)))
        assert close(float(row["shared_a_mse"]), float(row["disjoint_a_mse"]))
        by_patient[patient].append(row)
    assert len(patients) == summary["patients_scored"]
    assert len(targets) == summary["targets_scored"] == 4 * len(patients)
    assert set(by_patient) == {row["patient"] for row in patients}
    assert len(summary["failures"]) + len(patients) == 374
    values = []
    for row in patients:
        patient = row["patient"]
        found = by_patient[patient]
        assert len(found) == 4
        assert Counter(int(item["residue"]) for item in found) == {1: 2, 3: 2}
        residue_means = [np.mean([float(item["delta_o"]) for item in found
                                  if int(item["residue"]) == residue]) for residue in (1, 3)]
        average = float(np.mean(residue_means))
        assert close(float(row["delta_o"]), average)
        assert close(float(row["residue_1_delta_o"]), residue_means[0])
        assert close(float(row["residue_3_delta_o"]), residue_means[1])
        values.append(average)
    data = np.asarray(values, dtype=float)
    assert close(float(summary["mean_delta_o"]), float(data.mean()))
    rng = np.random.default_rng(20261004)
    ci = np.percentile(data[rng.integers(0, len(data), (5000, len(data)))].mean(axis=1),
                       [2.5, 97.5])
    assert np.allclose(ci, summary["ci95_delta_o"], rtol=1e-8, atol=1e-8)
    assert summary["positive_patients"] == int((data > 0).sum())
    assert summary["negative_patients"] == int((data < 0).sum())
    assert summary["primary_success"] == (len(data) >= 300 and ci[0] > 0)
    print(json.dumps({"status": "PASS", "patients": len(data), "targets": len(targets),
                      "mean_delta_o": float(data.mean()), "ci95": ci.tolist()}, indent=2))


if __name__ == "__main__":
    main()
