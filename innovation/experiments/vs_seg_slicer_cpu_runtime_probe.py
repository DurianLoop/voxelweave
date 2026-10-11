"""Standalone PythonSlicer CPU classes, without a Slicer application or renderer."""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "tools/vs_seg_slicer_cpu"
OUT = ROOT / "experiments/vs_seg_slicer_cpu_runtime_probe"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    result = {"attempt": attempt, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "complete": False, "patient_pixels_read": False, "gui_application_created": False, "render_window_created": False}
    try:
        for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VTK_SMP_MAX_THREADS"):
            os.environ[name] = "1"
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        kernel = ctypes.windll.kernel32
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        result["below_normal_priority"] = bool(kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000))
        extension, = (STAGE / "extension").glob("34645-*")
        library = extension / "lib/Slicer-5.12/qt-loadable-modules"
        handles = [os.add_dll_directory(str(p)) for p in (library, extension / "bin") if p.exists()]
        sys.path.insert(0, str(library))
        import vtk
        vtk.vtkMultiThreader.SetGlobalMaximumNumberOfThreads(1)
        vtk.vtkSMPTools.Initialize(1)
        def deny_render(*args, **kwargs):
            raise RuntimeError("Rendering is forbidden during CPU contour conversion")
        for name in ("vtkRenderWindow", "vtkGenericOpenGLRenderWindow", "vtkWin32OpenGLRenderWindow", "vtkOpenGLRenderWindow", "vtkRenderer"):
            if hasattr(vtk, name):
                setattr(vtk, name, deny_render)
        import vtkSegmentationCore as core
        import vtkSlicerDicomRtImportExportConversionRulesPython as rt
        rule = rt.vtkPlanarContourToClosedSurfaceConversionRule()
        binary_rule = core.vtkClosedSurfaceToBinaryLabelmapConversionRule()
        result.update({"python": sys.version, "executable": sys.executable, "vtk_version": vtk.vtkVersion.GetVTKVersion(),
                       "core_classes": [name for name in dir(core) if any(k in name for k in ("ConversionRule", "Converter", "Oriented", "Segmentation", "Segment"))],
                       "planar_rule_methods": [name for name in dir(rule) if any(k in name for k in ("Convert", "Parameter", "Representation"))],
                       "planar_rule": {"source": rule.GetSourceRepresentationName(), "target": rule.GetTargetRepresentationName(), "cost": rule.GetConversionCost()},
                       "binary_rule": {"source": binary_rule.GetSourceRepresentationName(), "target": binary_rule.GetTargetRepresentationName(), "cost": binary_rule.GetConversionCost()},
                       "vtk_threads": vtk.vtkMultiThreader.GetGlobalMaximumNumberOfThreads(), "complete": True})
    except Exception as exc:
        result.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
