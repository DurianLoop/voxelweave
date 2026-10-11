"""Single-case CPU feasibility for native T2 and RTSTRUCT tumor masks."""

from __future__ import annotations

import hashlib
import io
import json
import os
import zipfile
from collections import defaultdict
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
import pydicom
from PIL import Image
from scipy.interpolate import PchipInterpolator
from skimage.draw import polygon


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/vs_seg_001_header_pilot"
HEADER = ROOT / "literature/source_cache/vs_seg_001_two_series_headers_2026-10-01/index.json"
GEOMETRY = ROOT / "literature/source_cache/vs_seg_001_contour_geometry_2026-10-01.json"
PROTOCOL = ROOT / "VS_SEG_001_LABEL_PIXEL_FEASIBILITY_PROTOCOL_2026-10-01.md"
OUT = ROOT / "experiments/vs_seg_001_label_pixel_feasibility"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_dicom(zip_path: Path) -> list:
    with zipfile.ZipFile(zip_path) as archive:
        return [pydicom.dcmread(io.BytesIO(archive.read(name)))
                for name in archive.namelist() if name.endswith(".dcm")]


def load_pair() -> tuple[np.ndarray, np.ndarray, dict]:
    records = json.loads(HEADER.read_text(encoding="utf-8"))
    for item in records:
        if sha256(ROOT / item["file"]) != item["sha256"]:
            raise ValueError("Official source ZIP changed")
    if not json.loads(GEOMETRY.read_text(encoding="utf-8"))["t2_tumor_contour_gate"]:
        raise ValueError("Frozen T2 contour geometry gate failed")
    images = read_dicom(SOURCE / "t2.zip")
    structure, = read_dicom(SOURCE / "rtstruct.zip")
    orientation = np.asarray(images[0].ImageOrientationPatient, dtype=np.float64)
    col_dir, row_dir = orientation[:3], orientation[3:]
    normal = np.cross(col_dir, row_dir)
    images.sort(key=lambda ds: float(np.dot(normal, np.asarray(ds.ImagePositionPatient, dtype=np.float64))))
    if len(images) != 80 or len({str(ds.SOPInstanceUID) for ds in images}) != 80:
        raise ValueError("Expected 80 original T2 slices")
    positions = np.array([np.dot(normal, np.asarray(ds.ImagePositionPatient, dtype=np.float64)) for ds in images])
    if not np.allclose(np.diff(positions), 1.5, rtol=0, atol=1e-4):
        raise ValueError("Nonuniform original T2 plane spacing")
    volume = np.stack([ds.pixel_array.astype(np.float32) for ds in images], axis=-1)
    if not np.isfinite(volume).all() or any(str(ds.PhotometricInterpretation) != "MONOCHROME2" for ds in images):
        raise ValueError("Invalid T2 pixel data")
    sop_to_index = {str(ds.SOPInstanceUID): i for i, ds in enumerate(images)}
    names = {int(x.ROINumber): str(x.ROIName) for x in structure.StructureSetROISequence}
    tumor = next(x for x in structure.ROIContourSequence if names[int(x.ReferencedROINumber)] == "TV")
    mask = np.zeros(volume.shape, dtype=bool)
    count_by_slice = defaultdict(int)
    for contour in tumor.ContourSequence:
        ref = str(contour.ContourImageSequence[0].ReferencedSOPInstanceUID)
        ds = images[sop_to_index[ref]]
        origin = np.asarray(ds.ImagePositionPatient, dtype=np.float64)
        points = np.asarray(contour.ContourData, dtype=np.float64).reshape(-1, 3)
        delta = points - origin
        if float(np.max(np.abs(delta @ normal))) > 1e-3:
            raise ValueError("Tumor contour off reference plane")
        rr = delta @ row_dir / float(ds.PixelSpacing[0])
        cc = delta @ col_dir / float(ds.PixelSpacing[1])
        if rr.min() < -.5 or cc.min() < -.5 or rr.max() > int(ds.Rows) - .5 or cc.max() > int(ds.Columns) - .5:
            raise ValueError("Tumor contour outside T2 image")
        row, column = polygon(rr, cc, shape=volume.shape[:2])
        z = sop_to_index[ref]
        mask[row, column, z] = True
        count_by_slice[z] += 1
    if len(count_by_slice) != 13 or any(x != 1 for x in count_by_slice.values()):
        raise ValueError("Unexpected tumor contour multiplicity")
    return volume, mask, {"t2_slice_positions_mm": positions.tolist(),
                          "contour_slice_indices": sorted(count_by_slice),
                          "tumor_pixels_by_slice": {str(z): int(mask[:, :, z].sum()) for z in sorted(count_by_slice)},
                          "volume_shape": list(volume.shape)}


