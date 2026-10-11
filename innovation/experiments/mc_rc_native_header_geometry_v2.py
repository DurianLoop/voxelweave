"""Prespecified all-IPP fit for new source batches; no magnitude decoding."""
from __future__ import annotations

import re

import numpy as np


def geometry(records, source):
    issues, pending, reasons = [], [], []
    types = sorted({r["mr_acquisition_type"] for r in records})
    result = {
        "issues": issues, "pending_fields": pending,
        "header_qualified_candidate": False, "qualification_fail_reasons": reasons,
        "image_types": sorted({tuple(r["image_type"]) for r in records}),
        "mr_acquisition_types": types,
        "slice_thicknesses_mm": sorted({r["slice_thickness"] for r in records if r["slice_thickness"] is not None}),
        "fit_method": "centered linear regression of all ordered IPPs; prespecified for this batch",
        "missing_acquisition_type_pending": any(not r["mr_acquisition_type"] for r in records),
    }
    if len(records) != source["ImageCount"]:
        issues.append("Object count differs from API ImageCount")
    if len({r["sop_uid"] for r in records}) != len(records) or any(not r["sop_uid"] for r in records):
        issues.append("Duplicate/missing SOPUID")
    if any(r["patient"] != source["PatientID"] or r["series_uid"] != source["SeriesInstanceUID"] or r["study_uid"] != source["StudyInstanceUID"] or r["modality"] != "MR" for r in records):
        issues.append("Patient/study/series/modality identity differs")
    if len(records) < 2:
        pending.append("Fewer than two classic MR planes")
    if any(r["frames"] != 1 for r in records):
        pending.append("Enhanced/multiframe geometry not interpreted")
    if any(not r["rows"] or not r["columns"] or len(r["pixel_spacing"]) != 2 or len(r["iop"]) != 6 or len(r["ipp"]) != 3 or r["slice_thickness"] is None or not r["frame_uid"] for r in records):
        pending.append("Required classic MR geometry field absent")
    if pending:
        return result
    iop = np.array([r["iop"] for r in records], dtype=float)
    ps = np.array([r["pixel_spacing"] for r in records], dtype=float)
    pos = np.array([r["ipp"] for r in records], dtype=float)
    thickness = np.array([r["slice_thickness"] for r in records], dtype=float)
    if not all(np.isfinite(x).all() for x in (iop, ps, pos, thickness)) or (ps <= 0).any() or (thickness <= 0).any():
        issues.append("Nonfinite/nonpositive geometry fields")
        return result
    first = iop[0]
    normal = np.cross(first[:3], first[3:])
    order = np.argsort(pos @ normal)
    pos = pos[order]
    z = np.arange(len(pos), dtype=float)
    center = z - z.mean()
    step = (center[:, None] * (pos - pos.mean(axis=0))).sum(axis=0) / (center @ center)
    origin = pos.mean(axis=0) - z.mean() * step
    residual = float(np.linalg.norm(pos - origin - z[:, None] * step, axis=1).max())
    gap = np.diff(pos @ normal)
    deviation = float(abs(gap - np.median(gap)).max())
    if len({(r["rows"], r["columns"]) for r in records}) != 1:
        issues.append("Rows/columns inconsistent")
    if len({r["frame_uid"] for r in records}) != 1:
        issues.append("FrameOfReferenceUID inconsistent")
    if abs(iop - first).max() > 1e-6:
        issues.append("Orientation inconsistent")
    if abs(ps - ps[0]).max() > 1e-6:
        issues.append("PixelSpacing inconsistent")
    if max(abs(np.linalg.norm(first[:3]) - 1), abs(np.linalg.norm(first[3:]) - 1), abs(first[:3] @ first[3:])) > 1e-4:
        issues.append("IOP not orthonormal")
    if gap.min() <= 1e-4:
        issues.append("Duplicate/degenerate planes")
    if residual > .02 or deviation > .02:
        issues.append("Nonuniform/non-affine slice geometry")
    acq = types == ["3D"]
    original = all("ORIGINAL" in [v.upper() for v in r["image_type"]] and "DERIVED" not in [v.upper() for v in r["image_type"]] for r in records)
    derivative = any(re.search(r"MPR|REFORMAT|LOCALIZER", r["series_description"] + " " + r["derivation_description"] + " " + " ".join(r["image_type"]), re.I) for r in records)
    spacing = [float(ps[0, 0]), float(ps[0, 1]), float(np.linalg.norm(step))]
    thin = max(spacing) <= 1.5 and float(thickness.max()) <= 1.5
    if not acq:
        reasons.append("Missing MR Acquisition Type pending" if result["missing_acquisition_type_pending"] else "MR Acquisition Type not uniformly 3D")
    if not original:
        reasons.append("Not uniformly ORIGINAL without DERIVED")
    if derivative:
        reasons.append("MPR/Reformat/localizer evidence")
    if not thin:
        reasons.append("Native spacing or nominal SliceThickness >1.5mm")
    affine = np.eye(4)
    affine[:3, 0] = first[3:] * ps[0, 0]
    affine[:3, 1] = first[:3] * ps[0, 1]
    affine[:3, 2] = step
    affine[:3, 3] = origin
    result.update(
        header_qualified_candidate=bool(not issues and not pending and acq and original and not derivative and thin),
        geometry_passed=not issues, native_spacing_rcz_mm=spacing,
        rows=records[0]["rows"], columns=records[0]["columns"], planes=len(records),
        actual_spacing_min_max_mm=[float(gap.min()), float(gap.max())],
        max_spacing_deviation_mm=deviation, max_affine_position_residual_mm=residual,
        affine_rcz_lps=affine.tolist(), affine_rcz_ras=(np.diag([-1., -1., 1., 1.]) @ affine).tolist(),
        ordered_zip_members=[records[int(i)]["zip_member"] for i in order],
        original_no_derived=original, acquisition_type_3D=acq,
        derivative_evidence=bool(derivative), thin_geometry=thin,
    )
    return result
