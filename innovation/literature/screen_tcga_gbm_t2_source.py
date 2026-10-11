"""Archive TCIA TCGA-GBM page and MR-series metadata without reading pixels."""
from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "TCGA_GBM_T2_SOURCE_SCREEN_PLAN_2026-10-01.md"
OUT = ROOT / "literature/source_cache"
PAGE = OUT / "tcga_gbm_collection_page_2026-10-01.html"
SERIES = OUT / "tcga_gbm_getSeries_2026-10-01.json"
COLLECTIONS = OUT / "tcga_gbm_getCollectionValues_2026-10-01.json"
SUMMARY = ROOT / "literature/tcga_gbm_t2_metadata_screen.json"
PAGE_URL = "https://www.cancerimagingarchive.net/collection/tcga-gbm/"
SERIES_URL = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getSeries?" + urllib.parse.urlencode(
    {"Collection": "TCGA-GBM", "Modality": "MR"})
COLLECTIONS_URL = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getCollectionValues"
T2 = re.compile(r"(?:\bT2W?\b|\bTSE\b|TURBO.?SPIN.?ECHO)", re.IGNORECASE)
EXCLUDE = re.compile(r"FLAIR|\bDWI\b|\bADC\b|\bSWI\b|\bT1\b|SEGMENT|\bMAP\b|POST.?CONTRAST|\bPOST\b", re.IGNORECASE)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(opener: urllib.request.OpenerDirector, url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-qualification/1.0"})
    with opener.open(request, timeout=90) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return response.read()


def main() -> None:
    if any(path.exists() for path in (PAGE, SERIES, COLLECTIONS, SUMMARY)):
        raise FileExistsError("Refusing to overwrite official-source evidence")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    page = fetch(opener, PAGE_URL)
    series = fetch(opener, SERIES_URL)
    collections = fetch(opener, COLLECTIONS_URL)
    listed = json.loads(collections)
    if not isinstance(listed, list):
        raise ValueError("Official NBIA collection list is malformed")
    source_available = bool(series)
    rows = json.loads(series) if source_available else []
    if not isinstance(rows, list):
        raise ValueError("Official TCGA-GBM series response is malformed")
    descriptions = Counter(str(row.get("SeriesDescription", "")) for row in rows)
    candidates = defaultdict(list)
    for row in rows:
        desc = str(row.get("SeriesDescription", ""))
        if (row.get("Modality") == "MR" and T2.search(desc) and not EXCLUDE.search(desc)
                and int(row.get("ImageCount", 0)) >= 24):
            candidates[desc].append(row)
    candidate_descriptions = {
        desc: {"series": len(group),
               "patients": len({row.get("PatientID") for row in group}),
               "image_count_range": [min(int(row["ImageCount"]) for row in group),
                                     max(int(row["ImageCount"]) for row in group)]}
        for desc, group in candidates.items()}
    ranking = sorted(candidate_descriptions, key=lambda desc: (
        -candidate_descriptions[desc]["patients"], -candidate_descriptions[desc]["series"], desc))
    summary = {"plan_sha256": sha256(PLAN.read_bytes()),
               "script_sha256": sha256(Path(__file__).read_bytes()),
               "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
               "collection_page": {"url": PAGE_URL, "file": PAGE.relative_to(ROOT).as_posix(),
                                   "bytes": len(page), "sha256": sha256(page)},
               "official_series": {"url": SERIES_URL, "file": SERIES.relative_to(ROOT).as_posix(),
                                   "bytes": len(series), "sha256": sha256(series)},
               "official_collection_values": {
                   "url": COLLECTIONS_URL, "file": COLLECTIONS.relative_to(ROOT).as_posix(),
                   "bytes": len(collections), "sha256": sha256(collections),
                   "tcga_gbm_listed": any(row.get("Collection") == "TCGA-GBM" for row in listed)},
               "source_available": source_available,
               "series_count": len(rows) if source_available else None,
               "patient_count": len({row.get("PatientID") for row in rows}) if source_available else None,
               "licenses": dict(Counter(str(row.get("LicenseURI", "")) for row in rows)),
               "collection_uris": dict(Counter(str(row.get("CollectionURI", "")) for row in rows)),
               "all_descriptions": dict(descriptions.most_common()),
               "candidate_descriptions": candidate_descriptions,
               "ranked_candidate_descriptions": ranking,
               "pixel_data_read": False}
    PAGE.write_bytes(page)
    SERIES.write_bytes(series)
    COLLECTIONS.write_bytes(collections)
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "source_available", "series_count", "patient_count", "licenses", "collection_uris",
        "official_collection_values",
        "ranked_candidate_descriptions", "pixel_data_read")}, indent=2))


if __name__ == "__main__":
    main()