def metrics(output: np.ndarray, target: np.ndarray, roi: np.ndarray, span: float) -> dict:
    errors = (output - target)[roi].astype(np.float64)
    return {"pixels": int(roi.sum()), "normalized_mse": float(np.mean(errors ** 2) / span ** 2),
            "mae": float(np.mean(np.abs(errors)))}


def overlay(volume: np.ndarray, mask: np.ndarray, z: int, path: Path) -> None:
    plane = volume[:, :, z]
    lo, hi = np.percentile(plane[plane > 0], [1, 99])
    gray = np.uint8(np.clip((plane - lo) / (hi - lo), 0, 1) * 255)
    rgb = np.repeat(gray[:, :, None], 3, axis=2)
    from scipy.ndimage import binary_erosion
    edge = mask[:, :, z] & ~binary_erosion(mask[:, :, z])
    rgb[edge] = [0, 255, 180]
    Image.fromarray(rgb).save(path)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    result = {"patient": "VS-SEG-001", "protocol_sha256": sha256(PROTOCOL),
              "source_index_sha256": sha256(HEADER), "contour_gate_sha256": sha256(GEOMETRY),
              "gpu_used": False, "model_inference": False}
    try:
        volume, mask, source = load_pair()
        result.update(source)
        anchors = volume[:, :, ::4]
        span = float(anchors.max() - anchors.min())
        if not np.isfinite(span) or span <= 0:
            raise ValueError("Invalid observed-only span")
        eligible = {"1": [], "3": []}
        supports = {}
        for residue in (1, 3):
            for z in range(residue, volume.shape[2] - 4, 4):
                i = z // 4
                left, right = anchors[:, :, i], anchors[:, :, i + 1]
                support = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                           (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
                supports[z] = support
                if int((mask[:, :, z] & support).sum()) >= 64 and i >= 1 and i + 2 < anchors.shape[2]:
                    eligible[str(residue)].append(z)
        targets = {}
        for residue in (1, 3):
            candidates = eligible[str(residue)]
            if len(candidates) < 3:
                raise ValueError(f"Insufficient residue-{residue} eligible targets")
            chosen = [candidates[(len(candidates) - 1) // 3],
                      candidates[2 * (len(candidates) - 1) // 3]]
            if len(set(chosen)) != 2:
                raise ValueError("Selected target indices are not distinct")
            targets[str(residue)] = chosen
        rows = []
        for residue in (1, 3):
            for z in targets[str(residue)]:
                i = z // 4
                rel = (z - 4 * i) / 4
                left, right = anchors[:, :, i], anchors[:, :, i + 1]
                linear = (1 - rel) * left + rel * right
                indices = np.arange(i - 1, i + 3)
                pchip = PchipInterpolator(4 * indices, np.moveaxis(anchors[:, :, indices], -1, 0), axis=0)(z)
                target = volume[:, :, z]
                row = {"z": z, "residue": residue}
                for name, roi in (("tumor", mask[:, :, z] & supports[z]), ("support", supports[z])):
                    row[name] = {"linear": metrics(linear, target, roi, span),
                                 "pchip": metrics(pchip, target, roi, span)}
                rows.append(row)
        result.update({"complete": True, "observed_span": span,
                       "eligible_targets": eligible, "targets": targets,
                       "rows": rows, "tumor_voxels": int(mask.sum())})
        overlay(volume, mask, sorted(source["contour_slice_indices"])[6], OUT / "tumor_overlay.png")
    except Exception as exc:
        result.update({"complete": False, "failure_type": type(exc).__name__,
                       "failure_reason": str(exc)[:250]})
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("t2_slice_positions_mm", "rows")}, indent=2))


if __name__ == "__main__":
    main()
