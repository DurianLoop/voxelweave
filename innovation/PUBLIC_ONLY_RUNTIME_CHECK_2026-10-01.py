"""Read-only runtime and source audit for the public-source MIRA inference."""
from __future__ import annotations

import hashlib
import json
import sys
from importlib.metadata import version
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PYTHON = (3, 12)
PACKAGES = {
    "numpy": "2.4.3",
    "scipy": "1.17.1",
    "scikit-image": "0.26.0",
    "torch": "2.11.0+cu128",
    "nibabel": "5.4.2",
    "pydicom": "3.0.2",
    "pandas": "3.0.2",
    "pytorch-msssim": "1.0.0",
    "tqdm": "4.67.3",
}
SOURCES = {
    "baseline/ixi_hat_2p5d/train.py": "e10cd174b7aa366d1c281de4d611a2daa46ea4464bc1fde3a205d0d92e1f7e54",
    "baseline/ixi_hat_2p5d/model.py": "68a01c948a6ebfb727a862918c5ebb4de8288ae37ff3a87c28e0010a3e2bcd76",
    "baseline/ixi_hat_2p5d/settings.py": "e48ca641c324bc7fd50dc1743f295823e3c4ab434af86eea3fb0298b06361746",
    "baseline/ixi_swinir_2p5d/train.py": "ad55a3f8404d16156b3d24b463978526d1dc9160059a3660da2145e005783e2f",
    "baseline/ixi_swinir_2p5d/model.py": "c09a9011309750f96fc95988042a1ade4be9618849f44f43e118082a592dee78",
    "baseline/ixi_swinir_2p5d/settings.py": "2a79adbe866efc11a9553fcbdeffb1df437a7f7e1e9570ab1c403bb7401f721a",
    "pre/ixi_diffusion/common.py": "fa7b57e5c58efd74a269c0e339feb9825ce729654adf4c636cd2bd03bb570818",
    "pre/ixi_diffusion/data.py": "afcaf78e52db63335010eeec4850c19ef8117f477964c59bb34582d0297b2071",
    "pre/ixi_diffusion/settings.py": "2a726b806a0705ea4878dfa757b04014781097eee99841f80d8e134862c76c0d",
    "pre/topcow_diffusion/losses.py": "b674e3b80f049fd0e689248ff03b51c9eb7ef987440b69ea38f3efc039bce240",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    packages = {name: version(name) for name in PACKAGES}
    sources = {name: sha256(ROOT / name) for name in SOURCES}
    errors = []
    if sys.version_info[:2] != EXPECTED_PYTHON:
        errors.append(f"Python {sys.version_info[:2]} != {EXPECTED_PYTHON}")
    errors.extend(f"{name} {actual} != {PACKAGES[name]}" for name, actual in packages.items()
                  if actual != PACKAGES[name])
    errors.extend(f"source drift: {name}" for name, actual in sources.items()
                  if actual != SOURCES[name])
    print(json.dumps({"python": sys.version.split()[0], "packages": packages,
                      "source_hashes": sources, "errors": errors}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
