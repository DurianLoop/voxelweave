"""Outcome-blind integrity gate for the five P25-P84 influence batches."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
EXTRACTION = ROOT / "literature/msvalid_extraction_manifest.json"
OUT = EXPERIMENTS / "msvalid_influence_p25_p84_integrity"
STARTS = (25, 37, 49, 61, 73)


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    source = json.loads(EXTRACTION.read_text(encoding="utf-8"))
    extracted = {item["patient"]: item for item in source["records"]}
    batches = []
    configurations = []
    for start in STARTS:
        directory = EXPERIMENTS / f"msvalid_influence_remaining_p{start}_p{start + 11}"
        csv_path, summary_path = directory / "per_context.csv", directory / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        frame = pd.read_csv(csv_path)
        expected = [f"P{i}" for i in range(start, start + 12)]
        groups = frame.groupby(["patient", "z"])
        if (summary["patient_ids"] != expected or summary["start_patient"] != start or
                summary["target_mode"] != "median-per-residue" or
                summary["patients"] != 12 or summary["targets"] != 24 or
                summary["contexts"] != 216 or summary["fields"] != 4 or
                summary["epsilon"] != .01 or
                set(frame.patient) != set(expected) or len(frame) != 216 or
                groups.ngroups != 24 or not groups.size().eq(9).all() or
                not np.isfinite(frame.select_dtypes(include="number").to_numpy()).all()):
            raise AssertionError(f"Batch sample mismatch: {directory}")
        overlaps = frame.groupby(["patient", "z", "shared_anchor_count"]).size().unstack()
        if not (overlaps.to_numpy() == [4, 4, 1]).all():
            raise AssertionError(f"Batch overlap mismatch: {directory}")
        residues = groups.residue.first().groupby(level="patient").apply(lambda x: tuple(sorted(x)))
        if not residues.map(lambda pair: pair == (1, 3)).all():
            raise AssertionError(f"Residue pair mismatch: {directory}")
        configurations.append((summary["plan_sha256"], summary["script_sha256"],
                               summary["qualification_sha256"], summary["checkpoint_sha256"]))
        batches.append({"patients": expected, "targets": groups.ngroups, "contexts": len(frame),
                        "per_context_csv_sha256": sha256(csv_path),
                        "summary_sha256": sha256(summary_path)})
    if not all(item == configurations[0] for item in configurations):
        raise AssertionError("Batch protocol, code, qualification or checkpoint hash changed")
    volumes = []
    for patient_number in range(25, 85):
        patient = f"P{patient_number}"
        record = extracted[patient]
        path = ROOT / record["path"]
        actual = sha256(path)
        if actual != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise AssertionError(f"Extracted NIfTI changed: {patient}")
        volumes.append({"patient": patient, "sha256": actual})
    result = {"status": "PASS; outcome-blind integrity check only",
              "extraction_manifest_sha256": sha256(EXTRACTION),
              "script_sha256": sha256(Path(__file__)),
              "matching_plan_script_qualification_checkpoints": True,
              "patients": 60, "targets": 120, "contexts": 1080,
              "volumes_sha256_verified": len(volumes),
              "batches": batches,
              "volume_hashes": volumes}
    OUT.mkdir(parents=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in
                      ("status", "patients", "targets", "contexts", "volumes_sha256_verified")},
                     indent=2), flush=True)


if __name__ == "__main__":
    main()
