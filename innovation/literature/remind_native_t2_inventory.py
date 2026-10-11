"""Freeze official TCIA ReMIND preoperative 2D T2 series metadata."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "literature/remind_native_t2_inventory.json"
URL = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getSeries?Collection=ReMIND&Modality=MR"
CONTRACTS = {"2D_AX_T2_BLADE", "2D_AX_T2"}


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    with urllib.request.urlopen(URL, timeout=60) as response:
        raw = response.read()
    series = json.loads(raw)
    selected = [
        {
            "patient": item["PatientID"],
            "series_uid": item["SeriesInstanceUID"],
            "study_uid": item["StudyInstanceUID"],
            "series_description": item["SeriesDescription"],
            "study_description": item["StudyDesc"],
            "image_count": int(item["ImageCount"]),
            "file_size": int(item["FileSize"]),
            "license_name": item["LicenseName"],
            "license_uri": item["LicenseURI"],
            "collection_uri": item["CollectionURI"],
        }
        for item in series
        if item.get("StudyDesc") == "Preop" and item.get("SeriesDescription") in CONTRACTS
    ]
    selected.sort(key=lambda item: (item["patient"], item["series_description"], item["series_uid"]))
    patients = [item["patient"] for item in selected]
    if len(selected) != 63 or len(set(patients)) != 63:
        raise ValueError(f"unexpected selected series/patient count: {len(selected)}/{len(set(patients))}")
    if {item["license_uri"] for item in selected} != {"https://creativecommons.org/licenses/by/4.0/"}:
        raise ValueError("mixed or changed license")
    counts = {contract: sum(item["series_description"] == contract for item in selected)
              for contract in sorted(CONTRACTS)}
    if counts != {"2D_AX_T2": 36, "2D_AX_T2_BLADE": 27}:
        raise ValueError(f"unexpected protocol counts: {counts}")
    payload = {
        "source_url": URL,
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "collection_doi": "10.7937/3RAG-D070",
        "series_count": len(selected),
        "distinct_patients": len(set(patients)),
        "protocol_counts": counts,
        "series": selected,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("series_count", "distinct_patients", "protocol_counts", "response_sha256")}, indent=2))


if __name__ == "__main__":
    main()
