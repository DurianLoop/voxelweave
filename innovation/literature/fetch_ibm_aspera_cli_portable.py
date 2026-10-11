"""Fetch and safely extract the digest-verified official Windows ascli portable ZIP."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
INNOVATION = HERE.parent
INDEX = HERE / "source_cache" / "ibm_aspera_cli_release_gate_2026-10-01" / "index.json"
OUT = INNOVATION / "tools" / "aspera_cli_4.27.3"
ZIP = OUT / "portable.zip"
EXTRACT = OUT / "extracted"
REPORT = OUT / "fetch_report.json"
MAX_DOWNLOAD = 42_000_000
MAX_UNCOMPRESSED = 300_000_000


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    release = json.loads(INDEX.read_text(encoding="utf-8"))
    assets = release["portable_assets"]
    if len(assets) != 1 or release["version"] != "v4.27.3":
        raise ValueError("Unexpected IBM portable release")
    asset = assets[0]
    if asset["name"] != "aspera-cli-4.27.3-windows-x86_64-portable.zip":
        raise ValueError("Unexpected asset name")
    expected = asset["digest"].removeprefix("sha256:")
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(asset["url"], headers={"User-Agent": "MRI-source-audit/1.0"})
    digest = hashlib.sha256()
    total = 0
    with opener.open(request, timeout=45) as response, ZIP.open("wb") as stream:
        if response.status != 200:
            raise RuntimeError("Unexpected portable asset status")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_DOWNLOAD:
                raise RuntimeError("Portable asset exceeded byte cap")
            digest.update(chunk)
            stream.write(chunk)
    if total != asset["size"] or digest.hexdigest() != expected:
        raise RuntimeError("Official asset size or digest mismatch")
    with zipfile.ZipFile(ZIP) as archive:
        members = archive.infolist()
        if sum(entry.file_size for entry in members) > MAX_UNCOMPRESSED:
            raise RuntimeError("Portable archive exceeds extraction cap")
        for entry in members:
            name = entry.filename.replace("\\", "/")
            parts = Path(name).parts
            if name.startswith("/") or ":" in name or ".." in parts:
                raise RuntimeError("Unsafe archive member path")
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise RuntimeError("Archive contains symbolic link")
            target = (EXTRACT / name).resolve()
            if not target.is_relative_to(EXTRACT.resolve()):
                raise RuntimeError("Archive member escapes destination")
        archive.extractall(EXTRACT)
    launchers = [str(path.relative_to(OUT)) for path in EXTRACT.rglob("ascli.cmd")]
    report = {"source_url": asset["url"], "bytes": total, "sha256": digest.hexdigest(),
              "entry_count": len(members), "uncompressed_bytes": sum(e.file_size for e in members),
              "launchers": launchers, "system_install_performed": False,
              "patient_data_requested": False, "transfer_started": False}
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
