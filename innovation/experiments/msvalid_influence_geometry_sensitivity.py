"""Post-result sensitivity: exact context and target effects on influence alignment."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from msvalid_mira_confirmation import sha256


ROOT = Path(__file__).resolve().parents[2] / "innovation"
SOURCE = ROOT / "experiments/msvalid_influence_stage1_analysis/per_context.csv"
OUT = ROOT / "experiments/msvalid_influence_geometry_sensitivity"


def partial(frame: pd.DataFrame, adjust_partner_error: bool) -> float:
    a = rankdata(frame.influence).astype(float)
    b = rankdata(frame.error_cosine).astype(float)
    target = pd.get_dummies(frame.target_id, drop_first=True, dtype=float).to_numpy()
    context = pd.get_dummies(frame.context_type, drop_first=True, dtype=float).to_numpy()
    columns = [np.ones(len(frame)), target, context]
    if adjust_partner_error:
        columns.append(rankdata(frame.b_mae).astype(float))
    design = np.column_stack(columns)
    ra = a - design @ np.linalg.lstsq(design, a, rcond=None)[0]
    rb = b - design @ np.linalg.lstsq(design, b, rcond=None)[0]
    denominator = np.sqrt((ra @ ra) * (rb @ rb))
    return float((ra @ rb) / denominator) if denominator > 0 else float("nan")


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite: {OUT}")
    frame = pd.read_csv(SOURCE)
    frame = frame[frame.shared_anchor_count == 1].copy()
    frame["target_id"] = frame.patient + "/z" + frame.z.astype(str)
    frame["context_type"] = (frame.residue.astype(str) + ":" +
                             frame.context_left_offset.astype(str) + "," +
                             frame.context_right_offset.astype(str))
    if (len(frame) != 96 or frame.patient.nunique() != 12 or
            frame.target_id.nunique() != 24 or not frame.groupby("target_id").size().eq(4).all()):
        raise AssertionError("Stage-1 sample contract mismatch")
    points = {"target_and_exact_context": partial(frame, False),
              "plus_retrospective_partner_mae": partial(frame, True)}
    patient_ids = sorted(frame.patient.unique(), key=lambda name: int(name[1:]))
    chunks = {patient: frame[frame.patient == patient].copy() for patient in patient_ids}
    rng = np.random.default_rng(20261006)
    draws = {key: [] for key in points}
    for _ in range(3000):
        parts = []
        for replicate, index in enumerate(rng.integers(0, len(patient_ids), len(patient_ids))):
            chunk = chunks[patient_ids[index]].copy()
            chunk["patient"] = f"B{replicate}"
            chunk["target_id"] = chunk.patient + "/z" + chunk.z.astype(str)
            parts.append(chunk)
        sample = pd.concat(parts, ignore_index=True)
        draws["target_and_exact_context"].append(partial(sample, False))
        draws["plus_retrospective_partner_mae"].append(partial(sample, True))
    result = {"status": "post-result sensitivity; not independent confirmation or deployment score",
              "source_csv_sha256": sha256(SOURCE), "script_sha256": sha256(Path(__file__)),
              "patients": 12, "targets": 24, "one_overlap_rows": len(frame),
              "context_types": frame.context_type.nunique(), "points": points,
              "ci95_patient_bootstrap_exploratory": {
                  key: np.percentile(values, [2.5, 97.5]).tolist()
                  for key, values in draws.items()}}
    OUT.mkdir(parents=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
