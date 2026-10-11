"""Bounded official MSD tar-member transfer and frozen ROI qualification."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import shutil
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy.ndimage import distance_transform_edt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "literature" / "source_cache" / "msd_task01_official_2026-10-01"
INDEX = SOURCE / "tar_index_full.json"
DATASET = SOURCE / "dataset.json"
DATA = ROOT / "data" / "msd_task01_brain_tumour"
MIN_FREE_BYTES = 15_000_000_000
HEADERS = SOURCE / "all_training_pair_headers.json"
HEADER_RETRY = SOURCE / "brats230_header_transport_retry.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_record(scan: str, kind: str, indexed: dict, entries: dict) -> tuple[dict, Path]:
    if kind not in ("imagesTr", "labelsTr") or not scan.startswith("BRATS_"):
        raise ValueError("Invalid official case/member")
    name = f"Task01_BrainTumour/{kind}/{scan}.nii.gz"
    if name not in entries or entries[name]["type"] != "0":
        raise ValueError("Exact official tar member missing")
    return entries[name], DATA / kind / f"{scan}.nii.gz"


def fetch_member(entry: dict, destination: Path, indexed: dict) -> dict:
    if shutil.disk_usage(DATA.parent).free < MIN_FREE_BYTES:
        raise OSError("Free-space floor would be violated")
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected = entry["size"]
    if expected <= 0 or expected > 15_000_000:
        raise ValueError("Member size outside frozen bound")
    if not destination.exists():
        first, last = entry["data_offset"], entry["data_offset"] + expected - 1
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        request = urllib.request.Request(indexed["tar_url"], headers={
            "Range": f"bytes={first}-{last}", "User-Agent": "MRI-source-audit/1.0"})
        with opener.open(request, timeout=90) as response:
            if (response.status != 206 or
                    response.headers.get("Content-Range") != f"bytes {first}-{last}/{indexed['tar_bytes']}" or
                    response.headers.get("ETag") != indexed["tar_etag"]):
                raise ValueError("Official S3 object/Range response changed")
            content = response.read(expected + 1)
        if len(content) != expected:
            raise ValueError("Exact tar member transfer length changed")
        destination.write_bytes(content)
    if destination.stat().st_size != expected:
        raise ValueError("Stored member size differs from tar index")
    uncompressed = 0
    with gzip.open(destination, "rb") as stream:
        while chunk := stream.read(1_048_576):
            uncompressed += len(chunk)
    return {"member": entry["name"], "compressed_bytes": expected,
            "compressed_sha256": sha256(destination),
            "uncompressed_bytes_crc_checked": uncompressed,
            "local_path": destination.relative_to(ROOT).as_posix()}


@lru_cache(maxsize=1)
def frozen_headers() -> dict:
    report = json.loads(HEADERS.read_text(encoding="utf-8"))
    records = {row["scan"]: row for row in report["records"] if row["eligible"]}
    retry = json.loads(HEADER_RETRY.read_text(encoding="utf-8"))
    if (report["pairs_attempted"] != 484 or len(records) != 483 or
            retry["scan"] != "BRATS_230" or not retry["same_grid"]):
        raise ValueError("Frozen header qualification changed")
    records[retry["scan"]] = retry
    return records


def load_exact_pair(scan: str, indexed: dict, entries: dict) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    metadata = []
    paths = []
    for kind in ("imagesTr", "labelsTr"):
        entry, destination = source_record(scan, kind, indexed, entries)
        metadata.append(fetch_member(entry, destination, indexed))
        paths.append(destination)
    frozen = frozen_headers()[scan]
    for kind, path in zip(("image", "label"), paths):
        with gzip.open(path, "rb") as stream:
            header_hash = hashlib.sha256(stream.read(352)).hexdigest()
        if header_hash != frozen[kind]["header_352_sha256"]:
            raise ValueError(f"Decoded {kind} header differs from frozen qualification")
    image, label = (nib.load(str(path)) for path in paths)
    if (image.shape != (240, 240, 155, 4) or label.shape != (240, 240, 155) or
            image.get_data_dtype() != np.dtype("float32") or
            label.get_data_dtype() != np.dtype("uint8") or
            not np.allclose(image.affine, label.affine, atol=1e-4, rtol=0)):
        raise ValueError("Decoded NIfTI differs from frozen same-grid header")
    if (not np.allclose(image.affine, frozen["image"]["best_affine"], atol=1e-4, rtol=0) or
            not np.allclose(label.affine, frozen["label"]["best_affine"], atol=1e-4, rtol=0)):
        raise ValueError("Decoded affine differs from frozen qualification")
    t2 = np.asarray(image.dataobj[..., 3], dtype=np.float32)
    mask = np.asarray(label.dataobj, dtype=np.uint8)
    if not np.isfinite(t2).all() or not np.isin(mask, [0, 1, 2, 3]).all():
        raise ValueError("Nonfinite T2 or unexpected label code")
    return t2, mask, metadata


def selected_targets(mask: np.ndarray) -> dict[str, list[int]]:
    depth = mask.shape[2]
    anchors = {phase: list(range(phase, depth, 4)) for phase in (0, 2)}
    output: dict[str, list[int]] = {}
    for residue in (1, 3):
        candidates = []
        for z in range(residue, depth, 4):
            if (all(sum(anchor < z for anchor in anchors[phase]) >= 2 and
                    sum(anchor > z for anchor in anchors[phase]) >= 2 for phase in (0, 2)) and
                    int(np.count_nonzero(mask[:, :, z])) >= 64):
                candidates.append(z)
        if len(candidates) < 2:
            raise ValueError(f"Fewer than two tumor-positive targets in residue {residue}")
        m = len(candidates)
        positions = [math.floor((m - 1) / 3), math.ceil(2 * (m - 1) / 3)]
        if positions[0] == positions[1]:
            raise ValueError("Target quantiles were not distinct")
        output[str(residue)] = [candidates[position] for position in positions]
    return output


def region_masks(t2: np.ndarray, label: np.ndarray, z: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    left_index = (z // 4) * 4
    right_index = left_index + 4
    left, right = t2[:, :, left_index], t2[:, :, right_index]
    support = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
               (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
    lesion = (label[:, :, z] > 0) & support
    size = int(lesion.sum())
    if size < 64:
        raise ValueError("Fewer than 64 labeled pixels in acquired support")
    normal = (label[:, :, z] == 0) & support
    if int(normal.sum()) < size:
        raise ValueError("Insufficient same-area label-negative control")
    distances = distance_transform_edt(~lesion).ravel()
    candidates = np.flatnonzero(normal.ravel())
    order = np.lexsort((candidates, distances[candidates]))
    local = np.zeros(normal.size, dtype=bool)
    local[candidates[order[:size]]] = True
    return support, lesion, local.reshape(normal.shape)


def official_index() -> tuple[dict, dict]:
    indexed = json.loads(INDEX.read_text(encoding="utf-8"))
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    if indexed["tar_bytes"] != 7_608_266_240 or len(dataset["training"]) != 484:
        raise ValueError("Official source identity changed")
    entries = {item["name"]: item for item in indexed["entries"]}
    return indexed, entries
