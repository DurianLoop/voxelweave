"""Fixed development inputs 001/182, headers only; retain source lineage."""
from __future__ import annotations

import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pydicom

from probe_vs_seg_original_mask_routes import ROOT, OUT, fetch

DATA = ROOT / "data/vs_seg_original_mask_development"
AUTHOR = ROOT / "literature/source_cache/vs_seg_author_code_2026-10-01"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    attempt = len(list(DATA.glob("prepare_attempt_*.json"))) + 1
    result = {"attempt": attempt, "complete": False, "patient_pixels_read": False, "patients": [], "plan_sha256": sha(ROOT / "VS_SEG_ORIGINAL_MASK_CONVERSION_SOURCE_PLAN_2026-10-02.md")}
    try:
        tree = json.loads((AUTHOR / "tree.json").read_text())
        for case in ("001", "182"):
            patient = "VS-SEG-" + case
            contour_path = f"preprocessing/createBIDSdataset/VS-SEG-BIDS-nonifti/sourcedata/contours/sub-{case}/anat/sub-{case}_contours_space-individual_T2w.json"
            blob = next(x for x in tree["tree"] if x["path"] == contour_path)
            local = AUTHOR / contour_path
            if case == "182":
                repository = tree["url"].split("/git/trees/", 1)[0].removeprefix("https://api.github.com/repos/")
                rec = fetch("original_contours_182.json", "https://raw.githubusercontent.com/" + repository + "/" + tree["sha"] + "/" + contour_path, 2_000_000)
                if "error" in rec:
                    raise OSError(rec["error"])
                local = OUT / rec["file"]
            raw = local.read_bytes()
            if hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() != blob["sha"]:
                raise ValueError("Author original contour Git blob differs")
            if case == "001":
                image_zip = ROOT / "data/vs_seg_001_header_pilot/t2.zip"
                rt_zip = ROOT / "data/vs_seg_001_header_pilot/rtstruct.zip"
                expected_sha = "87217a07189be409a2a67c71ade97a88da51be17ca182f6bc30e8011ce6cd271"
            else:
                row = next(x for x in json.loads((ROOT / "literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json").read_text())["t2_series"] if x["patient"] == patient)
                image_zip = DATA / "VS-SEG-182_t2.zip"
                rt_zip = ROOT / "data/vs_seg_rtstruct_audit/VS-SEG-182_rtstruct.zip"
                url = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?SeriesInstanceUID=" + row["series_uid"]
                result["native_image_source_182"] = {"url": url, "inventory_row": row}
                if not image_zip.exists():
                    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                    with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=45) as response:
                        content = response.read(75_000_001)
                    if len(content) > 75_000_000:
                        raise ValueError("Development image cap exceeded")
                    image_zip.write_bytes(content)
                expected_sha = sha(image_zip)
            if sha(image_zip) != expected_sha:
                raise ValueError("Existing native image source changed")
            audit = json.loads((ROOT / f"literature/source_cache/vs_seg_rtstruct_labels_2026-10-01/{patient}.json").read_text())
            if sha(rt_zip) != audit["zip_sha256"]:
                raise ValueError("Archived RTSTRUCT changed")
            with zipfile.ZipFile(image_zip) as archive:
                headers = [pydicom.dcmread(io.BytesIO(archive.read(n)), stop_before_pixels=True) for n in archive.namelist() if n.lower().endswith(".dcm")]
            with zipfile.ZipFile(rt_zip) as archive:
                structures = [pydicom.dcmread(io.BytesIO(archive.read(n)), stop_before_pixels=True) for n in archive.namelist() if n.lower().endswith(".dcm")]
            structure, = structures
            first = headers[0]
            orientation = np.asarray(first.ImageOrientationPatient, dtype=float)
            col_dir, row_dir = orientation[:3], orientation[3:]
            normal = np.cross(col_dir, row_dir)
            headers.sort(key=lambda h: float(np.asarray(h.ImagePositionPatient, dtype=float) @ normal))
            origins = np.asarray([h.ImagePositionPatient for h in headers], dtype=float)
            step = float(np.median(np.diff(origins @ normal)))
            for h in headers:
                if str(h.PatientID) != patient or str(h.FrameOfReferenceUID) != str(first.FrameOfReferenceUID) or not np.allclose(h.ImageOrientationPatient, orientation, atol=1e-6, rtol=0) or int(h.Rows) != int(first.Rows) or int(h.Columns) != int(first.Columns):
                    raise ValueError("Native image patient/orientation/grid mismatch")
            if not np.allclose(np.diff(origins, axis=0), normal * step, atol=1e-4, rtol=0):
                raise ValueError("Native image planes not a uniform orthogonal grid")
            rois = list(structure.StructureSetROISequence)
            roi = rois[0]
            if str(roi.ReferencedFrameOfReferenceUID) != str(first.FrameOfReferenceUID):
                raise ValueError("RTSTRUCT native frame differs")
            rt = next(r for r in structure.ROIContourSequence if int(r.ReferencedROINumber) == int(roi.ROINumber))
            sop = {str(h.SOPInstanceUID) for h in headers}
            if any(str(c.ContourImageSequence[0].ReferencedSOPInstanceUID) not in sop for c in rt.ContourSequence):
                raise ValueError("RTSTRUCT contour reference not in original T2 grid")
            original = json.loads(raw)[0]
            if original["structure_name"] != str(roi.ROIName):
                raise ValueError("Original and RTSTRUCT first-structure names differ")
            affine_lps = np.eye(4)
            affine_lps[:3, 0] = col_dir * float(first.PixelSpacing[1])
            affine_lps[:3, 1] = row_dir * float(first.PixelSpacing[0])
            affine_lps[:3, 2] = normal * step
            affine_lps[:3, 3] = origins[0]
            payload = {"patient": patient, "author_split": "training" if case == "001" else "validation", "dimensions_ijk": [int(first.Columns), int(first.Rows), len(headers)], "affine_ijk_ras": (np.diag([-1., -1., 1., 1.]) @ affine_lps).tolist(), "spacing": [float(first.PixelSpacing[1]), float(first.PixelSpacing[0]), step], "frame_of_reference_uid": str(first.FrameOfReferenceUID), "series_instance_uid": str(first.SeriesInstanceUID), "contour_structure": original["structure_name"], "original_contours_lps": original["LPS_contour_points"], "rtstruct_contours_lps": [np.asarray(c.ContourData, dtype=float).reshape(-1, 3).tolist() for c in rt.ContourSequence], "source_inputs": {"image_zip": {"path": image_zip.relative_to(ROOT).as_posix(), "sha256": sha(image_zip)}, "rtstruct_zip": {"path": rt_zip.relative_to(ROOT).as_posix(), "sha256": sha(rt_zip)}, "original_json": {"path": local.relative_to(ROOT).as_posix(), "sha256": sha(local), "git_blob_sha": blob["sha"], "git_tree": tree["sha"]}}, "pixels_decoded": False}
            payload["rtstruct_structures_lps"] = [
                {"structure_name": str(r.ROIName), "LPS_contour_points": [np.asarray(c.ContourData, dtype=float).reshape(-1, 3).tolist() for c in next(x for x in structure.ROIContourSequence if int(x.ReferencedROINumber) == int(r.ROINumber)).ContourSequence]}
                for r in rois]
            target = DATA / f"{patient}_conversion_input_attempt_{attempt:02d}.json"
            target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result["patients"].append({"patient": patient, "file": target.relative_to(ROOT).as_posix(), "sha256": sha(target), "dimensions_ijk": payload["dimensions_ijk"], "spacing": payload["spacing"], "original_contours": len(payload["original_contours_lps"]), "rtstruct_contours": len(payload["rtstruct_contours_lps"])})
        result["complete"] = True
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    (DATA / f"prepare_attempt_{attempt:02d}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
