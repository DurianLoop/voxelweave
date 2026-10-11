"""Audit frozen x4 target feasibility from cached RTSTRUCTs, without MR pixels."""

from __future__ import annotations

import io
import json
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "literature/source_cache/vs_seg_rtstruct_labels_2026-10-01"
COHORT = ROOT / "literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json"
OUT = ROOT / "experiments/vs_seg_nonpixel_target_upper_bound_2026-10-01.json"


def first_dataset(path: Path):
    with zipfile.ZipFile(path) as archive:
        members = [x for x in archive.infolist() if x.filename.lower().endswith(".dcm")]
        if len(members) != 1:
            raise ValueError(f"Expected one RTSTRUCT DICOM: {path}")
        return pydicom.dcmread(io.BytesIO(archive.read(members[0])))


def refs(roi):
    return [str(c.ContourImageSequence[0].ReferencedSOPInstanceUID)
            for c in roi.ContourSequence if len(c.get("ContourImageSequence", [])) == 1]


def main() -> None:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    image_counts = {x["patient"]: x["image_count"] for x in cohort["t2_series"]}
    cases = []
    for record_path in sorted(AUDIT.glob("VS-SEG-*.json")):
        rec = json.loads(record_path.read_text(encoding="utf-8"))
        patient = rec["patient"]
        row = {"patient": patient, "first_roi": rec["rois"][0]["name"],
               "first_contours": rec["rois"][0]["contours"],
               "image_count": image_counts.get(patient), "qualification": None}
        if patient not in image_counts:
            row["qualification"] = "not_in_nbia_t2_list"
            cases.append(row)
            continue
        if row["first_roi"] == "Men":
            row["qualification"] = "men_label_excluded_from_vs_claim"
            cases.append(row)
            continue
        src = ROOT / rec["source_path"]
        ds = first_dataset(src)
        names = {int(x.ROINumber): str(x.ROIName) for x in ds.StructureSetROISequence}
        contours = {names[int(x.ReferencedROINumber)]: x for x in ds.ROIContourSequence}
        tumor = contours[row["first_roi"]]
        skull = contours["*Skull"]
        skull_refs = refs(skull)
        tumor_refs = refs(tumor)
        row["skull_refs"] = len(skull_refs)
        row["unique_skull_refs"] = len(set(skull_refs))
        row["unique_tumor_refs"] = len(set(tumor_refs))
        if len(tumor_refs) != len(tumor.ContourSequence):
            row["qualification"] = "tumor_contour_without_single_reference"
            cases.append(row)
            continue
        points = np.asarray(skull.ContourSequence[0].ContourData, dtype=np.float64).reshape(-1, 3)
        _, _, v = np.linalg.svd(points - points.mean(0), full_matrices=False)
        normal = v[-1]
        planes = {}
        for contour, uid in zip(skull.ContourSequence, skull_refs):
            pts = np.asarray(contour.ContourData, dtype=np.float64).reshape(-1, 3)
            projections = pts @ normal
            if uid in planes and abs(planes[uid][0] - float(np.mean(projections))) > .001:
                raise ValueError(f"Duplicate skull SOP has different planes: {patient}")
            planes[uid] = (float(np.mean(projections)), float(np.ptp(projections)))
        positions = sorted(x[0] for x in planes.values())
        step = np.diff(positions)
        if len(step) < 2 or step.min() <= 0:
            row["qualification"] = "skull_planes_unusable"
            cases.append(row)
            continue
        nominal_step = float(np.median(step))
        row["skull_plane_max_spread_mm"] = max(x[1] for x in planes.values())
        row["skull_plane_step_min_mm"] = float(step.min())
        row["skull_plane_step_max_mm"] = float(step.max())
        row["incomplete_or_duplicate_skull_reference"] = (len(skull_refs) != image_counts[patient]
                                                        or len(set(skull_refs)) != len(skull_refs))
        rel_indices = []
        max_plane_error = 0.0
        for contour, uid in zip(tumor.ContourSequence, tumor_refs):
            pts = np.asarray(contour.ContourData, dtype=np.float64).reshape(-1, 3)
            position = planes[uid][0] if uid in planes else float(np.mean(pts @ normal))
            coordinate = (position - positions[0]) / nominal_step
            index = int(round(coordinate))
            max_plane_error = max(max_plane_error, abs(coordinate - index) * nominal_step)
            rel_indices.append(index)
        row["tumor_plane_grid_max_error_mm"] = max_plane_error
        if max_plane_error > .001 or row["skull_plane_max_spread_mm"] > .001:
            row["qualification"] = "contour_plane_grid_unusable"
            cases.append(row)
            continue
        n = image_counts[patient]
        max_rel = max(max(rel_indices), int(round((positions[-1] - positions[0]) / nominal_step)))
        if max_rel >= n:
            row["qualification"] = "skull_span_exceeds_nbia_count"
            cases.append(row)
            continue
        phase_counts = []
        for direction in (1, -1):
            for shift in range(n - max_rel):
                indices = {shift + x if direction == 1 else n - 1 - shift - x for x in rel_indices}
                for phase in range(4):
                    anchors = list(range(phase, n, 4))
                    eligible = {1: 0, 3: 0}
                    for i in range(1, len(anchors) - 2):
                        for residue in (1, 3):
                            z = anchors[i] + residue
                            if z < n and z in indices:
                                eligible[residue] += 1
                    phase_counts.append({"direction": direction, "shift": shift, "phase": phase,
                                         "residue_1": eligible[1], "residue_3": eligible[3],
                                         "could_pass_ignoring_pixels": min(eligible.values()) >= 3})
        row["phase_counts"] = phase_counts
        row["could_pass_any_phase_ignoring_pixels"] = any(x["could_pass_ignoring_pixels"] for x in phase_counts)
        row["qualification"] = "nonpixel_audited"
        cases.append(row)
    summary = {"mapped": len(cases), "nbia_t2": len(image_counts),
               "qualification_counts": dict(Counter(x["qualification"] for x in cases)),
               "could_pass_any_phase_ignoring_pixels": sum(x.get("could_pass_any_phase_ignoring_pixels", False) for x in cases),
               "incomplete_or_duplicate_skull_reference": sum(x.get("incomplete_or_duplicate_skull_reference", False) for x in cases),
               "cannot_pass_any_phase_ignoring_pixels": sum(x.get("qualification") == "nonpixel_audited" and not x["could_pass_any_phase_ignoring_pixels"] for x in cases),
               "patient_pixels_read": False,
               "interpretation": "Upper bound only: all four possible phases, both slice directions and plausible missing-edge shifts; no 64-pixel, support, DICOM orientation, or geometry gate."}
    OUT.write_text(json.dumps({"summary": summary, "cases": cases}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
