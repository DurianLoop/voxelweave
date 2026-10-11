"""Frozen, nonpixel screen of all manifest cases with multiple T2 series."""
from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import pydicom

from fastmri_repeat_t2_header_gate import compare, describe_series, sha256


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "innovation/FASTMRI_ALL_T2_HEADER_GATE_PLAN_2026-10-01.md"
MANIFEST = ROOT / "dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_series_manifest.csv"
MANIFEST_SHA = "042730d2802b4b01326d6f297e6bd46e76d5a56d7b044fe60c87d8ccf41c5c2d"
DATA_ROOT = (ROOT / "dataset/fastMRI_brain_DICOM").resolve()
OUT = ROOT / "innovation/experiments/fastmri_all_t2_header_gate"
TECHNICAL_REASONS_EXCLUDED = {"time_missing", "series_time_not_distinct"}


def selected_cases() -> list[str]:
    if sha256(MANIFEST) != MANIFEST_SHA:
        raise ValueError("T2 manifest hash changed")
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    counts = Counter(row["case_id"] for row in rows if row["is_t2"].lower() == "true")
    chosen = sorted(case_id for case_id, count in counts.items() if count >= 2)
    if len(chosen) != 61 or sum(counts[case_id] for case_id in chosen) != 138:
        raise ValueError("Frozen multi-T2 selection changed")
    return chosen


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite existing header screen")
    case_rows = []
    pair_rows = []
    total_files = 0
    for ordinal, case_id in enumerate(selected_cases(), 1):
        case_dir = (DATA_ROOT / case_id).resolve()
        if case_dir.parent != DATA_ROOT or not case_dir.is_dir():
            raise ValueError("Selected case directory missing or outside expected source")
        files = sorted(case_dir.glob("*.dcm"))
        if not files or any(path.parent != case_dir for path in files):
            raise ValueError("Selected case has missing or invalid DICOM files")
        total_files += len(files)
        groups = defaultdict(list)
        for path in files:
            ds = pydicom.dcmread(str(path), stop_before_pixels=True)
            uid = str(getattr(ds, "SeriesInstanceUID", ""))
            if not uid:
                raise ValueError("Missing SeriesInstanceUID")
            groups[uid].append(ds)
        descriptions = [describe_series(groups[uid]) for uid in sorted(groups)]
        label = f"candidate_{ordinal:02d}"
        case_rows.append({
            "candidate": label,
            "dicom_headers": len(files),
            "series": len(descriptions),
            "t2_labeled_series": sum(item["t2_label"] for item in descriptions),
            "repeat_labeled_series": sum(item["repeat_label"] for item in descriptions),
        })
        for (i, left), (j, right) in itertools.combinations(enumerate(descriptions, 1), 2):
            if not (left["t2_label"] and right["t2_label"]):
                continue
            result = compare(left, right)
            technical_reasons = [reason for reason in result["reasons"]
                                 if reason not in TECHNICAL_REASONS_EXCLUDED]
            centers_match = (left["distinct_positions"] and right["distinct_positions"]
                             and result["max_slice_center_difference_mm"] is not None
                             and result["max_slice_center_difference_mm"] <= 0.1)
            pair_rows.append({
                "candidate": label,
                "series_a": i,
                "series_b": j,
                "one_repeat_labeled": left["repeat_label"] or right["repeat_label"],
                "centers_match": centers_match,
                "technical_match": not technical_reasons,
                "timing_evidence": result["series_time_difference_seconds"] is not None
                                   and result["series_time_difference_seconds"] >= 1,
                "header_traceback_candidate": result["header_compatible"],
                "max_slice_center_difference_mm": result["max_slice_center_difference_mm"],
                "series_time_difference_seconds": result["series_time_difference_seconds"],
                "technical_failure_reasons": technical_reasons,
                "timing_failure_reasons": [reason for reason in result["reasons"]
                                           if reason in TECHNICAL_REASONS_EXCLUDED],
            })
    if total_files != 2944:
        raise ValueError("Frozen DICOM file count changed")
    reason_counts = Counter(reason for row in pair_rows
                            for reason in row["technical_failure_reasons"] + row["timing_failure_reasons"])
    summary = {
        "status": "local nonpixel feasibility; release rights and independent acquisition unverified",
        "plan_sha256": sha256(PLAN),
        "script_sha256": sha256(Path(__file__)),
        "helper_script_sha256": sha256(ROOT / "innovation/experiments/fastmri_repeat_t2_header_gate.py"),
        "manifest_sha256": MANIFEST_SHA,
        "cases": len(case_rows),
        "dicom_headers_read": total_files,
        "series": sum(row["series"] for row in case_rows),
        "t2_pairs": len(pair_rows),
        "center_matched_pairs": sum(row["centers_match"] for row in pair_rows),
        "technical_matched_pairs": sum(row["technical_match"] for row in pair_rows),
        "technical_and_time_candidates": sum(row["header_traceback_candidate"] for row in pair_rows),
        "independent_acquisition_proven_pairs": 0,
        "failure_reason_counts": dict(sorted(reason_counts.items())),
        "case_rows": case_rows,
        "pair_rows": pair_rows,
    }
    OUT.mkdir(parents=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "cases", "dicom_headers_read", "series", "t2_pairs", "center_matched_pairs",
        "technical_matched_pairs", "technical_and_time_candidates", "independent_acquisition_proven_pairs")}, indent=2))


if __name__ == "__main__":
    main()
