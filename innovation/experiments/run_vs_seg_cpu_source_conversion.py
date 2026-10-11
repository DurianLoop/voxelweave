"""Capture the native launcher return code and streams independently of PowerShell."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/vs_seg_full_volume_source_masks"


def main():
    command = [str(ROOT / "tools/vs_seg_slicer_cpu/application/bin/PythonSlicer.exe"), "--launcher-ignore-user-additional-settings", "--launcher-no-splash", "-B", str(ROOT / "experiments/vs_seg_full_volume_source_mask_conversion.py")]
    environment = os.environ.copy()
    environment.update({"CUDA_VISIBLE_DEVICES": "-1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "VTK_SMP_MAX_THREADS": "1"})
    process = subprocess.run(command, capture_output=True, env=environment, timeout=240, shell=False)
    stdout = OUT / "explicit_launcher_stdout.log"
    stderr = OUT / "explicit_launcher_stderr.log"
    stdout.write_bytes(process.stdout)
    stderr.write_bytes(process.stderr)
    record = {"argv": command, "return_code": process.returncode, "shell": False, "stdout_sha256": hashlib.sha256(process.stdout).hexdigest(), "stderr_sha256": hashlib.sha256(process.stderr).hexdigest(), "reason_for_repeat": "PowerShell tool reported status 1 despite a complete 46-case result; retain original logs and verify native exit status and mask reproducibility via direct subprocess capture."}
    (OUT / "explicit_launcher_status.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if process.returncode == 0:
        first = json.loads((OUT / "attempt_01.json").read_text())
        second = json.loads((OUT / "attempt_02.json").read_text())
        record["both_complete"] = first["complete"] and second["complete"]
        record["all_mask_archives_identical_sha256"] = [r["masks_sha256"] for r in first["patients"]] == [r["masks_sha256"] for r in second["patients"]]
        (OUT / "explicit_launcher_status.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if not record["both_complete"] or not record["all_mask_archives_identical_sha256"]:
            raise ValueError("Source-conversion reproducibility failed")
    print(json.dumps(record, indent=2))
    if process.returncode:
        raise SystemExit(process.returncode)


if __name__ == "__main__":
    main()
