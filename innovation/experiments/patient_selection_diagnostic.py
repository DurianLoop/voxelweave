"""Read existing development metrics; no inference, training, or test access."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRICS = ("psnr", "ssim", "mae", "mse", "ncc", "dice_proxy", "hd95_proxy", "tail10_mse")
base_path = ROOT / "design/pastnet_v2/runs/full_control_seed3407_vram20/validation/per_patient.csv"
candidate_path = ROOT / "design/pastnet_orientation/runs/full_orientation_seed3407_vram20/validation/per_patient.csv"

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {r["patient_id"]: {k: float(r[k]) for k in METRICS} for r in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate patient IDs")
    return result

base, candidate = read(base_path), read(candidate_path)
if set(base) != set(candidate):
    raise ValueError("Patient sets differ")
ids = sorted(base)
delta = {p: {k: candidate[p][k] - base[p][k] for k in METRICS} for p in ids}
policies = {
    "always_candidate": lambda d: True,
    "oracle_psnr": lambda d: d["psnr"] > 0,
    "oracle_psnr_and_mae": lambda d: d["psnr"] > 0 and d["mae"] <= 0,
    "oracle_psnr_mae_ssim_hd95": lambda d: d["psnr"] > 0 and d["mae"] <= 0 and d["ssim"] >= 0 and d["hd95_proxy"] <= 0,
}
summary = []
for name, select in policies.items():
    selected = [p for p in ids if select(delta[p])]
    summary.append({
        "policy": name,
        "selected_patients": len(selected),
        "total_patients": len(ids),
        "mean_change_vs_base": {k: sum(delta[p][k] for p in selected) / len(ids) for k in METRICS},
    })

record = {
    "date": "2026-09-30",
    "status": "historical_development_diagnostic_not_deployable",
    "selection_unit": "entire_patient",
    "notes": [
        "Oracle policies use target-derived metrics and are unavailable at deployment.",
        "The two existing models share the old-data evaluation contract; repaired-data results are not mixed in.",
        "Per-patient guardrails are stricter than original cohort-average guardrails.",
        "This is not an upper bound for patch selection, blending, retraining, or MRI reconstruction.",
        "No independence claim: these 23 validation patients have been used repeatedly during development.",
        "The stopped orientation branch remains stopped; no new model or checkpoint was selected.",
    ],
    "sources": [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (base_path, candidate_path)],
    "summary": summary,
}
dest = ROOT / "innovation/experiments/patient_selection_diagnostic.json"
dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, ensure_ascii=False, indent=2))
