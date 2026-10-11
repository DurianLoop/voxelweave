"""Read-only audit of ReMIND common-normalization and reverse-phase controls."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "experiments/remind_postresult_controls"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def eq(a: float, b: float) -> None:
    assert np.isclose(float(a), float(b), rtol=1e-10, atol=1e-12), (a, b)


def main() -> None:
    report = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    cohort = json.loads((BASE / "literature/remind_native_t2_qualification.json").read_text(encoding="utf-8"))
    main = json.loads((BASE / "experiments/remind_native_t2_ixi_pair/summary.json").read_text(encoding="utf-8"))
    checks = {"plan_sha256": BASE / "REMIND_POSTRESULT_CONTROLS_PLAN_2026-10-01.md",
              "script_sha256": BASE / "experiments/remind_postresult_controls.py",
              "qualification_sha256": BASE / "literature/remind_native_t2_qualification.json",
              "original_summary_sha256": BASE / "experiments/remind_native_t2_ixi_pair/summary.json",
              "original_per_patient_sha256": BASE / "experiments/remind_native_t2_ixi_pair/per_patient.csv"}
    for key, path in checks.items():
        assert report[key] == sha(path), key
    checkpoints = {"hat": BASE.parent / "baseline/ixi_hat_2p5d/runs/full_test115/checkpoints/hat_epoch_best.pth",
                   "swinir": BASE.parent / "baseline/ixi_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth"}
    assert report["checkpoint_sha256"] == main["checkpoint_sha256"]
    for name, path in checkpoints.items():
        assert report["checkpoint_sha256"][name] == sha(path)
    qualified = {r["patient"]: r for r in cohort["records"]}
    assert len(qualified) == report["patients_expected"] == 63
    downloads = json.loads((BASE / "literature/remind_native_t2_download_manifest.json").read_text(encoding="utf-8"))
    assert len(downloads["records"]) == 63
    for record in downloads["records"]:
        assert record["zip_sha256"] == sha(BASE / record["path"])
    target = rows(OUT / "per_target.csv")
    patient = rows(OUT / "per_patient.csv")
    original = {r["patient"]: r for r in rows(BASE / "experiments/remind_native_t2_ixi_pair/per_patient.csv")}
    assert len(original) == 62
    ids = [r["patient"] for r in patient]
    failed = {r["patient"] for r in report["failures"]}
    assert len(set(ids)) == len(ids)
    assert set(ids).isdisjoint(failed)
    assert set(ids) | failed == set(qualified)
    assert len(patient) == report["patients_scored"]
    assert len(target) == report["targets_scored"] == 4 * len(patient)
    assert report["failures"] == [{"patient": "ReMIND-092", "stage": "header",
                                   "error": qualified["ReMIND-092"]["reason"]}]
    grouped = defaultdict(list)
    for row in target:
        record = qualified[row["patient"]]
        assert row["series_description"] == record["series_description"]
        assert int(row["z"]) in record["targets"][row["residue"]]
        assert 0 < int(row["forward_support_pixels"]) <= np.prod(record["shape"])
        assert 0 < int(row["reverse_support_pixels"]) <= np.prod(record["shape"])
        for direction in ("forward", "reverse"):
            for condition in ("shared", "disjoint"):
                stem = f"{direction}_{condition}_"
                pair = (float(row[stem + "a_mse"]) + float(row[stem + "b_mse"])) / 2
                eq(row[stem + "paired_mse"], pair)
                eq(row[stem + "observable"], float(row[stem + "disagreement_mse"]) / (4 * pair))
            eq(row[f"{direction}_shared_a_mse"], row[f"{direction}_disjoint_a_mse"])
            eq(row[f"{direction}_shared_a_mae"], row[f"{direction}_disjoint_a_mae"])
            eq(row[f"{direction}_delta_o"],
               float(row[f"{direction}_disjoint_observable"]) - float(row[f"{direction}_shared_observable"]))
        grouped[row["patient"]].append(row)
    assert set(grouped) == set(ids)
    for p in patient:
        record = qualified[p["patient"]]
        sample = grouped[p["patient"]]
        assert len(sample) == int(p["targets"]) == 4
        assert {(r["residue"], int(r["z"])) for r in sample} == {
            (str(residue), z) for residue in (1, 3) for z in record["targets"][str(residue)]}
        assert p["series_description"] == record["series_description"]
        for row in sample:
            eq(row["common_lo"], p["common_lo"])
            eq(row["common_hi"], p["common_hi"])
        for direction in ("forward", "reverse"):
            for key in ("shared_observable", "disjoint_observable", "delta_o",
                        "shared_b_mae", "disjoint_b_mae"):
                name = f"{direction}_{key}"
                result = np.mean([np.mean([float(r[name]) for r in sample if r["residue"] == str(residue)])
                                  for residue in (1, 3)])
                eq(p[name], result)
            for residue in (1, 3):
                result = np.mean([float(r[f"{direction}_delta_o"]) for r in sample
                                  if r["residue"] == str(residue)])
                eq(p[f"{direction}_residue_{residue}_delta_o"], result)
        eq(p["original_delta_o"], original[p["patient"]]["delta_o"])
        eq(p["change_vs_original"], float(p["forward_delta_o"]) - float(p["original_delta_o"]))
    samples = np.array([[float(p["forward_delta_o"]), float(p["reverse_delta_o"])] for p in patient])
    eq(report["mean_forward_delta_o"], samples[:, 0].mean())
    eq(report["mean_reverse_delta_o"], samples[:, 1].mean())
    eq(report["mean_change_vs_original"], np.mean([float(p["change_vs_original"]) for p in patient]))
    assert report["positive_forward"] == int((samples[:, 0] > 0).sum())
    assert report["positive_reverse"] == int((samples[:, 1] > 0).sum())
    rng = np.random.default_rng(20261003)
    pooled = np.zeros((5000, 2))
    for name in ("2D_AX_T2", "2D_AX_T2_BLADE"):
        group = np.array([[float(p["forward_delta_o"]), float(p["reverse_delta_o"])]
                          for p in patient if p["series_description"] == name])
        stat = report["strata"][name]
        assert stat["patients"] == len(group)
        draws = group[rng.integers(0, len(group), (5000, len(group)))].mean(axis=1)
        pooled += draws * len(group) / len(patient)
        for j, direction in enumerate(("forward", "reverse")):
            eq(stat[f"mean_{direction}_delta_o"], group[:, j].mean())
            assert stat[f"positive_{direction}"] == int((group[:, j] > 0).sum())
            for got, expected in zip(stat[f"ci95_{direction}"], np.percentile(draws[:, j], [2.5, 97.5])):
                eq(got, expected)
    for j, direction in enumerate(("forward", "reverse")):
        for got, expected in zip(report[f"ci95_{direction}"], np.percentile(pooled[:, j], [2.5, 97.5])):
            eq(got, expected)
    sensitivity = (len(patient) == 62 and len(target) == 248 and report["ci95_forward"][0] > 0
                   and samples[:, 0].mean() >= main["mean_delta_o"] / 2
                   and all(report["strata"][name]["ci95_forward"][0] > 0 for name in report["strata"]))
    assert report["exploratory_normalization_sensitivity_pass"] == sensitivity
    print(f"PASS: {len(patient)}/63 patients, {len(target)} targets; "
          f"forward={samples[:, 0].mean():.6f}, reverse={samples[:, 1].mean():.6f}, "
          f"normalization_sensitivity={sensitivity}")


if __name__ == "__main__":
    main()
