"""CPU-only matched-geometry synthetic independent-noise control on MSValid."""
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

import msvalid_ixi_weights_secondary as original


ROOT = Path(__file__).resolve().parents[2]
INNOVATION = ROOT / "innovation"
PLAN = INNOVATION / "MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_PLAN_2026-10-01.md"
MAIN_TARGETS = INNOVATION / "experiments/msvalid_ixi_weights_secondary/per_target.csv"
MAIN_TARGETS_SHA256 = "ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4"
OUT = INNOVATION / "experiments/msvalid_matched_geometry_noise_control"
LEVELS = (0.01, 0.05)


def fixed_prepared(anchors: np.ndarray, lo: float, hi: float) -> tuple:
    norm = np.clip((anchors - lo) / (hi - lo + 1e-8), 0, 1).astype(np.float32)
    resized = [original.resize(norm[:, :, j], (256, 256), preserve_range=True,
                               anti_aliasing=True).astype(np.float32)
               for j in range(anchors.shape[2])]
    return resized, lo, hi


def magnitude_noise(signal: np.ndarray, sigma: float,
                    real: np.ndarray, imag: np.ndarray) -> np.ndarray:
    return np.sqrt((signal + sigma * real) ** 2 + (sigma * imag) ** 2).astype(np.float32)


def original_target_rows() -> dict[tuple[str, int], dict[str, str]]:
    if original.sha256(MAIN_TARGETS) != MAIN_TARGETS_SHA256:
        raise ValueError("original IXI-weight target CSV changed")
    with MAIN_TARGETS.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 479:
        raise ValueError("original target count changed")
    return {(row["patient"], int(row["z"])): row for row in rows}


