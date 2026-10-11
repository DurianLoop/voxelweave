"""Qualify every official MSD training image/label pair without voxel decoding."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np

from pilot_msd_task01_headers import header_from_member


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_cache" / "msd_task01_official_2026-10-01"
INDEX = SOURCE / "tar_index_full.json"
DATASET = SOURCE / "dataset.json"
PLAN = ROOT.parent / "MSD_TASK01_FULL_HEADER_QUALIFICATION_PLAN_2026-10-01.md"
OUT = SOURCE / "all_training_pair_headers.json"
PILOT_INDEX_SHA256 = "0a1c66190fe9d22335ef537a9695d534d2d2137eb3ff45756d34da642de4dcec"
DATASET_SHA256 = "77f38db2fcf1a39ad4923f482f30c948cc7349fa7823cd307ceb3145adb81412"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_pair(pair: dict, entries: dict, indexed: dict) -> dict:
    scan = Path(pair["image"]).name.removesuffix(".nii.gz")
    result = {"scan": scan, "eligible": False}
    try:
        if Path(pair["label"]).name != Path(pair["image"]).name:
            raise ValueError("Image/label case names differ")
        paths = ["Task01_BrainTumour/" + pair[kind].removeprefix("./")
                 for kind in ("image", "label")]
        if any(path not in entries for path in paths):
            raise ValueError("Missing exact tar member")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        headers = [header_from_member(opener, indexed["tar_url"], indexed["tar_bytes"],
                                      indexed["tar_etag"], entries[path]) for path in paths]
        image, label = headers
        result["image"], result["label"] = image, label
        for item, shape, datatype in ((image, [240, 240, 155, 4], "float32"),
                                       (label, [240, 240, 155], "uint8")):
            if (item["magic"] != "n+1\x00" or item["shape"] != shape or
                    item["datatype"] != datatype or item["qform_code"] <= 0 or
                    item["sform_code"] <= 0 or
                    not np.allclose(item["zooms"][:3], [1, 1, 1], rtol=0, atol=1e-4)):
                raise ValueError("Strict NIfTI shape/type/spacing/form mismatch")
        affine = np.asarray(image["best_affine"], dtype=float)
        other = np.asarray(label["best_affine"], dtype=float)
        if (not np.isfinite(affine).all() or not np.isfinite(other).all() or
                abs(np.linalg.det(affine[:3, :3])) < 1e-8 or
                not np.allclose(affine, other, rtol=0, atol=1e-4)):
            raise ValueError("Image/label affine mismatch or singular transform")
        result["eligible"] = True
    except (OSError, urllib.error.URLError, ValueError, KeyError) as error:
        result["error_type"] = type(error).__name__
        result["error_reason"] = str(error)[:140]
    return result


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite full qualification")
    if sha256(INDEX) != PILOT_INDEX_SHA256 or sha256(DATASET) != DATASET_SHA256:
        raise ValueError("Official index/dataset changed since the frozen pilot")
    indexed = json.loads(INDEX.read_text(encoding="utf-8"))
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    pairs = sorted(dataset["training"], key=lambda item: item["image"])
    if len(pairs) != 484 or len({item["image"] for item in pairs}) != 484:
        raise ValueError("Expected 484 distinct frozen training pairs")
    entries = {item["name"]: item for item in indexed["entries"]}
    results: list[dict | None] = [None] * len(pairs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        tasks = {executor.submit(inspect_pair, pair, entries, indexed): index
                 for index, pair in enumerate(pairs)}
        for done, task in enumerate(concurrent.futures.as_completed(tasks), 1):
            results[tasks[task]] = task.result()
            if done % 25 == 0 or done == len(pairs):
                print(f"headers checked {done}/{len(pairs)}", flush=True)
    complete = [item for item in results if item is not None]
    errors = Counter(item.get("error_reason", "") for item in complete if not item["eligible"])
    eligible = sum(bool(item["eligible"]) for item in complete)
    report = {"plan_sha256": sha256(PLAN), "tar_index_sha256": sha256(INDEX),
              "dataset_json_sha256": sha256(DATASET),
              "tar_etag": indexed["tar_etag"], "pairs_attempted": len(pairs),
              "pairs_eligible": eligible, "numeric_minimum_pass": eligible >= 450,
              "error_counts": dict(errors), "patient_pixels_decoded": False,
              "records": complete}
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "records"}, indent=2))


if __name__ == "__main__":
    main()
