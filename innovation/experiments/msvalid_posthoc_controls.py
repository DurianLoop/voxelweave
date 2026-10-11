"""Post-result CPU controls for MSValid MIRA; not an independent confirmation."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import torch

from msvalid_mira_confirmation import MODELS, metrics, predict, prepared, sha256, write_csv


ROOT = Path(__file__).resolve().parents[2]
INNOVATION = ROOT / "innovation"
QUALIFIED = INNOVATION / "literature/msvalid_geometry_qualification.json"
ORIGINAL = INNOVATION / "experiments/msvalid_mira_confirmation/per_target.csv"
OUT = INNOVATION / "experiments/msvalid_posthoc_controls"


def linear(volume: np.ndarray, z: int, phase: int) -> np.ndarray:
    left = phase + ((z - phase) // 4) * 4
    rel = (z - left) / 4
    return ((1 - rel) * volume[:, :, left] + rel * volume[:, :, left + 4]).astype(np.float32)


def mean_balanced(rows: list[dict], key: str) -> float:
    return float(np.mean([np.mean([row[key] for row in rows if row["residue"] == r])
                          for r in (1, 3)]))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite exploratory run: {OUT}")
    cohort = json.loads(QUALIFIED.read_text(encoding="utf-8"))["patients"]
    if len(cohort) != 84 or not all(p["geometry_eligible"] for p in cohort):
        raise RuntimeError("Frozen MSValid cohort mismatch")
    for name, (_, path, expected) in MODELS.items():
        if sha256(path) != expected:
            raise ValueError(f"{name} checkpoint hash mismatch")
    with ORIGINAL.open(newline="", encoding="utf-8") as stream:
        original = {(r["patient"], int(r["z"])): r for r in csv.DictReader(stream)}
    if len(original) != 479:
        raise RuntimeError("Original target count mismatch")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    OUT.mkdir(parents=True)
    per_target, per_patient = [], []
    started = time.perf_counter()
    max_replay_error = 0.0
    for i, patient in enumerate(cohort, 1):
        pid = patient["patient"]
        volume = nib.load(str(INNOVATION / f"data/msvalid_first_t2/{pid}.nii.gz")).get_fdata(dtype=np.float32)
        if tuple(volume.shape) != tuple(patient["shape"]) or not np.isfinite(volume).all():
            raise ValueError(f"{pid}: volume changed or nonfinite")
        phases = {}
        for phase in (0, 2):
            positions = list(range(phase, volume.shape[2], 4))
            anchors = np.ascontiguousarray(volume[:, :, positions])
            phases[phase] = (positions, anchors, prepared(anchors))
        all_anchors = np.concatenate([phases[0][1].ravel(), phases[2][1].ravel()])
        span = float(all_anchors.max() - all_anchors.min())
        if span <= 0:
            raise ValueError(f"{pid}: invalid anchor intensity range")
        norm_lo_diff = abs(phases[0][2][1] - phases[2][2][1]) / span
        norm_hi_diff = abs(phases[0][2][2] - phases[2][2][2]) / span
        patient_rows = []
        for residue in (1, 3):
            for z in patient["eligible_targets"][f"residue_{residue}"]:
                idx0, idx2 = z // 4, (z - 2) // 4
                a0 = phases[0][1]
                left, right = a0[:, :, idx0], a0[:, :, idx0 + 1]
                mask = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                        (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
                if not mask.any():
                    raise ValueError(f"{pid}/z{z}: empty support")
                h0 = predict(hat, phases[0][2], idx0, (z - phases[0][0][idx0]) / 4, volume.shape[:2])
                h2 = predict(hat, phases[2][2], idx2, (z - phases[2][0][idx2]) / 4, volume.shape[:2])
                s0 = predict(swinir, phases[0][2], idx0, (z - phases[0][0][idx0]) / 4, volume.shape[:2])
                s2 = predict(swinir, phases[2][2], idx2, (z - phases[2][0][idx2]) / 4, volume.shape[:2])
                l0, l2 = linear(volume, z, 0), linear(volume, z, 2)
                y = volume[:, :, z]
                evaluations = {
                    "forward_shared": metrics(h0, s0, y, mask),
                    "forward_disjoint": metrics(h0, s2, y, mask),
                    "reverse_shared": metrics(h2, s2, y, mask),
                    "reverse_disjoint": metrics(h2, s0, y, mask),
                    "linear_shared": metrics(h0, l0, y, mask),
                    "linear_disjoint": metrics(h0, l2, y, mask),
                }
                prior = original[(pid, z)]
                for condition in ("shared", "disjoint"):
                    error = abs(evaluations[f"forward_{condition}"]["observable"]
                                - float(prior[f"{condition}_observable"]))
                    max_replay_error = max(max_replay_error, error)
                    if error > 1e-7:
                        raise AssertionError(f"{pid}/z{z}: original result replay mismatch {error}")
                row = {"patient": pid, "z": z, "residue": residue,
                       "z_spacing_mm": patient["zooms_mm"][2], "support_pixels": int(mask.sum())}
                for label, result in evaluations.items():
                    for key in ("observable", "a_mae", "b_mae", "paired_mse"):
                        row[f"{label}_{key}"] = result[key]
                for family in ("forward", "reverse", "linear"):
                    row[f"{family}_delta_o"] = (row[f"{family}_disjoint_observable"]
                                                 - row[f"{family}_shared_observable"])
                patient_rows.append(row)
        if not patient_rows:
            raise ValueError(f"{pid}: no targets")
        summary = {"patient": pid, "targets": len(patient_rows),
                   "z_spacing_mm": patient["zooms_mm"][2],
                   "relative_lo_difference": norm_lo_diff,
                   "relative_hi_difference": norm_hi_diff}
        for family in ("forward", "reverse", "linear"):
            for key in ("delta_o", "shared_observable", "disjoint_observable",
                        "shared_b_mae", "disjoint_b_mae"):
                summary[f"{family}_{key}"] = mean_balanced(patient_rows, f"{family}_{key}")
        per_target.extend(patient_rows)
        per_patient.append(summary)
        with (OUT / "progress.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"patient": summary, "targets": patient_rows}) + "\n")
        print(f"{i}/84 {pid} targets={len(patient_rows)} elapsed={time.perf_counter()-started:.1f}s", flush=True)
    write_csv(OUT / "per_target.csv", per_target)
    write_csv(OUT / "per_patient.csv", per_patient)
    rng = np.random.default_rng(20261001)
    draws = rng.integers(0, len(per_patient), (5000, len(per_patient)))
    contrasts = {}
    for family in ("forward", "reverse", "linear"):
        values = np.array([p[f"{family}_delta_o"] for p in per_patient])
        low, high = np.percentile(values[draws].mean(axis=1), [2.5, 97.5])
        contrasts[family] = {
            "mean_shared_o": float(np.mean([p[f"{family}_shared_observable"] for p in per_patient])),
            "mean_disjoint_o": float(np.mean([p[f"{family}_disjoint_observable"] for p in per_patient])),
            "mean_delta_o": float(values.mean()), "ci95_exploratory": [float(low), float(high)],
            "positive_patients": int((values > 0).sum()),
            "negative_patients": int((values < 0).sum()),
            "mean_shared_b_mae": float(np.mean([p[f"{family}_shared_b_mae"] for p in per_patient])),
            "mean_disjoint_b_mae": float(np.mean([p[f"{family}_disjoint_b_mae"] for p in per_patient])),
        }
    result = {"status": "post-result exploratory; not independent confirmation",
              "plan_sha256": sha256(INNOVATION / "MSVALID_POSTHOC_CONTROL_PLAN_2026-09-30.md"),
              "script_sha256": sha256(Path(__file__)), "original_per_target_sha256": sha256(ORIGINAL),
              "checkpoint_sha256": {name: spec[2] for name, spec in MODELS.items()},
              "patients": len(per_patient), "targets": len(per_target),
              "max_forward_replay_abs_o": max_replay_error,
              "median_relative_lo_difference": float(np.median([p["relative_lo_difference"] for p in per_patient])),
              "median_relative_hi_difference": float(np.median([p["relative_hi_difference"] for p in per_patient])),
              "contrasts": contrasts, "elapsed_seconds": time.perf_counter() - started}
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
