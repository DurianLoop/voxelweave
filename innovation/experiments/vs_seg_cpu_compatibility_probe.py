"""Strict official-weight loading and tiny synthetic-only CPU forward checks."""

from __future__ import annotations

import hashlib
import argparse
import ctypes
import importlib
import importlib.machinery
import io
import json
import os
import sys
import time
import traceback
import types
import zipfile
from pathlib import Path


os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "tools/vs_seg_cpu_compat"
OUT = ROOT / "experiments/vs_seg_cpu_compatibility_probe"
PLAN = ROOT / "VS_SEG_CPU_COMPATIBILITY_PROBE_PLAN_2026-10-02.md"
ZIP = ROOT / "data/vs_seg_task_model_release/UNet2d5_Att_Hard_T2_final.zip"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-window", action="store_true")
    args = parser.parse_args()
    shape = [384, 384, 64] if args.full_window else [32, 32, 8]
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    result = {"attempt": attempt, "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "patient_pixels_read": False, "cpu_only": True, "synthetic_spatial_shape": shape,
              "compatibility_shims": [], "success": False}
    start = time.perf_counter()
    try:
        if args.full_window:
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                            ("total_physical", ctypes.c_ulonglong), ("available_physical", ctypes.c_ulonglong),
                            ("total_page", ctypes.c_ulonglong), ("available_page", ctypes.c_ulonglong),
                            ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
                            ("available_extended_virtual", ctypes.c_ulonglong)]
            status = MemoryStatus()
            status.length = ctypes.sizeof(status)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                raise OSError("Cannot inspect full-window memory floor")
            result["available_physical_memory_before_bytes"] = int(status.available_physical)
            if status.available_physical < 8_000_000_000:
                raise OSError("8 GB available physical-memory floor reached")
            kernel = ctypes.windll.kernel32
            kernel.GetCurrentProcess.restype = ctypes.c_void_p
            kernel.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            result["own_process_below_normal_priority"] = bool(kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000))
        sys.path.insert(0, str(STAGE))
        sys.path.insert(0, str(STAGE / "vendor"))
        import torch

        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        def deny_cuda(*args, **kwargs):
            raise RuntimeError("CUDA initialization is prohibited for this probe")
        torch.cuda._lazy_init = deny_cuda
        result["torch_version"] = torch.__version__
        if not hasattr(importlib.machinery.FileFinder, "find_module"):
            # MONAI 0.4 already calls import_module(name) immediately before
            # this obsolete loader call. Preserve that module import locally.
            def find_module(self, fullname, path=None):
                return types.SimpleNamespace(load_module=importlib.import_module)
            importlib.machinery.FileFinder.find_module = find_module
            result["compatibility_shims"].append("process-local FileFinder.find_module/load_module delegates to importlib.import_module")
        from params.networks.nets.unet2d5_spvPA import UNet2d5_spvPA
        import monai

        result["monai_version"] = monai.__version__
        model = UNet2d5_spvPA(
            dimensions=3, in_channels=1, out_channels=2, channels=(16, 32, 48, 64, 80, 96),
            strides=((2, 2, 1), (2, 2, 1), (2, 2, 2), (2, 2, 2), (2, 2, 2)),
            kernel_sizes=((3, 3, 1), (3, 3, 1), (3, 3, 3), (3, 3, 3), (3, 3, 3), (3, 3, 3)),
            sample_kernel_sizes=((3, 3, 1), (3, 3, 1), (3, 3, 3), (3, 3, 3), (3, 3, 3)),
            num_res_units=2, norm="BATCH", dropout=0.1, attention_module=True).cpu().eval()
        with zipfile.ZipFile(ZIP) as archive:
            weights = archive.read("UNet2d5_Att_Hard_T2_final/model/best_metric_model.pth")
        result["checkpoint_sha256"] = hashlib.sha256(weights).hexdigest()
        state = torch.load(io.BytesIO(weights), map_location="cpu", weights_only=True)
        model.load_state_dict(state, strict=True)
        result["checkpoint_strict_load_passed"] = True
        result["parameters"] = sum(p.numel() for p in model.parameters())
        generator = torch.Generator(device="cpu").manual_seed(20261002)
        synthetic = torch.randn(1, 1, *shape, generator=generator, device="cpu")
        inference_start = time.perf_counter()
        with torch.inference_mode():
            first = model(synthetic)[0].clone()
            second = None if args.full_window else model(synthetic)[0].clone()
        result.update({"output_shape": list(first.shape), "finite": bool(torch.isfinite(first).all()),
                       "repeat_max_absolute_difference": None if second is None else float((first - second).abs().max()),
                       "forward_seconds": time.perf_counter() - inference_start,
                       "output_min": float(first.min()), "output_max": float(first.max()),
                       "cuda_initialized": torch.cuda.is_initialized(),
                       "all_model_tensors_cpu": all(p.device.type == "cpu" for p in model.parameters())})
        result["success"] = (list(first.shape) == [1, 2, *shape] and result["finite"]
                             and (second is None or result["repeat_max_absolute_difference"] == 0)
                             and not result["cuda_initialized"] and result["all_model_tensors_cpu"])
        if args.full_window:
            class ProcessMemoryCounters(ctypes.Structure):
                _fields_ = [("cb", ctypes.c_ulong), ("page_fault_count", ctypes.c_ulong),
                            ("peak_working_set", ctypes.c_size_t), ("working_set", ctypes.c_size_t),
                            ("quota_peak_paged", ctypes.c_size_t), ("quota_paged", ctypes.c_size_t),
                            ("quota_peak_nonpaged", ctypes.c_size_t), ("quota_nonpaged", ctypes.c_size_t),
                            ("pagefile", ctypes.c_size_t), ("peak_pagefile", ctypes.c_size_t)]
            counters = ProcessMemoryCounters()
            counters.cb = ctypes.sizeof(counters)
            memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
            memory_info.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
            if memory_info(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
                result["own_process_peak_resident_bytes"] = int(counters.peak_working_set)
    except Exception as exc:
        result.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    result["elapsed_seconds"] = time.perf_counter() - start
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
