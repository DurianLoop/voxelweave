"""Read only the NIfTI headers of the frozen first official MSD pair."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import zlib
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_cache" / "msd_task01_official_2026-10-01"
INDEX = SOURCE / "tar_index_full.json"
DATASET = SOURCE / "dataset.json"
OUT = SOURCE / "brats001_header_pilot.json"


def header_from_member(opener, url: str, total: int,
                       etag: str, entry: dict) -> dict:
    first = entry["data_offset"]
    for length in (4096, 8192):
        last = first + length - 1
        request = urllib.request.Request(url, headers={"Range": f"bytes={first}-{last}",
                                                       "User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=40) as response:
            status, headers, content = response.status, response.headers, response.read(length + 1)
        if (status != 206 or len(content) != length or
                headers.get("Content-Range") != f"bytes {first}-{last}/{total}" or
                headers.get("ETag") != etag):
            raise ValueError("Bounded S3 object response changed")
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        raw_header = decoder.decompress(content, 352)
        if len(raw_header) >= 352:
            break
    else:
        raise ValueError("NIfTI header absent within permitted compressed prefix")
    header = nib.Nifti1Header(binaryblock=raw_header[:348])
    affine = header.get_best_affine()
    return {"member": entry["name"], "declared_member_bytes": entry["size"],
            "prefix_bytes_requested": length,
            "compressed_prefix_sha256": hashlib.sha256(content).hexdigest(),
            "header_352_sha256": hashlib.sha256(raw_header).hexdigest(),
            "magic": bytes(header["magic"]).decode("ascii", "replace"),
            "shape": list(header.get_data_shape()),
            "datatype": str(header.get_data_dtype()),
            "zooms": [float(v) for v in header.get_zooms()],
            "qform_code": int(header["qform_code"]),
            "sform_code": int(header["sform_code"]),
            "best_affine": affine.tolist()}


def main() -> None:
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite frozen header pilot")
    indexed = json.loads(INDEX.read_text(encoding="utf-8"))
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    training = sorted(dataset["training"], key=lambda item: item["image"])
    if (len(training) != 484 or
            training[0] != {"image": "./imagesTr/BRATS_001.nii.gz",
                            "label": "./labelsTr/BRATS_001.nii.gz"}):
        raise ValueError("Frozen first pair changed")
    entries = {item["name"]: item for item in indexed["entries"]}
    paths = ["Task01_BrainTumour/" + training[0][kind].removeprefix("./")
             for kind in ("image", "label")]
    if any(path not in entries for path in paths):
        raise ValueError("Frozen member is missing")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {"scan": "BRATS_001", "source_tar_url": indexed["tar_url"],
              "tar_etag": indexed["tar_etag"], "tar_index_sha256": hashlib.sha256(INDEX.read_bytes()).hexdigest(),
              "dataset_json_sha256": hashlib.sha256(DATASET.read_bytes()).hexdigest(),
              "range_requests_only": True, "patient_pixels_decoded": False}
    try:
        image, label = [header_from_member(opener, indexed["tar_url"], indexed["tar_bytes"],
                                           indexed["tar_etag"], entries[path]) for path in paths]
        report["image"] = image
        report["label"] = label
        spatial = image["shape"][:3]
        report["same_grid"] = (len(image["shape"]) == 4 and image["shape"][3] == 4 and
                               len(label["shape"]) == 3 and spatial == label["shape"] and
                               np.allclose(image["best_affine"], label["best_affine"],
                                           rtol=0, atol=1e-4) and
                               all(np.isfinite(image["zooms"][:3])) and
                               all(v > 0 for v in image["zooms"][:3]) and
                               all(np.isfinite(label["zooms"][:3])) and
                               all(v > 0 for v in label["zooms"][:3]))
    except Exception as error:
        report["error_type"] = type(error).__name__
        report["same_grid"] = False
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
