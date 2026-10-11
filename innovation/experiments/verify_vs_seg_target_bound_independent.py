"""Independent, looser count bound from axial RTSTRUCT planes; never reads MR."""

from __future__ import annotations

import hashlib
import io
import json
import statistics
import zipfile
from collections import Counter
from pathlib import Path

import pydicom


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "literature/source_cache/vs_seg_rtstruct_labels_2026-10-01"
OUT = ROOT / "experiments/vs_seg_target_bound_independent_2026-10-02.json"


def plane_z(contour) -> float:
    coords = list(map(float, contour.ContourData))
    z = coords[2::3]
    if max(z) - min(z) > 1e-6:
        raise ValueError("Non-axial contour: cannot use independent z-only check")
    return statistics.mean(z)


def main() -> None:
    nbia = json.loads((ROOT / "literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json").read_text())
    listed = {x["patient"] for x in nbia["t2_series"]}
    rows = []
    for path in sorted(AUDIT.glob("VS-SEG-*.json")):
        record = json.loads(path.read_text())
        row = {"patient": record["patient"], "nbia_t2_listed": record["patient"] in listed}
        try:
            source = ROOT / record["source_path"]
            raw = source.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest != record["zip_sha256"]:
                raise ValueError("Source ZIP hash differs from all-label audit")
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                files = [x for x in archive.namelist() if x.lower().endswith(".dcm")]
                if len(files) != 1:
                    raise ValueError("RTSTRUCT ZIP does not contain one DICOM")
                ds = pydicom.dcmread(io.BytesIO(archive.read(files[0])), stop_before_pixels=True)
            if str(ds.PatientID) != record["patient"]:
                raise ValueError("Patient identity differs")
            rois = list(ds.StructureSetROISequence)
            first_name = str(rois[0].ROIName)
            if first_name != record["rois"][0]["name"]:
                raise ValueError("First ROI differs from audited record")
            tumor_number = int(rois[0].ROINumber)
            skull_numbers = [int(x.ROINumber) for x in rois if str(x.ROIName) == "*Skull"]
            if len(skull_numbers) != 1:
                raise ValueError("Skull ROI not unique")
            tumor = [x for x in ds.ROIContourSequence if int(x.ReferencedROINumber) == tumor_number]
            skull = [x for x in ds.ROIContourSequence if int(x.ReferencedROINumber) == skull_numbers[0]]
            if len(tumor) != 1 or len(skull) != 1:
                raise ValueError("ROIContour identity not unique")
            skull_z = sorted({round(plane_z(c), 6) for c in skull[0].ContourSequence})
            spacing = statistics.median(b - a for a, b in zip(skull_z, skull_z[1:]))
            if not 0.999 <= spacing <= 1.501:
                raise ValueError("Cannot infer 1.0-1.5 mm RTSTRUCT plane grid")
            tumor_z = [plane_z(c) for c in tumor[0].ContourSequence]
            origin = min(tumor_z)
            indices = {round((z - origin) / spacing) for z in tumor_z}
            error = max(abs((z - origin) / spacing - round((z - origin) / spacing)) * spacing for z in tumor_z)
            if error > 1e-4:
                raise ValueError("Tumor planes are not on inferred grid")
            bins = [sum(i % 4 == k for i in indices) for k in range(4)]
            # Allow every origin/phase and both directions, ignore every edge and
            # pixel gate. This is looser than the original four-anchor contract.
            possible = min(bins[0], bins[2]) >= 3 or min(bins[1], bins[3]) >= 3
            row.update({"status": "verified", "first_roi": first_name,
                        "zip_sha256": digest, "spacing_mm": spacing,
                        "grid_error_mm": error, "unique_tumor_planes": len(indices),
                        "modulo_4_bins_from_tumor_min": bins, "possible_ignoring_all_edges_pixels": possible})
        except Exception as exc:
            row.update({"status": "unknown", "error": f"{type(exc).__name__}: {exc}"})
        rows.append(row)
    unknown = sum(r["status"] == "unknown" for r in rows)
    relaxed = sum(r.get("possible_ignoring_all_edges_pixels", False) for r in rows)
    strict = json.loads((ROOT / "experiments/vs_seg_nonpixel_target_upper_bound_2026-10-01.json").read_text())
    strict_by_id = {x["patient"]: x for x in strict["cases"]}
    incompatible = [r["patient"] for r in rows if strict_by_id[r["patient"]].get("could_pass_any_phase_ignoring_pixels", False)
                    and not r.get("possible_ignoring_all_edges_pixels", True)]
    summary = {"mapped_rtstructs": len(rows), "statuses": dict(Counter(r["status"] for r in rows)),
               "relaxed_upper_bound_all_242": relaxed + unknown,
               "relaxed_possible_nbia_241": sum(r.get("possible_ignoring_all_edges_pixels", False) for r in rows if r["nbia_t2_listed"]),
               "strict_bound_exceeds_relaxed_cases": incompatible,
               "original_minimum_100_feasible_under_relaxed_bound": relaxed + unknown >= 100,
               "patient_pixels_read": False,
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    OUT.write_text(json.dumps({"summary": summary, "cases": rows}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if unknown or incompatible:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
