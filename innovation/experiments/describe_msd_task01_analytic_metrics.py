"""Descriptive paired-error components for the complete analytic control."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments/msd_task01_analytic_context_control"
OUT = RUN / "metrics_descriptive.json"


def mean_case(rows: list[dict], region: str, condition: str, field: str) -> float:
    return float(np.mean([np.mean([row[region][condition][field] for row in rows
                                   if row["residue"] == residue])
                          for residue in (1, 3)]))


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite analytic metric description")
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
    cases = [json.loads(path.read_text(encoding="utf-8"))
             for path in sorted((RUN / "cases").glob("BRATS_*.json"))]
    complete = [case for case in cases if case["complete"]]
    if len(cases) != 484 or len(complete) != summary["cases_complete"]:
        raise ValueError("Complete analytic case denominator changed")
    result = {"classification": "post-result descriptive components; patient-equal residue-balanced",
              "complete_patients": len(complete), "regions": {}}
    for region in ("lesion", "local_control"):
        metrics = {}
        for condition in ("shared", "disjoint"):
            metrics[condition] = {
                field: float(np.mean([mean_case(case["rows"], region, condition, field)
                                      for case in complete]))
                for field in ("a_mse", "b_mse", "paired_mse", "disagreement_mse", "observable")}
        result["regions"][region] = metrics
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
