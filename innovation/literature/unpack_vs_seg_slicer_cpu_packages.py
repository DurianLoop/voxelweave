"""Audit archive paths and space before unpacking a standalone CPU runtime."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

from stage_vs_seg_slicer_cpu_packages import STAGE, ROOT, digest


def main():
    attempt = len(list(STAGE.glob("unpack_attempt_*.json"))) + 1
    report = {"attempt": attempt, "installer_executed": False, "complete": False, "archives": []}
    try:
        download = json.loads((STAGE / "download_attempt_01.json").read_text())
        if not download["complete"]:
            raise ValueError("Authenticated download absent")
        records = []
        for number, row in enumerate(download["packages"]):
            package = STAGE / row["file"]
            if digest(package) != row["official_sha512"]:
                raise ValueError("Official package changed")
            listing = subprocess.run(["D:/7-Zip/7z.exe", "l", "-slt", str(package)], capture_output=True, text=True, check=True)
            (STAGE / f"package_{number}_listing.txt").write_text(listing.stdout, encoding="utf-8")
            body = listing.stdout.split("----------", 1)[1]
            size = 0
            unknown_sizes = 0
            count = 0
            for block in re.split(r"\n\s*\n", body):
                fields = dict(line.split(" = ", 1) for line in block.splitlines() if " = " in line)
                if "Path" not in fields:
                    continue
                name = fields["Path"].replace("\\", "/")
                pure = PurePosixPath(name)
                if pure.is_absolute() or ".." in pure.parts or ":" in name or fields.get("Symbolic Link") or fields.get("Hard Link"):
                    raise ValueError(f"Unsafe archive entry: {name}")
                count += 1
                unknown_sizes += int(fields.get("Size") == "")
                size += int(fields.get("Size") or 0)
            target = STAGE / ("application" if number == 0 else "extension")
            if not target.resolve().is_relative_to(STAGE.resolve()) or target.exists():
                raise ValueError("Extraction target must be a new child of standalone staging directory")
            records.append((package, target))
            report["archives"].append({"file": row["file"], "entries": count, "known_entry_bytes": size, "entries_without_size": unknown_sizes, "paths_checked": True, "target": target.relative_to(ROOT).as_posix()})
        total = 3_000_000_000 if any(row["entries_without_size"] for row in report["archives"]) else sum(row["known_entry_bytes"] for row in report["archives"])
        if total > 3_000_000_000 or shutil.disk_usage(ROOT).free - total < 15_000_000_000:
            raise OSError("Expansion cap or free-space floor failed")
        report["reserved_expansion_bytes"] = total
        for number, (package, target) in enumerate(records):
            operation = subprocess.run(["D:/7-Zip/7z.exe", "x", str(package), "-o" + str(target), "-y", "-mmt=1"], capture_output=True, text=True, check=True)
            (STAGE / f"package_{number}_extraction.txt").write_text(operation.stdout + operation.stderr, encoding="utf-8")
            report["archives"][number]["actual_expanded_bytes"] = sum(p.stat().st_size for p in target.rglob("*") if p.is_file())
        if sum(row["actual_expanded_bytes"] for row in report["archives"]) > 3_000_000_000:
            raise OSError("Actual extracted runtime exceeds cap")
        report["complete"] = True
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    report["free_after_bytes"] = shutil.disk_usage(ROOT).free
    (STAGE / f"unpack_attempt_{attempt:02d}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
