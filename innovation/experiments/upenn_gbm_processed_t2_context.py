"""CPU-only published-plane context audit on all frozen processed UPENN T2 patients."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
sys.path.insert(0, str(ROOT / "experiments"))
from remind_native_t2_ixi_pair import MODELS, patient_result, sha256, write_csv


PROTOCOL = ROOT / "UPENN_GBM_PROCESSED_T2_CONTEXT_PROTOCOL_2026-10-01.md"
INVENTORY = ROOT / "literature/upenn_gbm_processed_t2_inventory.json"
DOWNLOADS = ROOT / "literature/upenn_gbm_processed_t2_download_manifest.json"
QUALIFIED = ROOT / "literature/upenn_gbm_processed_t2_qualification.json"
REFERENCE_SCRIPT = ROOT / "experiments/remind_native_t2_ixi_pair.py"
OUT = ROOT / "experiments/upenn_gbm_processed_t2_context"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    downloads = json.loads(DOWNLOADS.read_text(encoding="utf-8"))
    qualified = json.loads(QUALIFIED.read_text(encoding="utf-8"))
    patients = qualified["records"]
    if (len(patients) != 374 or inventory["patients_selected"] != 374 or
            qualified["protocol_sha256"] != sha256(PROTOCOL) or
            qualified["inventory_sha256"] != sha256(INVENTORY) or
            qualified["download_manifest_sha256"] != sha256(DOWNLOADS) or
            downloads["inventory_sha256"] != sha256(INVENTORY)):
        raise ValueError("Frozen source, qualification or protocol changed")
    for name, (_, path, expected) in MODELS.items():
        if sha256(path) != expected:
            raise ValueError(f"{name} checkpoint SHA-256 changed")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    OUT.mkdir(parents=True)
    per_target, per_patient, failures = [], [], []
    started = time.perf_counter()
    for index, patient in enumerate(patients, 1):
        if not patient["eligible"]:
            failures.append({"patient": patient["patient"], "stage": "header_or_download",
                             "reason": patient["reason"]})
            print(f"{index}/374 {patient['patient']} HEADER_FAIL", flush=True)
            continue
        try:
            rows, summary = patient_result(patient, hat, swinir)
            per_target.extend(rows)
            per_patient.append(summary)
            print(f"{index}/374 {patient['patient']} targets={len(rows)} "
                  f"elapsed={time.perf_counter() - started:.1f}s", flush=True)
        except Exception as error:
            failures.append({"patient": patient["patient"], "stage": "pixel_or_inference",
                             "reason": f"{type(error).__name__}: {error}"})
            print(f"{index}/374 {patient['patient']} FAIL {error}", flush=True)
    write_csv(OUT / "per_target.csv", per_target)
    write_csv(OUT / "per_patient.csv", per_patient)
    values = np.asarray([row["delta_o"] for row in per_patient], dtype=np.float64)
    if len(values):
        rng = np.random.default_rng(20261004)
        draws = values[rng.integers(0, len(values), (5000, len(values)))].mean(axis=1)
        ci = np.percentile(draws, [2.5, 97.5]).tolist()
        mean = float(values.mean())
    else:
        ci, mean = [None, None], None
    payload = {
        "protocol_sha256": sha256(PROTOCOL),
        "script_sha256": sha256(Path(__file__)),
        "reference_script_sha256": sha256(REFERENCE_SCRIPT),
        "inventory_sha256": sha256(INVENTORY),
        "download_manifest_sha256": sha256(DOWNLOADS),
        "qualification_sha256": sha256(QUALIFIED),
        "checkpoint_sha256": {name: specification[2] for name, specification in MODELS.items()},
        "precision": "CPU float32", "patients_expected": 374,
        "patients_header_eligible": qualified["patients_header_eligible"],
        "patients_scored": len(per_patient), "targets_scored": len(per_target),
        "failures": failures, "mean_delta_o": mean, "ci95_delta_o": ci,
        "positive_patients": int((values > 0).sum()),
        "negative_patients": int((values < 0).sum()),
        "mean_shared_o": (float(np.mean([row["shared_observable"] for row in per_patient]))
                          if per_patient else None),
        "mean_disjoint_o": (float(np.mean([row["disjoint_observable"] for row in per_patient]))
                            if per_patient else None),
        "mean_residue_1_delta_o": (float(np.mean([row["residue_1_delta_o"] for row in per_patient]))
                                   if per_patient else None),
        "mean_residue_3_delta_o": (float(np.mean([row["residue_3_delta_o"] for row in per_patient]))
                                   if per_patient else None),
        "primary_success": len(per_patient) >= 300 and ci[0] is not None and ci[0] > 0,
        "elapsed_seconds": time.perf_counter() - started,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in (
        "patients_header_eligible", "patients_scored", "targets_scored", "mean_delta_o",
        "ci95_delta_o", "primary_success", "elapsed_seconds")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
