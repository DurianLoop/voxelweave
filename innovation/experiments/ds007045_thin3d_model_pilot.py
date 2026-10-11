"""CPU-only 34-case high-resolution 3D T2 model pilot."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
import torch

import ds007045_model_replication as base


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "DS007045_THIN3D_MODEL_PILOT_PROTOCOL_2026-10-01.md"
SIDECARS = ROOT / "literature/source_cache/ds007045_raw_t2_sidecars_2026-10-01/summary.json"
QUALIFICATION = ROOT / "experiments/ds007045_cohort_label_qualification"
OUT = ROOT / "experiments/ds007045_thin3d_model_pilot"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--preflight-one"):
        raise ValueError("Supported: full run or --preflight-one")
    preflight = len(sys.argv) == 2
    sidecar_summary = json.loads(SIDECARS.read_text(encoding="utf-8"))
    cases = sorted(sidecar_summary["thin_3d_<=1_5mm"])
    qualification_summary = json.loads((QUALIFICATION / "summary.json").read_text(encoding="utf-8"))
    if (len(cases) != 34 or len(set(cases)) != 34 or
            sidecar_summary["attempted"] != 363 or qualification_summary["eligible"] != 359):
        raise ValueError("Frozen outcome-independent source qualification changed")
    if not base.live_description_matches():
        raise ValueError("Current v2.0.1 description changed")
    for name, (_, path, expected) in base.MODELS.items():
        if base.sha256(path) != expected:
            raise ValueError(f"Frozen {name} checkpoint changed")
    records = []
    for case in cases:
        record = json.loads((QUALIFICATION / "cases" / f"{case}.json").read_text(encoding="utf-8"))
        if not record["eligible"]:
            raise ValueError(f"Thin-3D case failed prior label qualification: {case}")
        records.append(record)
    OUT.mkdir(parents=True, exist_ok=True)
    base.DATA.mkdir(parents=True, exist_ok=True)
    contract = {"protocol_sha256": digest(PROTOCOL),
                "sidecar_summary_sha256": digest(SIDECARS),
                "qualification_summary_sha256": digest(QUALIFICATION / "summary.json"),
                "base_script_sha256": digest(Path(base.__file__)),
                "script_sha256": digest(Path(__file__)),
                "checkpoint_sha256": {name: spec[2] for name, spec in base.MODELS.items()},
                "attempted_cases": 34, "gpu_used": False}
    contract_path = OUT / "run_contract.json"
    if contract_path.exists():
        if json.loads(contract_path.read_text(encoding="utf-8")) != contract:
            raise ValueError("Existing pilot run contract differs")
    else:
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    hat = base.MODELS["hat"][0](base.MODELS["hat"][1], device="cpu")
    swinir = base.MODELS["swinir"][0](base.MODELS["swinir"][1], device="cpu")
    case_dir = OUT / "cases"
    case_dir.mkdir(exist_ok=True)
    selected = records[:1] if preflight else records
    completed, failures = [], []
    for index, record in enumerate(selected, 1):
        case = record["case"]
        path = case_dir / f"{case}.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
            if result.get("contract_sha256") != digest(contract_path):
                raise ValueError(f"Existing case contract differs: {case}")
        else:
            try:
                result = base.score_case(record, hat, swinir)
            except Exception as exc:
                result = {"case": case, "complete": False,
                          "failure_type": type(exc).__name__, "failure_reason": str(exc)[:200]}
            result["contract_sha256"] = digest(contract_path)
            path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        if result["complete"]:
            completed.append(result)
        else:
            failures.append({"case": case, "reason": result["failure_reason"]})
        print(f"thin3d CPU model {index}/{len(selected)} {case} complete={result['complete']}", flush=True)
    if not base.live_description_matches():
        raise ValueError("Dataset description changed after pilot")
    patients = [item["patient"] for item in completed]
    targets = [{"case": item["case"], **row} for item in completed for row in item["rows"]]
    write_csv(OUT / ("preflight_per_patient.csv" if preflight else "per_patient.csv"), patients)
    write_csv(OUT / ("preflight_per_target.csv" if preflight else "per_target.csv"), targets)
    summary = {"attempted": len(selected), "completed": len(patients), "failures": failures,
               "protocol_sha256": digest(PROTOCOL), "contract_sha256": digest(contract_path),
               "complete_cohort": not preflight, "no_gpu": True,
               "bootstrap_seed": 20261004, "bootstrap_draws": 5000}
    if patients:
        rng = np.random.default_rng(20261004)
        draws = rng.integers(0, len(patients), (5000, len(patients)))
        fields = [f"{roi}_{model}_minus_{baseline}_normalized_mse"
                  for roi in ("tumor", "full") for model in ("swinir", "hat")
                  for baseline in ("pipeline_linear", "raw_linear")]
        summary["differences"] = {field: base.interval(
            np.array([p[field] for p in patients], dtype=np.float64), draws) for field in fields}
        discordance = sum(p["swinir_pipeline_sign_discordance"] for p in patients)
        summary["discordance"] = {"patients": discordance,
                                  "fraction": discordance / len(patients),
                                  "wilson_95_lower": base.wilson_lower(discordance, len(patients))}
        summary["sites"] = dict(sorted(Counter(p["site"] for p in patients).items()))
        summary["site_sensitivity"] = {
            site: {"patients": sum(p["site"] == site for p in patients),
                   "mean_tumor_difference": float(np.mean([
                       p["tumor_swinir_minus_pipeline_linear_normalized_mse"]
                       for p in patients if p["site"] == site])),
                   "mean_full_difference": float(np.mean([
                       p["full_swinir_minus_pipeline_linear_normalized_mse"]
                       for p in patients if p["site"] == site])),
                   "discordant": sum(p["swinir_pipeline_sign_discordance"]
                                     for p in patients if p["site"] == site)}
            for site in sorted(summary["sites"])}
        tumor_ci = summary["differences"]["tumor_swinir_minus_pipeline_linear_normalized_mse"]["ci95"]
        full_ci = summary["differences"]["full_swinir_minus_pipeline_linear_normalized_mse"]["ci95"]
        summary["directional_pilot_signal"] = bool(
            not preflight and len(patients) >= 30 and tumor_ci[0] > 0 and full_ci[1] < 0 and
            summary["discordance"]["wilson_95_lower"] > .20)
    (OUT / ("preflight_summary.json" if preflight else "summary.json")).write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("failures", "differences")}, indent=2))


if __name__ == "__main__":
    main()
