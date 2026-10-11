"""Freeze one official processed axial T2 series per UPENN-GBM patient."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "literature/source_cache/upenn_gbm_getSeries_2026-10-01.json"
PROTOCOL = ROOT / "UPENN_GBM_PROCESSED_T2_CONTEXT_PROTOCOL_2026-10-01.md"
OUTPUT = ROOT / "literature/upenn_gbm_processed_t2_inventory.json"
EXPECTED_SOURCE_SHA256 = "bbae9a76f75a42cc35d460448c3afa87c55119d4ee5a84b9b18179fe28908de9"
DESCRIPTION = "Axial T2 tse: Processed_CaPTk"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise ValueError("Official source changed")
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    by_patient = defaultdict(list)
    for row in rows:
        if (row.get("Modality") == "MR" and row.get("SeriesDescription") == DESCRIPTION
                and int(row.get("ImageCount", 0)) >= 24):
            by_patient[row["PatientID"]].append(row)
    if sum(map(len, by_patient.values())) != 402 or len(by_patient) != 374:
        raise ValueError("Frozen stratum count changed")
    selected = []
    for patient in sorted(by_patient):
        row = min(by_patient[patient], key=lambda entry: (
            entry.get("StudyDate", ""), entry["SeriesInstanceUID"]))
        if (row.get("LicenseURI", "").rstrip("/")
                != "https://creativecommons.org/licenses/by/4.0"):
            raise ValueError(f"License changed for {patient}")
        selected.append({"patient": patient, "series_uid": row["SeriesInstanceUID"],
                         "study_uid": row["StudyInstanceUID"],
                         "series_description": DESCRIPTION,
                         "study_description": row.get("StudyDesc", ""),
                         "study_date": row.get("StudyDate", ""),
                         "image_count": int(row["ImageCount"]),
                         "file_size": int(row.get("FileSize", 0)),
                         "license_uri": row["LicenseURI"],
                         "collection_uri": row.get("CollectionURI", "")})
    payload = {"source_sha256": EXPECTED_SOURCE_SHA256,
               "protocol_sha256": sha256(PROTOCOL),
               "script_sha256": sha256(Path(__file__)),
               "series_candidates": 402,
               "patients_selected": len(selected),
               "series": selected}
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"series_candidates": 402, "patients_selected": len(selected),
                      "official_file_bytes": sum(x["file_size"] for x in selected),
                      "first_patient": selected[0]["patient"]}, indent=2))


if __name__ == "__main__":
    main()
