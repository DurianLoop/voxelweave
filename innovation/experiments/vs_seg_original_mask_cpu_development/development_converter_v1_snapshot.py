"""Official author helpers and official MRML export on fixed native grids."""
from __future__ import annotations

import ast
import ctypes
import hashlib
import json
import os
import sys
import time
import traceback
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "tools/vs_seg_slicer_cpu"
OUT = ROOT / "experiments/vs_seg_original_mask_cpu_development"
AUTHOR = ROOT / "literature/source_cache/vs_seg_author_code_2026-10-01"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    report = {"attempt": attempt, "complete": False, "script_sha256": sha(Path(__file__)), "plan_sha256": sha(ROOT / "VS_SEG_ORIGINAL_MASK_CONVERSION_SOURCE_PLAN_2026-10-02.md"), "independent_task_confirmation": False, "patient_pixels_decoded": False, "gpu_rendering": False, "application_created": False, "patients": []}
    start = time.perf_counter()
    try:
        for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VTK_SMP_MAX_THREADS"):
            os.environ[name] = "1"
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        kernel = ctypes.windll.kernel32
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        report["below_normal_priority"] = bool(kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000))
        runtime = json.loads((STAGE / "runtime_manifest.json").read_text(encoding="utf-8"))
        for row in runtime["entries"]:
            if sha(STAGE / row["file"]) != row["sha256"]:
                raise ValueError("Authenticated unpacked runtime changed")
        report["runtime_manifest_sha256"] = sha(STAGE / "runtime_manifest.json")
        extension, = (STAGE / "extension").glob("34645-*")
        library = extension / "lib/Slicer-5.12/qt-loadable-modules"
        handles = [os.add_dll_directory(str(p)) for p in (library, extension / "bin") if p.exists()]
        sys.path.insert(0, str(library))
        import numpy as np
        import vtk
        from vtk.util.numpy_support import vtk_to_numpy
        vtk.vtkMultiThreader.SetGlobalMaximumNumberOfThreads(1)
        vtk.vtkSMPTools.Initialize(1)
        def deny_render(*args, **kwargs):
            raise RuntimeError("Rendering forbidden during CPU contour conversion")
        for name in ("vtkRenderWindow", "vtkGenericOpenGLRenderWindow", "vtkWin32OpenGLRenderWindow", "vtkOpenGLRenderWindow", "vtkRenderer"):
            if hasattr(vtk, name):
                setattr(vtk, name, deny_render)
        import vtkSegmentationCore as core
        import MRMLCorePython as mrml
        import vtkSlicerSegmentationsModuleMRMLPython as segmrml
        import vtkSlicerSegmentationsModuleLogicPython as seglogic
        import vtkSlicerDicomRtImportExportConversionRulesPython as rt
        factory = core.vtkSegmentationConverterFactory.GetInstance()
        planar_rule = rt.vtkPlanarContourToClosedSurfaceConversionRule()
        binary_rule = core.vtkClosedSurfaceToBinaryLabelmapConversionRule()
        factory.RegisterConverterRule(planar_rule)
        factory.RegisterConverterRule(binary_rule)
        report["runtime"] = {"slicer_release": "5.12.4", "slicer_revision": "34645", "slicerrt_git_tree": "3b6ce695aadf6133c0e97778843aa577f6ddbe64", "python": sys.version, "vtk": vtk.vtkVersion.GetVTKVersion(), "default_end_capping": planar_rule.GetConversionParameter("End capping"), "default_slice_thickness": planar_rule.GetConversionParameter("Default slice thickness"), "reference_parameter_name": core.vtkSegmentationConverter.GetReferenceImageGeometryParameterName(), "registration": False, "contours_snapped_to_native_planes": False}
        source = AUTHOR / "preprocessing/data_conversion.py"
        author_record = next(r for r in json.loads((AUTHOR / "index.json").read_text()) if r.get("file") == "preprocessing/data_conversion.py")
        if sha(source) != author_record["sha256"]:
            raise ValueError("Author conversion helpers changed")
        names = {"createSegNodeFromContourPoints", "transform_contour_points", "create_segments_from_structure_contour_list"}
        parsed = ast.parse(source.read_text(encoding="utf-8"))
        helper_ast = ast.Module(body=[n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[])
        if len(helper_ast.body) != len(names):
            raise ValueError("Expected exact original helper functions")
        helpers = {"np": np, "vtk": vtk, "slicer": types.SimpleNamespace(vtkSegment=core.vtkSegment)}
        exec(compile(helper_ast, str(source), "exec"), helpers)
        report["author_helpers"] = {"file_sha256": author_record["sha256"], "git_blob_sha": author_record["git_blob_sha"], "functions": sorted(names), "function_bodies_modified": False}
        prepared = json.loads((ROOT / "data/vs_seg_original_mask_development/prepare_attempt_03.json").read_text())
        for item in prepared["patients"]:
            case_start = time.perf_counter()
            input_path = ROOT / item["file"]
            if sha(input_path) != item["sha256"]:
                raise ValueError("Frozen development input changed")
            data = json.loads(input_path.read_text())
            for record in data["source_inputs"].values():
                if sha(ROOT / record["path"]) != record["sha256"]:
                    raise ValueError("Development source input changed")
            original_structures = json.loads((ROOT / data["source_inputs"]["original_json"]["path"]).read_text())
            reference_image = vtk.vtkImageData()
            reference_image.SetDimensions(*data["dimensions_ijk"])
            reference_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
            vtk_to_numpy(reference_image.GetPointData().GetScalars()).fill(0)
            affine = np.asarray(data["affine_ijk_ras"], dtype=float)
            matrix = vtk.vtkMatrix4x4()
            for i in range(4):
                for j in range(4):
                    matrix.SetElement(i, j, float(affine[i, j]))
            masks = {}
            details = {}
            for kind, structures in (("original_json", original_structures), ("rtstruct", data["rtstruct_structures_lps"])):
                scene = mrml.vtkMRMLScene()
                reference = mrml.vtkMRMLScalarVolumeNode()
                reference.SetAndObserveImageData(reference_image)
                reference.SetIJKToRASMatrix(matrix)
                scene.AddNode(reference)
                node = mrml.vtkMRMLSegmentationNode()
                scene.AddNode(node)
                node.SetReferenceImageGeometryParameterFromVolumeNode(reference)
                helpers["create_segments_from_structure_contour_list"](node, structures)
                if node.GetSegmentation().GetNthSegment(0).GetName() != data["contour_structure"]:
                    raise ValueError("Author first-structure selection differs")
                ids = vtk.vtkStringArray()
                node.GetSegmentation().GetSegmentIDs(ids)
                first_id = ids.GetValue(0)
                chosen = vtk.vtkStringArray()
                chosen.InsertNextValue(first_id)
                labelmap = mrml.vtkMRMLLabelMapVolumeNode()
                scene.AddNode(labelmap)
                logic = seglogic.vtkSlicerSegmentationsModuleLogic()
                logic.SetMRMLScene(scene)
                success = logic.ExportSegmentsToLabelmapNode(node, chosen, labelmap, reference)
                if not success:
                    raise ValueError("Official ExportSegmentsToLabelmapNode failed")
                output_affine = vtk.vtkMatrix4x4()
                labelmap.GetIJKToRASMatrix(output_affine)
                output_matrix = np.asarray([[output_affine.GetElement(i, j) for j in range(4)] for i in range(4)])
                output = labelmap.GetImageData()
                if list(output.GetDimensions()) != data["dimensions_ijk"] or not np.allclose(output_matrix, affine, rtol=0, atol=1e-6):
                    raise ValueError("Official export did not preserve native grid")
                array = vtk_to_numpy(output.GetPointData().GetScalars()).reshape(tuple(reversed(data["dimensions_ijk"]))).transpose(1, 2, 0).copy().astype(bool)
                masks[kind] = array
                segment = node.GetSegmentation().GetSegment(first_id)
                surface = segment.GetRepresentation("Closed surface")
                counts = array.sum(axis=(0, 1)).astype(int)
                details[kind] = {"voxels": int(array.sum()), "volume_mm3": float(array.sum() * np.prod(data["spacing"])), "positive_slice_indices": np.flatnonzero(counts).tolist(), "voxels_by_slice": counts.tolist(), "closed_surface_points": surface.GetNumberOfPoints(), "closed_surface_cells": surface.GetNumberOfCells(), "closed_surface_bounds_ras": list(surface.GetBounds()), "native_grid_exact": True}
                scene.Clear(0)
            original, interpolated = masks["original_json"], masks["rtstruct"]
            target = OUT / f"{data['patient']}_masks_attempt_{attempt:02d}.npz"
            np.savez_compressed(target, original_mask_rcz=original, rtstruct_mask_rcz=interpolated, affine_ijk_ras=affine)
            report["patients"].append({"patient": data["patient"], "author_split": data["author_split"], "input_sha256": item["sha256"], "input_file": item["file"], "dimensions_ijk": data["dimensions_ijk"], "spacing": data["spacing"], "masks_file": target.relative_to(ROOT).as_posix(), "masks_sha256": sha(target), "mask_details": details, "json_vs_rtstruct_dice": float(2 * (original & interpolated).sum() / (original.sum() + interpolated.sum())), "json_only_voxels": int((original & ~interpolated).sum()), "rtstruct_only_voxels": int((interpolated & ~original).sum()), "json_only_positive_slices": np.flatnonzero(original.any(axis=(0, 1)) & ~interpolated.any(axis=(0, 1))).tolist(), "seconds": time.perf_counter() - case_start})
        report["complete"] = True
    except Exception as exc:
        report.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    report["elapsed_seconds"] = time.perf_counter() - start
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "patients"}, indent=2))
    print(json.dumps([{k: v for k, v in r.items() if k != "mask_details"} for r in report["patients"]], indent=2))
    if not report["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
