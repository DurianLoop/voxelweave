"""Read all eight prespecified labels and match their native grids without registration."""
from __future__ import annotations

import csv
import json
import math
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
from audit_mc_rc_three_patient_label_grid import best_grid_transform, corners, sha, read, write
from vs_seg_task_cpu_support import resource_gate

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ROOT / "literature/source_cache/mc_rc_004_006_native_headers_2026-10-02"
PRIOR = ROOT / "literature/source_cache/mc_rc_three_patient_headers_2026-10-02"
PREPARATION = ROOT / "experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json"
PLAN = ROOT / "MC_RC_004_006_NATIVE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md"
OUT = ROOT / "experiments/mc_rc_004_006_native_label_gate"
DATA = ROOT / "data/mc_rc_004_006_label_grid"
PREFIX = "VS-MC-RC-Segmentations_with_pathname_spreadsheet-Release2023/VS-MC-RC segmentations-NIfTI-Release 2023/"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resources = resource_gate()
    ledger = read(HEADERS / "attempt_01.json")
    selected = read(PREPARATION)
    prior_ledger = read(PRIOR / "attempt_01.json")
    artifact_path = ROOT / "experiments/mc_rc_native_t2_label_gate/official_pathnames_artifact_read.json"
    artifact = read(artifact_path)
    csv_path = PRIOR / "official_label_metadata_00_attempt_01.csv"
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        cells = list(csv.reader(f))
    if cells != artifact["values"] or sha(csv_path) != artifact["source_sha256"]:
        raise ValueError("Existing artifact/Python CSV proof differs")
    mapping = {r["series_instance_uid"]: r for r in (dict(zip(cells[0], v)) for v in cells[1:])}
    zip_path = ROOT / prior_ledger["labels"]["transfer"]["file"]
    if sha(zip_path) != prior_ledger["labels"]["transfer"]["sha256"]:
        raise ValueError("Previously authenticated official label ZIP differs")
    expected = {r["source"]["SeriesInstanceUID"] for r in selected["next_batch_series"]}
    if not ledger["complete"] or len(ledger["series"]) != 8 or {r["source"]["SeriesInstanceUID"] for r in ledger["series"]} != expected:
        raise ValueError("Fixed-eight header/selection scope incomplete or different")
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    compressed_total, array_total, rows = 0, 0, []
    with zipfile.ZipFile(zip_path) as archive:
        for row in ledger["series"]:
            resource_gate()
            source, summary = row["source"], row["summary"]
            uid = source["SeriesInstanceUID"]
            entry = {
                "patient": source["PatientID"], "series_uid": uid, "study_uid": source["StudyInstanceUID"],
                "description": source["SeriesDescription"], "header_qualified_candidate": summary["header_qualified_candidate"],
                "header_sha256": row["header_sha256"], "label_inspection_complete": False,
                "header_and_label_grid_preflight_passed": False,
            }
            try:
                m = mapping[uid]
                if m["patient_id"] != source["PatientID"] or m["study_instance_uid"] != source["StudyInstanceUID"] or int(m["num_files"]) != source["ImageCount"] or not m["SegmentationPath"]:
                    raise ValueError("Exact CSV patient/study/count/label mapping differs")
                member_name = PREFIX + m["SegmentationPath"]
                member = archive.getinfo(member_name)
                if member.file_size > 100_000_000 or compressed_total + member.file_size > 300_000_000:
                    raise ValueError("Fixed ZIP member budget exceeded")
                payload = archive.read(member)
                compressed_total += len(payload)
                dest = DATA / f"{source['PatientID']}_{uid}_label_attempt_{attempt:02d}.nii.gz"
                with dest.open("xb") as stream:
                    stream.write(payload)
                entry.update(label_file=dest.relative_to(ROOT).as_posix(), label_sha256=sha(dest), label_zip_member=member_name, zip_crc32=f"{member.CRC:08x}", zip_crc32_verified=True, label_member_bytes=len(payload))
                img = nib.load(dest)
                shape = list(img.shape)
                if len(shape) != 3:
                    raise ValueError("Label is not 3D")
                itemsize = np.dtype(img.get_data_dtype()).itemsize
                if img.dataobj.slope != 1 or img.dataobj.inter != 0:
                    itemsize = max(itemsize, 8)
                estimate = math.prod(shape) * itemsize
                if estimate > 100_000_000 or array_total + estimate > 300_000_000:
                    raise ValueError("Fixed label array budget exceeded before decoding")
                array_total += estimate
                data = np.asanyarray(img.dataobj)
                if not np.isfinite(data).all() or data.nbytes > estimate:
                    raise ValueError("Nonfinite label or array byte estimate violated")
                values = np.unique(data).tolist()
                qc, sc = int(img.header["qform_code"]), int(img.header["sform_code"])
                q, s = img.get_qform(), img.get_sform()
                if not np.isfinite(img.affine).all() or (qc > 0 and not np.isfinite(q).all()) or (sc > 0 and not np.isfinite(s).all()):
                    raise ValueError("Nonfinite label affine/form")
                form_error = float(np.linalg.norm(((q - s) @ corners(shape))[:3], axis=0).max()) if qc > 0 and sc > 0 else None
                forms_consistent = form_error is None or form_error <= .05
                if "affine_rcz_ras" in summary:
                    grid = best_grid_transform([summary["rows"], summary["columns"], summary["planes"]], np.array(summary["affine_rcz_ras"]), shape, img.affine)
                else:
                    grid = {"same_native_grid": False, "reason": "Header geometry pending; no affine manufactured"}
                binary = set(values) <= {0, 1}
                preflight = bool(summary["header_qualified_candidate"] and grid["same_native_grid"] and binary and forms_consistent and (qc > 0 or sc > 0))
                entry.update(
                    label_inspection_complete=True, label_shape=shape, label_dtype=str(data.dtype),
                    label_array_bytes=data.nbytes, label_values=values, label_is_binary=binary,
                    label_foreground_voxels=int((data != 0).sum()),
                    label_voxel_volume_mm3=float(abs(np.linalg.det(img.affine[:3, :3]))),
                    label_affine_xyz_ras=img.affine.tolist(), label_spacing_xyz_mm=list(map(float, img.header.get_zooms()[:3])),
                    qform_code=qc, sform_code=sc, qform=q.tolist(), sform=s.tolist(),
                    max_qform_sform_corner_difference_mm=form_error, forms_consistent=forms_consistent,
                    grid=grid, header_and_label_grid_preflight_passed=preflight,
                )
            except Exception as exc:
                entry["error"] = f"{type(exc).__name__}: {exc}"
            rows.append(entry)
            print(json.dumps({k: entry.get(k) for k in ("patient", "description", "header_qualified_candidate", "label_inspection_complete", "label_foreground_voxels", "grid", "header_and_label_grid_preflight_passed", "error")}), flush=True)
    result = {
        "attempt": attempt, "created_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": sha(__file__), "plan_sha256": sha(PLAN),
        "grid_helper_sha256": sha(ROOT / "experiments/audit_mc_rc_three_patient_label_grid.py"),
        "source_header_attempt_sha256": sha(HEADERS / "attempt_01.json"),
        "selection_sha256": sha(PREPARATION), "official_label_zip_sha256": sha(zip_path),
        "source_csv_sha256": sha(csv_path), "artifact_read_sha256": sha(artifact_path),
        "scope": "all fixed-eight label arrays and native-grid preflight; not reconstruction/segmentation performance",
        "resources": resources, "series": rows,
        "complete": all(r["label_inspection_complete"] for r in rows),
        "label_ZIP_member_bytes": compressed_total, "label_array_budget_used_bytes": array_total,
        "source_preflight_series_passed": sum(r["header_and_label_grid_preflight_passed"] for r in rows),
        "source_preflight_patients_with_a_passing_series": len({r["patient"] for r in rows if r["header_and_label_grid_preflight_passed"]}),
        "MR_pixel_arrays_decoded": False, "label_arrays_decoded": True,
        "full_public_label_coverage_certified": False, "scientific_independent_validation_patients": 0,
    }
    write(OUT / f"attempt_{attempt:02d}.json", result)
    print(json.dumps({k: result[k] for k in ("complete", "source_preflight_series_passed", "source_preflight_patients_with_a_passing_series", "label_array_budget_used_bytes")}), flush=True)
    return int(not result["complete"])


if __name__ == "__main__":
    raise SystemExit(main())
