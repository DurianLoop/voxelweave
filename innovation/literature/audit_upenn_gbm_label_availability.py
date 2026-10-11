"""Archive official UPENN metadata and count label availability by patient prefix."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "source_cache/upenn_gbm_label_availability_2026-10-01"
SELECTED = HERE / "upenn_gbm_processed_t2_inventory.json"
URLS = {
    "data_availability": "https://www.cancerimagingarchive.net/wp-content/uploads/"
                         "UPENN-GBM_data_availability.csv",
    "acquisition": "https://www.cancerimagingarchive.net/wp-content/uploads/"
                   "UPENN-GBM_acquisition.csv",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def subject_prefix(scan_id: str) -> str:
    return scan_id.split("_", 1)[0]


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    selected_bytes = SELECTED.read_bytes()
    selected = {row["patient"] for row in json.loads(selected_bytes)["series"]}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    fetched = {}
    for name, url in URLS.items():
        request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-qualification/1.0"})
        with opener.open(request, timeout=60) as response:
            if response.status != 200:
                raise RuntimeError(f"{name}: HTTP {response.status}")
            fetched[name] = response.read()
    availability = rows(fetched["data_availability"])
    acquisition = rows(fetched["acquisition"])
    subjects = {subject_prefix(row["ID"]) for row in availability}
    corrected = [row for row in availability
                 if row["Corrected Tumor Segmentation"].strip().lower() == "available"]
    corrected_subjects = {subject_prefix(row["ID"]) for row in corrected}
    if (len(availability) != 671 or len(acquisition) != 671 or len(subjects) != 630 or
            len(selected) != 374 or not selected <= subjects or len(corrected) != 232 or
            len(selected & corrected_subjects) != 114):
        raise ValueError("Unexpected official availability or patient-prefix join")
    summary = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_dicom_inventory_sha256": sha256(selected_bytes),
        "availability_scan_rows": len(availability),
        "availability_unique_subject_prefixes": len(subjects),
        "selected_dicom_subject_prefixes": len(selected),
        "selected_prefixes_present_in_availability": len(selected & subjects),
        "corrected_segmentation_scan_rows": len(corrected),
        "corrected_segmentation_scan_suffixes":
            dict(Counter(row["ID"].split("_", 1)[1] for row in corrected)),
        "selected_prefixes_with_corrected_segmentation": len(selected & corrected_subjects),
        "acquisition_scan_rows": len(acquisition),
        "scan_id_sets_match": {row["ID"] for row in availability}
                              == {row["ID"] for row in acquisition},
        "same_scan_or_space_alignment_proven": False,
        "patient_pixels_read": False,
        "sources": [],
    }
    if not summary["scan_id_sets_match"]:
        raise ValueError("Official CSV scan-ID sets differ")
    OUT.mkdir(parents=True)
    for name, data in fetched.items():
        filename = name + ".csv"
        (OUT / filename).write_bytes(data)
        summary["sources"].append({
            "name": name, "url": URLS[name], "file": filename,
            "bytes": len(data), "sha256": sha256(data),
        })
    (OUT / "index.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "availability_scan_rows", "availability_unique_subject_prefixes",
        "selected_dicom_subject_prefixes", "corrected_segmentation_scan_rows",
        "selected_prefixes_with_corrected_segmentation",
        "same_scan_or_space_alignment_proven")}, indent=2))


if __name__ == "__main__":
    main()
