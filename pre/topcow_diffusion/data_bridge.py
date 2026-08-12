from __future__ import annotations

import sys

from .common import ROOT


def import_v4_dataset():
    v4_dir = str(ROOT / "v4")
    if v4_dir not in sys.path:
        sys.path.insert(0, v4_dir)
    from config import MODEL_CONFIG  # type: ignore
    from dataset import MRIDataset  # type: ignore
    return MRIDataset, MODEL_CONFIG
