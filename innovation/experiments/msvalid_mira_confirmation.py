"""Frozen CPU-only HAT/SwinIR MSValid shared-vs-disjoint confirmation."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import torch
from skimage.transform import resize


ROOT = Path(__file__).resolve().parents[2]
INNOVATION = ROOT / "innovation"
sys.path[:0] = [str(ROOT / "baseline"), str(ROOT / "pre"), str(ROOT / "design")]
from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator
from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator
from ixi_diffusion.common import normalize_volume


PROTOCOL = INNOVATION / "MSVALID_CONFIRMATION_PROTOCOL_2026-09-30.md"
QUALIFIED = INNOVATION / "literature/msvalid_geometry_qualification.json"
DATA = INNOVATION / "data/msvalid_first_t2"
OUT = INNOVATION / "experiments/msvalid_mira_confirmation"
MODELS = {
    "hat": (FastMRIHAT2p5DInterpolator,
            ROOT / "baseline/fastmri_brain_hat_2p5d/runs/full/checkpoints/hat_epoch_best.pth",
            "842c1b7415cfa5a2a3c7b50ecf5ded6a0003872ae8ae2d2362220b9f58c6c094"),
    "swinir": (FastMRISwinIR2p5DInterpolator,
               ROOT / "baseline/fastmri_brain_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth",
               "a7f8883a4f19d695bd9f0cb0c2c082a44e0060ddbe8ab5d8575e7d4ce702efa5"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepared(anchors: np.ndarray) -> tuple[list[np.ndarray], float, float]:
    norm, lo, hi = normalize_volume(anchors)
    resized = [resize(norm[:, :, j], (256, 256), preserve_range=True,
                      anti_aliasing=True).astype(np.float32)
               for j in range(anchors.shape[2])]
    return resized, lo, hi


def predict(model: object, prep: tuple[list[np.ndarray], float, float],
            index: int, rel: float, shape: tuple[int, int]) -> np.ndarray:
    planes, lo, hi = prep
    left, right = planes[index], planes[index + 1]
    coarse = ((1 - rel) * left + rel * right).astype(np.float32)
    cond = np.stack([left, right, coarse, np.full((256, 256), rel, np.float32)])
    residual = model._predict_residual(cond)
    generated = np.clip(coarse + residual, 0, 1)
    return (resize(generated, shape, preserve_range=True, anti_aliasing=True)
            * (hi - lo) + lo).astype(np.float32)


def metrics(a: np.ndarray, b: np.ndarray, y: np.ndarray, mask: np.ndarray) -> dict:
    ea = (a - y)[mask].astype(np.float64)
    eb = (b - y)[mask].astype(np.float64)
    a_mse = float(np.mean(ea * ea))
    b_mse = float(np.mean(eb * eb))
    total = (a_mse + b_mse) / 2
    if not np.isfinite(total) or total <= 0:
        raise ValueError("nonpositive_or_nonfinite_pair_error")
    return {"observable": float(np.mean((ea - eb) ** 2) / (4 * total)),
            "a_mae": float(np.mean(np.abs(ea))), "b_mae": float(np.mean(np.abs(eb))),
            "a_mse": a_mse, "b_mse": b_mse, "paired_mse": total,
            "disagreement_mae": float(np.mean(np.abs(ea - eb)))}


def patient_result(patient: dict, hat: object, swinir: object) -> tuple[list[dict], dict]:
    path = DATA / f"{patient['patient']}.nii.gz"
    volume = nib.load(str(path)).get_fdata(dtype=np.float32)
    if tuple(volume.shape) != tuple(patient["shape"]):
        raise ValueError("header_shape_changed")
    if not np.isfinite(volume).all():
        raise ValueError("nonfinite_volume")
    if float(volume.max()) <= float(volume.min()):
        raise ValueError("constant_volume")
    phases = {}
    for phase in (0, 2):
        indices = list(range(phase, volume.shape[2], 4))
        anchors = np.ascontiguousarray(volume[:, :, indices])
        phases[phase] = (indices, anchors, prepared(anchors))
    rows = []
    for residue in (1, 3):
        for z in patient["eligible_targets"][f"residue_{residue}"]:
            i0 = (z - 0) // 4
            i2 = (z - 2) // 4
            a0 = phases[0][1]
            left, right = a0[:, :, i0], a0[:, :, i0 + 1]
            mask = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                    (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
            if not mask.any():
                raise ValueError(f"empty_acquired_mask_z{z}")
            a = predict(hat, phases[0][2], i0, (z - phases[0][0][i0]) / 4,
                        volume.shape[:2])
            b0 = predict(swinir, phases[0][2], i0, (z - phases[0][0][i0]) / 4,
                         volume.shape[:2])
            b2 = predict(swinir, phases[2][2], i2, (z - phases[2][0][i2]) / 4,
                         volume.shape[:2])
            y = volume[:, :, z]
            shared = metrics(a, b0, y, mask)
            disjoint = metrics(a, b2, y, mask)
            rows.append({"patient": patient["patient"], "z": z, "residue": residue,
                         "z_spacing_mm": patient["zooms_mm"][2], "support_pixels": int(mask.sum()),
                         **{f"shared_{key}": value for key, value in shared.items()},
                         **{f"disjoint_{key}": value for key, value in disjoint.items()},
                         "delta_o": disjoint["observable"] - shared["observable"]})
    if not rows:
        raise ValueError("no_eligible_targets")
    residues = {r: [row for row in rows if row["residue"] == r] for r in (1, 3)}
    if any(not values for values in residues.values()):
        raise ValueError("missing_residue")
    patient_mean = {key: float(np.mean([np.mean([v[key] for v in residues[r]])
                                        for r in (1, 3)]))
                    for key in ("delta_o", "shared_observable", "disjoint_observable",
                                "shared_a_mae", "shared_b_mae", "disjoint_b_mae",
                                "shared_paired_mse", "disjoint_paired_mse")}
    patient_mean.update({"patient": patient["patient"], "targets": len(rows),
                         "z_spacing_mm": patient["zooms_mm"][2],
                         "residue_1_delta_o": float(np.mean([v["delta_o"] for v in residues[1]])),
                         "residue_3_delta_o": float(np.mean([v["delta_o"] for v in residues[3]]))})
    return rows, patient_mean


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite frozen run: {OUT}")
    cohort = json.loads(QUALIFIED.read_text(encoding="utf-8"))
    patients = cohort["patients"]
    if len(patients) != 84 or not all(p["geometry_eligible"] for p in patients):
        raise RuntimeError("Frozen cohort mismatch")
    missing = [p["patient"] for p in patients if not (DATA / f"{p['patient']}.nii.gz").is_file()]
    if missing:
        raise FileNotFoundError(f"Missing extracted patients: {missing}")
    for name, (_, path, expected) in MODELS.items():
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"{name} checkpoint hash mismatch: {actual}")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    OUT.mkdir(parents=True)
    per_target, per_patient, failures = [], [], []
    started = time.perf_counter()
    for i, patient in enumerate(patients, 1):
        try:
            rows, summary = patient_result(patient, hat, swinir)
            per_target.extend(rows)
            per_patient.append(summary)
            print(f"{i}/84 {patient['patient']} targets={len(rows)} elapsed={time.perf_counter()-started:.1f}s", flush=True)
        except (OSError, ValueError, RuntimeError) as error:
            failures.append({"patient": patient["patient"], "error": f"{type(error).__name__}: {error}"})
            print(f"{i}/84 {patient['patient']} FAIL {error}", flush=True)
    write_csv(OUT / "per_target.csv", per_target)
    write_csv(OUT / "per_patient.csv", per_patient)
    values = np.array([p["delta_o"] for p in per_patient], dtype=np.float64)
    if len(values):
        rng = np.random.default_rng(20260930)
        indices = rng.integers(0, len(values), (5000, len(values)))
        bootstrap = values[indices].mean(axis=1)
        ci = np.percentile(bootstrap, [2.5, 97.5]).tolist()
    else:
        ci = [None, None]
    summary = {
        "protocol_sha256": sha256(PROTOCOL), "script_sha256": sha256(Path(__file__)),
        "qualification_sha256": sha256(QUALIFIED),
        "checkpoint_sha256": {name: spec[2] for name, spec in MODELS.items()},
        "precision": "CPU float32", "patients_expected": 84,
        "patients_scored": len(per_patient), "targets_scored": len(per_target),
        "failures": failures, "mean_delta_o": float(values.mean()) if len(values) else None,
        "ci95_delta_o": ci, "positive_patients": int((values > 0).sum()),
        "negative_patients": int((values < 0).sum()),
        "mean_shared_o": float(np.mean([p["shared_observable"] for p in per_patient])) if per_patient else None,
        "mean_disjoint_o": float(np.mean([p["disjoint_observable"] for p in per_patient])) if per_patient else None,
        "mean_residue_1_delta_o": float(np.mean([p["residue_1_delta_o"] for p in per_patient])) if per_patient else None,
        "mean_residue_3_delta_o": float(np.mean([p["residue_3_delta_o"] for p in per_patient])) if per_patient else None,
        "primary_success": len(per_patient) >= 70 and ci[0] is not None and ci[0] > 0,
        "elapsed_seconds": time.perf_counter() - started,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
