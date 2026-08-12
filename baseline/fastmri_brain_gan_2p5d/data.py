from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRE_ROOT = ROOT / "pre"
if str(PRE_ROOT) not in sys.path:
    sys.path.insert(0, str(PRE_ROOT))

from ixi_diffusion.common import read_case_ids

from .settings import INDEX_PATH, SPLIT_ROOT


def load_index() -> pd.DataFrame:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"{INDEX_PATH} does not exist.")
    return pd.read_csv(INDEX_PATH)


def split_case_ids(split: str, limit: int | None = None) -> list[str]:
    path = SPLIT_ROOT / f"{split}_cases.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist.")
    return read_case_ids(path, limit)


def case_paths(split: str, limit: int | None = None) -> list[Path]:
    cases = load_index()
    lookup: dict[str, list[Path]] = {}
    for _, row in cases.iterrows():
        lookup.setdefault(str(row["case_id"]), []).append(Path(str(row["nifti_path"])))
    out: list[Path] = []
    for case_id in split_case_ids(split, limit):
        out.extend(lookup.get(case_id, []))
    return out

