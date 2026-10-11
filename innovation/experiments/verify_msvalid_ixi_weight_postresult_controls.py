"""Read-only audit of the IXI-weight MSValid common-scale/reverse controls."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "experiments/msvalid_ixi_weight_postresult_controls"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def eq(got: float, expected: float) -> None:
    assert np.isclose(float(got), float(expected), rtol=1e-10, atol=1e-12), (got, expected)


def main() -> None:
    report = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    paths = {"plan_sha256": BASE / "MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_PLAN_2026-10-01.md",
             "script_sha256": BASE / "experiments/msvalid_ixi_weight_postresult_controls.py",
             "qualification_sha256": BASE / "literature/msvalid_geometry_qualification.json",
             "source_manifest_sha256": BASE / "literature/msvalid_extraction_manifest.json",
             "original_summary_sha256": BASE / "experiments/msvalid_ixi_weights_secondary/summary.json",
             "original_per_patient_sha256": BASE / "experiments/msvalid_ixi_weights_secondary/per_patient.csv"}
    for key, path in paths.items():
        assert report[key] == sha(path), key
    main = json.loads(paths["original_summary_sha256"].read_text(encoding="utf-8"))
    assert report["checkpoint_sha256"] == main["checkpoint_sha256"]
    checkpoints = {"hat": BASE.parent / "baseline/ixi_hat_2p5d/runs/full_test115/checkpoints/hat_epoch_best.pth",
                   "swinir": BASE.parent / "baseline/ixi_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth"}
    for name, path in checkpoints.items():
        assert report["checkpoint_sha256"][name] == sha(path)
    cohort = json.loads(paths["qualification_sha256"].read_text(encoding="utf-8"))
    selected = {p["patient"]: p for p in cohort["patients"]}
    assert len(selected) == report["patients_expected"] == 84
    manifest = json.loads(paths["source_manifest_sha256"].read_text(encoding="utf-8"))
    sources = {r["patient"]: r["sha256"] for r in manifest["records"]}
    assert set(sources) == set(selected)
    for pid, expected in sources.items():
        assert expected == sha(BASE / f"data/msvalid_first_t2/{pid}.nii.gz")
    target = rows(OUT / "per_target.csv")
    patient = rows(OUT / "per_patient.csv")
    original = {r["patient"]: r for r in rows(paths["original_per_patient_sha256"])}
    assert len(original) == 84
    assert report["failures"] == []
    assert len(patient) == report["patients_scored"] == 84
    assert len(target) == report["targets_scored"] == 479
    assert {p["patient"] for p in patient} == set(selected)
    grouped = defaultdict(list)
    for row in target:
        record = selected[row["patient"]]
        assert int(row["z"]) in record["eligible_targets"][f"residue_{row['residue']}"]
        assert int(row["z"]) % 4 == int(row["residue"])
        assert 0 < int(row["forward_support_pixels"]) <= record["shape"][0] * record["shape"][1]
        assert 0 < int(row["reverse_support_pixels"]) <= record["shape"][0] * record["shape"][1]
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
    assert set(grouped) == set(selected)
    keys = ("forward_shared_observable", "forward_disjoint_observable", "forward_delta_o",
            "reverse_shared_observable", "reverse_disjoint_observable", "reverse_delta_o",
            "forward_shared_b_mae", "forward_disjoint_b_mae",
            "reverse_shared_b_mae", "reverse_disjoint_b_mae")
    for p in patient:
        sample = grouped[p["patient"]]
        record = selected[p["patient"]]
        expected = {(str(residue), z) for residue in (1, 3)
                    for z in record["eligible_targets"][f"residue_{residue}"]}
        assert {(r["residue"], int(r["z"])) for r in sample} == expected
        assert len(sample) == len(expected) == int(p["targets"])
        for r in sample:
            eq(r["common_lo"], p["common_lo"])
            eq(r["common_hi"], p["common_hi"])
        for key in keys:
            value = np.mean([np.mean([float(r[key]) for r in sample if r["residue"] == str(residue)])
                             for residue in (1, 3)])
            eq(p[key], value)
        for direction in ("forward", "reverse"):
            for residue in (1, 3):
                value = np.mean([float(r[f"{direction}_delta_o"]) for r in sample
                                 if r["residue"] == str(residue)])
                eq(p[f"{direction}_residue_{residue}_delta_o"], value)
        eq(p["original_delta_o"], original[p["patient"]]["delta_o"])
        eq(p["change_vs_original"], float(p["forward_delta_o"]) - float(p["original_delta_o"]))
    values = np.array([[float(p["forward_delta_o"]), float(p["reverse_delta_o"])] for p in patient])
    rng = np.random.default_rng(20261005)
    draws = values[rng.integers(0, len(values), (5000, len(values)))].mean(axis=1)
    for j, direction in enumerate(("forward", "reverse")):
        eq(report[f"mean_{direction}_delta_o"], values[:, j].mean())
        assert report[f"positive_{direction}"] == int((values[:, j] > 0).sum())
        for got, expected in zip(report[f"ci95_{direction}"], np.percentile(draws[:, j], [2.5, 97.5])):
            eq(got, expected)
    eq(report["mean_change_vs_original"], np.mean([float(p["change_vs_original"]) for p in patient]))
    sensitivity = (len(patient) == 84 and len(target) == 479 and report["ci95_forward"][0] > 0
                   and values[:, 0].mean() >= main["mean_delta_o"] / 2)
    assert report["exploratory_normalization_sensitivity_pass"] == sensitivity
    print(f"PASS: {len(patient)} patients, {len(target)} targets; "
          f"forward={values[:, 0].mean():.6f}, reverse={values[:, 1].mean():.6f}, "
          f"normalization_sensitivity={sensitivity}")


if __name__ == "__main__":
    main()
