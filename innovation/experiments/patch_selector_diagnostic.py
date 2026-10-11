"""Weak patient-held-out patch selector probe on frozen paired CPU predictions."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / "innovation/experiments"
ARCHIVE = EXPERIMENTS / "local_oracle_paired_arrays_val23/paired_predictions.npz"
ARCHIVE_MANIFEST = EXPERIMENTS / "local_oracle_paired_arrays_val23/manifest.json"
DATA_MANIFEST = ROOT / "design/pastnet_v2/manifests/fastmri/fold_00.json"
SCALAR = EXPERIMENTS / "scalar_selector_per_slice.csv"
SIZE, STRIDE = 32, 16


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def patch_data(base: np.ndarray, candidate: np.ndarray, target: np.ndarray,
               phase: float, gap: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    delta, residual = candidate-base, target-base
    gy, gx = np.gradient(base)
    base_edge = np.abs(gx) + np.abs(gy)
    gy, gx = np.gradient(delta)
    delta_edge = np.abs(gx) + np.abs(gy)
    features, alignment, energy = [], [], []
    for y in range(0, 256-SIZE+1, STRIDE):
        for x in range(0, 256-SIZE+1, STRIDE):
            box = np.s_[y:y+SIZE, x:x+SIZE]
            b, d, e = base[box], delta[box], residual[box]
            d2 = float(np.mean(d.astype(np.float64)**2))
            features.append([float(phase == 0.5), float(phase == 0.75), gap,
                             (x+SIZE/2)/256, (y+SIZE/2)/256,
                             float(np.mean(b)), float(np.std(b)),
                             float(np.mean(d)), float(np.sqrt(d2)),
                             float(np.mean(base_edge[box])),
                             float(np.mean(delta_edge[box]))])
            alignment.append(float(np.mean(d.astype(np.float64)*e)))
            energy.append(d2)
    return np.asarray(features), np.asarray(alignment), np.asarray(energy)


def weighted_ridge(train_x: np.ndarray, train_m: np.ndarray, train_d: np.ndarray,
                   test_x: np.ndarray) -> np.ndarray:
    center = train_x.mean(axis=0)
    scale = np.maximum(train_x.std(axis=0), 1e-8)
    x = np.column_stack((np.ones(len(train_x)), (train_x-center)/scale))
    q = np.column_stack((np.ones(len(test_x)), (test_x-center)/scale))
    d = np.maximum(train_d, 1e-12)
    weights = d / d.mean()
    target_alpha = train_m / d
    penalty = np.eye(x.shape[1])*100.0
    penalty[0, 0] = 0.0
    coef = np.linalg.solve(x.T @ (weights[:, None]*x) + penalty,
                           x.T @ (weights*target_alpha))
    return np.clip(q @ coef, 0, 1)


def reconstruct(base: np.ndarray, candidate: np.ndarray, patch_alphas: np.ndarray) -> np.ndarray:
    taper = 0.05 + 0.95*np.hanning(SIZE)
    window = np.outer(taper, taper).astype(np.float32)
    numerator = np.zeros_like(base)
    denominator = np.zeros_like(base)
    index = 0
    for y in range(0, 256-SIZE+1, STRIDE):
        for x in range(0, 256-SIZE+1, STRIDE):
            box = np.s_[y:y+SIZE, x:x+SIZE]
            numerator[box] += patch_alphas[index]*window
            denominator[box] += window
            index += 1
    if index != len(patch_alphas) or np.any(denominator <= 0):
        raise AssertionError("Patch reconstruction coverage mismatch")
    return base + (numerator/denominator)*(candidate-base)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    provenance = json.loads(ARCHIVE_MANIFEST.read_text(encoding="utf-8"))
    if sha256(ARCHIVE) != provenance["paired_predictions_sha256"]:
        raise AssertionError("Prediction archive hash mismatch")
    with np.load(ARCHIVE, allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in archive.files}
    if len(arrays["base"]) != 207 or len(set(arrays["patient_id"])) != 23:
        raise AssertionError("Expected complete historical validation set")
    manifest = json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))
    geometry = {r["case_id"]: r for r in manifest["records"] if r["split"] == "val"}
    fixed_alpha = {}
    with SCALAR.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["policy"] == "loo_fixed":
                fixed_alpha[row["patient_id"]] = float(row["alpha"])

    features, alignment, energy = [], [], []
    for i in range(len(arrays["base"])):
        case, z = str(arrays["case_id"][i]), int(arrays["z"][i])
        left = 4*((z-1)//4)
        gap = float(geometry[case]["geometry"]["z_mm"][left+4]
                    - geometry[case]["geometry"]["z_mm"][left])
        x, m, d = patch_data(arrays["base"][i], arrays["candidate"][i],
                             arrays["target"][i], float(arrays["phase"][i]), gap)
        features.append(x)
        alignment.append(m)
        energy.append(d)
    features = np.stack(features)
    alignment = np.stack(alignment)
    energy = np.stack(energy)

    from pastnet_v2.metrics import quality
    rows = []
    for patient in sorted(set(arrays["patient_id"])):
        train_idx = np.flatnonzero(arrays["patient_id"] != patient)
        test_idx = np.flatnonzero(arrays["patient_id"] == patient)
        predicted = weighted_ridge(features[train_idx].reshape(-1, features.shape[-1]),
                                   alignment[train_idx].ravel(), energy[train_idx].ravel(),
                                   features[test_idx].reshape(-1, features.shape[-1]))
        predicted = predicted.reshape(len(test_idx), -1)
        for k, i in enumerate(test_idx):
            base, candidate, target = (arrays[name][i]
                                       for name in ("base", "candidate", "target"))
            fixed = base + fixed_alpha[str(patient)]*(candidate-base)
            learned = reconstruct(base, candidate, predicted[k])
            for policy, image in (("loo_fixed", fixed), ("ridge_patch", learned)):
                metrics = quality(image, target, arrays["spacing"][i])
                rows.append(dict(case_id=str(arrays["case_id"][i]), patient_id=str(patient),
                                 z=int(arrays["z"][i]), phase=float(arrays["phase"][i]),
                                 policy=policy, mean_patch_alpha=float(np.mean(predicted[k]))
                                 if policy == "ridge_patch" else fixed_alpha[str(patient)],
                                 **metrics))
        print(f"selector held-out patient {len(set(r['patient_id'] for r in rows))}/23: {patient}",
              flush=True)

    metrics = ("psnr", "ssim", "mae", "mse", "ncc", "dice_proxy", "hd95_proxy", "tail10_mse")
    per_patient = []
    for patient in sorted(set(arrays["patient_id"])):
        for policy in ("loo_fixed", "ridge_patch"):
            selected = [row for row in rows if row["patient_id"] == patient and row["policy"] == policy]
            per_patient.append(dict(patient_id=str(patient), policy=policy,
                                    **{metric: float(np.mean([row[metric] for row in selected]))
                                       for metric in metrics}))
    summary = {policy: {metric: float(np.mean([row[metric] for row in per_patient
                                              if row["policy"] == policy]))
                        for metric in metrics} for policy in ("loo_fixed", "ridge_patch")}
    baseline = {row["patient_id"]: row for row in per_patient if row["policy"] == "loo_fixed"}
    candidate = {row["patient_id"]: row for row in per_patient if row["policy"] == "ridge_patch"}
    result = dict(scope="selector_only_LOPO_historical_validation",
                  patients=len(baseline), slices=len(arrays["base"]), patch_size=SIZE,
                  stride=STRIDE, features=["phase", "gap_mm", "x_y", "base_mean_std",
                                           "delta_mean_rms", "base_edge", "delta_edge"],
                  learner="weighted ridge, penalty 100, target m/d, weight d, clipped alpha",
                  source_sha256={str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p)
                                 for p in (ARCHIVE, ARCHIVE_MANIFEST, DATA_MANIFEST, SCALAR)},
                  summary=summary,
                  patient_wins={metric: sum((candidate[p][metric] > baseline[p][metric])
                                            if metric in ("psnr", "ssim", "ncc", "dice_proxy")
                                            else (candidate[p][metric] < baseline[p][metric])
                                            for p in baseline) for metric in metrics},
                  limitations=["Only the selector excludes held-out patient labels; base and candidate checkpoints used this validation cohort for selection.",
                               "Oracle targets train the ridge but never enter held-out feature construction.",
                               "All results are developmental and cannot establish independent clinical safety.",
                               "HD95 and Dice are intensity-threshold proxies."])
    write_csv(EXPERIMENTS / "patch_selector_per_slice.csv", rows)
    write_csv(EXPERIMENTS / "patch_selector_per_patient.csv", per_patient)
    (EXPERIMENTS / "patch_selector_diagnostic.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "patient_wins": result["patient_wins"]},
                     indent=2), flush=True)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT / "design"))
    main()
