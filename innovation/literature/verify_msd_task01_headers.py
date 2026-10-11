"""Independent read-only recomputation of MSD source and NIfTI header gates."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_cache" / "msd_task01_official_2026-10-01"
INDEX = SOURCE / "tar_index_full.json"
DATASET = SOURCE / "dataset.json"
INITIAL = SOURCE / "all_training_pair_headers.json"
RETRY = SOURCE / "brats230_header_transport_retry.json"
PLAN = ROOT.parent / "MSD_TASK01_FULL_HEADER_QUALIFICATION_PLAN_2026-10-01.md"
OUT = SOURCE / "header_verification.json"


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matched(image: dict, label: dict) -> bool:
    def valid(item: dict, shape: list[int], datatype: str) -> bool:
        return (item["magic"] == "n+1\x00" and item["shape"] == shape and
                item["datatype"] == datatype and item["qform_code"] > 0 and
                item["sform_code"] > 0 and
                all(math.isfinite(v) and abs(v - 1) <= 1e-4 for v in item["zooms"][:3]) and
                item["prefix_bytes_requested"] in (4096, 8192) and
                len(item["compressed_prefix_sha256"]) == 64 and
                len(item["header_352_sha256"]) == 64)
    if not valid(image, [240, 240, 155, 4], "float32") or not valid(label, [240, 240, 155], "uint8"):
        return False
    left, right = image["best_affine"], label["best_affine"]
    return (len(left) == len(right) == 4 and
            all(len(row) == 4 for row in left + right) and
            all(math.isfinite(a) and math.isfinite(b) and abs(a - b) <= 1e-4
                for row_a, row_b in zip(left, right) for a, b in zip(row_a, row_b)))


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing overwrite of independent verification")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    initial = json.loads(INITIAL.read_text(encoding="utf-8"))
    retry = json.loads(RETRY.read_text(encoding="utf-8"))
    pairs = sorted(dataset["training"], key=lambda row: row["image"])
    records = initial["records"]
    if (len(pairs) != len(records) or len(pairs) != 484 or
            initial["plan_sha256"] != hash_file(PLAN) or
            initial["tar_index_sha256"] != hash_file(INDEX) or
            initial["dataset_json_sha256"] != hash_file(DATASET) or
            retry["initial_report_sha256"] != hash_file(INITIAL)):
        raise ValueError("Source/protocol/record count mismatch")
    entries = {item["name"]: item for item in index["entries"]}
    if len(entries) != len(index["entries"]) or index["stop_reason"] != "tar_end_block":
        raise ValueError("Tar index incomplete or duplicate")
    failed = []
    for pair, record in zip(pairs, records):
        case = Path(pair["image"]).name.removesuffix(".nii.gz")
        paths = ["Task01_BrainTumour/" + pair[key].removeprefix("./")
                 for key in ("image", "label")]
        if case != record["scan"] or any(path not in entries for path in paths):
            raise ValueError("Exact pair mapping mismatch")
        if record["eligible"]:
            image, label = record["image"], record["label"]
            if (image["member"] != paths[0] or label["member"] != paths[1] or
                    image["declared_member_bytes"] != entries[paths[0]]["size"] or
                    label["declared_member_bytes"] != entries[paths[1]]["size"] or
                    not matched(image, label)):
                raise ValueError(f"Independent header mismatch: {case}")
        else:
            failed.append(case)
    if (failed != ["BRATS_230"] or retry["scan"] != failed[0] or
            not matched(retry["image"], retry["label"]) or not retry["same_grid"]):
        raise ValueError("Transport retry did not close exact failed case")
    result = {"initial_attempts": 484, "initial_same_grid": 483,
              "initial_failed_cases": failed, "retry_same_grid": True,
              "effective_same_grid": 484,
              "training_images_in_tar": sum(1 for pair in pairs if
                  "Task01_BrainTumour/" + pair["image"].removeprefix("./") in entries),
              "training_labels_in_tar": sum(1 for pair in pairs if
                  "Task01_BrainTumour/" + pair["label"].removeprefix("./") in entries),
              "patient_pixels_decoded": False, "verified": True}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
