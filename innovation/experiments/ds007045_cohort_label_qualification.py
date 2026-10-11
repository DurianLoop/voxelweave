"""CPU-only, outcome-independent ds007045 mask and T2-header qualification."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import shutil
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import nibabel as nib
import numpy as np

from msd_task01_source import selected_targets


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "DS007045_COHORT_LABEL_QUALIFICATION_PROTOCOL_2026-10-01.md"
SOURCE = ROOT / "literature/source_cache/ds007045_current_pair_audit_2026-10-01"
INVENTORY = SOURCE / "result.json"
DESCRIPTION = ROOT / "literature/source_cache/ds007045_pair_inventory_2026-10-01/dataset_description.json"
OUT = ROOT / "experiments/ds007045_cohort_label_qualification"
DATA = ROOT / "data/ds007045_label_qualification"
BASE = "https://s3.amazonaws.com/openneuro.org/"
NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
MIN_FREE = 15_000_000_000
DESC_SHA256 = "748fb52a1d943c6f50bb6e4795082e973c4a8694e01a287383a9bf1f20fff763"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def official_get(url: str, cap: int, headers: dict | None = None) -> tuple[bytes, int, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0", **(headers or {})})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for attempt in range(2):
        try:
            with opener.open(request, timeout=35) as response:
                body = response.read(cap + 1)
                if len(body) > cap:
                    raise ValueError("Official response exceeded byte cap")
                return body, response.status, dict(response.headers)
        except (urllib.error.URLError, TimeoutError):
            if attempt:
                raise
            time.sleep(2)
    raise AssertionError("unreachable")


def source_sizes(group: str) -> dict[str, int]:
    result = {}
    for path in sorted(SOURCE.glob(f"{group}_page_*.xml")):
        root = ET.parse(path).getroot()
        for entry in root.findall("s:Contents", NS):
            key = entry.findtext("s:Key", namespaces=NS)
            size = int(entry.findtext("s:Size", namespaces=NS))
            if key in result:
                raise ValueError(f"Duplicate official listing key: {key}")
            result[key] = size
    return result


def inspect(case: str, t2_sizes: dict, mask_sizes: dict) -> dict:
    if shutil.disk_usage(DATA).free < MIN_FREE:
        raise OSError("15 GB free-space floor reached")
    t2_key = f"ds007045/derivatives/processing/{case}/{case}_t2_MNI152_brain.nii.gz"
    mask_key = f"ds007045/derivatives/segmentation/{case}/{case}_MNI152_tumor-mask.nii.gz"
    t2_size, mask_size = t2_sizes[t2_key], mask_sizes[mask_key]
    if t2_size <= 65_536 or not 0 < mask_size <= 100_000:
        raise ValueError("Listed object size outside frozen bounds")
    mask_body, mask_status, mask_headers = official_get(BASE + mask_key, 100_000)
    if (mask_status != 200 or len(mask_body) != mask_size or
            int(mask_headers.get("Content-Length", -1)) != mask_size):
        raise ValueError("Unexpected full mask response")
    mask_path = DATA / f"{case}_tumor-mask.nii.gz"
    mask_path.write_bytes(mask_body)
    t2_body, t2_status, t2_headers = official_get(
        BASE + t2_key, 65_536, {"Range": "bytes=0-65535"})
    if (t2_status != 206 or len(t2_body) != 65_536 or
            t2_headers.get("Content-Range") != f"bytes 0-65535/{t2_size}"):
        raise ValueError("Unexpected T2 prefix range response")
    with gzip.GzipFile(fileobj=io.BytesIO(t2_body)) as stream:
        header_bytes = stream.read(352)
    if len(header_bytes) != 352:
        raise ValueError("Incomplete T2 NIfTI header")
    t2_header = nib.Nifti1Header.from_fileobj(io.BytesIO(header_bytes))
    mask_image = nib.load(str(mask_path))
    mask_header = mask_image.header
    t2_shape, mask_shape = t2_header.get_data_shape(), mask_header.get_data_shape()
    if (len(t2_shape) != 3 or t2_shape != mask_shape or
            not np.isfinite(t2_header.get_zooms()).all() or
            any(v <= 0 for v in t2_header.get_zooms())):
        raise ValueError("Non-3D, mismatched or invalid image/mask geometry")
    affine_diff = float(np.max(np.abs(t2_header.get_best_affine() - mask_image.affine)))
    if not np.isfinite(affine_diff) or affine_diff > 1e-4:
        raise ValueError(f"Image/mask affine mismatch: {affine_diff}")
    mask = np.asarray(mask_image.dataobj)
    if mask.dtype.kind not in "iu" or mask.min() < 0 or mask.max() > 3:
        raise ValueError("Mask values outside integer {0,1,2,3}")
    counts = np.bincount(mask.ravel().astype(np.uint8), minlength=4)
    if not counts[1:].sum():
        raise ValueError("Empty tumor mask")
    targets = selected_targets(mask)
    return {"case": case, "eligible": True,
            "t2_key": t2_key, "t2_listed_bytes": t2_size,
            "t2_prefix_65536_sha256": hashlib.sha256(t2_body).hexdigest(),
            "mask_key": mask_key, "mask_bytes": mask_size,
            "mask_sha256": hashlib.sha256(mask_body).hexdigest(),
            "mask_local_path": mask_path.relative_to(ROOT).as_posix(),
            "shape": list(t2_shape), "affine_max_difference_mm": affine_diff,
            "label_voxel_counts": {str(i): int(value) for i, value in enumerate(counts)},
            "targets": targets}


def main() -> None:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--preflight-one"):
        raise ValueError("Supported: full run or --preflight-one")
    preflight = len(sys.argv) == 2
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    cases = inventory["paired_subjects_list"]
    if len(cases) != 363 or len(set(cases)) != 363:
        raise ValueError("Current S3 cohort inventory changed")
    if digest(DESCRIPTION) != DESC_SHA256:
        raise ValueError("Archived v2.0.1 description hash changed")
    live_desc, status, _ = official_get(BASE + "ds007045/dataset_description.json", 10_000)
    if status != 200 or hashlib.sha256(live_desc).hexdigest() != DESC_SHA256:
        raise ValueError("Live dataset description changed before run")
    t2_sizes = source_sizes("processing")
    mask_sizes = source_sizes("segmentation")
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    contract = {"protocol_sha256": digest(PROTOCOL),
                "inventory_sha256": digest(INVENTORY),
                "description_sha256": DESC_SHA256,
                "script_sha256": digest(Path(__file__)),
                "attempted_cases": 363, "gpu_used": False,
                "t2_voxels_read": False}
    contract_path = OUT / "run_contract.json"
    if contract_path.exists():
        if json.loads(contract_path.read_text(encoding="utf-8")) != contract:
            raise ValueError("Existing run contract differs")
    else:
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    case_dir = OUT / "cases"
    case_dir.mkdir(exist_ok=True)
    selected = cases[:1] if preflight else cases
    records = []
    for index, case in enumerate(selected, 1):
        path = case_dir / f"{case}.json"
        if path.exists():
            row = json.loads(path.read_text(encoding="utf-8"))
            if row.get("contract_sha256") != digest(contract_path):
                raise ValueError(f"Existing case contract differs: {case}")
        else:
            try:
                row = inspect(case, t2_sizes, mask_sizes)
            except Exception as exc:
                row = {"case": case, "eligible": False,
                       "failure_type": type(exc).__name__, "failure_reason": str(exc)[:200]}
            row["contract_sha256"] = digest(contract_path)
            path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        records.append(row)
        if index % 20 == 0 or index == len(selected):
            print(f"ds007045 label qualification {index}/{len(selected)} eligible={sum(r['eligible'] for r in records)}", flush=True)
    live_desc, status, _ = official_get(BASE + "ds007045/dataset_description.json", 10_000)
    if status != 200 or hashlib.sha256(live_desc).hexdigest() != DESC_SHA256:
        raise ValueError("Live dataset description changed after run")
    summary = {"protocol_sha256": digest(PROTOCOL),
               "run_contract_sha256": digest(contract_path),
               "attempted": len(selected), "eligible": sum(r["eligible"] for r in records),
               "failed": [r for r in records if not r["eligible"]],
               "no_gpu": True, "no_t2_voxels": True,
               "complete_cohort": not preflight}
    (OUT / ("preflight_summary.json" if preflight else "summary.json")).write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "failed"}, indent=2))


if __name__ == "__main__":
    main()
