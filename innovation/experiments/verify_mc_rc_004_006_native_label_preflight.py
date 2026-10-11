"""Independent raw-header, all-label and inverse integer-grid verification."""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import nibabel as nib
import numpy as np
import pydicom
from vs_seg_task_cpu_support import resource_gate

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ROOT / "literature/source_cache/mc_rc_004_006_native_headers_2026-10-02"
OUT = ROOT / "experiments/mc_rc_004_006_native_label_gate"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def points(shape):
    return np.array([[*v, 1] for v in itertools.product(*[(0, n - 1) for n in shape])], dtype=float).T


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resource_gate()
    ledger, first, followup = read(HEADERS / "attempt_01.json"), read(OUT / "attempt_01.json"), read(OUT / "resource_followup_attempt_01.json")
    by_uid = {r["series_uid"]: r for r in followup["series"]}
    errors, records, object_count, label_count = [], [], 0, 0
    if not ledger["complete"] or first["complete"] or not followup["complete"] or followup["original_label_attempt_complete"]:
        errors.append("Original resource failure/follow-up scope differs")
    for row in ledger["series"]:
        resource_gate()
        src, summary = row["source"], row["summary"]
        uid = src["SeriesInstanceUID"]
        extraction = read(HEADERS / row["header_file"])
        saved = {r["sop_uid"]: r for r in extraction["records"]}
        path = ROOT / row["transfer"]["file"]
        if sha(path) != row["transfer"]["sha256"] or sha(HEADERS / row["header_file"]) != row["header_sha256"]:
            errors.append("Raw ZIP/header hash differs " + uid)
        datasets = []
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if member.is_dir() or not member.filename.lower().endswith(".dcm"):
                    continue
                with archive.open(member) as f:
                    ds = pydicom.dcmread(f, stop_before_pixels=True)
                datasets.append(ds)
                object_count += 1
                prior = saved.get(str(ds.SOPInstanceUID))
                if prior is None:
                    errors.append("SOP absent from extraction " + uid)
                    continue
                if str(ds.PatientID) != src["PatientID"] or str(ds.StudyInstanceUID) != src["StudyInstanceUID"] or str(ds.SeriesInstanceUID) != uid or str(ds.Modality) != "MR":
                    errors.append("Raw identity differs " + uid)
                for attr, field in [("PixelSpacing", "pixel_spacing"), ("ImageOrientationPatient", "iop"), ("ImagePositionPatient", "ipp")]:
                    if not np.array_equal(np.asarray(ds.get(attr), dtype=float), np.array(prior[field])):
                        errors.append("Raw vector differs " + uid + " " + attr)
                for attr, field in [("Rows", "rows"), ("Columns", "columns"), ("SliceThickness", "slice_thickness")]:
                    if float(ds.get(attr)) != prior[field]:
                        errors.append("Raw scalar differs " + uid + " " + attr)
                if str(ds.get("MRAcquisitionType", "")) != prior["mr_acquisition_type"] or list(ds.get("ImageType", [])) != prior["image_type"] or str(ds.FrameOfReferenceUID) != prior["frame_uid"]:
                    errors.append("Raw acquisition/frame tags differ " + uid)
        if len(datasets) != src["ImageCount"] or len({str(d.SOPInstanceUID) for d in datasets}) != len(datasets):
            errors.append("Raw count/uniqueness differs " + uid)
        orient = np.asarray(datasets[0].ImageOrientationPatient, dtype=float)
        normal = np.cross(orient[:3], orient[3:])
        positions = np.array([d.ImagePositionPatient for d in datasets], dtype=float)
        positions = positions[np.argsort(positions @ normal)]
        n = len(positions)
        coefficients = np.linalg.lstsq(np.stack((np.ones(n), np.arange(n)), axis=1), positions, rcond=None)[0]
        origin, step = coefficients
        residual = float(np.linalg.norm(positions - origin - np.arange(n)[:, None] * step, axis=1).max())
        endpoint = (positions[-1] - positions[0]) / (n - 1)
        endpoint_residual = float(np.linalg.norm(positions - positions[0] - np.arange(n)[:, None] * endpoint, axis=1).max())
        affine = np.eye(4)
        affine[:3, 0] = orient[3:] * float(datasets[0].PixelSpacing[0])
        affine[:3, 1] = orient[:3] * float(datasets[0].PixelSpacing[1])
        affine[:3, 2], affine[:3, 3] = step, origin
        ras = np.diag([-1., -1., 1., 1.]) @ affine
        if not np.allclose(ras, summary["affine_rcz_ras"], rtol=0, atol=1e-9) or abs(residual - summary["max_affine_position_residual_mm"]) > 1e-9:
            errors.append("Independent full least-squares fit differs " + uid)
        gap = np.diff(positions @ normal)
        consistent = len({(int(d.Rows), int(d.Columns), str(d.FrameOfReferenceUID)) for d in datasets}) == 1
        consistent = consistent and all(np.max(abs(np.asarray(d.ImageOrientationPatient, dtype=float) - orient)) <= 1e-6 and np.max(abs(np.asarray(d.PixelSpacing, dtype=float) - np.asarray(datasets[0].PixelSpacing, dtype=float))) <= 1e-6 for d in datasets)
        ortho = max(abs(np.linalg.norm(orient[:3]) - 1), abs(np.linalg.norm(orient[3:]) - 1), abs(orient[:3] @ orient[3:])) <= 1e-4
        geometry_ok = consistent and ortho and all(int(d.get("NumberOfFrames", 1)) == 1 for d in datasets) and residual <= .02 and gap.min() > 1e-4 and abs(gap - np.median(gap)).max() <= .02
        original = all("ORIGINAL" in [str(v).upper() for v in d.get("ImageType", [])] and "DERIVED" not in [str(v).upper() for v in d.get("ImageType", [])] for d in datasets)
        derivative = any(any(token in (" ".join(str(v) for v in d.get("ImageType", [])) + " " + str(d.get("SeriesDescription", "")) + " " + str(d.get("DerivationDescription", ""))).upper() for token in ("MPR", "REFORMAT", "LOCALIZER")) for d in datasets)
        spacing = [float(datasets[0].PixelSpacing[0]), float(datasets[0].PixelSpacing[1]), float(np.linalg.norm(step))]
        thin = max(spacing) <= 1.5 and max(float(d.SliceThickness) for d in datasets) <= 1.5
        acquisition = all(str(d.get("MRAcquisitionType", "")) == "3D" for d in datasets)
        qualified = bool(geometry_ok and original and not derivative and thin and acquisition)
        if qualified != summary["header_qualified_candidate"]:
            errors.append("Independent header qualification differs " + uid)
        label = by_uid[uid]
        label_path = ROOT / label["label_file"]
        if sha(label_path) != label["label_sha256"]:
            errors.append("Extracted label hash differs " + uid)
        img = nib.load(label_path)
        foreground, values, all_finite = 0, set(), True
        # Independent fixed 4-plane streaming, instead of the primary adaptive block size.
        for start in range(0, img.shape[-1], 4):
            slab = np.asarray(img.dataobj[..., start:start + 4])
            all_finite = all_finite and bool(np.isfinite(slab).all())
            foreground += int((slab != 0).sum())
            values.update(np.unique(slab).tolist())
        label_count += 1
        if foreground != label["label_foreground_voxels"] or sorted(values) != label["label_values"] or list(img.shape) != label["label_shape"] or not all_finite:
            errors.append("Independent all-label streaming contents differ " + uid)
        integer = np.rint(np.linalg.solve(ras, img.affine)).astype(int)
        mat = integer[:3, :3]
        signed = np.all(np.sum(abs(mat), axis=0) == 1) and np.all(np.sum(abs(mat), axis=1) == 1) and np.array_equal(integer[-1], [0, 0, 0, 1])
        mapped = integer @ points(img.shape)
        shape = np.array([int(datasets[0].Rows), int(datasets[0].Columns), n])
        extent = np.array_equal(mapped[:3].min(axis=1), [0, 0, 0]) and np.array_equal(mapped[:3].max(axis=1), shape - 1)
        corner_error = float(np.linalg.norm(((ras @ integer - img.affine) @ points(img.shape))[:3], axis=0).max())
        grid_passed = bool(signed and extent and corner_error <= .05)
        qc, sc = int(img.header["qform_code"]), int(img.header["sform_code"])
        form_error = float(np.linalg.norm(((img.get_qform() - img.get_sform()) @ points(img.shape))[:3], axis=0).max()) if qc > 0 and sc > 0 else None
        source_passed = bool(qualified and grid_passed and values <= {0, 1} and all_finite and (qc > 0 or sc > 0) and (form_error is None or form_error <= .05))
        if grid_passed != label["grid"]["same_native_grid"] or abs(corner_error - label["grid"]["max_corner_world_error_mm"]) > 1e-8 or source_passed != label["header_and_label_grid_preflight_passed"]:
            errors.append("Independent inverse integer-grid/source check differs " + uid)
        records.append({
            "patient": src["PatientID"], "uid": uid, "raw_objects": n,
            "header_qualified": qualified, "native_spacing_rcz_mm": spacing,
            "nominal_thicknesses_mm": sorted({float(d.SliceThickness) for d in datasets}),
            "least_squares_max_residual_mm": residual, "endpoint_max_residual_mm": endpoint_residual,
            "grid_max_corner_error_mm": corner_error, "inverse_integer_grid_matrix": integer.tolist(),
            "label_foreground_voxels": foreground, "source_preflight_passed": source_passed,
            "photometric_interpretations": sorted({str(d.get("PhotometricInterpretation", "")) for d in datasets}),
            "transfer_syntaxes": sorted({str(d.file_meta.get("TransferSyntaxUID", "")) for d in datasets}),
            "bits_allocated": sorted({int(d.get("BitsAllocated", 0)) for d in datasets}),
            "rescale_slopes": sorted({float(d.get("RescaleSlope", 1)) for d in datasets}),
            "rescale_intercepts": sorted({float(d.get("RescaleIntercept", 0)) for d in datasets}),
        })
    counts = {
        "raw_DICOM_objects_checked": object_count, "series": len(records), "label_arrays_checked": label_count,
        "header_qualified_series": sum(r["header_qualified"] for r in records),
        "source_preflight_series": sum(r["source_preflight_passed"] for r in records),
        "source_preflight_patients": len({r["patient"] for r in records if r["source_preflight_passed"]}),
    }
    if object_count != 701 or len(records) != 8 or label_count != 8 or counts["source_preflight_series"] != followup["source_preflight_series_passed"]:
        errors.append("Fixed-eight independent verification scope/count differs")
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "verification_script_sha256": sha(__file__),
        "header_result_sha256": sha(HEADERS / "attempt_01.json"), "first_label_result_sha256": sha(OUT / "attempt_01.json"),
        "resource_followup_result_sha256": sha(OUT / "resource_followup_attempt_01.json"),
        "scope": "raw DICOM headers, independent fits and all-eight label/integer-grid source verification; no model performance",
        "counts": counts, "series": records, "errors": errors, "MR_pixel_arrays_decoded": False,
        "original_label_resource_gate_complete": False, "full_public_label_coverage_certified": False,
        "scientific_independent_validation_patients": 0,
    }
    (OUT / "independent_raw_geometry_grid_verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"counts": counts, "errors": errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
