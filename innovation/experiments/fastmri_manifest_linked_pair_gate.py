"""Header-only pair screen for manifest-linked T2 candidate series UIDs."""
from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import pydicom

from fastmri_repeat_t2_header_gate import compare, describe_series, sha256


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "innovation/FASTMRI_MANIFEST_LINKED_PAIR_PLAN_2026-10-01.md"
MANIFEST = ROOT / "dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_series_manifest.csv"
MANIFEST_SHA = "042730d2802b4b01326d6f297e6bd46e76d5a56d7b044fe60c87d8ccf41c5c2d"
DATA_ROOT = (ROOT / "dataset/fastMRI_brain_DICOM").resolve()
CROSSWALK = ROOT / "innovation/experiments/fastmri_manifest_uid_crosswalk/summary.json"
OUT = ROOT / "innovation/experiments/fastmri_manifest_linked_pair_gate"
EXCLUDED = {"not_two_T2_labeled_series", "time_missing", "series_time_not_distinct"}
TIME_REASONS = {"time_missing", "series_time_not_distinct"}


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite manifest-linked pair result")
    if sha256(MANIFEST) != MANIFEST_SHA:
        raise ValueError("T2 manifest hash changed")
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    grouped_rows = defaultdict(list)
    for row in rows:
        if row["is_t2"].lower() == "true":
            grouped_rows[row["case_id"]].append(row)
    selected = sorted(case_id for case_id, items in grouped_rows.items() if len(items) >= 2)
    if len(selected) != 61 or sum(len(grouped_rows[x]) for x in selected) != 138:
        raise ValueError("Frozen selection changed")
    crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    pair_rows = []
    case_rows = []
    total_headers = 0
    for ordinal, case_id in enumerate(selected, 1):
        case_dir = (DATA_ROOT / case_id).resolve()
        linked_uids = set()
        for row in grouped_rows[case_id]:
            path = Path(row["first_dicom"]).resolve()
            if path.parent != case_dir or path.suffix.lower() != ".dcm" or not path.is_file():
                raise ValueError("Manifest pointer missing or outside case directory")
            ds = pydicom.dcmread(str(path), stop_before_pixels=True)
            uid = str(getattr(ds, "SeriesInstanceUID", ""))
            if not uid:
                raise ValueError("Manifest pointer lacks series UID")
            linked_uids.add(uid)
        if len(linked_uids) != crosswalk["case_rows"][ordinal - 1]["referenced_distinct_uids"]:
            raise ValueError("Crosswalk UID count changed")
        groups = defaultdict(list)
        files = sorted(case_dir.glob("*.dcm"))
        total_headers += len(files)
        for path in files:
            ds = pydicom.dcmread(str(path), stop_before_pixels=True)
            uid = str(getattr(ds, "SeriesInstanceUID", ""))
            if not uid:
                raise ValueError("DICOM file lacks series UID")
            groups[uid].append(ds)
        if not linked_uids.issubset(groups):
            raise ValueError("Manifest-linked UID absent from case directory")
        all_uids = sorted(groups)
        descriptions = {uid: describe_series(groups[uid]) for uid in linked_uids}
        label = f"candidate_{ordinal:02d}"
        case_rows.append({"candidate": label, "linked_uids": len(linked_uids),
                          "linked_pairs": len(linked_uids) * (len(linked_uids) - 1) // 2})
        for left_uid, right_uid in itertools.combinations(sorted(linked_uids), 2):
            left, right = descriptions[left_uid], descriptions[right_uid]
            checked = compare(left, right)
            technical_reasons = [reason for reason in checked["reasons"] if reason not in EXCLUDED]
            timing_reasons = [reason for reason in checked["reasons"] if reason in TIME_REASONS]
            centers_match = (left["distinct_positions"] and right["distinct_positions"]
                             and checked["max_slice_center_difference_mm"] is not None
                             and checked["max_slice_center_difference_mm"] <= 0.1)
            time_ok = checked["series_time_difference_seconds"] is not None and checked["series_time_difference_seconds"] >= 1
            pair_rows.append({
                "candidate": label,
                "series_a": all_uids.index(left_uid) + 1,
                "series_b": all_uids.index(right_uid) + 1,
                "literal_t2_labels": int(left["t2_label"]) + int(right["t2_label"]),
                "centers_match": centers_match,
                "technical_match": not technical_reasons,
                "timing_evidence": time_ok,
                "header_traceback_candidate": not technical_reasons and time_ok,
                "max_slice_center_difference_mm": checked["max_slice_center_difference_mm"],
                "series_time_difference_seconds": checked["series_time_difference_seconds"],
                "technical_failure_reasons": technical_reasons,
                "timing_failure_reasons": timing_reasons,
            })
    if total_headers != 2944:
        raise ValueError("DICOM file count changed")
    summary = {
        "status": "manifest-classified nonpixel candidates; T2 identity, acquisition and rights unverified",
        "plan_sha256": sha256(PLAN),
        "script_sha256": sha256(Path(__file__)),
        "helper_script_sha256": sha256(ROOT / "innovation/experiments/fastmri_repeat_t2_header_gate.py"),
        "manifest_sha256": MANIFEST_SHA,
        "crosswalk_sha256": sha256(CROSSWALK),
        "cases": len(case_rows),
        "dicom_headers_read": total_headers,
        "linked_uids": sum(row["linked_uids"] for row in case_rows),
        "linked_pairs": len(pair_rows),
        "literal_t2_pair_counts": dict(sorted(Counter(row["literal_t2_labels"] for row in pair_rows).items())),
        "center_matched_pairs": sum(row["centers_match"] for row in pair_rows),
        "technical_matched_pairs": sum(row["technical_match"] for row in pair_rows),
        "technical_and_time_candidates": sum(row["header_traceback_candidate"] for row in pair_rows),
        "independent_acquisition_proven_pairs": 0,
        "technical_failure_counts": dict(sorted(Counter(reason for row in pair_rows
                                                        for reason in row["technical_failure_reasons"]).items())),
        "case_rows": case_rows,
        "pair_rows": pair_rows,
    }
    OUT.mkdir(parents=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "cases", "dicom_headers_read", "linked_uids", "linked_pairs", "literal_t2_pair_counts",
        "center_matched_pairs", "technical_matched_pairs", "technical_and_time_candidates")}, indent=2))


if __name__ == "__main__":
    main()
