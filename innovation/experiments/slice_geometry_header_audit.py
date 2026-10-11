"""CPU-only DICOM-header audit on existing fastMRI train/validation records.

Reads no pixel data or test records. DICOM SliceThickness is a nominal field,
not a measured slice-selection point-spread function.
"""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pydicom

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from processing.fastmri_brain_t2_prepare import infer_series_label

MANIFEST = ROOT / "design/pastnet_v2/manifests/fastmri/fold_00.json"
SOURCE = ROOT / "dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_nifti_manifest.csv"
OUT = ROOT / "innovation/experiments/slice_geometry_header_audit.json"

records = json.loads(MANIFEST.read_text(encoding="utf-8"))["records"]
with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
    source_rows = {row["case_id"]: row for row in csv.DictReader(stream)}

by_split: dict[str, list[dict]] = defaultdict(list)
issues = Counter()
for record in records:
    if record["split"] not in ("train", "val"):
        continue
    source_row = source_rows.get(record["case_id"])
    if source_row is None:
        issues["missing_source_mapping"] += 1
        continue
    directory = ROOT / "dataset/fastMRI_brain_DICOM" / source_row["source_case_id"]
    candidates = sorted(p for p in directory.glob("*.dcm")
                        if infer_series_label(p) == source_row["series_label"])
    if not candidates:
        issues["missing_matching_dicom"] += 1
        continue
    headers = [pydicom.dcmread(str(p), stop_before_pixels=True, force=True)
               for p in candidates]
    headers.sort(key=lambda ds: int(getattr(ds, "InstanceNumber", 0)))
    thickness = [float(ds.SliceThickness) if "SliceThickness" in ds else None
                 for ds in headers]
    between = [float(ds.SpacingBetweenSlices) if "SpacingBetweenSlices" in ds else None
               for ds in headers]
    if len(set(thickness)) > 1:
        issues["inconsistent_slice_thickness_across_series"] += 1
    if len(set(between)) > 1:
        issues["inconsistent_spacing_between_slices_across_series"] += 1
    geometry = record.get("geometry", {})
    spacing = geometry.get("spacing", [None, None, None])[2]
    by_split[record["split"]].append({
        "thickness_mm": thickness[0],
        "between_tag_mm": between[0],
        "position_spacing_mm": spacing if geometry.get("spacing_known") else None,
        "dicom_headers_in_series": len(candidates),
    })


def summarize(rows: list[dict]) -> dict:
    t = [r["thickness_mm"] for r in rows if r["thickness_mm"] is not None]
    b = [r["between_tag_mm"] for r in rows if r["between_tag_mm"] is not None]
    s = [r["position_spacing_mm"] for r in rows if r["position_spacing_mm"] is not None]
    pairs = [(r["thickness_mm"], r["position_spacing_mm"]) for r in rows
             if r["thickness_mm"] is not None and r["position_spacing_mm"] is not None]
    return {
        "series": len(rows), "thickness_tag_present": len(t),
        "between_tag_present": len(b), "verified_position_spacing_present": len(s),
        "thickness_unique_rounded_mm": dict(sorted(Counter(round(v, 3) for v in t).items())),
        "between_unique_rounded_mm": dict(sorted(Counter(round(v, 3) for v in b).items())),
        "thickness_median_mm": statistics.median(t) if t else None,
        "position_spacing_median_mm": statistics.median(s) if s else None,
        "thickness_minus_position_spacing_median_mm": statistics.median(a - z for a, z in pairs) if pairs else None,
        "absolute_difference_over_0_1mm": sum(abs(a - z) > 0.1 for a, z in pairs),
        "paired_tag_and_verified_spacing": len(pairs),
    }


result = {
    "scope": "fastmri_original_train_and_clean_validation_manifest_only",
    "input_source": [
        {"path": str(p.relative_to(ROOT)).replace("\\", "/"),
         "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in (MANIFEST, SOURCE)
    ],
    "limitations": [
        "DICOM SliceThickness is nominal; it does not identify the full slice response or pulse sequence.",
        "Position-derived slice-center spacing is not the same physical quantity as thickness.",
        "All matching series headers are checked for tag consistency; no pixel or test data are read.",
        "Original training series includes the historical mixed-series issue; this audit does not modify repaired training data."
    ],
    "by_split": {split: summarize(rows) for split, rows in sorted(by_split.items())},
    "issues": dict(issues),
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"by_split": result["by_split"], "issues": result["issues"]},
                 ensure_ascii=False, indent=2))
