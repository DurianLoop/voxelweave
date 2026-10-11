"""Independent DICOM coordinates, aligned-contour check, and known Fig.2 audit."""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path

import nibabel as nib
import numpy as np
import pydicom
from skimage.draw import polygon

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/vs_seg_original_mask_cpu_development"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    conversion = OUT / "attempt_03.json"
    report = {"conversion_sha256": sha(conversion), "script_sha256": sha(Path(__file__)), "errors": [], "patients": [], "independent_publication_claim": False}
    for row in json.loads(conversion.read_text())["patients"]:
        payload = json.loads((ROOT / row["input_file"]).read_text())
        masks_file = ROOT / row["masks_file"]
        if sha(masks_file) != row["masks_sha256"]:
            raise ValueError("Mask archive changed")
        saved = np.load(masks_file)
        with zipfile.ZipFile(ROOT / payload["source_inputs"]["image_zip"]["path"]) as archive:
            headers = [pydicom.dcmread(io.BytesIO(archive.read(n)), stop_before_pixels=True) for n in archive.namelist() if n.endswith(".dcm")]
        h = headers[0]
        direction = np.asarray(h.ImageOrientationPatient, dtype=float)
        normal = np.cross(direction[:3], direction[3:])
        headers.sort(key=lambda x: float(np.asarray(x.ImagePositionPatient, dtype=float) @ normal))
        native_shape = (int(h.Rows), int(h.Columns), len(headers))
        affine = saved["affine_ijk_ras"]
        errors_mm = []
        for z in (0, len(headers) // 2, len(headers) - 1):
            for r, c in ((0, 0), (11, 23), (native_shape[0] - 1, native_shape[1] - 1)):
                point_lps = np.asarray(headers[z].ImagePositionPatient, dtype=float) + direction[:3] * c * float(h.PixelSpacing[1]) + direction[3:] * r * float(h.PixelSpacing[0])
                point_ras = point_lps * [-1., -1., 1.]
                errors_mm.append(float(np.max(abs(point_ras - (affine @ [c, r, z, 1])[:3]))))
        original, rt = saved["original_mask_rcz"], saved["rtstruct_mask_rcz"]
        if original.shape != native_shape or rt.shape != native_shape or max(errors_mm) > 1e-6:
            report["errors"].append(row["patient"] + ": native grid mismatch")
        planar = np.zeros(native_shape, dtype=bool)
        for contour in payload["rtstruct_contours_lps"]:
            ras = np.asarray(contour) * [-1., -1., 1.]
            coordinates = nib.affines.apply_affine(np.linalg.inv(affine), ras)
            z = int(round(float(coordinates[:, 2].mean())))
            if np.max(abs(coordinates[:, 2] - z)) > 1e-3:
                raise ValueError("RTSTRUCT should be aligned to native grid")
            rr, cc = polygon(coordinates[:, 1], coordinates[:, 0], shape=native_shape[:2])
            planar[rr, cc, z] = True
        rec = {"patient": row["patient"], "max_independent_physical_coordinate_error_mm": max(errors_mm), "native_shape_rcz": native_shape, "original_vs_rt_dice": row["json_vs_rtstruct_dice"], "rtstruct_slicerrt_vs_independent_planar_voxel_differences": int((planar ^ rt).sum()), "original_json_positive_slices": np.flatnonzero(original.any(axis=(0, 1))).tolist(), "rtstruct_positive_slices": np.flatnonzero(rt.any(axis=(0, 1))).tolist()}
        if row["patient"] == "VS-SEG-001":
            previous = ROOT / "experiments/vs_seg_001_native_task_preflight/attempt_01.json"
            old = json.loads(previous.read_text())
            prediction_file = previous.parent / "prediction_attempt_01.npz"
            if sha(prediction_file) != old["prediction_sha256"]:
                raise ValueError("Previous training-case prediction changed")
            prediction = np.load(prediction_file)["prediction_ras"]
            affine_rcz = affine[:, [1, 0, 2, 3]]
            transform = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine_rcz), nib.orientations.axcodes2ornt("RAS"))
            def dice(reference):
                ref = nib.orientations.apply_orientation(reference, transform)
                return float(2 * (prediction & ref).sum() / (prediction.sum() + ref.sum()))
            rec["same_saved_training_prediction_reference_audit"] = {"previous_prediction_sha256": old["prediction_sha256"], "rtstruct_dice": dice(rt), "original_json_dice": dice(original), "new_model_inference": False, "independent_confirmation": False}
            if abs(dice(rt) - old["native_planar_reference_dice"]) > 1e-12:
                report["errors"].append("Old native preflight orientation/reference does not agree")
        if row["patient"] == "VS-SEG-182":
            rec["published_fig2_first_last_slice_pattern_reproduced"] = rec["original_json_positive_slices"] == list(range(43, 49)) and rec["rtstruct_positive_slices"] == list(range(44, 48))
            if not rec["published_fig2_first_last_slice_pattern_reproduced"]:
                report["errors"].append("Published Fig.2 endpoint pattern not reproduced")
        report["patients"].append(rec)
    target = OUT / "independent_geometry_and_reference_verification.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
