"""Descriptive observable correction energy versus target-assisted action benefit."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/vs_seg_001_local_action_oracle"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc_scalar(scores, labels):
    positive = sum(labels)
    negative = len(labels)-positive
    if not positive or not negative:
        return None
    ordered = sorted(zip(scores, labels))
    credit, negatives_below, i = 0., 0, 0
    while i < len(ordered):
        j = i+1
        while j < len(ordered) and ordered[j][0] == ordered[i][0]:
            j += 1
        pos = sum(label for _, label in ordered[i:j])
        neg = j-i-pos
        credit += pos*(negatives_below+.5*neg)
        negatives_below += neg
        i = j
    return credit/(positive*negative)


def main():
    source_path, proof_path = OUT / "attempt_01.json", OUT / "independent_verification.json"
    result, proof = json.loads(source_path.read_text()), json.loads(proof_path.read_text())
    if not result["complete"] or not proof["complete"] or proof["errors"] or proof["result_sha256"] != sha(source_path):
        raise ValueError("Oracle output has no matching independent proof")
    table = ROOT / result["tile_stats_file"]
    if sha(table) != result["tile_stats_sha256"]:
        raise ValueError("Tile table changed")
    assert auc_scalar([0., 1., 1., 2.], [False, True, False, True]) == .875
    assert auc_scalar([1., 1.], [False, True]) == .5
    groups = defaultdict(list)
    with table.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = (row["action_base"], int(row["size"]))
            n = int(row["support_pixels"])
            energy, gain = float(row["d"])/n, float(row["candidate_gain"])/n
            if not math.isfinite(energy) or not math.isfinite(gain):
                raise ValueError("Nonfinite diagnostic data")
            groups[key].append((energy, gain, float(row["alpha"])))
    entries = []
    for (base, size), values in sorted(groups.items()):
        nongzero = [(d, gain) for d, gain, _ in values if gain != 0]
        scores, labels = [x[0] for x in nongzero], [x[1] > 0 for x in nongzero]
        auc = auc_scalar(scores, labels)
        positive = sum(labels)
        entries.append({"base": base, "size_pixels": size, "tile_count": len(values), "nonzero_candidate_gain_tiles": len(labels),
                        "candidate_improves_support_sse_tiles": positive, "candidate_worsens_support_sse_tiles": len(labels)-positive,
                        "candidate_improves_support_sse_fraction": positive/len(labels),
                        "auc_larger_observable_energy_for_candidate_benefit": auc,
                        "auc_larger_observable_energy_for_candidate_harm": 1-auc if auc is not None else None,
                        "true_target_assisted_oracle_stops_at_base_tiles": sum(a == 0 for _, _, a in values),
                        "fraction_action_norm_does_not_determine_direction": "AUC is descriptive on one reused patient; no deployment calibration or patient generalization"})
    report = {"script_sha256": sha(Path(__file__)), "oracle_result_sha256": sha(source_path), "oracle_proof_sha256": sha(proof_path),
              "entries": entries, "patient_count": 1, "target_images_used_for_gain_labels": True,
              "features_use_only_fixed_base_and_candidate": True, "new_head_trained": False, "inferential_statistics": False,
              "gpu_used": False, "publication_claim": False}
    (OUT / "observable_energy_diagnostic.json").write_text(json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
