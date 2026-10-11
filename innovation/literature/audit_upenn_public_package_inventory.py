"""Reconcile official Faspex listings with the TCIA availability CSV."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "source_cache"
CSV_DIR = CACHE / "upenn_gbm_label_availability_2026-10-01"
TREE6 = CACHE / "upenn_gbm_public_package_tree_v6_2026-10-01.json"
TREE7 = CACHE / "upenn_gbm_public_package_tree_v7_2026-10-01.json"
OUT = CACHE / "upenn_gbm_public_package_inventory_2026-10-01.json"


def read_csv(name: str) -> list[dict]:
    with (CSV_DIR / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    availability = read_csv("data_availability.csv")
    acquisition = {row["ID"]: row for row in read_csv("acquisition.csv")}
    csv_ids = {row["ID"] for row in availability}
    corrected = {row["ID"] for row in availability
                 if row["Corrected Tumor Segmentation"].strip().lower() == "available"}
    tree6 = json.loads(TREE6.read_text(encoding="utf-8"))
    tree7 = json.loads(TREE7.read_text(encoding="utf-8"))
    structural = {item["path"].rsplit("/", 1)[-1]: item
                  for item in tree6["listings"][0]["entries"]}
    manual = {item["path"].rsplit("/", 1)[-1].removesuffix("_segm.nii.gz"): item
              for item in tree6["listings"][1]["entries"]}
    automated = {item["path"].rsplit("/", 1)[-1].removesuffix("_automated_approx_segm.nii.gz"): item
                 for item in tree7["listings"][0]["entries"]}
    if (len(csv_ids) != 671 or len(structural) != 671 or set(structural) != csv_ids
            or len(corrected) != 232 or len(manual) != 147 or len(automated) != 611
            or not set(manual) <= corrected or not corrected <= set(automated)):
        raise ValueError("Unexpected official inventory reconciliation")
    thin_manual = sorted(scan for scan in manual
                         if acquisition[scan]["T2 Slice Thickness"].strip().startswith("0.9"))
    pilot = thin_manual[0]
    if pilot != "UPENN-GBM-00002_11":
        raise ValueError("Preselected pilot changed")
    result = {
        "source_sha256": {path.name: sha256(path) for path in (
            CSV_DIR / "data_availability.csv", CSV_DIR / "acquisition.csv", TREE6, TREE7)},
        "official_package_id": "604",
        "csv_scan_ids": len(csv_ids),
        "structural_directories": len(structural),
        "structural_csv_exact_match": set(structural) == csv_ids,
        "corrected_available_csv_ids": len(corrected),
        "manual_segmentation_entries": len(manual),
        "manual_entries_all_marked_corrected": set(manual) <= corrected,
        "corrected_csv_ids_without_manual_entry": len(corrected - set(manual)),
        "corrected_csv_ids_without_manual_entry_list": sorted(corrected - set(manual)),
        "automated_approx_entries": len(automated),
        "corrected_csv_ids_with_automated_approx": len(corrected & set(automated)),
        "manual_t2_thickness_counts": dict(Counter(acquisition[scan]["T2 Slice Thickness"] for scan in manual)),
        "thin_corrected_manual_ids": len(thin_manual),
        "preselected_header_pilot_scan": pilot,
        "preselected_manual_path": manual[pilot]["path"],
        "preselected_manual_declared_size": manual[pilot]["size"],
        "patient_pixels_read": False,
        "package_transfer_started": False,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("source_sha256", "corrected_csv_ids_without_manual_entry_list")}, indent=2))


if __name__ == "__main__":
    main()
