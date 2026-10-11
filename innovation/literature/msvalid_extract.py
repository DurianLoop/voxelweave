"""Extract the frozen first-T2 cohort from a public remote ZIP by byte ranges."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from msvalid_remote_inventory import RemoteZip


ROOT = Path(__file__).resolve().parents[1]
QUALIFIED = ROOT / "literature/msvalid_geometry_qualification.json"
DEST = ROOT / "data/msvalid_first_t2"
MANIFEST = ROOT / "literature/msvalid_extraction_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    data = json.loads(QUALIFIED.read_text(encoding="utf-8"))
    patients = [p for p in data["patients"] if p["geometry_eligible"]]
    if len(patients) != 84:
        raise RuntimeError("Frozen cohort count changed")
    DEST.mkdir(parents=True, exist_ok=True)
    remote = RemoteZip()
    records = []
    with zipfile.ZipFile(remote) as archive:
        for index, patient in enumerate(patients, 1):
            member = patient["member"]
            dest = DEST / f"{patient['patient']}.nii.gz"
            if not dest.exists():
                temp = dest.with_suffix(".nii.gz.part")
                with archive.open(member) as source, temp.open("wb") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
                temp.replace(dest)
            if dest.stat().st_size != archive.getinfo(member).file_size:
                raise IOError(f"Unexpected extracted size: {member}")
            records.append({"patient": patient["patient"], "member": member,
                            "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
                            "bytes": dest.stat().st_size, "sha256": sha256(dest),
                            "zip_crc32": patient["zip_crc32"]})
            if index % 10 == 0 or index == len(patients):
                print(f"extracted {index}/{len(patients)} range_bytes={remote.transferred}", flush=True)
    MANIFEST.write_text(json.dumps({"qualification_sha256": sha256(QUALIFIED),
                                    "range_bytes_transferred": remote.transferred,
                                    "records": records}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
