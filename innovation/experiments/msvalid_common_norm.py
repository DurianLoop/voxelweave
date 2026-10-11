"""Post-result CPU-only shared-normalization sensitivity control for MSValid."""
from __future__ import annotations

import csv
import json
import os
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import torch
from skimage.transform import resize

from msvalid_mira_confirmation import MODELS, metrics, predict, sha256, write_csv


ROOT = Path(__file__).resolve().parents[2]
INNOVATION = ROOT / "innovation"
QUALIFIED = INNOVATION / "literature/msvalid_geometry_qualification.json"
ORIGINAL = INNOVATION / "experiments/msvalid_mira_confirmation/per_patient.csv"
PLAN = INNOVATION / "MSVALID_COMMON_NORM_PLAN_2026-09-30.md"
OUT = INNOVATION / "experiments/msvalid_common_norm"


def prepare_with_range(anchors: np.ndarray, lo: float, hi: float):
    normalized = ((anchors - lo) / (hi - lo + 1e-8)).astype(np.float32)
    planes = [resize(normalized[:, :, j], (256, 256), preserve_range=True,
                     anti_aliasing=True).astype(np.float32)
              for j in range(anchors.shape[2])]
    return planes, lo, hi


def mean_balanced(rows: list[dict], key: str) -> float:
    return float(np.mean([np.mean([row[key] for row in rows if row["residue"] == r])
                          for r in (1, 3)]))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite: {OUT}")
    patients = json.loads(QUALIFIED.read_text(encoding="utf-8"))["patients"]
    if len(patients) != 84 or not all(p["geometry_eligible"] for p in patients):
        raise RuntimeError("Frozen cohort mismatch")
    for name, (_, path, expected) in MODELS.items():
        if sha256(path) != expected:
            raise ValueError(f"{name} checkpoint hash mismatch")
    with ORIGINAL.open(newline="", encoding="utf-8") as stream:
        original = {row["patient"]: row for row in csv.DictReader(stream)}
    if len(original) != 84:
        raise RuntimeError("Original patient count mismatch")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    OUT.mkdir(parents=True)
    target_rows, patient_rows = [], []
    started = time.perf_counter()
    for number, patient in enumerate(patients, 1):
        pid = patient["patient"]
        volume = nib.load(str(INNOVATION / f"data/msvalid_first_t2/{pid}.nii.gz")).get_fdata(dtype=np.float32)
        if tuple(volume.shape) != tuple(patient["shape"]) or not np.isfinite(volume).all():
            raise ValueError(f"{pid}: changed/nonfinite volume")
        phase0 = np.ascontiguousarray(volume[:, :, list(range(0, volume.shape[2], 4))])
        phase2 = np.ascontiguousarray(volume[:, :, list(range(2, volume.shape[2], 4))])
        lo = min(float(phase0.min()), float(phase2.min()))
        hi = max(float(phase0.max()), float(phase2.max()))
        if hi <= lo:
            raise ValueError(f"{pid}: invalid range")
        prep0 = prepare_with_range(phase0, lo, hi)
        prep2 = prepare_with_range(phase2, lo, hi)
        rows = []
        for residue in (1, 3):
            for z in patient["eligible_targets"][f"residue_{residue}"]:
                i0, i2 = z // 4, (z - 2) // 4
                left, right = phase0[:, :, i0], phase0[:, :, i0 + 1]
                mask = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                        (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
                if not mask.any():
                    raise ValueError(f"{pid}/z{z}: empty support")
                h0 = predict(hat, prep0, i0, (z - 4 * i0) / 4, volume.shape[:2])
                s0 = predict(swinir, prep0, i0, (z - 4 * i0) / 4, volume.shape[:2])
                s2 = predict(swinir, prep2, i2, (z - (2 + 4 * i2)) / 4, volume.shape[:2])
                y = volume[:, :, z]
                shared, disjoint = metrics(h0, s0, y, mask), metrics(h0, s2, y, mask)
                row = {"patient": pid, "z": z, "residue": residue,
                       "support_pixels": int(mask.sum()), "shared_o": shared["observable"],
                       "disjoint_o": disjoint["observable"],
                       "delta_o": disjoint["observable"] - shared["observable"],
                       "shared_b_mae": shared["b_mae"], "disjoint_b_mae": disjoint["b_mae"]}
                rows.append(row)
        if not rows or {row["residue"] for row in rows} != {1, 3}:
            raise ValueError(f"{pid}: incomplete targets")
        old = original[pid]
        summary = {"patient": pid, "targets": len(rows), "common_lo": lo, "common_hi": hi,
                   "original_delta_o": float(old["delta_o"])}
        for key in ("shared_o", "disjoint_o", "delta_o", "shared_b_mae", "disjoint_b_mae"):
            summary[key] = mean_balanced(rows, key)
        summary["delta_change_vs_original"] = summary["delta_o"] - summary["original_delta_o"]
        target_rows.extend(rows)
        patient_rows.append(summary)
        with (OUT / "progress.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"patient": summary, "targets": rows}) + "\n")
        print(f"{number}/84 {pid} targets={len(rows)} elapsed={time.perf_counter()-started:.1f}s", flush=True)
    if len(target_rows) != 479:
        raise RuntimeError(f"Target count changed: {len(target_rows)}")
    write_csv(OUT / "per_target.csv", target_rows)
    write_csv(OUT / "per_patient.csv", patient_rows)
    values = np.array([row["delta_o"] for row in patient_rows])
    rng = np.random.default_rng(20261002)
    draws = rng.integers(0, len(values), (5000, len(values)))
    ci = np.percentile(values[draws].mean(axis=1), [2.5, 97.5]).tolist()
    result = {"status": "post-result exploratory; not independent confirmation",
              "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
              "original_per_patient_sha256": sha256(ORIGINAL),
              "checkpoint_sha256": {name: spec[2] for name, spec in MODELS.items()},
              "patients": len(patient_rows), "targets": len(target_rows),
              "mean_shared_o": float(np.mean([row["shared_o"] for row in patient_rows])),
              "mean_disjoint_o": float(np.mean([row["disjoint_o"] for row in patient_rows])),
              "mean_delta_o": float(values.mean()), "ci95_exploratory": ci,
              "positive_patients": int((values > 0).sum()),
              "negative_patients": int((values < 0).sum()),
              "mean_change_vs_original": float(np.mean([row["delta_change_vs_original"] for row in patient_rows])),
              "mean_shared_b_mae": float(np.mean([row["shared_b_mae"] for row in patient_rows])),
              "mean_disjoint_b_mae": float(np.mean([row["disjoint_b_mae"] for row in patient_rows])),
              "elapsed_seconds": time.perf_counter() - started}
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