def score_patient(patient: dict, hat: object, swinir: object,
                  rng: np.random.Generator, targets: dict) -> list[dict]:
    pid = patient["patient"]
    path = original.DATA / f"{pid}.nii.gz"
    volume = nib.load(str(path)).get_fdata(dtype=np.float32)
    if tuple(volume.shape) != tuple(patient["shape"]) or not np.isfinite(volume).all():
        raise ValueError(f"geometry or pixels changed: {pid}")
    indices = list(range(0, volume.shape[2], 4))
    clean = np.ascontiguousarray(volume[:, :, indices])
    positive = np.abs(clean)[np.abs(clean) > 0]
    if not len(positive):
        raise ValueError(f"no positive anchors: {pid}")
    scale = float(np.median(positive))
    lo, hi = float(clean.min()), float(clean.max())
    if not np.isfinite(scale) or scale <= 0 or hi <= lo:
        raise ValueError(f"invalid noise scale/range: {pid}")
    noise = [rng.standard_normal(clean.shape, dtype=np.float32) for _ in range(4)]
    rows = []
    for level in LEVELS:
        sigma = level * scale
        a_anchors = magnitude_noise(clean, sigma, noise[0], noise[1])
        b_anchors = magnitude_noise(clean, sigma, noise[2], noise[3])
        a_prepared = fixed_prepared(a_anchors, lo, hi)
        b_prepared = fixed_prepared(b_anchors, lo, hi)
        for residue in (1, 3):
            for z in patient["eligible_targets"][f"residue_{residue}"]:
                i0 = z // 4
                left, right = clean[:, :, i0], clean[:, :, i0 + 1]
                mask = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                        (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
                if not mask.any() or int(mask.sum()) != int(targets[(pid, z)]["support_pixels"]):
                    raise ValueError(f"support mismatch: {pid} z{z}")
                rel = (z - indices[i0]) / 4
                a = original.predict(hat, a_prepared, i0, rel, volume.shape[:2])
                shared = original.predict(swinir, a_prepared, i0, rel, volume.shape[:2])
                independent = original.predict(swinir, b_prepared, i0, rel, volume.shape[:2])
                y = volume[:, :, z]
                m_shared = original.metrics(a, shared, y, mask)
                m_independent = original.metrics(a, independent, y, mask)
                rows.append({"patient": pid, "z": z, "residue": residue,
                             "noise_fraction": level, "sigma": sigma,
                             "support_pixels": int(mask.sum()),
                             "shared_o": m_shared["observable"],
                             "independent_o": m_independent["observable"],
                             "delta_o": m_independent["observable"] - m_shared["observable"],
                             "shared_b_mae": m_shared["b_mae"],
                             "independent_b_mae": m_independent["b_mae"],
                             "a_mae": m_shared["a_mae"]})
    return rows


def balanced(rows: list[dict], key: str) -> float:
    return float(np.mean([np.mean([row[key] for row in rows if row["residue"] == residue])
                          for residue in (1, 3)]))


def aggregate(rows: list[dict]) -> tuple[list[dict], dict]:
    by_patient: dict[str, list[dict]] = {}
    for row in rows:
        by_patient.setdefault(row["patient"], []).append(row)
    patient_rows = []
    for pid, targets in by_patient.items():
        for level in LEVELS:
            selected = [row for row in targets if row["noise_fraction"] == level]
            if not selected or not all(any(row["residue"] == residue for row in selected)
                                       for residue in (1, 3)):
                raise ValueError(f"incomplete patient level: {pid} {level}")
            patient_rows.append({"patient": pid, "noise_fraction": level,
                                 "targets": len(selected),
                                 **{key: balanced(selected, key) for key in
                                    ("shared_o", "independent_o", "delta_o",
                                     "shared_b_mae", "independent_b_mae", "a_mae")}})
    if len(by_patient) != 84 or len(rows) != 958:
        raise ValueError("incomplete full-cohort output")
    results = {}
    for index, level in enumerate(LEVELS):
        selected = [row for row in patient_rows if row["noise_fraction"] == level]
        values = np.array([row["delta_o"] for row in selected], dtype=np.float64)
        rng = np.random.default_rng(20261003 + index)
        indices = rng.integers(0, len(values), (5000, len(values)))
        ci = np.percentile(values[indices].mean(axis=1), [2.5, 97.5]).tolist()
        results[str(level)] = {
            "patients": len(selected), "targets": sum(row["targets"] for row in selected),
            "shared_o": float(np.mean([row["shared_o"] for row in selected])),
            "independent_o": float(np.mean([row["independent_o"] for row in selected])),
            "delta_o": float(values.mean()), "ci95": ci,
            "positive_patients": int((values > 0).sum()),
            "negative_patients": int((values < 0).sum()),
            "shared_b_mae": float(np.mean([row["shared_b_mae"] for row in selected])),
            "independent_b_mae": float(np.mean([row["independent_b_mae"] for row in selected]))}
    return patient_rows, results


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUT}")
    cohort = json.loads(original.QUALIFIED.read_text(encoding="utf-8"))["patients"]
    manifest = json.loads(original.SOURCE_MANIFEST.read_text(encoding="utf-8"))["records"]
    hashes = {row["patient"]: row["sha256"] for row in manifest}
    if len(cohort) != 84 or set(hashes) != {row["patient"] for row in cohort}:
        raise ValueError("source patient set changed")
    for patient in cohort:
        pid = patient["patient"]
        if original.sha256(original.DATA / f"{pid}.nii.gz") != hashes[pid]:
            raise ValueError(f"source hash changed: {pid}")
    for name, (_, path, expected) in original.MODELS.items():
        if original.sha256(path) != expected:
            raise ValueError(f"model checkpoint changed: {name}")
    targets = original_target_rows()
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = original.MODELS["hat"][0](original.MODELS["hat"][1], device="cpu")
    swinir = original.MODELS["swinir"][0](original.MODELS["swinir"][1], device="cpu")
    rng = np.random.default_rng(20261003)
    started = time.perf_counter()
    per_target, failures = [], []
    for index, patient in enumerate(cohort, 1):
        pid = patient["patient"]
        try:
            rows = score_patient(patient, hat, swinir, rng, targets)
            per_target.extend(rows)
            print(f"{index}/84 {pid} targets={len(rows)} elapsed={time.perf_counter()-started:.1f}s",
                  flush=True)
        except (OSError, ValueError, RuntimeError) as error:
            failures.append({"patient": pid, "error": f"{type(error).__name__}: {error}"})
            print(f"{index}/84 {pid} FAIL {error}", flush=True)
    per_patient, levels = aggregate(per_target) if not failures else ([], {})
    summary = {"status": "post-result synthetic mechanism experiment",
               "plan_sha256": original.sha256(PLAN),
               "script_sha256": original.sha256(Path(__file__)),
               "qualification_sha256": original.sha256(original.QUALIFIED),
               "source_manifest_sha256": original.sha256(original.SOURCE_MANIFEST),
               "original_per_target_sha256": MAIN_TARGETS_SHA256,
               "checkpoint_sha256": {name: spec[2] for name, spec in original.MODELS.items()},
               "noise_rng_seed": 20261003, "levels": levels,
               "patients_expected": 84, "failures": failures,
               "patients_complete": len(per_patient) // len(LEVELS),
               "targets_scored": len(per_target),
               "elapsed_seconds": time.perf_counter() - started}
    OUT.mkdir(parents=True)
    if per_target:
        write_csv(OUT / "per_target.csv", per_target)
    if per_patient:
        write_csv(OUT / "per_patient.csv", per_patient)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
