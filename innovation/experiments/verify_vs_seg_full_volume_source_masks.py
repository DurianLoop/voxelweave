"""Independently verify all held-out native geometries and label-source lineage."""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pydicom

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/vs_seg_full_volume_source_masks"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    source_path = ROOT / "literature/source_cache/vs_seg_full_volume_source_gate_2026-10-02/attempt_01.json"
    source = json.loads(source_path.read_text())
    conversion_path = OUT / "attempt_01.json"
    conversion = json.loads(conversion_path.read_text())
    rows = []
    errors = []
    source_rows = {r["patient"]: r for r in source["patients"]}
    if not source["complete"] or not conversion["complete"] or [r["patient"] for r in conversion["patients"]] != source["fixed_roster"]:
        errors.append("Source/conversion completion or fixed roster differs")
    for r in conversion["patients"]:
        p = ROOT / r["input_file"]
        if sha(p) != r["input_sha256"] or sha(ROOT / r["masks_file"]) != r["masks_sha256"]:
            errors.append(r["patient"] + ": frozen conversion input/output hash differs")
        data = json.loads(p.read_text())
        with zipfile.ZipFile(ROOT / data["source_inputs"]["image_zip"]["path"]) as archive:
            headers = [pydicom.dcmread(io.BytesIO(archive.read(n)), stop_before_pixels=True) for n in archive.namelist() if n.lower().endswith(".dcm")]
        direction = np.asarray(headers[0].ImageOrientationPatient, dtype=float)
        normal = np.cross(direction[:3], direction[3:])
        headers.sort(key=lambda h: float(np.asarray(h.ImagePositionPatient, dtype=float) @ normal))
        saved = np.load(ROOT / r["masks_file"])
        affine = saved["affine_ijk_ras"]
        largest = 0.0
        for z in (0, len(headers) // 2, len(headers) - 1):
            h = headers[z]
            for row, col in ((0, 0), (11, 23), (int(h.Rows) - 1, int(h.Columns) - 1)):
                lps = np.asarray(h.ImagePositionPatient, dtype=float) + direction[:3] * col * float(h.PixelSpacing[1]) + direction[3:] * row * float(h.PixelSpacing[0])
                largest = max(largest, float(abs(lps * [-1, -1, 1] - (affine @ [col, row, z, 1])[:3]).max()))
        shape = (int(headers[0].Rows), int(headers[0].Columns), len(headers))
        if largest > 1e-6 or any(saved[k].shape != shape for k in ("original_mask_rcz", "rtstruct_mask_rcz")):
            errors.append(r["patient"] + ": native geometry differs")
        coverage = {}
        for kind in ("original_mask_rcz", "rtstruct_mask_rcz"):
            mask = saved[kind]
            counts = mask.sum(axis=(0, 1))
            # Mask-only bound: >=64 lesion pixels before intersection with any image support.
            old_candidates = {residue: [z for z in range(shape[2]) if z % 4 == residue and z // 4 >= 1 and z // 4 + 2 < len(range(0, shape[2], 4)) and counts[z] >= 64] for residue in (1, 3)}
            coverage[kind] = {"voxels": int(mask.sum()), "positive_slice_count": int(np.count_nonzero(counts)), "old_mask_only_rule_possible": all(len(old_candidates[r]) >= 3 for r in (1, 3)), "old_candidate_counts": {str(k): len(v) for k, v in old_candidates.items()}, "lesion_voxels_beyond_last_phase0_observation": int(mask[:, :, (shape[2] - 1) // 4 * 4 + 1:].sum())}
            if not mask.any():
                errors.append(r["patient"] + ": empty source lesion label")
        rows.append({"patient": r["patient"], "sequence": source_rows[r["patient"]]["sequence"], "qualified_main_ciss": source_rows[r["patient"]]["main_ciss_source_qualified"], "first_structure": data["contour_structure"], "max_coordinate_error_mm": largest, "json_vs_rtstruct_dice": r["json_vs_rtstruct_dice"], "coverage": coverage})
    main_rows = [r for r in rows if r["qualified_main_ciss"]]
    summary = {"all_source_patients": len(rows), "main_ciss_patients": len(main_rows), "sequences": dict(Counter(r["sequence"] for r in rows)), "first_structures": dict(Counter(r["first_structure"] for r in rows)), "largest_coordinate_error_mm": max(r["max_coordinate_error_mm"] for r in rows), "old_rule_mask_only_upper_bound_in_main_ciss": {kind: sum(r["coverage"][kind]["old_mask_only_rule_possible"] for r in main_rows) for kind in ("original_mask_rcz", "rtstruct_mask_rcz")}, "source_label_comparison_dice_range": [min(r["json_vs_rtstruct_dice"] for r in rows), max(r["json_vs_rtstruct_dice"] for r in rows)]}
    report = {"source_index_sha256": sha(source_path), "conversion_sha256": sha(conversion_path), "script_sha256": sha(Path(__file__)), "summary": summary, "patients": rows, "errors": errors, "task_or_reconstruction_inference": False, "independent_publication_claim": False}
    (OUT / "independent_source_geometry_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "errors": errors}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
