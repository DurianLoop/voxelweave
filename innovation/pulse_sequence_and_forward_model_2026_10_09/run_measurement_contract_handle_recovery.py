"""Correct Windows ABI prototypes; run unchanged scientific probe."""
import ctypes
from ctypes import wintypes
k=ctypes.windll.kernel32
k.GetCurrentProcess.argtypes=[];k.GetCurrentProcess.restype=wintypes.HANDLE
k.SetPriorityClass.argtypes=[wintypes.HANDLE,wintypes.DWORD];k.SetPriorityClass.restype=wintypes.BOOL
k.GetPriorityClass.argtypes=[wintypes.HANDLE];k.GetPriorityClass.restype=wintypes.DWORD
from probe_measurement_contract import main
if __name__=='__main__':main()
