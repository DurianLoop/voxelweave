"""First frozen MSD pair: source integrity and label/ROI selection, no model."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from msd_task01_source import ROOT, official_index, load_exact_pair, region_masks, selected_targets


PROTOCOL = ROOT / "MSD_TASK01_TUMOR_ROI_CONTEXT_PROTOCOL_2026-10-01.md"
HEADERS = ROOT / "literature/source_cache/msd_task01_official_2026-10-01/header_verification.json"
OUT = ROOT / "experiments/msd_task01_brats001_pixel_qualification.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of first-case qualification")
    checked = json.loads(HEADERS.read_text(encoding="utf-8"))
    if not checked["verified"] or checked["effective_same_grid"] != 484:
        raise ValueError("All-pair source header gate is absent")
    indexed, entries = official_index()
    report = {"scan": "BRATS_001",
              "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
              "all_header_verification_sha256": hashlib.sha256(HEADERS.read_bytes()).hexdigest(),
              "model_predictions_computed": False, "gpu_used": False}
    try:
        t2, label, files = load_exact_pair("BRATS_001", indexed, entries)
        report["files"] = files
        report["t2_shape"] = list(t2.shape)
        report["label_shape"] = list(label.shape)
        report["label_code_counts"] = {str(value): int((label == value).sum())
                                       for value in np.unique(label)}
        targets = selected_targets(label)
        report["selected_targets"] = targets
        report["regions"] = []
        for residue in ("1", "3"):
            for z in targets[residue]:
                support, lesion, local = region_masks(t2, label, z)
                report["regions"].append({"z": z, "residue": int(residue),
                    "support_pixels": int(support.sum()),
                    "lesion_pixels": int(lesion.sum()),
                    "local_control_pixels": int(local.sum())})
        report["eligible"] = True
    except Exception as error:
        report["eligible"] = False
        report["error_type"] = type(error).__name__
        report["error_reason"] = str(error)[:160]
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "files"}, indent=2))


if __name__ == "__main__":
    main()
