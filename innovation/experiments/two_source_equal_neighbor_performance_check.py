"""Read-only join of archived MSValid/ReMIND model and linear target CSVs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments"
OUT = BASE / "two_source_equal_neighbor_performance_check"
SOURCES = {
    "msvalid": (BASE / "msvalid_ixi_weights_secondary/per_target.csv",
                BASE / "public_linear_partner_control/msvalid/per_target.csv", 479, 84),
    "remind": (BASE / "remind_native_t2_ixi_pair/per_target.csv",
               BASE / "public_linear_partner_control/remind/per_target.csv", 248, 62),
}


def read(path: Path) -> dict[tuple[str, int, int], dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    indexed = {(row["patient"], int(row["z"]), int(row["residue"])): row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError(f"Duplicate target key: {path}")
    return indexed


def balanced(rows: list[dict], field: str) -> float:
    return sum(sum(row[field] for row in rows if row["residue"] == residue) /
               sum(row["residue"] == residue for row in rows)
               for residue in (1, 3)) / 2


def main() -> None:
    summary = {"status": "post-result exploratory; acquired-foreground support only",
               "results": {}}
    per_patient = []
    for name, (model_path, linear_path, expected_targets, expected_patients) in SOURCES.items():
        models, linear = read(model_path), read(linear_path)
        if models.keys() != linear.keys() or len(models) != expected_targets:
            raise ValueError(f"Target set mismatch: {name}")
        grouped = defaultdict(list)
        for key in sorted(models):
            m, l = models[key], linear[key]
            if (m["support_pixels"] != l["support_pixels"] or
                    abs(float(m["z_spacing_mm"]) - float(l["z_spacing_mm"])) > 1e-8 or
                    abs(float(m["shared_a_mae"]) - float(l["a_mae"])) > 1e-5):
                raise ValueError(f"Source/support/HAT reference mismatch: {name} {key}")
            grouped[key[0]].append({"residue": key[2],
                                    "linear": float(l["shared_b_mse"]),
                                    "hat": float(m["shared_a_mse"]),
                                    "swinir": float(m["shared_b_mse"])})
        if len(grouped) != expected_patients:
            raise ValueError(f"Patient denominator mismatch: {name}")
        rows = []
        for patient, targets in sorted(grouped.items()):
            if {row["residue"] for row in targets} != {1, 3}:
                raise ValueError(f"Missing residue: {patient}")
            row = {"source": name, "patient": patient,
                   "targets": len(targets)}
            for method in ("linear", "hat", "swinir"):
                row[f"{method}_mse"] = balanced(targets, method)
            row["hat_minus_linear"] = row["hat_mse"] - row["linear_mse"]
            row["swinir_minus_linear"] = row["swinir_mse"] - row["linear_mse"]
            rows.append(row)
        per_patient.extend(rows)
        stats = {"patients": len(rows), "targets": len(models),
                 "patient_equal_mse": {method: sum(row[f"{method}_mse"] for row in rows) / len(rows)
                                       for method in ("linear", "hat", "swinir")}}
        for model in ("hat", "swinir"):
            values = [row[f"{model}_minus_linear"] for row in rows]
            stats[f"{model}_minus_linear"] = {
                "patient_equal_mean": sum(values) / len(values),
                "positive_patients": sum(value > 0 for value in values),
                "negative_patients": sum(value < 0 for value in values),
                "tied_patients": sum(value == 0 for value in values)}
        summary["results"][name] = stats
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "per_patient.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(per_patient[0]))
        writer.writeheader()
        writer.writerows(per_patient)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
