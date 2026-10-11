"""Stage pinned author code and MONAI wheel locally; do not alter MRI env."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
AUTHOR = ROOT / "literature/source_cache/vs_seg_author_code_2026-10-01"
SOURCES = ROOT / "literature/source_cache/vs_seg_task_model_sources_2026-10-02"
OUT = ROOT / "literature/source_cache/vs_seg_cpu_compat_sources_2026-10-02"
STAGE = ROOT / "tools/vs_seg_cpu_compat"


def fetch(url: str, cap: int) -> bytes:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=40) as response:
        raw = response.read(cap + 1)
    if len(raw) > cap:
        raise ValueError("Dependency exceeds download cap")
    return raw


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    STAGE.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(STAGE).free < 15_000_000_000:
        raise OSError("15 GB free-space floor reached")
    tree = json.loads((AUTHOR / "tree.json").read_text())
    blobs = {x["path"]: x for x in tree["tree"] if x["type"] == "blob"}
    records = []
    for path in ("params/networks/nets/unet2d5_spvPA.py", "params/networks/blocks/convolutions.py",
                 "params/networks/blocks/attentionblock.py"):
        url = "https://raw.githubusercontent.com/KCL-BMEIS/VS_Seg/" + tree["sha"] + "/" + urllib.parse.quote(path)
        local = SOURCES / path
        raw = local.read_bytes() if local.exists() else fetch(url, 500_000)
        if hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() != blobs[path]["sha"]:
            raise ValueError("Author source blob differs")
        if not local.exists():
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(raw)
        target = STAGE / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        records.append({"file": path, "url": url, "sha256": hashlib.sha256(raw).hexdigest(), "git_blob_verified": True})
    metadata_path = OUT / "pypi_monai_0_4_0.json"
    raw = metadata_path.read_bytes() if metadata_path.exists() else fetch("https://pypi.org/pypi/monai/0.4.0/json", 1_000_000)
    metadata_path.write_bytes(raw)
    metadata = json.loads(raw)
    wheels = [x for x in metadata["urls"] if x["filename"].endswith(".whl")]
    if len(wheels) != 1 or wheels[0]["size"] > 5_000_000:
        raise ValueError("Unexpected official MONAI wheel inventory")
    wheel = wheels[0]
    path = OUT / wheel["filename"]
    wheel_raw = path.read_bytes() if path.exists() else fetch(wheel["url"], 5_000_000)
    if hashlib.sha256(wheel_raw).hexdigest() != wheel["digests"]["sha256"]:
        raise ValueError("Official PyPI wheel SHA-256 failed")
    path.write_bytes(wheel_raw)
    vendor = STAGE / "vendor"
    vendor.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(wheel_raw)) as archive:
        if sum(x.file_size for x in archive.infolist()) > 30_000_000:
            raise ValueError("Uncompressed MONAI wheel exceeds cap")
        for item in archive.infolist():
            parts = PurePosixPath(item.filename).parts
            if item.filename.startswith(("/", "\\")) or ".." in parts or any(":" in p for p in parts):
                raise ValueError("Unsafe wheel member")
            if item.is_dir() or parts[0] != "monai":
                continue
            target = vendor.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(item))
    result = {"author_tree_sha": tree["sha"], "author_sources": records,
              "monai_wheel": {"file": path.name, "bytes": len(wheel_raw), "url": wheel["url"],
                              "sha256": wheel["digests"]["sha256"], "pypi_digest_verified": True},
              "stage": STAGE.relative_to(ROOT).as_posix(), "installed_into_user_environment": False,
              "checkpoint_deserialized": False, "patient_pixels_read": False}
    (OUT / "index.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
