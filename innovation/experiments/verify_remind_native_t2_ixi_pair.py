"""Read-only audit of the frozen ReMIND patient-level confirmation output."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


INNOVATION = Path(__file__).resolve().parents[1]
QUALIFIED = INNOVATION / "literature/remind_native_t2_qualification.json"
OUT = INNOVATION / "experiments/remind_native_t2_ixi_pair"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def close(actual: float, expected: float) -> None:
    if not np.isclose(actual, expected, rtol=1e-10, atol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    cohort = json.loads(QUALIFIED.read_text(encoding="utf-8"))
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    targets = read_csv(OUT / "per_target.csv")
    patients = read_csv(OUT / "per_patient.csv")
    assert len(cohort["records"]) == summary["patients_expected"] == 63
    assert cohort["patients_header_eligible"] == summary["patients_header_eligible"] == 62
    assert summary["qualification_sha256"] == sha256(QUALIFIED)
    assert summary["protocol_sha256"] == sha256(INNOVATION / "REMIND_NATIVE_T2_CONFIRMATION_PROTOCOL_2026-10-01.md")
    assert summary["script_sha256"] == sha256(INNOVATION / "experiments/remind_native_t2_ixi_pair.py")
    assert summary["inventory_sha256"] == sha256(INNOVATION / "literature/remind_native_t2_inventory.json")
    assert summary["download_manifest_sha256"] == sha256(INNOVATION / "literature/remind_native_t2_download_manifest.json")
    assert summary["precision"] == "CPU float32"
    checkpoints = {
        "hat": INNOVATION.parent / "baseline/ixi_hat_2p5d/runs/full_test115/checkpoints/hat_epoch_best.pth",
        "swinir": INNOVATION.parent / "baseline/ixi_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth",
    }
    assert summary["checkpoint_sha256"] == {
        "hat": "2fae831ab933cf260972260ebec4349f3895106ac7b4d1af3ba368f407498eae",
        "swinir": "6a819e47e65bd96c2d6e5b6d3adc212e1a46347080a0a661c602367be8a6f323",
    }
    for name, path in checkpoints.items():
        assert summary["checkpoint_sha256"][name] == sha256(path)

    by_id = {record["patient"]: record for record in cohort["records"]}
    assert len(by_id) == 63
    downloads = json.loads((INNOVATION / "literature/remind_native_t2_download_manifest.json").read_text(encoding="utf-8"))
    assert len(downloads["records"]) == 63
    assert downloads["inventory_sha256"] == summary["inventory_sha256"]
    assert downloads["protocol_sha256"] == summary["protocol_sha256"]
    assert cohort["inventory_sha256"] == summary["inventory_sha256"]
    assert cohort["download_manifest_sha256"] == summary["download_manifest_sha256"]
    assert cohort["protocol_sha256"] == summary["protocol_sha256"]
    downloaded_ids = set()
    for record in downloads["records"]:
        downloaded_ids.add(record["patient"])
        assert record["zip_sha256"] == sha256(INNOVATION / record["path"])
        qualified = by_id[record["patient"]]
        if qualified["eligible"]:
            assert qualified["zip_sha256"] == record["zip_sha256"]
            assert qualified["path"] == record["path"]
    assert downloaded_ids == set(by_id)
    failure_ids = [failure["patient"] for failure in summary["failures"]]
    scored_ids = [patient["patient"] for patient in patients]
    assert len(set(failure_ids + scored_ids)) == 63
    assert set(failure_ids).isdisjoint(scored_ids)
    assert set(failure_ids + scored_ids) == set(by_id)
    assert summary["patients_scored"] == len(patients)
    assert summary["targets_scored"] == len(targets) == 4 * len(patients)
    for failure in summary["failures"]:
        record = by_id[failure["patient"]]
        if not record["eligible"]:
            assert failure["stage"] == "header"
            assert failure["error"] == record["reason"]

    by_patient = defaultdict(list)
    for row in targets:
        record = by_id[row["patient"]]
        assert record["eligible"]
        assert row["series_description"] == record["series_description"]
        assert int(row["z"]) in record["targets"][row["residue"]]
        assert int(row["z"]) % 4 == int(row["residue"])
        assert 0 < float(row["support_fraction"]) <= 1
        assert 0 < int(row["support_pixels"]) <= record["shape"][0] * record["shape"][1]
        for prefix in ("shared", "disjoint"):
            a_mse = float(row[f"{prefix}_a_mse"])
            b_mse = float(row[f"{prefix}_b_mse"])
            pair_mse = float(row[f"{prefix}_paired_mse"])
            close(pair_mse, (a_mse + b_mse) / 2)
            close(float(row[f"{prefix}_observable"]),
                  float(row[f"{prefix}_disagreement_mse"]) / (4 * pair_mse))
        close(float(row["shared_a_mae"]), float(row["disjoint_a_mae"]))
        close(float(row["shared_a_mse"]), float(row["disjoint_a_mse"]))
        close(float(row["delta_o"]),
              float(row["disjoint_observable"]) - float(row["shared_observable"]))
        by_patient[row["patient"]].append(row)

    assert set(by_patient) == set(scored_ids)
    for patient in patients:
        record = by_id[patient["patient"]]
        rows = by_patient[patient["patient"]]
        expected = {(str(residue), str(z)) for residue in (1, 3)
                    for z in record["targets"][str(residue)]}
        assert {(row["residue"], row["z"]) for row in rows} == expected
        assert len(rows) == len(expected) == int(patient["targets"]) == 4
        assert patient["series_description"] == record["series_description"]
        for key in ("delta_o", "shared_observable", "disjoint_observable",
                    "shared_a_mae", "shared_b_mae", "disjoint_b_mae",
                    "shared_paired_mse", "disjoint_paired_mse"):
            value = np.mean([np.mean([float(row[key]) for row in rows
                                      if row["residue"] == str(residue)])
                             for residue in (1, 3)])
            close(float(patient[key]), value)
        for residue in (1, 3):
            value = np.mean([float(row["delta_o"]) for row in rows
                             if row["residue"] == str(residue)])
            close(float(patient[f"residue_{residue}_delta_o"]), value)

    values = np.array([float(p["delta_o"]) for p in patients])
    close(summary["mean_delta_o"], float(values.mean()))
    assert summary["positive_patients"] == int((values > 0).sum())
    assert summary["negative_patients"] == int((values < 0).sum())
    for key in ("shared_observable", "disjoint_observable"):
        close(summary[f"mean_{key.split('_')[0]}_o"],
              float(np.mean([float(p[key]) for p in patients])))
    for residue in (1, 3):
        close(summary[f"mean_residue_{residue}_delta_o"],
              float(np.mean([float(p[f'residue_{residue}_delta_o']) for p in patients])))

    rng = np.random.default_rng(20261002)
    pooled = np.zeros(5000)
    for name in ("2D_AX_T2", "2D_AX_T2_BLADE"):
        stratum = np.array([float(p["delta_o"]) for p in patients
                            if p["series_description"] == name])
        report = summary["strata"][name]
        assert report["patients"] == len(stratum)
        assert report["positive_patients"] == int((stratum > 0).sum())
        if len(stratum):
            close(report["mean_delta_o"], float(stratum.mean()))
            draws = stratum[rng.integers(0, len(stratum), (5000, len(stratum)))].mean(axis=1)
            for got, expected in zip(report["ci95_delta_o"], np.percentile(draws, [2.5, 97.5])):
                close(got, expected)
            pooled += draws * len(stratum) / len(values)
        else:
            assert report["mean_delta_o"] is None
            assert report["ci95_delta_o"] == [None, None]
    ci = np.percentile(pooled, [2.5, 97.5])
    for got, expected in zip(summary["ci95_delta_o"], ci):
        close(got, expected)
    success = (len(patients) >= 50 and summary["strata"]["2D_AX_T2"]["patients"] >= 25
               and summary["strata"]["2D_AX_T2_BLADE"]["patients"] >= 20
               and ci[0] > 0
               and all(summary["strata"][name]["mean_delta_o"] is not None
                       and summary["strata"][name]["mean_delta_o"] > 0
                       for name in summary["strata"]))
    assert summary["primary_success"] == success
    print(f"PASS: {len(patients)}/63 patients, {len(targets)} targets; "
          f"delta O={values.mean():.6f}, CI=({ci[0]:.6f}, {ci[1]:.6f}), "
          f"primary_success={success}")


if __name__ == "__main__":
    main()
