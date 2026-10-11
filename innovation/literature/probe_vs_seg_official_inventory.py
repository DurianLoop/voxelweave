"""Archive official VS-SEG nonpixel series list and modality mapping."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/vs_seg_official_inventory_2026-10-01"
SOURCES = {
    "series": ("https://services.cancerimagingarchive.net/nbia-api/services/v1/getSeries?" +
               urllib.parse.urlencode({"Collection": "Vestibular-Schwannoma-SEG", "Modality": "MR"}),
               5_000_000),
    "mapping": ("https://www.cancerimagingarchive.net/wp-content/uploads/DirectoryNamesMappingModality.csv",
                1_000_000),
}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for name, (url, cap) in SOURCES.items():
        entry = {"name": name, "url": url, "pixel_data_read": False}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
            with opener.open(req, timeout=90) as response:
                raw = response.read(cap + 1)
                entry["status"] = response.status
            if len(raw) > cap:
                raise ValueError("Response exceeded cap")
            file = "series.json" if name == "series" else "mapping.csv"
            (OUT / file).write_bytes(raw)
            entry.update({"file": file, "bytes": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()})
            if name == "series":
                rows = json.loads(raw)
                if not isinstance(rows, list):
                    raise ValueError("Series response is not a list")
                entry.update({"series_count": len(rows),
                              "patient_count": len({r.get("PatientID") for r in rows}),
                              "descriptions": dict(Counter(str(r.get("SeriesDescription", "")) for r in rows))})
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
        records.append(entry)
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
