"""Read-only cross-check of the ReMIND post-result algebraic decomposition."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "experiments/remind_error_alignment_decomposition"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eq(a: float, b: float) -> None:
    assert np.isclose(float(a), float(b), rtol=1e-10, atol=1e-12), (a, b)


def main() -> None:
    report = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    source = BASE / "experiments/remind_native_t2_ixi_pair/per_target.csv"
    main_summary = BASE / "experiments/remind_native_t2_ixi_pair/summary.json"
    assert report["source_sha256"] == sha(source)
    assert report["main_summary_sha256"] == sha(main_summary)
    assert report["plan_sha256"] == sha(BASE / "REMIND_ERROR_ALIGNMENT_DECOMPOSITION_PLAN_2026-10-01.md")
    assert report["script_sha256"] == sha(BASE / "experiments/remind_error_alignment_decomposition.py")
    original = pd.read_csv(source).sort_values(["patient", "z"]).reset_index(drop=True)
    scored = pd.read_csv(OUT / "per_target.csv").sort_values(["patient", "z"]).reset_index(drop=True)
    assert len(original) == len(scored) == report["targets"] == 248
    assert scored.patient.nunique() == report["patients"] == 62
    for key in original.columns:
        if is_numeric_dtype(original[key]):
            assert np.allclose(original[key], scored[key], rtol=1e-12, atol=1e-12), key
        else:
            assert original[key].equals(scored[key]), key
    a = original.shared_a_mse.to_numpy()
    bs = original.shared_b_mse.to_numpy()
    bd = original.disjoint_b_mse.to_numpy()
    os = original.shared_observable.to_numpy()
    od = original.disjoint_observable.to_numpy()
    rs = (.5 - os) * (a + bs) / np.sqrt(a * bs)
    rd = (.5 - od) * (a + bd) / np.sqrt(a * bd)
    assert np.allclose(rs, scored.shared_error_cosine, atol=1e-12)
    assert np.allclose(rd, scored.disjoint_error_cosine, atol=1e-12)
    f = lambda r, b: .5 - r * np.sqrt(a * b) / (a + b)
    q = (f(rs, bd) - f(rs, bs) + f(rd, bd) - f(rd, bs)) / 2
    c = (f(rd, bs) - f(rs, bs) + f(rd, bd) - f(rs, bd)) / 2
    assert np.allclose(q, scored.quality_imbalance_contribution, atol=1e-12)
    assert np.allclose(c, scored.alignment_contribution, atol=1e-12)
    assert np.allclose(q + c, original.delta_o, atol=1e-12)
    keys = ["delta_o", "shared_error_cosine", "disjoint_error_cosine",
            "quality_imbalance_contribution", "alignment_contribution"]
    patient = (scored.groupby(["patient", "series_description", "residue"])[keys].mean()
               .groupby(["patient", "series_description"]).mean().reset_index())
    saved_patient = pd.read_csv(OUT / "per_patient.csv").sort_values("patient").reset_index(drop=True)
    patient = patient.sort_values("patient").reset_index(drop=True)
    assert patient.patient.equals(saved_patient.patient)
    for key in keys:
        assert np.allclose(patient[key], saved_patient[key], atol=1e-12)
        eq(report["points"][key], patient[key].mean())
    eq(report["points"]["delta_o"], json.loads(main_summary.read_text(encoding="utf-8"))["mean_delta_o"])
    rng = np.random.default_rng(20261004)
    pooled = np.zeros((5000, len(keys)))
    for name in ("2D_AX_T2", "2D_AX_T2_BLADE"):
        values = patient.loc[patient.series_description == name, keys].to_numpy()
        stat = report["strata"][name]
        assert stat["patients"] == len(values)
        draws = values[rng.integers(0, len(values), (5000, len(values)))].mean(axis=1)
        pooled += draws * len(values) / len(patient)
        for j, key in enumerate(keys):
            eq(stat["points"][key], values[:, j].mean())
            for got, expected in zip(stat["ci95"][key], np.percentile(draws[:, j], [2.5, 97.5])):
                eq(got, expected)
    for j, key in enumerate(keys):
        for got, expected in zip(report["ci95_exploratory"][key], np.percentile(pooled[:, j], [2.5, 97.5])):
            eq(got, expected)
    for entry in report["matched_target_descriptive"]:
        tolerance = entry["mse_ratio_tolerance"]
        ratio = bd / bs
        subset = original[(ratio >= 1 / (1 + tolerance)) & (ratio <= 1 + tolerance)]
        assert entry["targets"] == len(subset)
        assert entry["patients"] == subset.patient.nunique()
        eq(entry["target_equal_mean_delta_o"], subset.delta_o.mean())
        assert entry["positive_targets"] == int((subset.delta_o > 0).sum())
    print(f"PASS: {len(patient)} patients, {len(scored)} targets; "
          f"quality={patient.quality_imbalance_contribution.mean():.6f}, "
          f"alignment={patient.alignment_contribution.mean():.6f}")


if __name__ == "__main__":
    main()
