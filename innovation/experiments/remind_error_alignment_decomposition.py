"""Read-only post-result decomposition of ReMIND paired-error observability."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "experiments/remind_native_t2_ixi_pair/per_target.csv"
MAIN = BASE / "experiments/remind_native_t2_ixi_pair/summary.json"
PLAN = BASE / "REMIND_ERROR_ALIGNMENT_DECOMPOSITION_PLAN_2026-10-01.md"
OUT = BASE / "experiments/remind_error_alignment_decomposition"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observable(r: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return .5 - r * np.sqrt(a * b) / (a + b)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    frame = pd.read_csv(SOURCE)
    main = json.loads(MAIN.read_text(encoding="utf-8"))
    if len(frame) != 248 or frame.patient.nunique() != 62 or main["patients_scored"] != 62:
        raise AssertionError("sample mismatch")
    a = frame.shared_a_mse.to_numpy(dtype=float)
    bs = frame.shared_b_mse.to_numpy(dtype=float)
    bd = frame.disjoint_b_mse.to_numpy(dtype=float)
    os = frame.shared_observable.to_numpy(dtype=float)
    od = frame.disjoint_observable.to_numpy(dtype=float)
    if not np.isfinite(np.column_stack([a, bs, bd, os, od])).all() or min(a.min(), bs.min(), bd.min()) <= 0:
        raise AssertionError("nonfinite or nonpositive inputs")
    if not np.allclose(a, frame.disjoint_a_mse, rtol=0, atol=1e-8):
        raise AssertionError("fixed reference changed")
    rs = (.5 - os) * (a + bs) / np.sqrt(a * bs)
    rd = (.5 - od) * (a + bd) / np.sqrt(a * bd)
    if np.max(np.abs(rs)) > 1 + 1e-8 or np.max(np.abs(rd)) > 1 + 1e-8:
        raise AssertionError("invalid cosine")
    if not np.allclose(observable(rs, a, bs), os, atol=1e-10) or not np.allclose(observable(rd, a, bd), od, atol=1e-10):
        raise AssertionError("observable identity failed")
    fss = observable(rs, a, bs)
    fsd = observable(rs, a, bd)
    fds = observable(rd, a, bs)
    fdd = observable(rd, a, bd)
    quality = .5 * ((fsd - fss) + (fdd - fds))
    alignment = .5 * ((fds - fss) + (fdd - fsd))
    error = np.max(np.abs(quality + alignment - frame.delta_o.to_numpy(dtype=float)))
    if error > 1e-10:
        raise AssertionError("component sum failed")
    frame["shared_error_cosine"] = rs
    frame["disjoint_error_cosine"] = rd
    frame["quality_imbalance_contribution"] = quality
    frame["alignment_contribution"] = alignment
    keys = ["delta_o", "shared_error_cosine", "disjoint_error_cosine",
            "quality_imbalance_contribution", "alignment_contribution"]
    residues = frame.groupby(["patient", "series_description", "residue"])[keys].mean()
    counts = residues.groupby(level="patient").size()
    if not counts.eq(2).all():
        raise AssertionError("incomplete residue")
    patients = residues.groupby(["patient", "series_description"]).mean().reset_index()
    if not np.isclose(patients.delta_o.mean(), main["mean_delta_o"], atol=1e-12):
        raise AssertionError("main estimate mismatch")
    rng = np.random.default_rng(20261004)
    pooled = np.zeros((5000, len(keys)))
    strata = {}
    for name in ("2D_AX_T2", "2D_AX_T2_BLADE"):
        values = patients.loc[patients.series_description == name, keys].to_numpy(dtype=float)
        draws = values[rng.integers(0, len(values), (5000, len(values)))].mean(axis=1)
        pooled += draws * len(values) / len(patients)
        strata[name] = {"patients": len(values), "points": dict(zip(keys, values.mean(axis=0).tolist())),
                        "ci95": {key: np.percentile(draws[:, i], [2.5, 97.5]).tolist()
                                 for i, key in enumerate(keys)}}
    ratio = bd / bs
    matched = []
    for tolerance in (.05, .10, .20):
        subset = frame[(ratio >= 1 / (1 + tolerance)) & (ratio <= 1 + tolerance)]
        matched.append({"mse_ratio_tolerance": tolerance, "targets": len(subset),
                        "patients": subset.patient.nunique(),
                        "target_equal_mean_delta_o": float(subset.delta_o.mean()) if len(subset) else None,
                        "positive_targets": int((subset.delta_o > 0).sum())})
    result = {"status": "post-result algebraic description; not independent or causal evidence",
              "source_sha256": sha(SOURCE), "main_summary_sha256": sha(MAIN),
              "plan_sha256": sha(PLAN), "script_sha256": sha(Path(__file__)),
              "patients": len(patients), "targets": len(frame),
              "points": patients[keys].mean().to_dict(),
              "ci95_exploratory": {key: np.percentile(pooled[:, i], [2.5, 97.5]).tolist()
                                   for i, key in enumerate(keys)},
              "strata": strata, "matched_target_descriptive": matched,
              "max_abs_component_identity_error": float(error)}
    OUT.mkdir(parents=True)
    frame.to_csv(OUT / "per_target.csv", index=False)
    patients.to_csv(OUT / "per_patient.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
