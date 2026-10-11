"""Archive official T2 checkpoint ZIP, inspect only file metadata and text logs."""

from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "literature/source_cache/vs_seg_task_model_sources_2026-10-02/zenodo_record.json"
OUT = ROOT / "literature/source_cache/vs_seg_t2_release_logs_2026-10-02"
DATA = ROOT / "data/vs_seg_task_model_release"
PLAN = ROOT / "VS_SEG_TASK_CHECKPOINT_LOG_AUDIT_PLAN_2026-10-02.md"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    metadata = json.loads(META.read_text(encoding="utf-8"))
    source = next(f for f in metadata["files"] if f["key"] == "UNet2d5_Att_Hard_T2_final.zip")
    path = DATA / source["key"]
    if not path.exists():
        if shutil.disk_usage(DATA).free < 15_000_000_000 + int(source["size"]):
            raise OSError("15 GB disk-space floor reached")
        req = urllib.request.Request(source["links"]["self"], headers={"User-Agent": "MRI-source-audit/1.0"})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=90) as response:
            raw = response.read(int(source["size"]) + 1)
        if len(raw) != source["size"]:
            raise ValueError("Unexpected release size")
        if "md5:" + hashlib.md5(raw).hexdigest() != source["checksum"]:
            raise ValueError("Official checksum failed")
        path.write_bytes(raw)
    raw = path.read_bytes()
    if len(raw) != source["size"] or "md5:" + hashlib.md5(raw).hexdigest() != source["checksum"]:
        raise ValueError("Cached release differs from official metadata")
    members, logs = [], []
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            parts = PurePosixPath(item.filename).parts
            if item.filename.startswith(("/", "\\")) or ".." in parts or any(":" in p for p in parts):
                raise ValueError("Unsafe release ZIP member")
            if item.is_dir():
                continue
            members.append({"name": item.filename, "bytes": item.file_size,
                            "compressed_bytes": item.compress_size, "crc32": f"{item.CRC:08x}"})
            if item.filename.lower().endswith(".txt") and "logs" in parts:
                if item.file_size > 5_000_000:
                    raise ValueError("Log exceeds text-only inspection cap")
                content = archive.read(item)
                local = OUT.joinpath(*parts)
                local.parent.mkdir(parents=True, exist_ok=True)
                local.write_bytes(content)
                logs.append({"member": item.filename, "file": local.relative_to(OUT).as_posix(),
                             "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    result = {"plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
              "source": path.relative_to(ROOT).as_posix(), "source_url": source["links"]["self"],
              "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
              "official_md5_verified": True, "members": members, "text_logs": logs,
              "checkpoint_deserialized": False, "patient_pixels_read": False}
    (OUT / "index.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"archive_bytes": len(raw), "official_md5_verified": True,
                      "members": len(members), "text_logs": logs}, indent=2))


if __name__ == "__main__":
    main()
