"""Different AUC implementation using SciPy average ranks, without significance tests."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/vs_seg_001_local_action_oracle"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    diagnostic_path = OUT / "observable_energy_diagnostic.json"
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    oracle = json.loads((OUT / "attempt_01.json").read_text(encoding="utf-8"))
    table = ROOT / oracle["tile_stats_file"]
    if sha(table) != oracle["tile_stats_sha256"]:
        raise ValueError("Saved tile table changed")
    with table.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    checked = []
    for entry in diagnostic["entries"]:
        subset = [r for r in rows if r["action_base"] == entry["base"] and int(r["size"]) == entry["size_pixels"] and float(r["candidate_gain"]) != 0]
        score = np.array([float(r["d"])/int(r["support_pixels"]) for r in subset])
        positive = np.array([float(r["candidate_gain"]) > 0 for r in subset])
        p, n = int(positive.sum()), len(positive)-int(positive.sum())
        auc = float((rankdata(score, method="average")[positive].sum()-p*(p+1)/2)/(p*n))
        if abs(auc-entry["auc_larger_observable_energy_for_candidate_benefit"]) > 1e-12:
            raise ValueError("Independent rank-sum AUC differs")
        checked.append({"base": entry["base"], "size_pixels": entry["size_pixels"], "rank_sum_auc": auc})
    report = {"complete": True, "script_sha256": sha(Path(__file__)), "diagnostic_sha256": sha(diagnostic_path),
              "tile_stats_sha256": sha(table), "checked": checked, "errors": [],
              "method": "SciPy average ranks and Mann-Whitney rank sum; no p-values or patient confidence intervals",
              "scientific_independent_confirmation": False}
    (OUT / "observable_energy_independent_rank_verification_v2.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
