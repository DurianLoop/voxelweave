"""Post-result, read-only robustness summaries for the prespecified secondary HAT arm."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/ds007045_thin3d_model_pilot/per_patient.csv"
OUT = ROOT / "experiments/ds007045_thin3d_model_pilot/hat_secondary_sensitivity.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 33 or len({row["case"] for row in rows}) != 33:
        raise ValueError("Frozen 33-case result table changed")
    tumor = np.array([float(row["tumor_hat_minus_pipeline_linear_normalized_mse"])
                      for row in rows], dtype=np.float64)
    full = np.array([float(row["full_hat_minus_pipeline_linear_normalized_mse"])
                     for row in rows], dtype=np.float64)
    nsk = np.array([float(row["tumor_hat_minus_pipeline_linear_normalized_mse"])
                    for row in rows if row["site"] == "NSK"], dtype=np.float64)
    if len(nsk) != 30:
        raise ValueError("NSK denominator changed")
    rng = np.random.default_rng(20261004)
    draws = rng.integers(0, len(tumor), (5000, len(tumor)))
    nsk_draws = rng.integers(0, len(nsk), (5000, len(nsk)))
    result = {
        "status": "post-result sensitivity, not new confirmatory endpoint",
        "source_csv_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "patients": 33,
        "hat_tumor_worse_full_better": int(((tumor > 0) & (full < 0)).sum()),
        "hat_tumor_positive_patients": int((tumor > 0).sum()),
        "hat_full_negative_patients": int((full < 0).sum()),
        "hat_tumor_mean": float(tumor.mean()),
        "hat_tumor_eight_comparison_bonferroni_95_interval": [
            float(value) for value in np.percentile(tumor[draws].mean(axis=1), [.3125, 99.6875])],
        "nsk_patients": 30,
        "nsk_hat_tumor_positive_patients": int((nsk > 0).sum()),
        "nsk_hat_tumor_mean": float(nsk.mean()),
        "nsk_hat_tumor_exploratory_95_interval": [
            float(value) for value in np.percentile(nsk[nsk_draws].mean(axis=1), [2.5, 97.5])],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
