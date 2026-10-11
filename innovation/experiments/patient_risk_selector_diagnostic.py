"""Weak patient-held-out safety-amplitude probe using observable image features."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "innovation/experiments"
ARCHIVE = OUT / "local_oracle_paired_arrays_val23/paired_predictions.npz"
FRONTIER = OUT / "oracle_guard_frontier_per_patient.csv"
ORACLE = OUT / "patient_guard_oracle_per_patient.csv"
MANIFEST = ROOT / "design/pastnet_v2/manifests/fastmri/fold_00.json"
METRICS = ("psnr", "ssim", "mae", "mse", "ncc", "dice_proxy", "hd95_proxy", "tail10_mse")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe(candidate: dict, base: dict) -> bool:
    return (all(candidate[key] >= base[key] for key in ("ssim", "ncc", "dice_proxy"))
            and all(candidate[key] <= base[key]
                    for key in ("mae", "mse", "hd95_proxy", "tail10_mse")))


def ridge(train_x: np.ndarray, train_y: np.ndarray, query: np.ndarray) -> float:
    center, scale = train_x.mean(axis=0), np.maximum(train_x.std(axis=0), 1e-8)
    x = np.column_stack((np.ones(len(train_x)), (train_x-center)/scale))
    q = np.r_[1.0, (query-center)/scale]
    penalty = np.eye(x.shape[1])*10.0
    penalty[0, 0] = 0.0
    coef = np.linalg.solve(x.T @ x + penalty, x.T @ train_y)
    return float(q @ coef)


def main() -> None:
    with np.load(ARCHIVE, allow_pickle=False) as archive:
        images = {key: archive[key] for key in archive.files}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = {r["case_id"]: r for r in data["records"] if r["split"] == "val"}
    with FRONTIER.open(newline="", encoding="utf-8") as stream:
        frontier = [{key: (row[key] if key == "patient_id" else float(row[key]))
                     for key in row} for row in csv.DictReader(stream)]
    with ORACLE.open(newline="", encoding="utf-8") as stream:
        oracle = {row["patient_id"]: round(float(row["beta"]), 1)
                  for row in csv.DictReader(stream)}
    by_patient: dict[str, dict[float, dict]] = defaultdict(dict)
    for row in frontier:
        by_patient[row["patient_id"]][round(row["beta"], 1)] = row
    features = {}
    for patient in sorted(by_patient):
        ids = np.flatnonzero(images["patient_id"] == patient)
        base = images["base"][ids]
        delta = images["candidate"][ids] - base
        gaps = []
        for i in ids:
            rec = records[str(images["case_id"][i])]
            left = 4*((int(images["z"][i])-1)//4)
            gaps.append(float(rec["geometry"]["z_mm"][left+4]
                              - rec["geometry"]["z_mm"][left]))
        features[patient] = np.array([float(np.mean(gaps)), float(np.mean(base)),
                                      float(np.std(base)), float(np.mean(np.abs(delta))),
                                      float(np.sqrt(np.mean(delta.astype(np.float64)**2)))])
    results = []
    for held in sorted(by_patient):
        training = [p for p in sorted(by_patient) if p != held]
        base_train = {p: by_patient[p][0.0] for p in training}
        candidates = []
        for beta in np.linspace(0, 1, 11):
            beta = round(float(beta), 1)
            means = {metric: np.mean([by_patient[p][beta][metric] for p in training])
                     for metric in METRICS}
            baseline = {metric: np.mean([base_train[p][metric] for p in training])
                        for metric in METRICS}
            if safe(means, baseline):
                candidates.append((means["psnr"], beta))
        fixed_beta = max(candidates)[1]
        predicted = ridge(np.stack([features[p] for p in training]),
                          np.array([oracle[p] for p in training]), features[held])
        conservative_beta = round(float(np.clip(np.floor((predicted-.1)*10)/10, 0, 1)), 1)
        for policy, beta in (("loo_cohort_guard_fixed", fixed_beta),
                             ("loo_ridge_conservative", conservative_beta),
                             ("target_assisted_patient_oracle", oracle[held])):
            row = by_patient[held][beta]
            results.append(dict(patient_id=held, policy=policy, beta=beta,
                                strict_patient_guard_pass=safe(row, by_patient[held][0.0]),
                                **{metric: row[metric] for metric in METRICS}))
    summary = {}
    for policy in ("loo_cohort_guard_fixed", "loo_ridge_conservative",
                   "target_assisted_patient_oracle"):
        selected = [r for r in results if r["policy"] == policy]
        summary[policy] = dict(mean_beta=float(np.mean([r["beta"] for r in selected])),
                               strict_patient_guard_passes=sum(r["strict_patient_guard_pass"]
                                                               for r in selected),
                               **{metric: float(np.mean([r[metric] for r in selected]))
                                  for metric in METRICS})
    baseline = float(np.mean([by_patient[p][0.0]["psnr"] for p in by_patient]))
    for value in summary.values():
        value["psnr_gain_vs_base_db"] = value["psnr"] - baseline
    result = dict(scope="weak_selector_only_LOPO_on_historical_validation",
                  patients=len(by_patient), features=["gap_mm", "base_mean", "base_std",
                                                      "delta_mean_absolute", "delta_rms"],
                  learner="ridge penalty 10, subtract 0.1 beta then floor to 0.1 grid",
                  summary=summary,
                  source_sha256={str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p)
                                 for p in (ARCHIVE, FRONTIER, ORACLE, MANIFEST)},
                  limitations=["The image-level patch correction used to build the frontier already sees the target; only beta prediction is held out.",
                               "Both frozen checkpoints were selected on these same validation patients.",
                               "Patient features are low-dimensional and the cohort has only 23 patients; this is a falsification probe, not a calibrated risk certificate.",
                               "The structure metrics are intensity-threshold proxies."])
    with (OUT / "patient_risk_selector_per_patient.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    (OUT / "patient_risk_selector_diagnostic.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
