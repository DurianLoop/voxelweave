"""CPU-only analysis of two frozen, historical fastMRI validation predictions.

The same 23 patients were used in model development. This is a feasibility
diagnostic, not an independent estimate of any deployable policy's performance.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
METRICS = ("psnr", "ssim", "mae", "mse", "ncc", "dice_proxy", "hd95_proxy", "tail10_mse")
BASE = ROOT / "design/pastnet_v2/runs/full_control_seed3407_vram20/validation"
CANDIDATE = ROOT / "design/pastnet_orientation/runs/full_orientation_seed3407_vram20/validation"
GEOMETRY = ROOT / "design/pastnet_v2/results/domain_audit/per_series.csv"
OUT = ROOT / "innovation/experiments/slice_selection_diagnostic.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def gap_band(mm: float) -> str:
    if mm <= 16:
        return "at_most_16mm"
    if mm <= 22:
        return "16_to_22mm"
    return "above_22mm"


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def strict_benefit(row: dict) -> bool:
    delta = row["delta"]
    return (delta["psnr"] > 0 and delta["mae"] <= 0 and delta["ssim"] >= 0
            and delta["hd95_proxy"] <= 0)


def policy_summary(rows: list[dict], selected: dict[tuple, bool]) -> dict:
    per_patient = defaultdict(list)
    for row in rows:
        delta = row["delta"] if selected[row["key"]] else {name: 0.0 for name in METRICS}
        per_patient[row["patient_id"]].append(delta)
    per_patient_mean = {
        patient: {name: mean([r[name] for r in values]) for name in METRICS}
        for patient, values in per_patient.items()
    }
    return {
        "selected_slices": sum(selected.values()),
        "total_slices": len(rows),
        "patients": len(per_patient_mean),
        "mean_change_vs_control": {
            name: mean([r[name] for r in per_patient_mean.values()]) for name in METRICS
        },
    }


def choose_from_other_patients(rows: list[dict], features: tuple[str, ...]) -> dict[tuple, bool]:
    """A weak rule on already-used validation data, never called confirmation."""
    chosen = {}
    for patient in sorted({r["patient_id"] for r in rows}):
        others = [r for r in rows if r["patient_id"] != patient]
        grouped = defaultdict(list)
        for row in others:
            key = tuple(row[name] for name in features)
            grouped[key].append(row)
        for row in (r for r in rows if r["patient_id"] == patient):
            key = tuple(row[name] for name in features)
            group = grouped[key]
            if len({r["patient_id"] for r in group}) < 5:
                # Predefined fallback uses only other patients at the same phase.
                group = [r for r in others if r["phase"] == row["phase"]]
            chosen[row["key"]] = mean([r["delta"]["psnr"] for r in group]) > 0
    return chosen


base = read_csv(BASE / "per_slice.csv")
candidate = read_csv(CANDIDATE / "per_slice.csv")
key_names = ("case_id", "patient_id", "z", "phase")
as_key = lambda row: tuple(row[name] for name in key_names)
base_by_key = {as_key(row): row for row in base}
candidate_by_key = {as_key(row): row for row in candidate}
if len(base_by_key) != len(base) or len(candidate_by_key) != len(candidate):
    raise ValueError("Duplicate slice key")
if set(base_by_key) != set(candidate_by_key):
    raise ValueError("Different slice supports")
geometry = {r["case_id"]: float(r["gap_x4"]) for r in read_csv(GEOMETRY)
            if r["dataset"] == "fastmri" and r["split"] == "val"}
rows = []
for key in sorted(base_by_key):
    original, proposed = base_by_key[key], candidate_by_key[key]
    if key[0] not in geometry:
        raise ValueError(f"Missing validation geometry: {key[0]}")
    delta = {name: float(proposed[name]) - float(original[name]) for name in METRICS}
    rows.append({"key": key, "patient_id": key[1], "phase": key[3],
                 "gap_band": gap_band(geometry[key[0]]), "delta": delta,
                 "base_mse": float(original["mse"])})

# Verify the report uses exactly the same patient-level aggregation as the source.
for path, source in ((BASE, base_by_key), (CANDIDATE, candidate_by_key)):
    reported = {r["patient_id"]: r for r in read_csv(path / "per_patient.csv")}
    for patient, record in reported.items():
        selected = [source[row["key"]] for row in rows if row["patient_id"] == patient]
        for name in METRICS:
            if not math.isclose(mean([float(r[name]) for r in selected]),
                                float(record[name]), abs_tol=1e-10, rel_tol=0):
                raise ValueError(f"Patient aggregate mismatch: {patient} {name}")

policies = {
    "always_control": {r["key"]: False for r in rows},
    "always_orientation": {r["key"]: True for r in rows},
    "oracle_slice_psnr": {r["key"]: r["delta"]["psnr"] > 0 for r in rows},
    "oracle_slice_strict": {r["key"]: strict_benefit(r) for r in rows},
    "phase_only_other_patients": choose_from_other_patients(rows, ("phase",)),
    "phase_and_gap_other_patients": choose_from_other_patients(rows, ("phase", "gap_band")),
}

def group_summary(group: list[dict]) -> dict:
    return {"slices": len(group), "patients": len({r["patient_id"] for r in group}),
            "orientation_slice_wins": sum(r["delta"]["psnr"] > 0 for r in group),
            "mean_psnr_change_db": mean([r["delta"]["psnr"] for r in group]),
            "mean_mae_change": mean([r["delta"]["mae"] for r in group]),
            "mean_hd95_proxy_change": mean([r["delta"]["hd95_proxy"] for r in group])}

source_paths = [BASE / "per_slice.csv", BASE / "per_patient.csv",
                CANDIDATE / "per_slice.csv", CANDIDATE / "per_patient.csv", GEOMETRY]
result = {
    "scope": "historical_fastmri_validation_only",
    "models": ["old_data_control", "old_data_orientation_stopped_branch"],
    "key": list(key_names), "patient_equal_aggregation_verified": True,
    "slices": len(rows), "patients": len({r["patient_id"] for r in rows}),
    "limitations": [
        "Both checkpoints were selected using this historical validation cohort.",
        "Leave-one-patient-out rules only exclude a patient's labels when fitting this simple rule; they do not make the full model pipeline out of fold.",
        "Oracle policies use the target and cannot be deployed.",
        "Per-slice metric selection is not the metric of a spatial blend or patchwise correction.",
        "HD95 and Dice are intensity-threshold proxies, not anatomical segmentation outcomes.",
        "This comparison does not reopen the stopped orientation branch or enter test data."
    ],
    "sources": [{"path": str(path.relative_to(ROOT)).replace("\\", "/"),
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in source_paths],
    "phase": {phase: group_summary([r for r in rows if r["phase"] == phase])
              for phase in ("0.25", "0.5", "0.75")},
    "gap_band": {band: group_summary([r for r in rows if r["gap_band"] == band])
                 for band in ("at_most_16mm", "16_to_22mm", "above_22mm")
                 if any(r["gap_band"] == band for r in rows)},
    "policies": {name: policy_summary(rows, selected) for name, selected in policies.items()},
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"patients": result["patients"], "slices": result["slices"],
                  "phase": result["phase"], "gap_band": result["gap_band"],
                  "policies": {k: {"selected_slices": v["selected_slices"],
                                   "psnr_change_db": v["mean_change_vs_control"]["psnr"],
                                   "hd95_change": v["mean_change_vs_control"]["hd95_proxy"]}
                               for k, v in result["policies"].items()}},
                 ensure_ascii=False, indent=2))
