"""Frozen CPU-only MIRA tumor-region audit on all official MSD training cases."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import numpy as np
import torch
from scipy.interpolate import PchipInterpolator

from msd_task01_source import (DATASET, ROOT, load_exact_pair, official_index,
                               region_masks, selected_targets, sha256)
from remind_native_t2_ixi_pair import MODELS, metrics, predict, prepared


PROTOCOL = ROOT / "MSD_TASK01_TUMOR_ROI_CONTEXT_PROTOCOL_2026-10-01.md"
LABELS = ROOT / "experiments/msd_task01_label_qualification.json"
HEADERS = ROOT / "literature/source_cache/msd_task01_official_2026-10-01/header_verification.json"
OUT = ROOT / "experiments/msd_task01_tumor_roi_context"


def mse(a: np.ndarray, b: np.ndarray, roi: np.ndarray) -> float:
    difference = (a - b)[roi].astype(np.float64)
    return float(np.mean(difference * difference))


def region_result(a: np.ndarray, b0: np.ndarray, b2: np.ndarray,
                  y: np.ndarray, pchip: np.ndarray, roi: np.ndarray) -> dict:
    shared = metrics(a, b0, y, roi)
    disjoint = metrics(a, b2, y, roi)
    return {"pixels": int(roi.sum()), "shared": shared, "disjoint": disjoint,
            "delta_o": disjoint["observable"] - shared["observable"],
            "delta_o_fixed_shared_denominator":
                (disjoint["disagreement_mse"] - shared["disagreement_mse"]) /
                (4 * shared["paired_mse"]),
            "shared_ensemble_mse": mse((a + b0) / 2, y, roi),
            "disjoint_ensemble_mse": mse((a + b2) / 2, y, roi),
            "pchip_mse": mse(pchip, y, roi)}


def optional_region_result(a: np.ndarray, b0: np.ndarray, b2: np.ndarray,
                           y: np.ndarray, pchip: np.ndarray, roi: np.ndarray) -> dict | None:
    if not roi.any():
        return None
    try:
        return region_result(a, b0, b2, y, pchip, roi)
    except ValueError:
        return {"pixels": int(roi.sum()), "metric_undefined": True}


def selected_mean(rows: list[dict], region: str, field: str) -> float:
    return float(np.mean([np.mean([row[region][field] for row in rows
                                   if row["residue"] == residue])
                          for residue in (1, 3)]))


def score_case(scan: str, expected_targets: dict, expected_label_hash: str,
               hat: object, swinir: object,
               indexed: dict, entries: dict) -> dict:
    t2, label, sources = load_exact_pair(scan, indexed, entries)
    if sources[1]["compressed_sha256"] != expected_label_hash:
        raise ValueError("Label bytes changed after target qualification")
    targets = selected_targets(label)
    if targets != expected_targets:
        raise ValueError("Label-derived targets changed after qualification")
    depth = t2.shape[2]
    phases = {}
    for phase in (0, 2):
        indices = list(range(phase, depth, 4))
        anchors = t2[:, :, indices]
        if float(anchors.max()) <= float(anchors.min()):
            raise ValueError("Constant observed-anchor phase")
        phases[phase] = (indices, prepared(anchors))
    rows = []
    for residue in (1, 3):
        for z in targets[str(residue)]:
            support, lesion, local = region_masks(t2, label, z)
            i0, i2 = z // 4, (z - 2) // 4
            rel0 = (z - phases[0][0][i0]) / 4
            rel2 = (z - phases[2][0][i2]) / 4
            a = predict(hat, phases[0][1], i0, rel0, (240, 240))
            b0 = predict(swinir, phases[0][1], i0, rel0, (240, 240))
            b2 = predict(swinir, phases[2][1], i2, rel2, (240, 240))
            if not all(np.isfinite(v).all() for v in (a, b0, b2)):
                raise ValueError("Nonfinite model prediction")
            even_indices = [z - 3, z - 1, z + 1, z + 3]
            neighbors = np.moveaxis(t2[:, :, even_indices], -1, 0)
            pchip = np.asarray(PchipInterpolator(even_indices, neighbors, axis=0)(z), dtype=np.float32)
            y = t2[:, :, z]
            edema = (label[:, :, z] == 1) & support
            core = np.isin(label[:, :, z], [2, 3]) & support
            row = {"z": z, "residue": residue,
                   "lesion": region_result(a, b0, b2, y, pchip, lesion),
                   "local_control": region_result(a, b0, b2, y, pchip, local),
                   "full_support": region_result(a, b0, b2, y, pchip, support),
                   "edema_pixels": int(edema.sum()),
                   "tumor_core_pixels": int(core.sum()),
                   "edema": optional_region_result(a, b0, b2, y, pchip, edema),
                   "tumor_core": optional_region_result(a, b0, b2, y, pchip, core)}
            rows.append(row)
    if len(rows) != 4:
        raise ValueError("Frozen four-target case incomplete")
    delta_lesion = selected_mean(rows, "lesion", "delta_o")
    delta_local = selected_mean(rows, "local_control", "delta_o")
    summary = {"delta_o_lesion": delta_lesion, "delta_o_local_control": delta_local,
               "delta_o_lesion_minus_local": delta_lesion - delta_local,
               "delta_o_full_support": selected_mean(rows, "full_support", "delta_o"),
               "delta_o_lesion_fixed_denominator":
                   selected_mean(rows, "lesion", "delta_o_fixed_shared_denominator"),
               "lesion_shared_ensemble_mse": selected_mean(rows, "lesion", "shared_ensemble_mse"),
               "lesion_disjoint_ensemble_mse": selected_mean(rows, "lesion", "disjoint_ensemble_mse"),
               "lesion_pchip_mse": selected_mean(rows, "lesion", "pchip_mse")}
    return {"scan": scan, "complete": True, "targets": targets,
            "source_files": sources, "rows": rows, "summary": summary}


def main() -> None:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--preflight-one"):
        raise ValueError("Only full run or fixed first-case software preflight is supported")
    preflight = len(sys.argv) == 2
    label_report = json.loads(LABELS.read_text(encoding="utf-8"))
    header_report = json.loads(HEADERS.read_text(encoding="utf-8"))
    protocol_hash = sha256(PROTOCOL)
    if (label_report["protocol_sha256"] != protocol_hash or
            label_report["cases_attempted"] != 484 or
            not label_report["meets_350_case_floor_before_image_inference"] or
            header_report["effective_same_grid"] != 484 or
            label_report["header_verification_sha256"] != sha256(HEADERS)):
        raise ValueError("Frozen source/label qualification contract changed")
    for name, (_, path, expected) in MODELS.items():
        if sha256(path) != expected:
            raise ValueError(f"Frozen {name} checkpoint changed")
    indexed, entries = official_index()
    records = label_report["records"]
    if len(records) != 484 or records[0]["scan"] != "BRATS_001":
        raise ValueError("Frozen case order changed")
    OUT.mkdir(parents=True, exist_ok=True)
    cases_dir = OUT / "cases"
    cases_dir.mkdir(exist_ok=True)
    metadata_path = OUT / "run_contract.json"
    metadata = {"protocol_sha256": protocol_hash,
                "label_qualification_sha256": sha256(LABELS),
                "all_header_verification_sha256": sha256(HEADERS),
                "dataset_json_sha256": sha256(DATASET),
                "script_sha256": sha256(Path(__file__)),
                "source_script_sha256": sha256(ROOT / "experiments/msd_task01_source.py"),
                "prediction_script_sha256": sha256(ROOT / "experiments/remind_native_t2_ixi_pair.py"),
                "checkpoint_sha256": {name: spec[2] for name, spec in MODELS.items()},
                "attempted_cases": 484, "precision": "CPU float32",
                "gpu_used": False}
    if metadata_path.exists():
        if json.loads(metadata_path.read_text(encoding="utf-8")) != metadata:
            raise ValueError("Cannot resume under a different run contract")
    else:
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    selected = records[:1] if preflight else records
    for count, record in enumerate(selected, 1):
        scan = record["scan"]
        destination = cases_dir / f"{scan}.json"
        if destination.exists():
            existing = json.loads(destination.read_text(encoding="utf-8"))
            if existing.get("scan") != scan or existing.get("protocol_sha256") != protocol_hash:
                raise ValueError("Existing case result has a different contract")
            print(f"{count}/{len(selected)} {scan} existing", flush=True)
            continue
        if not record["eligible"]:
            result = {"scan": scan, "complete": False, "failure_stage": "label_qualification",
                      "failure_type": record.get("error_type", "ValueError")}
        else:
            try:
                result = score_case(scan, record["targets"],
                                    record["source"]["compressed_sha256"],
                                    hat, swinir, indexed, entries)
            except Exception as error:
                result = {"scan": scan, "complete": False,
                          "failure_stage": "source_or_prediction", "failure_type": type(error).__name__,
                          "failure_reason": str(error)[:180]}
        result["protocol_sha256"] = protocol_hash
        result["run_contract_sha256"] = sha256(metadata_path)
        temporary = destination.with_suffix(".json.partial")
        temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        temporary.replace(destination)
        print(f"{count}/{len(selected)} {scan} {'PASS' if result['complete'] else 'FAIL'}", flush=True)


if __name__ == "__main__":
    main()
