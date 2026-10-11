"""Run the frozen ds007045 two-header, nonpixel geometry check."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import urllib.request
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "DS007045_BA3_TWO_HEADER_RESULT_2026-10-01.json"
BASE = "https://s3.amazonaws.com/openneuro.org/"
KEYS = {
    "processed_t2": "ds007045/derivatives/processing/sub-BA3/sub-BA3_t2_MNI152_brain.nii.gz",
    "tumor_mask": "ds007045/derivatives/segmentation/sub-BA3/sub-BA3_MNI152_tumor-mask.nii.gz",
}
CAP = 65_536


def inspect(key: str) -> tuple[dict, nib.Nifti1Header]:
    request = urllib.request.Request(
        BASE + key,
        headers={"User-Agent": "MRI-source-audit/1.0", "Range": "bytes=0-65535"},
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=25) as response:
        status = response.status
        content_range = response.headers.get("Content-Range")
        if status != 206:
            raise ValueError(f"Range not honored for {key}: HTTP {status}")
        raw = response.read(CAP + 1)
    if len(raw) > CAP:
        raise ValueError(f"Range exceeded byte cap for {key}")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        header_bytes = stream.read(352)
    if len(header_bytes) != 352:
        raise ValueError(f"Incomplete NIfTI header for {key}")
    header = nib.Nifti1Header.from_fileobj(io.BytesIO(header_bytes))
    qform, qcode = header.get_qform(coded=True)
    sform, scode = header.get_sform(coded=True)
    record = {
        "key": key,
        "http_status": status,
        "content_range": content_range,
        "compressed_bytes_read": len(raw),
        "compressed_sha256": hashlib.sha256(raw).hexdigest(),
        "shape": [int(value) for value in header.get_data_shape()],
        "zooms": [float(value) for value in header.get_zooms()],
        "datatype": str(header.get_data_dtype()),
        "qform_code": int(qcode),
        "sform_code": int(scode),
        "qform": qform.tolist() if qform is not None else None,
        "sform": sform.tolist() if sform is not None else None,
        "best_affine": header.get_best_affine().tolist(),
    }
    return record, header


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing overwrite: {OUT}")
    result: dict = {"protocol": "DS007045_TWO_HEADER_PROTOCOL_2026-10-01.md",
                    "version_scope": "current S3 / dataset_description v2.0.1",
                    "no_gpu": True, "no_voxel_data": True, "records": {}}
    headers = {}
    try:
        for name, key in KEYS.items():
            record, header = inspect(key)
            result["records"][name] = record
            headers[name] = header
        a, b = headers.values()
        result["same_shape"] = a.get_data_shape() == b.get_data_shape()
        result["same_best_affine_1e-4mm"] = bool(np.allclose(
            a.get_best_affine(), b.get_best_affine(), atol=1e-4, rtol=0))
        result["max_affine_absolute_difference_mm"] = float(np.max(np.abs(
            a.get_best_affine() - b.get_best_affine())))
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
