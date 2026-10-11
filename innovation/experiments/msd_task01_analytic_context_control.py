"""Post-result, frozen analytic context control on official local MSD pairs."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import numpy as np
from scipy.interpolate import PchipInterpolator

from msd_task01_source import (DATASET, ROOT, load_exact_pair, official_index,
                               region_masks, selected_targets, sha256, source_record)


PROTOCOL = ROOT / "MSD_TASK01_ANALYTIC_CONTEXT_CONTROL_PROTOCOL_2026-10-01.md"
LABELS = ROOT / "experiments/msd_task01_label_qualification.json"
NEURAL = ROOT / "experiments/msd_task01_tumor_roi_context"
OUT = ROOT / "experiments/msd_task01_analytic_context_control"


def linear(t2: np.ndarray, left: int, right: int, target: int) -> np.ndarray:
    weight = (target - left) / (right - left)
    return ((1 - weight) * t2[:, :, left].astype(np.float64) +
            weight * t2[:, :, right].astype(np.float64))


def metrics(a: np.ndarray, b: np.ndarray, y: np.ndarray, roi: np.ndarray) -> dict:
    ea = (a - y)[roi]
    eb = (b - y)[roi]
    a_mse = float(np.mean(ea * ea))
    b_mse = float(np.mean(eb * eb))
    paired_mse = (a_mse + b_mse) / 2
    disagreement_mse = float(np.mean((ea - eb) ** 2))
    if not np.isfinite([a_mse, b_mse, paired_mse, disagreement_mse]).all() or paired_mse <= 0:
        raise ValueError("Nonfinite or zero paired-error denominator")
    return {"a_mse": a_mse, "b_mse": b_mse, "paired_mse": paired_mse,
            "disagreement_mse": disagreement_mse,
            "observable": disagreement_mse / (4 * paired_mse)}


def region(a: np.ndarray, b0: np.ndarray, b2: np.ndarray,
           y: np.ndarray, roi: np.ndarray) -> dict:
    shared, disjoint = metrics(a, b0, y, roi), metrics(a, b2, y, roi)
    return {"pixels": int(roi.sum()), "shared": shared, "disjoint": disjoint,
            "delta_o": disjoint["observable"] - shared["observable"],
            "fixed_denominator_delta_o":
                (disjoint["disagreement_mse"] - shared["disagreement_mse"]) /
                (4 * shared["paired_mse"])}


def balanced(rows: list[dict], key: str, field: str) -> float:
    return float(np.mean([np.mean([row[key][field] for row in rows
                                   if row["residue"] == residue])
                          for residue in (1, 3)]))


def score(scan: str, record: dict, indexed: dict, entries: dict) -> dict:
    t2, label, sources = load_exact_pair(scan, indexed, entries)
    if sources[1]["compressed_sha256"] != record["source"]["compressed_sha256"]:
        raise ValueError("Label bytes changed after qualification")
    if selected_targets(label) != record["targets"]:
        raise ValueError("Frozen label targets changed")
    rows = []
    for residue in (1, 3):
        for z in record["targets"][str(residue)]:
            support, lesion, local = region_masks(t2, label, z)
            i = z // 4
            phase0 = [4 * (i + shift) for shift in (-1, 0, 1, 2)]
            if min(phase0) < 0 or max(phase0) >= t2.shape[2]:
                raise ValueError("Four phase-0 reference anchors unavailable")
            reference = PchipInterpolator(
                phase0, np.moveaxis(t2[:, :, phase0].astype(np.float64), -1, 0),
                axis=0)(z)
            b0 = linear(t2, 4 * i, 4 * (i + 1), z)
            j = (z - 2) // 4
            b2 = linear(t2, 4 * j + 2, 4 * (j + 1) + 2, z)
            y = t2[:, :, z].astype(np.float64)
            if not np.isfinite([reference, b0, b2, y]).all():
                raise ValueError("Nonfinite analytic prediction or target")
            rows.append({"z": z, "residue": residue,
                         "lesion": region(reference, b0, b2, y, lesion),
                         "local_control": region(reference, b0, b2, y, local),
                         "full_support_pixels": int(support.sum())})
    if len(rows) != 4:
        raise ValueError("Expected exactly four frozen targets")
    lesion_delta = balanced(rows, "lesion", "delta_o")
    local_delta = balanced(rows, "local_control", "delta_o")
    return {"scan": scan, "complete": True, "source_files": sources,
            "targets": record["targets"], "rows": rows,
            "summary": {"lesion_delta_o": lesion_delta,
                        "local_delta_o": local_delta,
                        "lesion_minus_local_delta_o": lesion_delta - local_delta,
                        "fixed_denominator_lesion_delta_o":
                            balanced(rows, "lesion", "fixed_denominator_delta_o"),
                        "fixed_denominator_local_delta_o":
                            balanced(rows, "local_control", "fixed_denominator_delta_o")}}


def main() -> None:
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    neural = json.loads((NEURAL / "summary.json").read_text(encoding="utf-8"))
    if labels["cases_attempted"] != 484 or neural["cases_attempted"] != 484:
        raise ValueError("Frozen case count changed")
    indexed, entries = official_index()
    for record in labels["records"]:
        if record["eligible"]:
            for kind in ("imagesTr", "labelsTr"):
                _, path = source_record(record["scan"], kind, indexed, entries)
                if not path.is_file():
                    raise FileNotFoundError(f"No new download is allowed: {path}")
    OUT.mkdir(exist_ok=True)
    cases = OUT / "cases"
    cases.mkdir(exist_ok=True)
    contract = {"protocol_sha256": sha256(PROTOCOL), "label_qualification_sha256": sha256(LABELS),
                "neural_summary_sha256": sha256(NEURAL / "summary.json"),
                "source_script_sha256": sha256(ROOT / "experiments/msd_task01_source.py"),
                "script_sha256": sha256(Path(__file__)), "dataset_json_sha256": sha256(DATASET),
                "attempted_cases": 484, "precision": "CPU float64 analytic", "gpu_used": False}
    contract_path = OUT / "run_contract.json"
    if contract_path.exists():
        if json.loads(contract_path.read_text(encoding="utf-8")) != contract:
            raise ValueError("Cannot resume under changed control contract")
    else:
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    for count, record in enumerate(labels["records"], 1):
        scan = record["scan"]
        path = cases / f"{scan}.json"
        if path.exists():
            item = json.loads(path.read_text(encoding="utf-8"))
            if item["run_contract_sha256"] != sha256(contract_path):
                raise ValueError("Existing case has changed run contract")
        elif not record["eligible"]:
            item = {"scan": scan, "complete": False,
                    "failure_stage": "label_qualification",
                    "failure_type": record["error_type"]}
        else:
            try:
                item = score(scan, record, indexed, entries)
            except Exception as error:
                item = {"scan": scan, "complete": False,
                        "failure_stage": "source_or_analytic_prediction",
                        "failure_type": type(error).__name__,
                        "failure_reason": str(error)[:180]}
        if not path.exists():
            item["run_contract_sha256"] = sha256(contract_path)
            temporary = path.with_suffix(".json.partial")
            temporary.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
            temporary.replace(path)
        if count % 25 == 0 or count == 484:
            print(f"analytic cases {count}/484", flush=True)


if __name__ == "__main__":
    main()
