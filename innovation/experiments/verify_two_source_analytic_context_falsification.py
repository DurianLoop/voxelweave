"""Read-only verification of the two-source analytic context control."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import zipfile
from collections import defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np
import pydicom
from scipy.interpolate import pchip_interpolate


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/two_source_analytic_context_falsification"
PLAN = ROOT / "TWO_SOURCE_ANALYTIC_CONTEXT_FALSIFICATION_PROTOCOL_2026-10-01.md"
SCRIPT = ROOT / "experiments/two_source_analytic_context_falsification.py"
ORIGINAL = {
    "msvalid": (ROOT / "experiments/msvalid_ixi_weights_secondary/per_target.csv",
                "ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4"),
    "remind": (ROOT / "experiments/remind_native_t2_ixi_pair/per_target.csv",
               "450def82f8f03261b55c36ffaed952ee865e7c3be83c0c5b77df1f6a8e441e1c"),
}
FIELDS = ("shared_o", "disjoint_o", "delta_o", "neural_delta_o",
          "analytic_minus_neural", "a_mse", "shared_b_mse", "disjoint_b_mse",
          "shared_paired_mse", "disjoint_paired_mse", "shared_disagreement_mse",
          "disjoint_disagreement_mse", "fixed_denominator_delta_o")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def near(left: float, right: float, name: str) -> None:
    if not math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-10):
        raise AssertionError(f"{name}: {left} != {right}")


def verify_pixel(source: str, result: dict, summary: dict) -> None:
    patient, z = result["patient"], int(result["z"])
    if source == "msvalid":
        manifest = json.loads((ROOT / "literature/msvalid_extraction_manifest.json").read_text(encoding="utf-8"))
        record = next(item for item in manifest["records"] if item["patient"] == patient)
        path = ROOT / record["path"]
        assert digest(path) == record["sha256"]
        volume = nib.load(str(path)).get_fdata(dtype=np.float32)
        plane = lambda q: volume[:, :, q]
    else:
        qualification = json.loads((ROOT / "literature/remind_native_t2_qualification.json").read_text(encoding="utf-8"))
        record = next(item for item in qualification["records"] if item["patient"] == patient)
        path = ROOT / record["path"]
        assert digest(path) == record["zip_sha256"]
        with zipfile.ZipFile(path) as archive:
            cache = {}
            for q in {z, 4 * (z // 4) - 4, 4 * (z // 4), 4 * (z // 4) + 4,
                      4 * (z // 4) + 8, 2 + 4 * ((z - 2) // 4), 6 + 4 * ((z - 2) // 4)}:
                with archive.open(record["ordered_files"][q]) as stream:
                    ds = pydicom.dcmread(stream)
                cache[q] = (ds.pixel_array.astype(np.float32) * float(ds.get("RescaleSlope", 1))
                            + float(ds.get("RescaleIntercept", 0)))
        plane = lambda q: cache[q]
    left = 4 * (z // 4)
    phase2 = 2 + 4 * ((z - 2) // 4)
    p0, p1 = plane(left), plane(left + 4)
    mask = ((np.abs(p0) > .01 * max(float(np.max(np.abs(p0))), 1e-6)) |
            (np.abs(p1) > .01 * max(float(np.max(np.abs(p1))), 1e-6)))
    assert int(mask.sum()) == int(result["support_pixels"])
    knots = [left - 4, left, left + 4, left + 8]
    a = pchip_interpolate(knots, np.stack([plane(q)[mask].astype(np.float64) for q in knots]), z, axis=0)
    y = plane(z)[mask].astype(np.float64)
    b0 = (1 - (z - left) / 4) * p0[mask].astype(np.float64) + (z - left) / 4 * p1[mask].astype(np.float64)
    b2 = ((1 - (z - phase2) / 4) * plane(phase2)[mask].astype(np.float64) +
          (z - phase2) / 4 * plane(phase2 + 4)[mask].astype(np.float64))
    for label, b in (("shared", b0), ("disjoint", b2)):
        near(np.mean((a - y) ** 2), result["a_mse"], f"{source} pixel a_mse")
        near(np.mean((b - y) ** 2), result[f"{label}_b_mse"], f"{source} pixel {label}_b_mse")
        near(np.mean((a - b) ** 2), result[f"{label}_disagreement_mse"],
             f"{source} pixel {label}_disagreement")


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    assert digest(PLAN) == summary["protocol_sha256"]
    assert digest(SCRIPT) == summary["script_sha256"]
    assert summary["gpu_used"] is False and summary["model_inference_run"] is False
    target_rows = rows(OUT / "per_target.csv")
    patient_rows = rows(OUT / "per_patient.csv")
    assert len(target_rows) == 727 and len(patient_rows) == 146
    original = {}
    for source, (path, expected) in ORIGINAL.items():
        assert digest(path) == expected
        for row in rows(path):
            original[(source, row["patient"], row["z"])] = row
    assert len(original) == 727
    assert {(r["source"], r["patient"], r["z"]) for r in target_rows} == set(original)
    grouped = defaultdict(list)
    for row in target_rows:
        key = (row["source"], row["patient"], row["z"])
        prior = original[key]
        assert int(row["support_pixels"]) == int(prior["support_pixels"])
        near(float(row["neural_delta_o"]), float(prior["delta_o"]), "neural target")
        a, b0, b2 = (float(row[name]) for name in ("a_mse", "shared_b_mse", "disjoint_b_mse"))
        d0, d2 = (float(row[name]) for name in ("shared_disagreement_mse", "disjoint_disagreement_mse"))
        o0, o2 = d0 / (2 * (a + b0)), d2 / (2 * (a + b2))
        near(o0, row["shared_o"], "shared O")
        near(o2, row["disjoint_o"], "disjoint O")
        near(o2 - o0, row["delta_o"], "target Delta O")
        near(o2 - o0 - float(prior["delta_o"]), row["analytic_minus_neural"], "target pair")
        near((d2 - d0) / (2 * (a + b0)), row["fixed_denominator_delta_o"], "fixed denominator")
        grouped[(row["source"], row["patient"])].append(row)
    assert set(grouped) == {(row["source"], row["patient"]) for row in patient_rows}
    by_patient = {(row["source"], row["patient"]): row for row in patient_rows}
    for key, targets in grouped.items():
        residues = {r: [row for row in targets if int(row["residue"]) == r] for r in (1, 3)}
        assert all(residues.values())
        patient = by_patient[key]
        assert len(targets) == int(patient["targets"])
        for name in FIELDS:
            value = np.mean([np.mean([float(row[name]) for row in residues[r]]) for r in (1, 3)])
            near(value, patient[name], f"patient {name}")
    for source, seed in (("msvalid", 20261007), ("remind", 20261008)):
        group = [row for row in patient_rows if row["source"] == source]
        recorded = summary["sources"][source]
        assert len(group) == recorded["patients"]
        assert sum(int(row["targets"]) for row in group) == recorded["targets"]
        for name in FIELDS:
            near(np.mean([float(row[name]) for row in group]), recorded[name], f"source {name}")
        assert sum(float(row["delta_o"]) > 0 for row in group) == recorded["positive_delta_patients"]
        rng = np.random.default_rng(seed)
        draw = np.zeros((5000, 2))
        if source == "msvalid":
            matrix = np.array([[float(row["delta_o"]), float(row["analytic_minus_neural"])] for row in group])
            draw = matrix[rng.integers(0, len(group), size=(5000, len(group)))].mean(axis=1)
        else:
            for label, n in (("2D_AX_T2", 35), ("2D_AX_T2_BLADE", 27)):
                matrix = np.array([[float(row["delta_o"]), float(row["analytic_minus_neural"])]
                                   for row in group if row["stratum"] == label])
                assert len(matrix) == n
                draw += matrix[rng.integers(0, n, size=(5000, n))].mean(axis=1) * n / len(group)
        for column, name in ((0, "delta_o_ci95"), (1, "analytic_minus_neural_ci95")):
            for actual, expected in zip(np.percentile(draw[:, column], [2.5, 97.5]), recorded[name]):
                near(actual, expected, f"{source} {name}")
        sample = next(row for row in target_rows if row["source"] == source)
        verify_pixel(source, sample, recorded)
    print("PASS: 727 target identities/formulas, 146 patient aggregates, four CIs, two pixel replays")


if __name__ == "__main__":
    main()
