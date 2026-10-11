"""Audit all extracted MSValid first-T2 images before model inference."""
from __future__ import annotations

import gzip
import json
import zlib
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
QUALIFIED = ROOT / "literature/msvalid_geometry_qualification.json"
MANIFEST = ROOT / "literature/msvalid_extraction_manifest.json"
OUT = ROOT / "literature/msvalid_integrity_audit.json"


def main() -> None:
    qualified = json.loads(QUALIFIED.read_text(encoding="utf-8"))
    extracted = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = {r["patient"]: r for r in extracted["records"]}
    results = []
    for patient in qualified["patients"]:
        pid = patient["patient"]
        entry = records[pid]
        path = ROOT / entry["path"]
        reasons = []
        checksum = 0
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                checksum = zlib.crc32(chunk, checksum)
        if f"{checksum:08x}" != patient["zip_crc32"]:
            reasons.append("zip_crc_mismatch")
        gzip_bytes = 0
        try:
            with gzip.open(path, "rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    gzip_bytes += len(chunk)
        except (OSError, EOFError, zlib.error):
            reasons.append("gzip_stream_invalid")
        try:
            image = nib.load(str(path))
            if tuple(image.shape) != tuple(patient["shape"]):
                reasons.append("nifti_shape_changed")
            volume = image.get_fdata(dtype=np.float32)
            if not np.isfinite(volume).all():
                reasons.append("nonfinite_pixels")
            if float(volume.max()) <= float(volume.min()):
                reasons.append("constant_pixels")
        except (OSError, EOFError, ValueError, zlib.error):
            reasons.append("nifti_pixels_unreadable")
        results.append({"patient": pid, "path": entry["path"], "gzip_uncompressed_bytes": gzip_bytes,
                        "crc32": f"{checksum:08x}", "qualified": not reasons, "reasons": reasons})
        if len(results) % 10 == 0 or len(results) == len(qualified["patients"]):
            print(f"audited {len(results)}/{len(qualified['patients'])}", flush=True)
    OUT.write_text(json.dumps({"patients_total": len(results),
                               "patients_passed": sum(r["qualified"] for r in results),
                               "records": results}, indent=2) + "\n", encoding="utf-8")
    if any(not r["qualified"] for r in results):
        raise SystemExit("Input integrity failures; inspect audit before inference")


if __name__ == "__main__":
    main()
