"""One-case CPU feasibility check under the frozen ds007045 protocol."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "DS007045_BA3_CPU_PILOT_RESULT_2026-10-01.json"
DATA = ROOT / "data/ds007045_ba3_pilot"
HEADER = ROOT / "DS007045_BA3_TWO_HEADER_RESULT_2026-10-01.json"
FILES = {
    "processed_t2": ("ds007045/derivatives/processing/sub-BA3/sub-BA3_t2_MNI152_brain.nii.gz", 5_765_102, 6_000_000),
    "tumor_mask": ("ds007045/derivatives/segmentation/sub-BA3/sub-BA3_MNI152_tumor-mask.nii.gz", 18_426, 32_000),
}


def download(name: str, key: str, expected: int, cap: int, prior_hash: str) -> dict:
    path = DATA / f"{name}.nii.gz"
    if path.exists():
        raise FileExistsError(path)
    request = urllib.request.Request("https://s3.amazonaws.com/openneuro.org/" + key,
                                     headers={"User-Agent": "MRI-source-audit/1.0"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=40) as response:
        if response.status != 200 or int(response.headers.get("Content-Length", -1)) != expected:
            raise ValueError(f"Unexpected object status or size for {key}")
        body = response.read(cap + 1)
    if len(body) != expected or len(body) > cap:
        raise ValueError(f"Object exceeded cap or expected size: {key}")
    if hashlib.sha256(body[:65_536]).hexdigest() != prior_hash:
        raise ValueError(f"Object changed since header check: {key}")
    path.write_bytes(body)
    return {"key": key, "path": path.relative_to(ROOT).as_posix(), "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest()}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    DATA.mkdir(parents=True, exist_ok=True)
    prior = json.loads(HEADER.read_text(encoding="utf-8"))["records"]
    records = {}
    for name, (key, size, cap) in FILES.items():
        records[name] = download(name, key, size, cap, prior[name]["compressed_sha256"])
    image = nib.load(str(DATA / "processed_t2.nii.gz"))
    mask = nib.load(str(DATA / "tumor_mask.nii.gz"))
    if image.shape != mask.shape or not np.allclose(image.affine, mask.affine, atol=1e-4, rtol=0):
        raise ValueError("Image and mask geometry differ")
    labels = np.asarray(mask.dataobj)
    volume = np.asarray(image.dataobj, dtype=np.float32)
    unique, counts = np.unique(labels, return_counts=True)
    if not set(unique.tolist()).issubset({0, 1, 2, 3}):
        raise ValueError("Unexpected tumor label values")
    observed = volume[:, :, ::4]
    positive_observed = observed[np.isfinite(observed) & (observed > 0)]
    if positive_observed.size == 0:
        raise ValueError("No positive finite observed T2 voxels")
    scale = float(np.percentile(positive_observed, 99))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("Invalid observed-only intensity scale")
    sums = {"tumor": 0.0, "non_tumor_brain": 0.0}
    voxels = {"tumor": 0, "non_tumor_brain": 0}
    lesion_slices = 0
    targets = 0
    for lower in range(0, image.shape[2] - 4, 4):
        a = volume[:, :, lower]
        b = volume[:, :, lower + 4]
        for offset in (1, 2, 3):
            target = volume[:, :, lower + offset]
            if not np.isfinite(target).all():
                raise ValueError("Non-finite target T2 intensity")
            prediction = a + (b - a) * (offset / 4)
            absolute_error = np.abs(prediction - target) / scale
            lesion = labels[:, :, lower + offset] > 0
            background = (labels[:, :, lower + offset] == 0) & (target > 0)
            lesion_slices += bool(lesion.any())
            targets += 1
            for name, region in (("tumor", lesion), ("non_tumor_brain", background)):
                sums[name] += float(absolute_error[region].sum(dtype=np.float64))
                voxels[name] += int(region.sum())
    result = {
        "protocol": "DS007045_SINGLE_CASE_CPU_PILOT_PROTOCOL_2026-10-01.md",
        "version_scope": "current S3 / dataset_description v2.0.1",
        "files": records, "shape": image.shape,
        "label_voxel_counts": {str(int(k)): int(v) for k, v in zip(unique, counts)},
        "observed_positive_p99": scale,
        "target_slices": targets, "lesion_bearing_target_slices": lesion_slices,
        "region_target_voxels": voxels,
        "linear_interpolation_normalized_mae": {
            name: sums[name] / voxels[name] if voxels[name] else None for name in sums
        },
        "no_gpu": True,
        "interpretation": "Single-case metric feasibility only; no model or clinical claim",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
