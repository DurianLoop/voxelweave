"""Descriptive post-result diagnostics; never modifies frozen primary inference."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import trim_mean


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments/msd_task01_tumor_roi_context"
OUT = RUN / "posthoc_descriptive.json"


def residue_mean(rows: list[dict], region: str, field: str) -> float:
    return float(np.mean([
        np.mean([row[region][field] for row in rows if row["residue"] == residue])
        for residue in (1, 3)]))


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite posthoc diagnostics")
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
    patients = []
    for path in sorted((RUN / "cases").glob("BRATS_*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        if not case["complete"]:
            continue
        rows = case["rows"]
        values = {"scan": case["scan"],
                  "contrast": case["summary"]["delta_o_lesion_minus_local"],
                  "fixed_denominator_contrast":
                      residue_mean(rows, "lesion", "delta_o_fixed_shared_denominator") -
                      residue_mean(rows, "local_control", "delta_o_fixed_shared_denominator")}
        for region in ("lesion", "local_control"):
            values[f"{region}_pchip_mse"] = residue_mean(rows, region, "pchip_mse")
            values[f"{region}_ensemble_mse"] = residue_mean(rows, region, "disjoint_ensemble_mse")
        patients.append(values)
    if len(patients) != summary["cases_complete"]:
        raise ValueError("Complete-case count changed")
    contrast = np.array([row["contrast"] for row in patients])
    result = {"classification": "post-result descriptive sensitivity; not a replacement primary endpoint",
              "complete_patients": len(patients),
              "contrast_median": float(np.median(contrast)),
              "contrast_q05_q25_q75_q95": [float(v) for v in np.percentile(contrast, [5, 25, 75, 95])],
              "contrast_10_percent_trimmed_mean": float(trim_mean(contrast, .1)),
              "contrast_leave_one_out_mean_range": [
                  float((contrast.sum() - contrast.max()) / (len(contrast) - 1)),
                  float((contrast.sum() - contrast.min()) / (len(contrast) - 1))],
              "fixed_denominator_contrast_mean": float(np.mean([
                  row["fixed_denominator_contrast"] for row in patients])),
              "pchip_comparisons": {}}
    for region in ("lesion", "local_control"):
        pchip = np.asarray([row[f"{region}_pchip_mse"] for row in patients])
        ensemble = np.asarray([row[f"{region}_ensemble_mse"] for row in patients])
        ratio = ensemble / pchip
        result["pchip_comparisons"][region] = {
            "mean_pchip_mse": float(pchip.mean()),
            "mean_disjoint_ensemble_mse": float(ensemble.mean()),
            "ratio_of_patient_mean_mse": float(ensemble.mean() / pchip.mean()),
            "median_patient_ensemble_to_pchip_mse_ratio": float(np.median(ratio)),
            "patients_ensemble_lower_mse_than_pchip": int((ensemble < pchip).sum()),
            "patients_pchip_lower_mse_than_ensemble": int((pchip < ensemble).sum()),
            "patients_equal_mse": int((pchip == ensemble).sum())}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
