"""Nonpixel crosswalk from manifest T2 rows to DICOM series UIDs."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import pydicom

from fastmri_repeat_t2_header_gate import sha256


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "innovation/FASTMRI_MANIFEST_UID_CROSSWALK_PLAN_2026-10-01.md"
MANIFEST = ROOT / "dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_series_manifest.csv"
MANIFEST_SHA = "042730d2802b4b01326d6f297e6bd46e76d5a56d7b044fe60c87d8ccf41c5c2d"
DATA_ROOT = (ROOT / "dataset/fastMRI_brain_DICOM").resolve()
FULL_SCREEN = ROOT / "innovation/experiments/fastmri_all_t2_header_gate/summary.json"
OUT = ROOT / "innovation/experiments/fastmri_manifest_uid_crosswalk"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite crosswalk result")
    if sha256(MANIFEST) != MANIFEST_SHA:
        raise ValueError("Manifest hash changed")
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    grouped = defaultdict(list)
    for row in rows:
        if row["is_t2"].lower() == "true":
            grouped[row["case_id"]].append(row)
    selected = sorted(case_id for case_id, items in grouped.items() if len(items) >= 2)
    if len(selected) != 61 or sum(len(grouped[case_id]) for case_id in selected) != 138:
        raise ValueError("Frozen case or row count changed")
    prior = json.loads(FULL_SCREEN.read_text(encoding="utf-8"))
    if prior["cases"] != 61:
        raise ValueError("Previous screen case count changed")
    results = []
    for ordinal, case_id in enumerate(selected, 1):
        case_dir = (DATA_ROOT / case_id).resolve()
        referenced = defaultdict(list)
        for row in grouped[case_id]:
            path = Path(row["first_dicom"]).resolve()
            if path.parent != case_dir or path.suffix.lower() != ".dcm" or not path.is_file():
                raise ValueError("Manifest pointer missing or outside selected case directory")
            ds = pydicom.dcmread(str(path), stop_before_pixels=True)
            uid = str(getattr(ds, "SeriesInstanceUID", ""))
            if not uid:
                raise ValueError("Manifest pointer has no series UID")
            referenced[uid].append("t2" in str(getattr(ds, "SeriesDescription", "")).lower())
        row_count = len(grouped[case_id])
        uid_count = len(referenced)
        desc_t2_uids = sum(any(labels) for labels in referenced.values())
        results.append({
            "candidate": f"candidate_{ordinal:02d}",
            "manifest_t2_rows": row_count,
            "referenced_distinct_uids": uid_count,
            "repeated_uid_rows": row_count - uid_count,
            "referenced_t2_labeled_uids": desc_t2_uids,
            "referenced_non_t2_labeled_uids": uid_count - desc_t2_uids,
            "prior_full_directory_t2_series": prior["case_rows"][ordinal - 1]["t2_labeled_series"],
        })
    summary = {
        "status": "nonpixel manifest-to-series crosswalk; acquisition and rights unverified",
        "plan_sha256": sha256(PLAN),
        "script_sha256": sha256(Path(__file__)),
        "manifest_sha256": MANIFEST_SHA,
        "prior_screen_sha256": sha256(FULL_SCREEN),
        "cases": len(results),
        "manifest_t2_rows": sum(row["manifest_t2_rows"] for row in results),
        "referenced_distinct_uids": sum(row["referenced_distinct_uids"] for row in results),
        "repeated_uid_rows": sum(row["repeated_uid_rows"] for row in results),
        "referenced_t2_labeled_uids": sum(row["referenced_t2_labeled_uids"] for row in results),
        "referenced_non_t2_labeled_uids": sum(row["referenced_non_t2_labeled_uids"] for row in results),
        "cases_with_repeated_uid_rows": sum(row["repeated_uid_rows"] > 0 for row in results),
        "case_rows": results,
    }
    OUT.mkdir(parents=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "cases", "manifest_t2_rows", "referenced_distinct_uids", "repeated_uid_rows",
        "referenced_t2_labeled_uids", "referenced_non_t2_labeled_uids",
        "cases_with_repeated_uid_rows")}, indent=2))


if __name__ == "__main__":
    main()
