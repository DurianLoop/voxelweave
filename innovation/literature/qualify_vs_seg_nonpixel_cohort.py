"""Cross-check VS-SEG mapping and NBIA T2 series without image pixels."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "literature/source_cache/vs_seg_official_inventory_2026-10-01"
OUT = ROOT / "literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json"
EXPECTED = {"T1 image", "T2 image", "T1 RTSTRUCT", "T2 RTSTRUCT",
            "T1 RTPLAN", "T2 RTPLAN", "T1 RTDOSE", "T2 RTDOSE"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    mapping_path, series_path = SOURCE / "mapping.csv", SOURCE / "series.json"
    with mapping_path.open(newline="", encoding="utf-8-sig") as stream:
        mapped = list(csv.DictReader(stream))
    series = json.loads(series_path.read_text(encoding="utf-8"))
    by_patient = defaultdict(dict)
    for row in mapped:
        patient = row["Descriptive Directory Name"].split("/")[0]
        modality = row["Modality"]
        if modality in by_patient[patient]:
            raise ValueError(f"Duplicate mapped modality: {patient} {modality}")
        uid = row["Classic Directory Name"].split("/")[-1]
        by_patient[patient][modality] = uid
    if len(mapped) != 1936 or len(by_patient) != 242:
        raise ValueError("Official mapping denominator differs")
    incomplete = {p: sorted(EXPECTED - set(m)) for p, m in by_patient.items() if set(m) != EXPECTED}
    t2 = [row for row in series if row.get("Modality") == "MR" and
          str(row.get("SeriesDescription", "")).lower().startswith("t2_")]
    if len(t2) != 241 or len({row["PatientID"] for row in t2}) != 241:
        raise ValueError("Official NBIA T2 denominator differs")
    mismatched = [row["PatientID"] for row in t2 if
                  by_patient[row["PatientID"]]["T2 image"] != row["SeriesInstanceUID"]]
    missing = sorted(set(by_patient) - {row["PatientID"] for row in t2})
    result = {
        "mapping_sha256": sha256(mapping_path), "nbia_series_sha256": sha256(series_path),
        "mapped_patients": len(by_patient), "mapped_rows": len(mapped),
        "mapping_incomplete": incomplete,
        "nbia_t2_patients": len(t2), "nbia_missing_from_mapping": mismatched,
        "mapped_t2_absent_from_nbia_mr_list": missing,
        "series_descriptions": dict(Counter(row["SeriesDescription"] for row in t2)),
        "image_count_distribution": dict(sorted(Counter(int(row["ImageCount"]) for row in t2).items())),
        "license_uris": dict(Counter(row.get("LicenseURI", "") for row in t2)),
        "collection_uris": dict(Counter(row.get("CollectionURI", "") for row in t2)),
        "t2_series": [{"patient": row["PatientID"],
                       "series_uid": row["SeriesInstanceUID"],
                       "description": row["SeriesDescription"],
                       "image_count": int(row["ImageCount"]),
                       "listed_bytes": int(row.get("FileSize") or 0)}
                      for row in sorted(t2, key=lambda r: r["PatientID"])],
        "patient_pixels_read": False,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "t2_series"}, indent=2))


if __name__ == "__main__":
    main()
