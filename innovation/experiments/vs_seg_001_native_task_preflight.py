"""One previously observed training case: native T2 task software preflight."""

from __future__ import annotations

import hashlib
import io
import json
import time
import traceback
import zipfile
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, load_model, resource_gate

import nibabel as nib
import numpy as np
import pydicom
from skimage.draw import polygon

from vs_seg_001_label_pixel_feasibility import load_pair


OUT = ROOT / "experiments/vs_seg_001_native_task_preflight"
PLAN = ROOT / "VS_SEG_001_NATIVE_TASK_PREFLIGHT_PROTOCOL_2026-10-02.md"
JSON_CONTOURS = ROOT / "literature/source_cache/vs_seg_author_code_2026-10-01/preprocessing/createBIDSdataset/VS-SEG-BIDS-nonifti/sourcedata/contours/sub-001/anat/sub-001_contours_space-individual_T2w.json"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    result = {"patient": "VS-SEG-001", "segmenter_split": "training",
              "attempt": attempt, "protocol_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "independent_task_confirmation": False, "complete": False}
    start = time.perf_counter()
    try:
        result["resource_gate"] = resource_gate()
        volume, mask, _ = load_pair()
        if int(mask.sum()) != 7505:
            raise ValueError("Existing preflight planar TV mask changed")
        with zipfile.ZipFile(ROOT / "data/vs_seg_001_header_pilot/t2.zip") as archive:
            headers = [pydicom.dcmread(io.BytesIO(archive.read(n)), stop_before_pixels=True)
                       for n in archive.namelist() if n.lower().endswith(".dcm")]
        orientation = np.asarray(headers[0].ImageOrientationPatient, dtype=float)
        col_dir, row_dir = orientation[:3], orientation[3:]
        normal = np.cross(col_dir, row_dir)
        headers.sort(key=lambda ds: float(np.dot(normal, np.asarray(ds.ImagePositionPatient, dtype=float))))
        origins = np.asarray([list(map(float, ds.ImagePositionPatient)) for ds in headers])
        positions = origins @ normal
        spacing = float(np.median(np.diff(positions)))
        affine_lps = np.eye(4)
        affine_lps[:3, 0] = row_dir * float(headers[0].PixelSpacing[0])
        affine_lps[:3, 1] = col_dir * float(headers[0].PixelSpacing[1])
        affine_lps[:3, 2] = normal * spacing
        affine_lps[:3, 3] = origins[0]
        affine_ras = np.diag([-1., -1., 1., 1.]) @ affine_lps
        ornt = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine_ras), nib.orientations.axcodes2ornt("RAS"))
        image_ras = np.ascontiguousarray(nib.orientations.apply_orientation(volume, ornt))
        mask_ras = np.ascontiguousarray(nib.orientations.apply_orientation(mask, ornt))
        canonical_affine = affine_ras @ nib.orientations.inv_ornt_aff(ornt, volume.shape)
        if nib.aff2axcodes(canonical_affine) != ("R", "A", "S"):
            raise ValueError("Canonical orientation not RAS")
        result["geometry"] = {"native_shape": list(volume.shape), "native_axes": list(nib.aff2axcodes(affine_ras)),
                              "canonical_shape": list(image_ras.shape), "canonical_axes": list(nib.aff2axcodes(canonical_affine)),
                              "native_ras_affine": affine_ras.tolist(), "canonical_affine": canonical_affine.tolist(),
                              "spatial_resampling": False}
        original = json.loads(JSON_CONTOURS.read_text())[0]
        if original["structure_name"] != "TV":
            raise ValueError("Author original first contour is not TV")
        json_mask = np.zeros(volume.shape, dtype=bool)
        max_error = 0.0
        for contour in original["LPS_contour_points"]:
            pts = np.asarray(contour, dtype=float)
            coordinate = float(np.mean(pts @ normal))
            z = int(np.argmin(abs(positions - coordinate)))
            delta = pts - origins[z]
            error = float(np.max(abs(delta @ normal)))
            max_error = max(max_error, error)
            if error <= .001:
                rr = delta @ row_dir / float(headers[z].PixelSpacing[0])
                cc = delta @ col_dir / float(headers[z].PixelSpacing[1])
                r, c = polygon(rr, cc, shape=volume.shape[:2])
                json_mask[r, c, z] = True
        result["original_contour_check"] = {"file_sha256": hashlib.sha256(JSON_CONTOURS.read_bytes()).hexdigest(),
                                             "contours": len(original["LPS_contour_points"]), "max_native_plane_error_mm": max_error,
                                             "all_contours_native_plane_aligned": max_error <= .001,
                                             "slicerrt_surface_conversion_reproduced": False}
        if max_error <= .001:
            result["original_contour_check"].update({"planar_json_voxels": int(json_mask.sum()),
                "planar_json_vs_rtstruct_dice": float(2 * (json_mask & mask).sum() / (json_mask.sum() + mask.sum()))})
        model, proof = load_model()
        result["runtime"] = proof
        import torch
        from monai.inferers import sliding_window_inference
        from monai.transforms import NormalizeIntensity
        normalized = NormalizeIntensity()(image_ras[None].copy())
        result["normalization"] = {"native_mean": float(image_ras.mean()), "native_std": float(image_ras.std()),
                                   "normalized_mean": float(normalized.mean()), "normalized_std": float(normalized.std()),
                                   "nonzero_only": False, "channel_wise": False}
        input_tensor = torch.from_numpy(np.ascontiguousarray(normalized)).unsqueeze(0).cpu()
        forward_start = time.perf_counter()
        with torch.inference_mode():
            logits = sliding_window_inference(inputs=input_tensor, roi_size=(384, 384, 64),
                sw_batch_size=1, predictor=lambda x: model(x)[0], mode="gaussian")
        prediction = logits.argmax(dim=1)[0].numpy().astype(bool)
        if torch.cuda.is_initialized() or not bool(torch.isfinite(logits).all()):
            raise ValueError("Invalid CPU task inference")
        tp = int((prediction & mask_ras).sum())
        fp = int((prediction & ~mask_ras).sum())
        fn = int((~prediction & mask_ras).sum())
        segmentation_path = OUT / f"prediction_attempt_{attempt:02d}.npz"
        np.savez_compressed(segmentation_path, prediction_ras=prediction, affine=canonical_affine)
        result.update({"complete": True, "task_reference": "native planar TV RTSTRUCT mask, not original SlicerRT mask",
                       "native_planar_reference_dice": float(2 * tp / (2 * tp + fp + fn)),
                       "reference_voxels": int(mask_ras.sum()), "prediction_voxels": int(prediction.sum()),
                       "confusion": {"tp": tp, "fp": fp, "fn": fn},
                       "segmentation_seconds": time.perf_counter() - forward_start,
                       "prediction_sha256": hashlib.sha256(segmentation_path.read_bytes()).hexdigest(),
                       "cuda_initialized": torch.cuda.is_initialized(), "reconstruction_conditions_tested": 0})
    except Exception as exc:
        result.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    result["elapsed_seconds"] = time.perf_counter() - start
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
