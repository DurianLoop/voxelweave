"""Target-assisted per-patient amplitude oracle over the fixed 0.1 beta grid."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "innovation/experiments"
SOURCE = OUT / "oracle_guard_frontier_per_patient.csv"
METRICS = ("psnr", "ssim", "mae", "mse", "ncc", "dice_proxy", "hd95_proxy", "tail10_mse")


def safe(candidate: dict, base: dict) -> bool:
    higher = ("ssim", "ncc", "dice_proxy")
    lower = ("mae", "mse", "hd95_proxy", "tail10_mse")
    return all(candidate[key] >= base[key] for key in higher) and all(
        candidate[key] <= base[key] for key in lower)


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        rows = [{key: (row[key] if key == "patient_id" else float(row[key]))
                 for key in row} for row in csv.DictReader(stream)]
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["patient_id"]].append(row)
    selected = []
    for patient, candidates in sorted(groups.items()):
        base = next(row for row in candidates if row["beta"] == 0)
        feasible = [row for row in candidates if safe(row, base)]
        winner = max(feasible, key=lambda row: row["psnr"])
        selected.append(dict(patient_id=patient, beta=winner["beta"],
                             psnr_gain_db=winner["psnr"]-base["psnr"],
                             **{metric: winner[metric] for metric in METRICS}))
    gains = np.asarray([row["psnr_gain_db"] for row in selected])
    rng = np.random.default_rng(3407)
    bootstrap = gains[rng.integers(0, len(gains), size=(10000, len(gains)))].mean(axis=1)
    result = dict(scope="target_assisted_patient_amplitude_oracle_historical_validation",
                  patients=len(selected), beta_grid_step=0.1,
                  strict_patient_metric_signs=list(METRICS[1:]),
                  mean_psnr_gain_db=float(gains.mean()),
                  bootstrap_95_percentile_descriptive=[float(x) for x in np.quantile(bootstrap, [.025, .975])],
                  patients_with_gain_at_least_0_10db=int((gains >= .10).sum()),
                  patients_kept_at_base=int(sum(row["beta"] == 0 for row in selected)),
                  source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  limitations=["The target determines both every patch alpha and each patient's beta; this is not deployable.",
                               "This is a stronger patient-level guard than the historical cohort-mean gate and is not an official promotion result.",
                               "The development cohort selected the two checkpoints; bootstrap intervals are descriptive, not independent confirmation.",
                               "Dice and HD95 are intensity-threshold proxies."])
    with (OUT / "patient_guard_oracle_per_patient.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(selected[0]))
        writer.writeheader()
        writer.writerows(selected)
    (OUT / "patient_guard_oracle.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
