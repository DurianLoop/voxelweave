"""One recorded retry of the sole transport-failed official MSD header pair."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np

from pilot_msd_task01_headers import header_from_member


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_cache" / "msd_task01_official_2026-10-01"
INDEX = SOURCE / "tar_index_full.json"
DATASET = SOURCE / "dataset.json"
INITIAL = SOURCE / "all_training_pair_headers.json"
PLAN = ROOT.parent / "MSD_TASK01_HEADER_RETRY_AMENDMENT_2026-10-01.md"
OUT = SOURCE / "brats230_header_transport_retry.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing repeated retry")
    indexed = json.loads(INDEX.read_text(encoding="utf-8"))
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    initial = json.loads(INITIAL.read_text(encoding="utf-8"))
    failed = [item for item in initial["records"] if not item["eligible"]]
    if len(failed) != 1 or failed[0]["scan"] != "BRATS_230" or failed[0]["error_type"] != "URLError":
        raise ValueError("Not the frozen transport failure")
    pair = [item for item in dataset["training"] if item["image"] == "./imagesTr/BRATS_230.nii.gz"]
    if len(pair) != 1 or pair[0]["label"] != "./labelsTr/BRATS_230.nii.gz":
        raise ValueError("Frozen pair changed")
    entries = {item["name"]: item for item in indexed["entries"]}
    paths = ["Task01_BrainTumour/" + pair[0][key].removeprefix("./") for key in ("image", "label")]
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    result = {"scan": "BRATS_230", "initial_report_sha256": hashlib.sha256(INITIAL.read_bytes()).hexdigest(),
              "amendment_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
              "patient_pixels_decoded": False, "same_grid": False}
    try:
        image, label = [header_from_member(opener, indexed["tar_url"], indexed["tar_bytes"],
                                           indexed["tar_etag"], entries[path]) for path in paths]
        result["image"], result["label"] = image, label
        result["same_grid"] = (image["magic"] == "n+1\x00" and label["magic"] == "n+1\x00" and
            image["shape"] == [240, 240, 155, 4] and label["shape"] == [240, 240, 155] and
            image["datatype"] == "float32" and label["datatype"] == "uint8" and
            image["qform_code"] > 0 and image["sform_code"] > 0 and
            label["qform_code"] > 0 and label["sform_code"] > 0 and
            np.allclose(image["zooms"][:3], [1, 1, 1], rtol=0, atol=1e-4) and
            np.allclose(label["zooms"][:3], [1, 1, 1], rtol=0, atol=1e-4) and
            np.allclose(image["best_affine"], label["best_affine"], rtol=0, atol=1e-4))
    except Exception as error:
        result["error_type"] = type(error).__name__
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ("image", "label")}, indent=2))


if __name__ == "__main__":
    main()
