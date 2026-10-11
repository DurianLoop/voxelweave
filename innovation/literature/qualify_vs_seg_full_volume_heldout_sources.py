"""One-worker official-source/header gate on the fixed 46-patient task roster."""
from __future__ import annotations

import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pydicom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from vs_seg_task_cpu_support import resource_gate

DATA = ROOT / "data/vs_seg_full_volume_heldout_source"
OUT = ROOT / "literature/source_cache/vs_seg_full_volume_source_gate_2026-10-02"
PLAN = ROOT / "VS_SEG_FULL_VOLUME_HELDOUT_SOURCE_GATE_PLAN_2026-10-02.md"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def download(path, url, cap):
    if not path.exists():
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
        with opener.open(req, timeout=45) as response:
            raw = response.read(cap + 1)
        if len(raw) > cap:
            raise ValueError("Source size cap exceeded")
        path.write_bytes(raw)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "url": url, "bytes": path.stat().st_size}


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    roster_file = ROOT / "literature/source_cache/vs_seg_t2_release_logs_2026-10-02/split_verification.json"
    roster = json.loads(roster_file.read_text())["test_ids"]
    tree_file = ROOT / "literature/source_cache/vs_seg_author_code_2026-10-01/tree.json"
    tree = json.loads(tree_file.read_text())
    blobs = {x["path"]: x for x in tree["tree"] if x["type"] == "blob"}
    inventory = json.loads((ROOT / "literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json").read_text())
    lookup = {x["patient"]: x for x in inventory["t2_series"]}
    report = {"attempt": attempt, "plan_sha256": sha(PLAN), "script_sha256": sha(Path(__file__)), "roster_sha256": sha(roster_file), "author_tree_sha256": sha(tree_file), "fixed_roster": roster, "complete": False, "pixels_decoded": False, "task_inference": False, "patients": [], "failures": []}
    for patient in roster:
        rec = {"patient": patient, "complete": False}
        try:
            rec["resource_gate"] = resource_gate()
            row = lookup[patient]
            case = patient.rsplit("-", 1)[-1]
            image_path = DATA / (patient + "_t2.zip")
            image = download(image_path, "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?SeriesInstanceUID=" + row["series_uid"], 75_000_000)
            contour_path = f"preprocessing/createBIDSdataset/VS-SEG-BIDS-nonifti/sourcedata/contours/sub-{case}/anat/sub-{case}_contours_space-individual_T2w.json"
            original_path = DATA / (patient + "_original_t2_contours.json")
            original = download(original_path, "https://raw.githubusercontent.com/KCL-BMEIS/VS_Seg/" + tree["sha"] + "/" + contour_path, 3_000_000)
            raw = original_path.read_bytes()
            if hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() != blobs[contour_path]["sha"]:
                raise ValueError("Original contour Git blob differs")
            original.update({"git_blob_sha": blobs[contour_path]["sha"], "git_tree": tree["sha"]})
            audit = json.loads((ROOT / f"literature/source_cache/vs_seg_rtstruct_labels_2026-10-01/{patient}.json").read_text())
            rt_path = ROOT / audit["source_path"]
            if sha(rt_path) != audit["zip_sha256"]:
                raise ValueError("RTSTRUCT authenticated archive differs")
            with zipfile.ZipFile(image_path) as z:
                headers = [pydicom.dcmread(io.BytesIO(z.read(n)), stop_before_pixels=True) for n in z.namelist() if n.lower().endswith(".dcm")]
            with zipfile.ZipFile(rt_path) as z:
                structures = [pydicom.dcmread(io.BytesIO(z.read(n)), stop_before_pixels=True) for n in z.namelist() if n.lower().endswith(".dcm")]
            structure, = structures
            first = headers[0]
            direction = np.asarray(first.ImageOrientationPatient, dtype=float)
            col_dir, row_dir = direction[:3], direction[3:]
            normal = np.cross(col_dir, row_dir)
            headers.sort(key=lambda h: float(np.asarray(h.ImagePositionPatient, dtype=float) @ normal))
            origins = np.asarray([h.ImagePositionPatient for h in headers], dtype=float)
            spacing = float(np.median(np.diff(origins @ normal)))
            sops = {str(h.SOPInstanceUID) for h in headers}
            if len(headers) != row["image_count"] or len(sops) != len(headers) or str(structure.PatientID) != patient:
                raise ValueError("Source completeness/identity failed")
            for h in headers:
                if str(h.PatientID) != patient or str(h.SeriesInstanceUID) != row["series_uid"] or str(h.Modality) != "MR" or str(h.FrameOfReferenceUID) != str(first.FrameOfReferenceUID) or int(h.Rows) != int(first.Rows) or int(h.Columns) != int(first.Columns) or not np.allclose(h.ImageOrientationPatient, direction, atol=1e-6, rtol=0) or not np.allclose(h.PixelSpacing, first.PixelSpacing, atol=1e-6, rtol=0):
                    raise ValueError("Per-slice native grid or patient mismatch")
            if not np.allclose(np.diff(origins, axis=0), normal * spacing, atol=1e-4, rtol=0):
                raise ValueError("Nonuniform/nonorthogonal native grid")
            rois = list(structure.StructureSetROISequence)
            if str(rois[0].ReferencedFrameOfReferenceUID) != str(first.FrameOfReferenceUID):
                raise ValueError("RTSTRUCT/native frame differs")
            rt_first = next(x for x in structure.ROIContourSequence if int(x.ReferencedROINumber) == int(rois[0].ROINumber))
            if any(str(c.ContourImageSequence[0].ReferencedSOPInstanceUID) not in sops for c in rt_first.ContourSequence):
                raise ValueError("RTSTRUCT first-structure SOP reference absent")
            original_structures = json.loads(raw)
            if original_structures[0]["structure_name"] != str(rois[0].ROIName):
                raise ValueError("Author-order first-structure name differs")
            affine_lps = np.eye(4)
            affine_lps[:3, 0] = col_dir * float(first.PixelSpacing[1])
            affine_lps[:3, 1] = row_dir * float(first.PixelSpacing[0])
            affine_lps[:3, 2] = normal * spacing
            affine_lps[:3, 3] = origins[0]
            dimensions = [int(first.Columns), int(first.Rows), len(headers)]
            acquisition_types = sorted({str(h.get("MRAcquisitionType", "")) for h in headers})
            image_types = sorted({tuple(map(str, h.get("ImageType", []))) for h in headers})
            thicknesses = sorted({float(h.get("SliceThickness", 0)) for h in headers})
            sequence = "CISS" if "ci3d" in row["description"].lower() else "TSE"
            native_thin3d = acquisition_types == ["3D"] and all(t and t[0] == "ORIGINAL" for t in image_types) and max(thicknesses) <= 1.5001 and spacing <= 1.5001
            payload = {"patient": patient, "author_split": "test", "dimensions_ijk": dimensions, "affine_ijk_ras": (np.diag([-1., -1., 1., 1.]) @ affine_lps).tolist(), "spacing": [float(first.PixelSpacing[1]), float(first.PixelSpacing[0]), spacing], "frame_of_reference_uid": str(first.FrameOfReferenceUID), "series_instance_uid": str(first.SeriesInstanceUID), "contour_structure": original_structures[0]["structure_name"], "original_contours_lps": original_structures[0]["LPS_contour_points"], "rtstruct_contours_lps": [np.asarray(c.ContourData, dtype=float).reshape(-1, 3).tolist() for c in rt_first.ContourSequence], "rtstruct_structures_lps": [{"structure_name": str(r.ROIName), "LPS_contour_points": [np.asarray(c.ContourData, dtype=float).reshape(-1, 3).tolist() for c in next(x for x in structure.ROIContourSequence if int(x.ReferencedROINumber) == int(r.ROINumber)).ContourSequence]} for r in rois], "source_inputs": {"image_zip": image, "rtstruct_zip": {"path": rt_path.relative_to(ROOT).as_posix(), "sha256": sha(rt_path)}, "original_json": original}, "pixels_decoded": False}
            target = OUT / f"{patient}_conversion_input.json"
            target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            rec.update({"complete": True, "file": target.relative_to(ROOT).as_posix(), "sha256": sha(target), "sequence": sequence, "description": row["description"], "dimensions_ijk": dimensions, "spacing": payload["spacing"], "thickness": thicknesses, "acquisition_types": acquisition_types, "image_types": image_types, "native_thin3d": native_thin3d, "main_ciss_source_qualified": sequence == "CISS" and native_thin3d, "first_structure": payload["contour_structure"], "original_contour_count": len(payload["original_contours_lps"]), "rtstruct_contour_count": len(payload["rtstruct_contours_lps"]), "sop_instance_uids_sorted": [str(h.SOPInstanceUID) for h in headers], "rescale_slope_intercept_values": sorted({(float(h.get("RescaleSlope", 1)), float(h.get("RescaleIntercept", 0))) for h in headers})})
        except Exception as exc:
            rec["error"] = f"{type(exc).__name__}: {exc}"
            report["failures"].append({"patient": patient, "error": rec["error"]})
        report["patients"].append(rec)
        (OUT / f"progress_attempt_{attempt:02d}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({k: rec.get(k) for k in ("patient", "complete", "sequence", "main_ciss_source_qualified", "error")}), flush=True)
    report["complete"] = len(report["patients"]) == 46 and not report["failures"]
    report["source_counts"] = {"completed": sum(r["complete"] for r in report["patients"]), "qualified_main_ciss": sum(r.get("main_ciss_source_qualified", False) for r in report["patients"])}
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"complete": report["complete"], "source_counts": report["source_counts"], "failures": report["failures"]}), flush=True)
    if not report["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
