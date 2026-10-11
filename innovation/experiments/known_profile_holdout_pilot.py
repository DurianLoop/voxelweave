"""CPU-only training-patient test of heldout profile selection."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.ndimage import gaussian_filter1d
from skimage.transform import resize


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "innovation/KNOWN_PROFILE_HOLDOUT_PILOT_PLAN_2026-10-01.md"
OUT = ROOT / "innovation/experiments/known_profile_holdout_pilot"
SPLITS = ROOT / "dataset/IXI/splits/seed3407"
T2 = ROOT / "dataset/IXI/raw/T2"
PATIENTS = ("IXI013", "IXI015", "IXI017")
TRUE_SIGMAS = (0.0, 1.5)
STRIDES = (4, 6)
CANDIDATES = (0.0, 1.5, 3.0)
SMOOTH = 0.03
RIDGE = 1e-5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def kernel(n: int, sigma: float) -> np.ndarray:
    identity = np.eye(n, dtype=np.float64)
    return identity if sigma == 0 else gaussian_filter1d(
        identity, sigma=sigma, axis=0, mode="reflect")


def reconstruct(g: np.ndarray, anchors: np.ndarray, observed: np.ndarray,
                roughness: np.ndarray) -> np.ndarray:
    a = g[anchors, :]
    normal = a.T @ a + SMOOTH * roughness + RIDGE * np.eye(g.shape[0])
    factor = cho_factor(normal, lower=True, check_finite=True)
    return cho_solve(factor, a.T @ observed, check_finite=True)


def mse(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> float:
    error = a[:, mask] - b[:, mask]
    value = float(np.mean(error * error))
    if not np.isfinite(value):
        raise ValueError("nonfinite MSE")
    return value


def score_condition(patient: str, image: np.ndarray, true_sigma: float,
                    stride: int) -> tuple[dict, list[dict]]:
    n, pixels = image.shape
    anchors = np.arange(0, n, stride)
    held = anchors[1::3]
    fit = np.array([z for z in anchors if z not in set(held)], dtype=np.int64)
    targets = np.array([z for z in range(n) if z not in set(anchors)], dtype=np.int64)
    if len(fit) < 10 or len(held) < 4 or len(targets) < 10:
        raise ValueError("insufficient anchor/heldout/target layers")
    true_g = kernel(n, true_sigma)
    acquired_raw = true_g[anchors, :] @ image
    scale = float(np.max(np.abs(acquired_raw)))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("invalid observed-only scale")
    latent = image / scale
    acquired = acquired_raw / scale
    support_values = np.mean(np.abs(acquired), axis=0)
    mask = support_values > 0.05 * float(support_values.max())
    if not mask.any():
        raise ValueError("empty observed-only support")
    fit_rows = np.searchsorted(anchors, fit)
    held_rows = np.searchsorted(anchors, held)
    second = np.diff(np.eye(n), n=2, axis=0)
    roughness = second.T @ second
    scores = []
    for candidate in CANDIDATES:
        g = kernel(n, candidate)
        fit_estimate = reconstruct(g, fit, acquired[fit_rows], roughness)
        hold_mse = mse(g[held, :] @ fit_estimate, acquired[held_rows], mask)
        all_estimate = reconstruct(g, anchors, acquired, roughness)
        target_mse = mse(all_estimate[targets], latent[targets], mask)
        scores.append({"patient": patient, "true_sigma": true_sigma,
                       "stride": stride, "candidate_sigma": candidate,
                       "heldout_mse": hold_mse, "target_mse": target_mse})
    chosen = min(scores, key=lambda row: (row["heldout_mse"], row["candidate_sigma"]))
    oracle = min(scores, key=lambda row: (row["target_mse"], row["candidate_sigma"]))
    fixed = next(row for row in scores if row["candidate_sigma"] == 0)
    true_profile = next(row for row in scores if row["candidate_sigma"] == true_sigma)
    result = {"patient": patient, "true_sigma": true_sigma, "stride": stride,
              "native_layers": n, "anchors": len(anchors), "fit_anchors": len(fit),
              "heldout_anchors": len(held), "target_layers": len(targets),
              "support_pixels": int(mask.sum()), "observed_scale": scale,
              "chosen_sigma": chosen["candidate_sigma"],
              "oracle_sigma": oracle["candidate_sigma"],
              "selected_target_mse": chosen["target_mse"],
              "fixed_target_mse": fixed["target_mse"],
              "true_profile_target_mse": true_profile["target_mse"],
              "oracle_target_mse": oracle["target_mse"],
              "selected_minus_fixed_mse": chosen["target_mse"] - fixed["target_mse"],
              "selected_matches_true": chosen["candidate_sigma"] == true_sigma}
    return result, scores


def load_train(patient: str) -> tuple[np.ndarray, Path]:
    matches = sorted(T2.glob(f"{patient}-*-T2.nii.gz"))
    if len(matches) != 1:
        raise ValueError(f"expected one T2 file for {patient}, found {len(matches)}")
    volume = nib.load(str(matches[0])).get_fdata(dtype=np.float32)
    if volume.ndim != 3 or not np.isfinite(volume).all():
        raise ValueError(f"invalid source volume: {patient}")
    planes = [resize(volume[:, :, z], (32, 32), preserve_range=True,
                     anti_aliasing=True).astype(np.float64).reshape(-1)
              for z in range(volume.shape[2])]
    return np.stack(planes), matches[0]


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    train = (SPLITS / "train_cases.txt").read_text(encoding="utf-8").splitlines()
    val = set((SPLITS / "val_cases.txt").read_text(encoding="utf-8").splitlines())
    test = set((SPLITS / "test_cases.txt").read_text(encoding="utf-8").splitlines())
    if tuple(train[:3]) != PATIENTS or set(PATIENTS) & (val | test):
        raise ValueError("frozen train-only patient selection failed")
    OUT.mkdir(parents=True)
    conditions, candidates, failures, source_hashes = [], [], [], {}
    started = time.perf_counter()
    for patient in PATIENTS:
        try:
            image, path = load_train(patient)
            source_hashes[patient] = sha256(path)
        except Exception as error:
            failures.append({"patient": patient, "condition": "load",
                             "error": f"{type(error).__name__}: {error}"})
            continue
        for true_sigma in TRUE_SIGMAS:
            for stride in STRIDES:
                try:
                    result, rows = score_condition(patient, image, true_sigma, stride)
                    conditions.append(result)
                    candidates.extend(rows)
                    print(f"{patient} sigma={true_sigma} stride={stride} chosen={result['chosen_sigma']} elapsed={time.perf_counter()-started:.1f}s", flush=True)
                except Exception as error:
                    failures.append({"patient": patient,
                                     "condition": f"sigma={true_sigma},stride={stride}",
                                     "error": f"{type(error).__name__}: {error}"})
    write_csv(OUT / "per_condition.csv", conditions)
    write_csv(OUT / "per_candidate.csv", candidates)
    differences = np.array([row["selected_minus_fixed_mse"] for row in conditions])
    summary = {"plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
               "split_sha256": {name: sha256(SPLITS / f"{name}_cases.txt")
                                for name in ("train", "val", "test")},
               "source_sha256": source_hashes, "patients_expected": len(PATIENTS),
               "conditions_expected": len(PATIENTS) * len(TRUE_SIGMAS) * len(STRIDES),
               "conditions_scored": len(conditions), "failures": failures,
               "selection_matches_true": sum(row["selected_matches_true"] for row in conditions),
               "selected_improves_fixed": int((differences < 0).sum()),
               "selected_harms_fixed": int((differences > 0).sum()),
               "elapsed_seconds": time.perf_counter() - started}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
