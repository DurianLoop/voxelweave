"""Target-assisted patch-oracle amplitude sweep with complete-image metrics."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "design"))
from pastnet_v2.metrics import quality
from innovation.experiments.local_correction_oracle import patch_oracle

ARCHIVE = ROOT / "innovation/experiments/local_oracle_paired_arrays_val23/paired_predictions.npz"
OUT = ROOT / "innovation/experiments"
METRICS = ("psnr", "ssim", "mae", "mse", "ncc", "dice_proxy", "hd95_proxy", "tail10_mse")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with np.load(ARCHIVE, allow_pickle=False) as file:
        data = {key: file[key] for key in file.files}
    beta_grid = np.linspace(0, 1, 11)
    rows = []
    for i in range(len(data["base"])):
        base, candidate, target = (data[name][i]
                                   for name in ("base", "candidate", "target"))
        patch, _ = patch_oracle(base, candidate, target)
        for beta in beta_grid:
            image = base + beta*(patch-base)
            rows.append(dict(case_id=str(data["case_id"][i]),
                             patient_id=str(data["patient_id"][i]),
                             z=int(data["z"][i]), phase=float(data["phase"][i]),
                             beta=float(beta),
                             **quality(image, target, data["spacing"][i])))
    by_patient: dict[tuple[float, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_patient[(row["beta"], row["patient_id"])].append(row)
    per_patient = [dict(beta=beta, patient_id=patient,
                        **{metric: float(np.mean([r[metric] for r in selected]))
                           for metric in METRICS})
                   for (beta, patient), selected in sorted(by_patient.items())]
    summary = [dict(beta=float(beta),
                    **{metric: float(np.mean([r[metric] for r in per_patient
                                              if r["beta"] == beta])) for metric in METRICS})
               for beta in beta_grid]
    base = summary[0]
    guards = []
    for row in summary:
        no_regression = (row["ssim"] >= base["ssim"] and row["mae"] <= base["mae"]
                         and row["mse"] <= base["mse"] and row["ncc"] >= base["ncc"]
                         and row["dice_proxy"] >= base["dice_proxy"]
                         and row["hd95_proxy"] <= base["hd95_proxy"]
                         and row["tail10_mse"] <= base["tail10_mse"])
        guards.append(dict(beta=row["beta"], gain_psnr_db=row["psnr"]-base["psnr"],
                           mean_metric_guards_pass=no_regression,
                           mean_guards_and_0_10db_pass=no_regression and row["psnr"]-base["psnr"] >= .10))
    feasible = [row for row, guard in zip(summary, guards)
                if guard["mean_metric_guards_pass"]]
    result = dict(scope="target_assisted_patch_oracle_amplitude_frontier_on_historical_validation",
                  patients=len(set(data["patient_id"])), slices=len(data["base"]),
                  beta_grid=[float(value) for value in beta_grid],
                  source_sha256=sha256(ARCHIVE), summary=summary, guards=guards,
                  best_psnr_with_strict_mean_metric_guards=max(feasible, key=lambda r: r["psnr"]) if feasible else None,
                  limitations=["Patch alphas use withheld target pixels; beta was scanned on the same development cohort.",
                               "Strict mean metric signs are only a screening check, not the full historical promotion protocol.",
                               "HD95 and Dice are intensity-threshold proxies, not anatomical segmentation outcomes."])
    write_csv(OUT / "oracle_guard_frontier_per_slice.csv", rows)
    write_csv(OUT / "oracle_guard_frontier_per_patient.csv", per_patient)
    (OUT / "oracle_guard_frontier.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"base": base, "guards": guards,
                      "best_psnr_with_strict_mean_metric_guards":
                          result["best_psnr_with_strict_mean_metric_guards"]}, indent=2))


if __name__ == "__main__":
    main()
