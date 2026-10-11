"""Read all official MSD labels to freeze tumor-positive targets before models."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np

from msd_task01_source import DATASET, ROOT, fetch_member, official_index, source_record, selected_targets


PROTOCOL = ROOT / "MSD_TASK01_TUMOR_ROI_CONTEXT_PROTOCOL_2026-10-01.md"
HEADERS = ROOT / "literature/source_cache/msd_task01_official_2026-10-01/header_verification.json"
OUT = ROOT / "experiments/msd_task01_label_qualification.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of label qualification")
    headers = json.loads(HEADERS.read_text(encoding="utf-8"))
    if not headers["verified"] or headers["effective_same_grid"] != 484:
        raise ValueError("Nonpixel source gate not passed")
    indexed, entries = official_index()
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    pairs = sorted(dataset["training"], key=lambda item: item["image"])
    if len(pairs) != 484:
        raise ValueError("Frozen training denominator changed")
    records = []
    for count, pair in enumerate(pairs, 1):
        scan = Path(pair["image"]).name.removesuffix(".nii.gz")
        row = {"scan": scan, "eligible": False}
        try:
            if pair["label"] != f"./labelsTr/{scan}.nii.gz":
                raise ValueError("Dataset image/label ID mismatch")
            entry, destination = source_record(scan, "labelsTr", indexed, entries)
            row["source"] = fetch_member(entry, destination, indexed)
            image = nib.load(str(destination))
            if (image.shape != (240, 240, 155) or
                    image.get_data_dtype() != np.dtype("uint8") or
                    not np.allclose(image.affine, np.eye(4), atol=1e-4, rtol=0)):
                raise ValueError("Decoded label differs from strict header gate")
            mask = np.asarray(image.dataobj, dtype=np.uint8)
            values, counts = np.unique(mask, return_counts=True)
            row["label_counts"] = {str(int(value)): int(number)
                                   for value, number in zip(values, counts)}
            if not set(row["label_counts"]).issubset({"0", "1", "2", "3"}):
                raise ValueError("Unexpected label code")
            row["targets"] = selected_targets(mask)
            row["eligible"] = True
        except Exception as error:
            row["error_type"] = type(error).__name__
            row["error_reason"] = str(error)[:160]
        records.append(row)
        if count % 25 == 0 or count == len(pairs):
            print(f"labels checked {count}/{len(pairs)}", flush=True)
    completed = sum(int(row["eligible"]) for row in records)
    report = {"protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
              "header_verification_sha256": hashlib.sha256(HEADERS.read_bytes()).hexdigest(),
              "dataset_json_sha256": hashlib.sha256(DATASET.read_bytes()).hexdigest(),
              "cases_attempted": len(records), "label_target_eligible": completed,
              "meets_350_case_floor_before_image_inference": completed >= 350,
              "model_predictions_computed": False, "gpu_used": False,
              "records": records}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "records"}, indent=2))


if __name__ == "__main__":
    main()
