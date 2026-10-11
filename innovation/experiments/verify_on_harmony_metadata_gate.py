"""Independently verify the nonimage ON-Harmony 2D/retest intersection."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "literature/source_cache/on_harmony_release_text_2026-10-01"
DELAYS = SOURCE / "s3_scan_delays.csv"
DESCRIPTION = SOURCE / "s3_description.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    assert sha256(DELAYS) == "164b9d6264eaba523c4813c11cff64198c490dbf9b849d5b7c8c4449e71fbf3b"
    assert sha256(DESCRIPTION) == "5e3d21af3a15662ec888de7b50d3890eab587c12d861c0cc03f7f2edc67ae690"
    with DELAYS.open(newline="", encoding="utf-8-sig") as stream:
        rows = [row for row in csv.DictReader(stream) if row["Phase"] in {"A", "B"}]
    assert len(rows) == 20
    assert len({row[""] for row in rows}) == 20
    repeated = [row for row in rows if row["Repeat scanner code"]]
    assert len(repeated) == 9
    assert all(all(row[f"repeat_{n:03d}"] for n in range(2, 7)) for row in repeated)
    counts = Counter(row["Repeat scanner code"] for row in repeated)
    assert counts == Counter({
        "OXF1PRI": 2, "OXF2PRI": 2, "OXF3TRI": 1, "NOT1ACH": 1,
        "NOT2ING": 1, "NOT4GEP": 1, "OXF4GEP": 1,
    })
    assert counts["NOT3GEM"] == 0
    assert sum(row["Phase"] == "A" and bool(row["NOT3GEM"]) for row in rows) == 10
    print("PASS: 20 participants, 9 within-scanner repeat participants, 0 MR750 repeats")


if __name__ == "__main__":
    main()
