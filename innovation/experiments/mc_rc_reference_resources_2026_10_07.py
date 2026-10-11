"""Resource contract for a new <=250MB evidence stage; never controls other PIDs."""
import os
for _key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[_key] = '1'
import ctypes
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def resource_guard():
    disk = shutil.disk_usage(ROOT).free
    class Memory(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [(name, ctypes.c_ulonglong) for name in ('total', 'avail', 'tp', 'ap', 'tv', 'av', 'ex')]
    status = Memory(); status.length = ctypes.sizeof(status)
    kernel = ctypes.windll.kernel32
    assert kernel.GlobalMemoryStatusEx(ctypes.byref(status))
    assert disk >= 8_000_000_000, 'New-stage 8GB disk reserve failed'
    assert status.avail >= 8_000_000_000, '8GB available RAM reserve failed'
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    own_low = bool(kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000))
    assert own_low
    return dict(workspace_free_bytes=disk, available_ram_bytes=status.avail, own_process_below_normal=True,
                cpu_threads=1, disk_reserve_bytes=8_000_000_000, new_stage_max_saved_bytes=250_000_000,
                other_processes_enumerated=False, other_processes_modified=False)
