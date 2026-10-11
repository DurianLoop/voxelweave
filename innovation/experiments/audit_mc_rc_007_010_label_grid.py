"""Fixed seven labels, bounded streaming arrays and integer native-grid audit."""
from __future__ import annotations
import csv
import json
import math
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import nibabel as nib
import numpy as np
from audit_mc_rc_three_patient_label_grid import best_grid_transform, corners, sha, read, write
from vs_seg_task_cpu_support import resource_gate
ROOT = Path(__file__).resolve().parents[1]
HEADERS = ROOT / "literature/source_cache/mc_rc_007_010_native_headers_2026-10-02"
PRIOR = ROOT / "literature/source_cache/mc_rc_three_patient_headers_2026-10-02"
SELECTION = ROOT / "experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json"
PLAN = ROOT / "MC_RC_007_010_SOURCE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md"
OUT = ROOT / "experiments/mc_rc_007_010_native_label_gate"
DATA = ROOT / "data/mc_rc_007_010_label_grid"
PREFIX = "VS-MC-RC-Segmentations_with_pathname_spreadsheet-Release2023/VS-MC-RC segmentations-NIfTI-Release 2023/"

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resources = resource_gate()
    selected, ledger, prior = read(SELECTION), read(HEADERS / "attempt_01.json"), read(PRIOR / "attempt_01.json")
    expected = {r["source"]["SeriesInstanceUID"] for r in selected["next_batch_series"]}
    if len(expected) != 7 or len(ledger["series"]) != 7 or {r["source"]["SeriesInstanceUID"] for r in ledger["series"]} != expected:
        raise ValueError("Fixed-seven source scope incomplete; wait for source task rather than restart")
    artifact_path = ROOT / "experiments/mc_rc_native_t2_label_gate/official_pathnames_artifact_read.json"
    artifact, csv_path = read(artifact_path), PRIOR / "official_label_metadata_00_attempt_01.csv"
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        cells = list(csv.reader(f))
    if cells != artifact["values"] or sha(csv_path) != artifact["source_sha256"]:
        raise ValueError("Previously authenticated full CSV/artifact read differs")
    mapping = {r["series_instance_uid"]: r for r in (dict(zip(cells[0], row)) for row in cells[1:])}
    if len(mapping) != len(cells) - 1:
        raise ValueError("Duplicate metadata UID")
    zip_path = ROOT / prior["labels"]["transfer"]["file"]
    if sha(zip_path) != prior["labels"]["transfer"]["sha256"]:
        raise ValueError("Official label ZIP hash differs")
    OUT.mkdir(exist_ok=False)
    DATA.mkdir(exist_ok=False)
    result = {"created_utc": datetime.now(timezone.utc).isoformat(), "script_sha256": sha(__file__), "plan_sha256": sha(PLAN), "grid_helper_sha256": sha(ROOT / "experiments/audit_mc_rc_three_patient_label_grid.py"),
              "header_result_sha256": sha(HEADERS / "attempt_01.json"), "selection_sha256": sha(SELECTION), "official_label_zip_sha256": sha(zip_path), "source_csv_sha256": sha(csv_path), "artifact_read_sha256": sha(artifact_path), "resources": resources,
              "max_label_nominal_bytes": 400_000_000, "max_total_nominal_bytes": 2_000_000_000, "max_block_bytes": 32_000_000, "max_zip_member_bytes": 50_000_000, "max_total_zip_member_bytes": 150_000_000,
              "scope": "all fixed-seven official labels/native-grid source qualification; no reconstruction/segmentation performance", "header_attempt_complete": ledger["complete"], "MR_pixel_arrays_decoded": False,
              "label_arrays_decoded": False, "full_public_label_coverage_certified": False, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False, "complete": False, "series": []}
    rows, members_total, nominal_total, images = [], 0, 0, {}
    with zipfile.ZipFile(zip_path) as archive:
        for row in ledger["series"]:
            resource_gate()
            src, summary = row["source"], row.get("summary", {})
            uid = src["SeriesInstanceUID"]
            entry = {"patient": src["PatientID"], "series_uid": uid, "study_uid": src["StudyInstanceUID"], "description": src["SeriesDescription"], "header_qualified_candidate": summary.get("header_qualified_candidate", False), "header_sha256": row.get("header_sha256"), "label_inspection_complete": False, "header_and_label_grid_preflight_passed": False}
            try:
                m = mapping[uid]
                if m["patient_id"] != src["PatientID"] or m["study_instance_uid"] != src["StudyInstanceUID"] or int(m["num_files"]) != src["ImageCount"] or not m["SegmentationPath"]:
                    raise ValueError("Exact patient/study/count/path UID linkage differs")
                member_name = PREFIX + m["SegmentationPath"]
                member = archive.getinfo(member_name)
                if member.file_size > 50_000_000 or members_total + member.file_size > 150_000_000:
                    raise ValueError("Fixed label ZIP payload budget exceeded")
                payload = archive.read(member)
                members_total += len(payload)
                dest = DATA / (src["PatientID"] + "_" + uid + "_label_attempt_01.nii.gz")
                with dest.open("xb") as stream:
                    stream.write(payload)
                entry.update(label_file=dest.relative_to(ROOT).as_posix(), label_sha256=sha(dest), label_zip_member=member_name, zip_crc32=f"{member.CRC:08x}", zip_crc32_verified=True, label_member_bytes=len(payload))
                img = nib.load(dest)
                if len(img.shape) != 3:
                    raise ValueError("Label is not 3D")
                width = np.dtype(img.get_data_dtype()).itemsize
                if img.dataobj.slope != 1 or img.dataobj.inter != 0:
                    width = max(width, 8)
                nominal = math.prod(img.shape) * width
                entry.update(nominal_array_bytes=nominal, estimated_element_bytes=width)
                nominal_total += nominal
                images[uid] = img
            except Exception as exc:
                entry["error"] = f"{type(exc).__name__}: {exc}"
            rows.append(entry)
    # All nominal headers/caps are inspected before decoding any new label slab.
    global_budget_ok = nominal_total <= 2_000_000_000 and all(r.get("nominal_array_bytes", 0) <= 400_000_000 for r in rows)
    header_by_uid = {r["source"]["SeriesInstanceUID"]: r for r in ledger["series"]}
    for entry in rows:
        resource_gate()
        uid = entry["series_uid"]
        if "error" in entry:
            continue
        if not global_budget_ok:
            entry["error"] = "Fixed seven-label nominal resource budget exceeded before array decode"
            continue
        try:
            img = images[uid]
            shape, width = list(img.shape), entry["estimated_element_bytes"]
            step = min(shape[2], 32_000_000 // (shape[0] * shape[1] * width))
            if step < 1:
                raise ValueError("One label plane exceeds fixed slab budget")
            foreground, values, actual_bytes = 0, set(), 0
            for start in range(0, shape[2], step):
                block = np.asanyarray(img.dataobj[:, :, start:min(start + step, shape[2])])
                if block.nbytes > 32_000_000 or not np.isfinite(block).all():
                    raise ValueError("Label slab finite/resource gate failed")
                actual_bytes += block.nbytes
                foreground += int(np.count_nonzero(block))
                values.update(np.unique(block).tolist())
                if len(values) > 32:
                    raise ValueError("Unexpected label with >32 values")
            if actual_bytes > entry["nominal_array_bytes"]:
                raise ValueError("Nominal label byte estimate violated")
            qc, sc = int(img.header["qform_code"]), int(img.header["sform_code"])
            q, s = img.get_qform(), img.get_sform()
            if not np.isfinite(img.affine).all() or (qc > 0 and not np.isfinite(q).all()) or (sc > 0 and not np.isfinite(s).all()):
                raise ValueError("Nonfinite affine/form")
            form_error = float(np.linalg.norm(((q - s) @ corners(shape))[:3], axis=0).max()) if qc > 0 and sc > 0 else None
            forms_consistent = form_error is None or form_error <= .05
            summary = header_by_uid[uid].get("summary", {})
            grid = best_grid_transform([summary["rows"], summary["columns"], summary["planes"]], np.array(summary["affine_rcz_ras"]), shape, img.affine) if "affine_rcz_ras" in summary else {"same_native_grid": False, "reason": "No authenticated native affine; grid pending"}
            binary = values <= {0, 1}
            entry.update(label_inspection_complete=True, label_shape=shape, label_dtype=str(img.get_data_dtype()), label_array_bytes=actual_bytes, streaming_step_last_axis=int(step),
                         label_values=sorted(values), label_is_binary=binary, label_foreground_voxels=foreground, label_voxel_volume_mm3=float(abs(np.linalg.det(img.affine[:3, :3]))),
                         label_affine_xyz_ras=img.affine.tolist(), label_spacing_xyz_mm=list(map(float, img.header.get_zooms()[:3])), qform_code=qc, sform_code=sc, qform=q.tolist(), sform=s.tolist(),
                         max_qform_sform_corner_difference_mm=form_error, forms_consistent=forms_consistent, grid=grid,
                         header_and_label_grid_preflight_passed=bool(entry["header_qualified_candidate"] and grid["same_native_grid"] and binary and forms_consistent and (qc > 0 or sc > 0)))
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
        result["series"] = rows
        write(OUT / "attempt_01.json", result)
        print(json.dumps({k: entry.get(k) for k in ("patient", "description", "label_inspection_complete", "label_foreground_voxels", "header_qualified_candidate", "header_and_label_grid_preflight_passed", "error")}), flush=True)
    result.update(series=rows, complete=len(rows) == 7 and all(r["label_inspection_complete"] for r in rows), label_arrays_decoded=any(r["label_inspection_complete"] for r in rows),
                  array_nominal_total_bytes=nominal_total, label_ZIP_member_bytes=members_total, source_preflight_series_passed=sum(r["header_and_label_grid_preflight_passed"] for r in rows),
                  source_preflight_patients_with_a_passing_series=len({r["patient"] for r in rows if r["header_and_label_grid_preflight_passed"]}), finished_utc=datetime.now(timezone.utc).isoformat())
    write(OUT / "attempt_01.json", result)
    print(json.dumps({k: result[k] for k in ("complete", "array_nominal_total_bytes", "source_preflight_series_passed", "source_preflight_patients_with_a_passing_series")}), flush=True)
    return int(not result["complete"])

if __name__ == "__main__":
    raise SystemExit(main())
