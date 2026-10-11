"""Exploratory clustered analysis of the P1-P12 finite-response stage."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from msvalid_mira_confirmation import sha256


ROOT = Path(__file__).resolve().parents[2] / "innovation" / "experiments"
PILOT = ROOT / "msvalid_influence_pilot_p1"
STAGE = ROOT / "msvalid_influence_stage1_p2_p12"
OUT = ROOT / "msvalid_influence_stage1_analysis"
SEED = 20261003


def rho(x: np.ndarray, y: np.ndarray) -> float:
    value = spearmanr(x, y).statistic
    return float(value) if np.isfinite(value) else float("nan")


def partial_rank(x: np.ndarray, y: np.ndarray, geometry: np.ndarray,
                 groups: np.ndarray) -> float:
    a, b = rankdata(x).astype(float), rankdata(y).astype(float)
    controls = np.column_stack([rankdata(geometry[:, j]) for j in range(geometry.shape[1])])
    for group in np.unique(groups):
        indices = groups == group
        a[indices] -= a[indices].mean()
        b[indices] -= b[indices].mean()
        controls[indices] -= controls[indices].mean(axis=0)
    a -= controls @ np.linalg.lstsq(controls, a, rcond=None)[0]
    b -= controls @ np.linalg.lstsq(controls, b, rcond=None)[0]
    denominator = np.sqrt((a @ a) * (b @ b))
    return float((a @ b) / denominator) if denominator > 0 else float("nan")


def prepare() -> pd.DataFrame:
    for path in (PILOT, STAGE):
        if not (path / "summary.json").is_file():
            raise FileNotFoundError(f"Missing completed run: {path}")
    p1 = pd.read_csv(PILOT / "per_context.csv")
    p1 = p1[p1.z.isin([11, 13])]
    later = pd.read_csv(STAGE / "per_context.csv")
    frame = pd.concat([p1, later], ignore_index=True)
    frame["target_id"] = frame.patient + "/z" + frame.z.astype(str)
    if (len(frame) != 216 or frame.patient.nunique() != 12 or
            frame.target_id.nunique() != 24 or
            not frame.groupby("target_id").size().eq(9).all() or
            not frame.groupby(["target_id", "shared_anchor_count"]).size()
                     .unstack().eq([4, 4, 1]).all().all()):
        raise AssertionError("Stage-1 geometry or sample count changed")
    if not np.isfinite(frame[["influence", "error_cosine", "observable",
                              "span_mm", "asymmetry_mm"]]).all().all():
        raise AssertionError("Nonfinite observations")
    if not frame.influence.between(-1 - 1e-6, 1 + 1e-6).all():
        raise AssertionError("Influence outside cosine range")
    return frame


def scores(frame: pd.DataFrame) -> dict:
    all_nonself = frame[frame.shared_anchor_count != 2]
    one = frame[frame.shared_anchor_count == 1]
    geometry = one[["span_mm", "asymmetry_mm"]].to_numpy()
    x, y = one.influence.to_numpy(), one.error_cosine.to_numpy()
    return {
        "rho_influence_alignment_all_nonself": rho(all_nonself.influence, all_nonself.error_cosine),
        "rho_count_alignment_all_nonself": rho(all_nonself.shared_anchor_count, all_nonself.error_cosine),
        "beyond_count_abs_rho": (abs(rho(all_nonself.influence, all_nonself.error_cosine)) -
                                 abs(rho(all_nonself.shared_anchor_count, all_nonself.error_cosine))),
        "fixed_count_rho": rho(x, y),
        "fixed_count_partial_patient": partial_rank(x, y, geometry, one.patient.to_numpy()),
        "fixed_count_partial_target": partial_rank(x, y, geometry, one.target_id.to_numpy()),
        "fixed_count_rho_observable": rho(x, one.observable.to_numpy()),
    }


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite: {OUT}")
    frame = prepare()
    point = scores(frame)
    rng = np.random.default_rng(SEED)
    patient_ids = sorted(frame.patient.unique(), key=lambda name: int(name[1:]))
    chunks = {patient: frame[frame.patient == patient].copy() for patient in patient_ids}
    endpoints = ("beyond_count_abs_rho", "fixed_count_partial_patient",
                 "fixed_count_partial_target")
    draws = {key: [] for key in endpoints}
    for _ in range(3000):
        parts = []
        for index in rng.integers(0, len(patient_ids), len(patient_ids)):
            part = chunks[patient_ids[index]].copy()
            replicate = len(parts)
            part["patient"] = f"B{replicate}"
            part["target_id"] = part.patient + "/z" + part.z.astype(str)
            parts.append(part)
        values = scores(pd.concat(parts, ignore_index=True))
        for key in endpoints:
            draws[key].append(values[key])
    ci = {key: np.percentile(values, [2.5, 97.5]).tolist()
          for key, values in draws.items()}

    one = frame[frame.shared_anchor_count == 1].copy()
    observed = point["fixed_count_partial_target"]
    permutations = []
    for _ in range(2000):
        altered = one.copy()
        for _, group in one.groupby("target_id", sort=False):
            altered.loc[group.index, "influence"] = rng.permutation(group.influence.to_numpy())
        geom = altered[["span_mm", "asymmetry_mm"]].to_numpy()
        permutations.append(partial_rank(altered.influence.to_numpy(),
                                         altered.error_cosine.to_numpy(), geom,
                                         altered.target_id.to_numpy()))
    permutation_p = (1 + sum(abs(value) >= abs(observed) for value in permutations)) / 2001
    by_overlap = frame.groupby("shared_anchor_count")[
        ["observable", "error_cosine", "influence", "b_mae"]].mean()
    result = {"status": "post-result and post-P1 exploratory; 12 patients, not independent confirmation",
              "pilot_per_context_sha256": sha256(PILOT / "per_context.csv"),
              "stage_per_context_sha256": sha256(STAGE / "per_context.csv"),
              "script_sha256": sha256(Path(__file__)), "patients": len(patient_ids),
              "targets": frame.target_id.nunique(), "contexts": len(frame),
              "one_overlap_rows": len(one), "point": point,
              "ci95_patient_bootstrap_exploratory": ci,
              "negative_control": {"type": "within-target influence-score permutation; not physical anchor-ID shuffle",
                                   "draws": 2000, "two_sided_p_exploratory": permutation_p},
              "mean_by_overlap": by_overlap.to_dict(orient="index")}
    OUT.mkdir(parents=True)
    frame.to_csv(OUT / "per_context.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
