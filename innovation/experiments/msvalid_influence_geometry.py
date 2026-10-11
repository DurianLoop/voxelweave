"""Read-only qualification-metadata check for the proposed influence contexts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "innovation"
SOURCE = ROOT / "literature/msvalid_geometry_qualification.json"
OUT = ROOT / "experiments/msvalid_influence_geometry.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    patients = json.loads(SOURCE.read_text(encoding="utf-8"))["patients"]
    summary = {"status": "metadata-only feasibility; no target pixels or model outputs read",
               "qualification_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "patients_total": len(patients), "patients_both_residues": 0,
               "targets_total": 0, "targets_full_six_pool": 0,
               "fixed_reference_one_overlap_pairs": 0,
               "fixed_reference_zero_overlap_pairs": 0,
               "fixed_reference_two_overlap_pairs": 0,
               "failures": []}
    offsets = (-3, -2, -1, 1, 2, 3)
    for patient in patients:
        depth = patient["shape"][2]
        residues = patient["eligible_targets"]
        if all(residues[f"residue_{r}"] for r in (1, 3)):
            summary["patients_both_residues"] += 1
        for residue in (1, 3):
            for z in residues[f"residue_{residue}"]:
                summary["targets_total"] += 1
                if any(z + offset < 0 or z + offset >= depth for offset in offsets):
                    summary["failures"].append({"patient": patient["patient"], "z": z,
                                                "reason": "six_neighbor_pool_outside_volume"})
                    continue
                reference = {4 * (z // 4), 4 * (z // 4) + 4}
                candidates = [{z + left, z + right}
                              for left in (-3, -2, -1) for right in (1, 2, 3)]
                counts = {k: sum(len(reference & candidate) == k
                                 for candidate in candidates) for k in (0, 1, 2)}
                if counts != {0: 4, 1: 4, 2: 1}:
                    summary["failures"].append({"patient": patient["patient"], "z": z,
                                                "reason": "unexpected_overlap_counts", "counts": counts})
                    continue
                summary["targets_full_six_pool"] += 1
                for overlap, key in ((0, "fixed_reference_zero_overlap_pairs"),
                                     (1, "fixed_reference_one_overlap_pairs"),
                                     (2, "fixed_reference_two_overlap_pairs")):
                    summary[key] += counts[overlap]
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["failures"] or summary["patients_both_residues"] != 84 or summary["targets_full_six_pool"] != 479:
        raise RuntimeError("Influence geometry feasibility failed")


if __name__ == "__main__":
    main()
