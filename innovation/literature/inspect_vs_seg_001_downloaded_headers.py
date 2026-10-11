"""Resume the exact VS-SEG pilot from already hashed official ZIP downloads."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from download_vs_seg_001_two_series_headers import OUT, REPORT, ROOT, SERIES, inspect_zip, sha256


def main() -> None:
    original = REPORT / "index.json"
    if not original.is_file() or (REPORT / "initial_download_failure.json").exists():
        raise ValueError("Expected one preserved initial index")
    records = json.loads(original.read_text(encoding="utf-8"))
    if len(records) != 2 or {r["name"] for r in records} != set(SERIES):
        raise ValueError("Original exact-two-series records differ")
    for record in records:
        name = record["name"]
        uid, cap = SERIES[name]
        path = ROOT / record["file"]
        if (record["series_instance_uid"] != uid or not path.is_file() or
                path.stat().st_size != record["bytes"] or path.stat().st_size > cap or
                hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]):
            raise ValueError(f"Frozen official ZIP differs: {name}")
    original.rename(REPORT / "initial_download_failure.json")
    for record in records:
        name = record["name"]
        try:
            header = inspect_zip(name, ROOT / record["file"], SERIES[name][0])
            header_path = REPORT / f"{name}_headers.json"
            header_path.write_text(json.dumps(header, indent=2) + "\n", encoding="utf-8")
            record.pop("error", None)
            record["header_file"] = header_path.relative_to(ROOT).as_posix()
            record["header_sha256"] = sha256(header_path.read_bytes())
            record["summary"] = header.get("summary", header.get("rtstruct"))
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
    original.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
