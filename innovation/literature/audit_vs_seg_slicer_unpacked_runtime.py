"""Correct the NSIS size interpretation and authenticate unpacked runtime files."""
from __future__ import annotations

import json
import shutil

from stage_vs_seg_slicer_cpu_packages import ROOT, STAGE, digest


def main():
    entries = []
    directories = []
    for name in ("application", "extension"):
        files = sorted(p for p in (STAGE / name).rglob("*") if p.is_file())
        directories.append({"name": name, "files": len(files), "actual_bytes": sum(p.stat().st_size for p in files)})
        for p in files:
            entries.append({"file": p.relative_to(STAGE).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p, "sha256")})
    total = sum(row["actual_bytes"] for row in directories)
    free = shutil.disk_usage(ROOT).free
    if total > 3_000_000_000 or free < 15_000_000_000:
        raise OSError("Actual size/free-space floor failed")
    result = {"correction": "unpack_attempt_02.json expanded_bytes counted only known 7-Zip NSIS entry sizes; blank sizes are unknown, not zero. That historical report is retained. Actual file sizes below supersede its size totals. Future extraction reserves the full 3 GB when sizes are unknown.", "directories": directories, "total_actual_bytes": total, "free_after_bytes": free, "size_cap_pass": True, "entries": entries}
    (STAGE / "runtime_manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "entries"}, indent=2))


if __name__ == "__main__":
    main()
