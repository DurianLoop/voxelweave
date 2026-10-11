"""CPU-only leave-one-patient-out scalar mixing probe on paired old-model outputs.

The base and candidate checkpoints were previously selected on this validation
set, so leave-one-patient-out applies only to the selector in this weak probe.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "innovation/experiments/local_oracle_full_val23"
SOURCE = RESULTS / "per_slice.csv"
MANIFEST = ROOT / "design/pastnet_v2/manifests/fastmri/fold_00.json"
OUT = ROOT / "innovation/experiments"
POLICIES = ("loo_fixed", "loo_phase", "ridge_phase_gap_z", "ridge_phase_gap_z_d",
            "oracle_slice")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def psnr(row: dict, alpha: float) -> float:
    mse = row["b_mse"] - 2 * alpha * row["m"] + alpha * alpha * row["d"]
    return float(-10 * np.log10(max(mse, 1e-12)))


def best_alpha(rows: list[dict]) -> float:
    grid = np.linspace(0.0, 1.0, 101)
    by_patient: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_patient[row["patient_id"]].append(row)
    return float(max(grid, key=lambda alpha: np.mean([
        np.mean([psnr(row, alpha) for row in patient_rows])
        for patient_rows in by_patient.values()])))


def features(row: dict, with_disagreement: bool) -> list[float]:
    values = [float(row["phase"] == 0.5), float(row["phase"] == 0.75),
              row["gap_mm"], row["z_fraction"]]
    if with_disagreement:
        values.append(np.log10(max(row["d"], 1e-12)))
    return values


def ridge_predict(train: list[dict], test: list[dict], with_disagreement: bool) -> np.ndarray:
    x = np.asarray([features(row, with_disagreement) for row in train], dtype=np.float64)
    q = np.asarray([features(row, with_disagreement) for row in test], dtype=np.float64)
    y = np.asarray([row["alpha_slice"] for row in train])
    center, scale = x.mean(axis=0), np.maximum(x.std(axis=0), 1e-8)
    x = np.column_stack((np.ones(len(x)), (x-center)/scale))
    q = np.column_stack((np.ones(len(q)), (q-center)/scale))
    penalty = np.eye(x.shape[1]) * 10.0
    penalty[0, 0] = 0.0
    coef = np.linalg.solve(x.T @ x + penalty, x.T @ y)
    return np.clip(q @ coef, 0.0, 1.0)


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        source = list(csv.DictReader(stream))
    by_slice: dict[tuple[str, int, float], dict[str, dict]] = defaultdict(dict)
    for row in source:
        key = row["case_id"], int(row["z"]), float(row["phase"])
        by_slice[key][row["policy"]] = row
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    geometry = {r["case_id"]: r for r in manifest["records"] if r["split"] == "val"}
    observations = []
    for (case, z, phase), policies in by_slice.items():
        if set(policies) != {"base", "orientation", "best_fixed", "oracle_slice", "oracle_patch32"}:
            raise AssertionError(f"Incomplete policy set for {case}, z={z}")
        base, candidate, fixed = (policies[name] for name in ("base", "orientation", "best_fixed"))
        a = 0.7
        b_mse, c_mse, f_mse = (float(row["mse"]) for row in (base, candidate, fixed))
        delta_1, delta_a = c_mse-b_mse, f_mse-b_mse
        m = (delta_a-a*a*delta_1)/(2*(a*a-a))
        d = delta_1+2*m
        if d <= 0:
            raise AssertionError(f"Nonpositive candidate disagreement: {case}, z={z}")
        alpha_slice = float(policies["oracle_slice"]["alpha_slice"])
        if abs(np.clip(m/d, 0, 1)-alpha_slice) > 0.005:
            raise AssertionError(f"Scalar oracle reconstruction differs: {case}, z={z}")
        rec = geometry[case]
        left = 4*((z-1)//4)
        gap = float(rec["geometry"]["z_mm"][left+4] - rec["geometry"]["z_mm"][left])
        observations.append(dict(case_id=case, patient_id=base["patient_id"], z=z,
                                 phase=phase, gap_mm=gap,
                                 z_fraction=z/max(int(rec["shape"][2])-1, 1),
                                 b_mse=b_mse, m=m, d=d, alpha_slice=alpha_slice))
    patients = sorted({row["patient_id"] for row in observations})
    results = []
    for patient in patients:
        train = [row for row in observations if row["patient_id"] != patient]
        test = [row for row in observations if row["patient_id"] == patient]
        fixed = best_alpha(train)
        phase_alpha = {phase: best_alpha([row for row in train if row["phase"] == phase])
                       for phase in (0.25, 0.5, 0.75)}
        ridge_basic = ridge_predict(train, test, False)
        ridge_disagreement = ridge_predict(train, test, True)
        for index, row in enumerate(test):
            alphas = (fixed, phase_alpha[row["phase"]], float(ridge_basic[index]),
                      float(ridge_disagreement[index]), row["alpha_slice"])
            for policy, alpha in zip(POLICIES, alphas):
                results.append(dict(case_id=row["case_id"], patient_id=patient, z=row["z"],
                                    phase=row["phase"], policy=policy, alpha=alpha,
                                    psnr=psnr(row, alpha)))

    per_patient = []
    for patient in patients:
        for policy in POLICIES:
            selected = [row for row in results if row["patient_id"] == patient and row["policy"] == policy]
            per_patient.append(dict(patient_id=patient, policy=policy,
                                    psnr=float(np.mean([row["psnr"] for row in selected])),
                                    mean_alpha=float(np.mean([row["alpha"] for row in selected]))))
    policy_means = {policy: float(np.mean([row["psnr"] for row in per_patient
                                          if row["policy"] == policy])) for policy in POLICIES}
    fixed_by_patient = {row["patient_id"]: row["psnr"] for row in per_patient
                        if row["policy"] == "loo_fixed"}
    wins = {policy: sum(row["psnr"] > fixed_by_patient[row["patient_id"]]
                        for row in per_patient if row["policy"] == policy)
            for policy in POLICIES if policy != "loo_fixed"}
    result = dict(scope="selector_only_leave_one_patient_out_on_historical_validation",
                  patients=len(patients), slices=len(observations),
                  outcome="whole_slice_PSNR_from_reconstructed_quadratic_MSE",
                  source_sha256=sha256(SOURCE), manifest_sha256=sha256(MANIFEST),
                  policies=dict(loo_fixed="Grid-tuned alpha on other patients, step 0.01",
                                loo_phase="Grid-tuned alpha per phase on other patients",
                                ridge_phase_gap_z="Ridge(10) predicts slice-oracle alpha",
                                ridge_phase_gap_z_d="Same plus model-disagreement energy",
                                oracle_slice="Target-assisted continuous whole-slice alpha"),
                  mean_patient_psnr=policy_means, patient_wins_over_loo_fixed=wins,
                  limitations=["Only the selector leaves each patient's labels out; both models saw validation during checkpoint choice.",
                               "Scalar policies were evaluated by MSE algebra, not by new image-level SSIM or HD95 scoring.",
                               "The local patch oracle is a separate, stronger target-assisted action space."])
    for filename, rows in (("scalar_selector_per_slice.csv", results),
                           ("scalar_selector_per_patient.csv", per_patient)):
        with (OUT / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    (OUT / "scalar_selector_diagnostic.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mean_patient_psnr": policy_means,
                      "patient_wins_over_loo_fixed": wins}, indent=2))


if __name__ == "__main__":
    main()
