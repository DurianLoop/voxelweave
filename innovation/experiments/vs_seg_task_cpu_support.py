"""Isolated official-model loader and resource gate shared by task preflights."""

from __future__ import annotations

import ctypes
import hashlib
import importlib
import importlib.machinery
import io
import json
import os
import shutil
import sys
import types
import zipfile
from pathlib import Path


os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "tools/vs_seg_cpu_compat"


def resource_gate() -> dict:
    free = shutil.disk_usage(ROOT).free
    if free < 15_000_000_000:
        raise OSError("15 GB workspace free-space floor reached")
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in ("total_physical", "available_physical", "total_page", "available_page",
                                                   "total_virtual", "available_virtual", "available_extended_virtual")]
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    kernel = ctypes.windll.kernel32
    if not kernel.GlobalMemoryStatusEx(ctypes.byref(status)) or status.available_physical < 8_000_000_000:
        raise OSError("8 GB available physical-memory floor reached")
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    low_priority = bool(kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000))
    return {"workspace_free_bytes_before": free, "available_physical_memory_before_bytes": status.available_physical,
            "own_process_below_normal_priority": low_priority}


def load_model():
    manifest_dir = ROOT / "literature/source_cache/vs_seg_cpu_compat_sources_2026-10-02"
    manifest = json.loads((manifest_dir / "index.json").read_text())
    for item in manifest["author_sources"]:
        if hashlib.sha256((STAGE / item["file"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Staged author source changed")
    wheel_path = manifest_dir / manifest["monai_wheel"]["file"]
    if hashlib.sha256(wheel_path.read_bytes()).hexdigest() != manifest["monai_wheel"]["sha256"]:
        raise ValueError("Staged MONAI source wheel changed")
    with zipfile.ZipFile(wheel_path) as archive:
        for name in archive.namelist():
            if name.startswith("monai/") and not name.endswith("/"):
                if archive.read(name) != (STAGE / "vendor" / name).read_bytes():
                    raise ValueError("Staged MONAI differs from authenticated wheel")
    sys.path.insert(0, str(STAGE))
    sys.path.insert(0, str(STAGE / "vendor"))
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    def deny_cuda(*args, **kwargs):
        raise RuntimeError("CUDA initialization prohibited")
    torch.cuda._lazy_init = deny_cuda
    shims = []
    if not hasattr(importlib.machinery.FileFinder, "find_module"):
        def find_module(self, fullname, path=None):
            return types.SimpleNamespace(load_module=importlib.import_module)
        importlib.machinery.FileFinder.find_module = find_module
        shims.append("process-local FileFinder.find_module/load_module delegates to importlib.import_module")
    from params.networks.nets.unet2d5_spvPA import UNet2d5_spvPA
    import monai
    model = UNet2d5_spvPA(
        dimensions=3, in_channels=1, out_channels=2, channels=(16, 32, 48, 64, 80, 96),
        strides=((2, 2, 1), (2, 2, 1), (2, 2, 2), (2, 2, 2), (2, 2, 2)),
        kernel_sizes=((3, 3, 1), (3, 3, 1), (3, 3, 3), (3, 3, 3), (3, 3, 3), (3, 3, 3)),
        sample_kernel_sizes=((3, 3, 1), (3, 3, 1), (3, 3, 3), (3, 3, 3), (3, 3, 3)),
        num_res_units=2, norm="BATCH", dropout=0.1, attention_module=True).cpu().eval()
    source = ROOT / "data/vs_seg_task_model_release/UNet2d5_Att_Hard_T2_final.zip"
    with zipfile.ZipFile(source) as archive:
        raw = archive.read("UNet2d5_Att_Hard_T2_final/model/best_metric_model.pth")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != "9105ad78fed0561bb04a82e660eed6083c3d182fc43642bc332f68a272ede0a7":
        raise ValueError("Official task checkpoint differs")
    model.load_state_dict(torch.load(io.BytesIO(raw), map_location="cpu", weights_only=True), strict=True)
    return model, {"checkpoint_sha256": digest, "torch_version": torch.__version__,
                   "monai_version": monai.__version__, "compatibility_shims": shims,
                   "cpu_threads": torch.get_num_threads(), "cpu_interop_threads": torch.get_num_interop_threads()}
