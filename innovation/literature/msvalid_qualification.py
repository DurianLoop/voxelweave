"""Freeze outcome-blind MSValid first-T2 geometry eligibility."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HEADERS = ROOT / "msvalid_header_all.json"
INDEX = ROOT / "msvalid_remote_inventory.json"
OUT = ROOT / "msvalid_geometry_qualification.json"


def eligible_targets(depth: int) -> dict[str, list[int]]:
    anchors = {phase: list(range(phase, depth, 4)) for phase in (0, 2)}
    eligible = {"residue_1": [], "residue_3": []}
    for z in range(depth):
        if z % 4 not in (1, 3):
            continue
        if all(sum(a < z for a in anchors[phase]) >= 2
               and sum(a > z for a in anchors[phase]) >= 2 for phase in (0, 2)):
            eligible[f"residue_{z % 4}"].append(z)
    return eligible


def main() -> None:
    headers = json.loads(HEADERS.read_text(encoding="utf-8"))
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    members = {entry["path"]: entry for entry in index["members"]}
    patients = []
    for entry in headers["samples"]:
        reasons = []
        if "error" in entry:
            reasons.append("header_unavailable")
        else:
            shape, zooms = entry["shape"], entry["zooms_mm"]
            if len(shape) != 3 or len(zooms) < 3:
                reasons.append("not_3d")
            if any(s <= 0 for s in zooms[:3]):
                reasons.append("invalid_voxel_spacing")
            if entry["sform_code"] <= 0 and entry["qform_code"] <= 0:
                reasons.append("missing_world_affine")
            targets = eligible_targets(shape[2]) if len(shape) == 3 else {}
            if not targets or any(not positions for positions in targets.values()):
                reasons.append("no_two_residues_with_four_real_anchors_per_phase")
        member = members.get(entry["member"])
        if member is None:
            reasons.append("archive_member_missing")
        patients.append({**entry, "eligible_targets": targets if "error" not in entry else {},
                         "zip_crc32": member["crc32"] if member else None,
                         "zip_compressed_bytes": member["compressed_bytes"] if member else None,
                         "geometry_eligible": not reasons, "exclusion_reasons": reasons})
    selected = [item for item in patients if item["geometry_eligible"]]
    if len({item["patient"] for item in patients}) != len(patients):
        raise AssertionError("Patient IDs are not unique")
    result = {
        "source_record": "https://zenodo.org/records/10875606",
        "license_from_record": "CC BY 4.0",
        "selection": "lexicographically first T2 NIfTI member for each P1..P84; no target pixels examined",
        "geometry_rule": "3D positive spacing, world affine, and at least one residue-1 and residue-3 target with two genuine acquired anchors below and above in both phase-0 and phase-2 x4 grids",
        "header_inventory_sha256": hashlib.sha256(HEADERS.read_bytes()).hexdigest(),
        "remote_zip_inventory_sha256": hashlib.sha256(INDEX.read_bytes()).hexdigest(),
        "patients_total": len(patients),
        "patients_geometry_eligible": len(selected),
        "selected_zip_compressed_bytes": sum(item["zip_compressed_bytes"] for item in selected),
        "native_depth_counts": dict(sorted(Counter(str(item["shape"][2]) for item in patients
                                                if "shape" in item).items(), key=lambda x: int(x[0]))),
        "native_z_spacing_mm_counts": dict(sorted(Counter(str(round(item["zooms_mm"][2], 3))
                                                      for item in patients if "zooms_mm" in item).items(),
                                                  key=lambda x: float(x[0]))),
        "patients": patients,
        "remaining_checks": ["Image finiteness, intensity range and gzip integrity after extraction.",
                             "Cross-dataset patient identity cannot be proved solely by local pseudonymous IDs.",
                             "Native 3-6 mm target layers test x4 subsampling of native scans, not true thin-slice deconvolution."],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "patients"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
