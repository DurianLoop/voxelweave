"""Read-only audit of the position-channel pilot's stored metrics and cohort."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2] / "innovation"
OUT = ROOT / "experiments/position_channel_only_pilot"
FIELDS = ("shared_o", "map_only_o", "disjoint_o", "delta_map_o", "delta_full_o",
          "shared_b_mae", "map_only_b_mae", "disjoint_b_mae")
EXPECTED = {"msvalid": ("P1", "P2", "P3"),
            "remind": ("ReMIND-003", "ReMIND-007", "ReMIND-009")}


def read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def near(actual: float, expected: float, label: str) -> None:
    if not np.isclose(actual, expected, rtol=0, atol=1e-8):
        raise AssertionError(f"{label}: {actual} != {expected}")


def main() -> None:
    targets = read(OUT / "per_target.csv")
    patients = read(OUT / "per_patient.csv")
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    assert summary["plan_sha256"] == sha256(ROOT / "POSITION_CHANNEL_ONLY_PILOT_PLAN_2026-10-01.md")
    assert summary["script_sha256"] == sha256(ROOT / "experiments/position_channel_only_pilot.py")
    assert not summary["failures"] and len(patients) == 6 and len(targets) == 35
    grouped = defaultdict(list)
    for row in targets:
        source, patient, z, residue = row["source"], row["patient"], int(row["z"]), int(row["residue"])
        assert patient in EXPECTED[source] and residue in (1, 3)
        assert (float(row["rel0"]), float(row["rel2"])) in ((.25, .75), (.75, .25))
        near(float(row["delta_map_o"]), float(row["map_only_o"])-float(row["shared_o"]), "map difference")
        near(float(row["delta_full_o"]), float(row["disjoint_o"])-float(row["shared_o"]), "full difference")
        near(float(row["absolute_delta_ratio"]),
             abs(float(row["delta_map_o"]))/abs(float(row["delta_full_o"])), "ratio")
        grouped[(source, patient)].append(row)
    assert len({(r["source"], r["patient"], int(r["z"])) for r in targets}) == len(targets)
    for source, names in EXPECTED.items():
        original = read(ROOT / "experiments" /
                        ("msvalid_ixi_weights_secondary" if source == "msvalid"
                         else "remind_native_t2_ixi_pair") / "per_target.csv")
        old = {(r["patient"], int(r["z"])): r for r in original}
        for row in [r for r in targets if r["source"] == source]:
            prior = old[(row["patient"], int(row["z"]))]
            near(float(row["shared_o"]), float(prior["shared_observable"]), "frozen shared")
            near(float(row["disjoint_o"]), float(prior["disjoint_observable"]), "frozen disjoint")
            assert int(row["support_pixels"]) == int(prior["support_pixels"])
        group = [p for p in patients if p["source"] == source]
        assert tuple(p["patient"] for p in group) == names
        assert summary["sources"][source]["patients_scored"] == 3
        assert summary["sources"][source]["targets_scored"] == sum(len(grouped[(source, n)]) for n in names)
        for patient in group:
            rows = grouped[(source, patient["patient"])]
            assert len(rows) == int(patient["targets"])
            for field in FIELDS:
                equal_residue = np.mean([np.mean([float(r[field]) for r in rows
                                                   if int(r["residue"]) == residue])
                                         for residue in (1, 3)])
                near(float(patient[field]), float(equal_residue), f"{patient['patient']} {field}")
        for field in FIELDS:
            near(float(summary["sources"][source][f"mean_{field}"]),
                 float(np.mean([float(p[field]) for p in group])), f"{source} {field}")
    print("PASS: 35 unique targets, six frozen patients, original controls and equal-residue aggregates")


if __name__ == "__main__":
    main()
