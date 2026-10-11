"""Complete five unread labels under a new, explicit streaming resource contract."""
from __future__ import annotations

import json
import math
import os
import sys
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
OUT = ROOT / "experiments/mc_rc_004_006_native_label_gate"
HEADERS = ROOT / "literature/source_cache/mc_rc_004_006_native_headers_2026-10-02"
PLAN = ROOT / "MC_RC_004_006_LABEL_RESOURCE_FOLLOWUP_PLAN_2026-10-02.md"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resources = resource_gate()
    first = read(OUT / "attempt_01.json")
    ledger = read(HEADERS / "attempt_01.json")
    by_uid = {r["source"]["SeriesInstanceUID"]: r for r in ledger["series"]}
    if first["complete"] or sum(r["label_inspection_complete"] for r in first["series"]) != 3:
        raise ValueError("Expected original resource-limited fixed-eight result")
    arrays = []
    for r in first["series"]:
        path = ROOT / r["label_file"]
        if sha(path) != r["label_sha256"]:
            raise ValueError("Previously extracted label differs")
        img = nib.load(path)
        if len(img.shape) != 3:
            raise ValueError("Unexpected label dimension")
        width = np.dtype(img.get_data_dtype()).itemsize
        if img.dataobj.slope != 1 or img.dataobj.inter != 0:
            width = max(width, 8)
        count = math.prod(img.shape) * width
        if count > 400_000_000:
            raise ValueError("Revised per-label array budget exceeded")
        arrays.append((r, img, count, width))
    total = sum(v[2] for v in arrays)
    if len(arrays) != 8 or total > 2_000_000_000:
        raise ValueError("Revised fixed-eight array budget exceeded")
    rows = []
    for old, img, nominal_bytes, width in arrays:
        resource_gate()
        entry = dict(old)
        entry["first_run_label_inspection_complete"] = old["label_inspection_complete"]
        entry["prior_array_result_reused"] = old["label_inspection_complete"]
        entry["nominal_array_bytes"] = nominal_bytes
        if old["label_inspection_complete"]:
            rows.append(entry)
            continue
        entry["first_run_error"] = entry.pop("error")
        try:
            shape = list(img.shape)
            step = max(1, min(shape[2], 32_000_000 // (shape[0] * shape[1] * width)))
            values, foreground, actual_bytes = set(), 0, 0
            for start in range(0, shape[2], step):
                block = np.asanyarray(img.dataobj[:, :, start:min(start + step, shape[2])])
                if block.nbytes > 32_000_000 or not np.isfinite(block).all():
                    raise ValueError("Streaming block budget/finite gate failed")
                actual_bytes += block.nbytes
                foreground += int(np.count_nonzero(block))
                values.update(np.unique(block).tolist())
                if len(values) > 32:
                    raise ValueError("More than 32 label values; unexpected nonbinary label")
            qc, sc = int(img.header["qform_code"]), int(img.header["sform_code"])
            q, s = img.get_qform(), img.get_sform()
            form_error = float(np.linalg.norm(((q - s) @ corners(shape))[:3], axis=0).max()) if qc > 0 and sc > 0 else None
            if not np.isfinite(img.affine).all() or (qc > 0 and not np.isfinite(q).all()) or (sc > 0 and not np.isfinite(s).all()):
                raise ValueError("Nonfinite label affine/form")
            summary = by_uid[old["series_uid"]]["summary"]
            grid = best_grid_transform([summary["rows"], summary["columns"], summary["planes"]], np.array(summary["affine_rcz_ras"]), shape, img.affine)
            binary = values <= {0, 1}
            forms_consistent = form_error is None or form_error <= .05
            entry.update(
                label_inspection_complete=True, label_shape=shape, label_dtype=str(img.get_data_dtype()),
                label_array_bytes=actual_bytes, label_values=sorted(values), label_is_binary=binary,
                label_foreground_voxels=foreground, label_voxel_volume_mm3=float(abs(np.linalg.det(img.affine[:3, :3]))),
                label_affine_xyz_ras=img.affine.tolist(), label_spacing_xyz_mm=list(map(float, img.header.get_zooms()[:3])),
                qform_code=qc, sform_code=sc, qform=q.tolist(), sform=s.tolist(),
                max_qform_sform_corner_difference_mm=form_error, forms_consistent=forms_consistent,
                grid=grid, streaming_step_last_axis=step,
                header_and_label_grid_preflight_passed=bool(summary["header_qualified_candidate"] and grid["same_native_grid"] and binary and forms_consistent and (qc > 0 or sc > 0)),
            )
        except Exception as exc:
            entry.update(label_inspection_complete=False, header_and_label_grid_preflight_passed=False, error=f"{type(exc).__name__}: {exc}")
        rows.append(entry)
        print(json.dumps({k: entry.get(k) for k in ("patient", "description", "label_inspection_complete", "label_foreground_voxels", "grid", "header_and_label_grid_preflight_passed", "error")}), flush=True)
    attempt = len(list(OUT.glob("resource_followup_attempt_*.json"))) + 1
    result = {
        "attempt": attempt, "created_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": sha(__file__), "plan_sha256": sha(PLAN),
        "grid_helper_sha256": sha(ROOT / "experiments/audit_mc_rc_three_patient_label_grid.py"),
        "first_attempt_sha256": sha(OUT / "attempt_01.json"),
        "header_attempt_sha256": sha(HEADERS / "attempt_01.json"), "resources": resources,
        "scope": "post-result resource revision only; retain original failure and all source/grid thresholds",
        "array_nominal_total_bytes": total, "max_label_nominal_bytes": 400_000_000,
        "max_total_nominal_bytes": 2_000_000_000, "max_block_bytes": 32_000_000,
        "prior_arrays_reused": 3, "new_label_arrays_requested": 5,
        "series": rows, "complete": all(r["label_inspection_complete"] for r in rows),
        "source_preflight_series_passed": sum(r["header_and_label_grid_preflight_passed"] for r in rows),
        "source_preflight_patients_with_a_passing_series": len({r["patient"] for r in rows if r["header_and_label_grid_preflight_passed"]}),
        "original_label_attempt_complete": first["complete"], "full_public_label_coverage_certified": False,
        "MR_pixel_arrays_decoded": False, "scientific_independent_validation_patients": 0,
    }
    write(OUT / f"resource_followup_attempt_{attempt:02d}.json", result)
    print(json.dumps({k: result[k] for k in ("complete", "array_nominal_total_bytes", "source_preflight_series_passed", "source_preflight_patients_with_a_passing_series", "original_label_attempt_complete")}), flush=True)
    return int(not result["complete"])


if __name__ == "__main__":
    raise SystemExit(main())
