"""Archive bounded public ds007045 raw T2 acquisition sidecars, no images."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROTOCOL = ROOT / "DS007045_RAW_T2_ACQUISITION_METADATA_PROTOCOL_2026-10-01.md"
INVENTORY = ROOT / "literature/source_cache/ds007045_current_pair_audit_2026-10-01/result.json"
OUT = ROOT / "literature/source_cache/ds007045_raw_t2_sidecars_2026-10-01"
DESCRIPTION_SHA256 = "748fb52a1d943c6f50bb6e4795082e973c4a8694e01a287383a9bf1f20fff763"
BASE = "https://s3.amazonaws.com/openneuro.org/"


def get(url: str) -> tuple[int, bytes]:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    for attempt in range(2):
        try:
            with opener.open(request, timeout=30) as response:
                body = response.read(10_001)
                if len(body) > 10_000:
                    raise ValueError("Sidecar exceeded 10 KB cap")
                return response.status, body
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and not attempt:
                time.sleep(2)
                continue
            return exc.code, exc.read(10_001)
        except (urllib.error.URLError, TimeoutError):
            if attempt:
                raise
            time.sleep(2)
    raise AssertionError("unreachable")


def description_matches() -> bool:
    status, body = get(BASE + "ds007045/dataset_description.json")
    return status == 200 and hashlib.sha256(body).hexdigest() == DESCRIPTION_SHA256


def numeric(value: object) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def main() -> None:
    cases = json.loads(INVENTORY.read_text(encoding="utf-8"))["paired_subjects_list"]
    if len(cases) != 363 or len(set(cases)) != 363:
        raise ValueError("Current cohort inventory changed")
    if not description_matches():
        raise ValueError("Dataset description changed before sidecar audit")
    OUT.mkdir(parents=True, exist_ok=True)
    raw_dir = OUT / "raw"
    raw_dir.mkdir(exist_ok=True)
    contract = {"protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
                "inventory_sha256": hashlib.sha256(INVENTORY.read_bytes()).hexdigest(),
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "description_sha256": DESCRIPTION_SHA256, "cases": 363, "no_images": True}
    contract_path = OUT / "run_contract.json"
    if contract_path.exists():
        if json.loads(contract_path.read_text(encoding="utf-8")) != contract:
            raise ValueError("Existing audit contract changed")
    else:
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    records = []
    for index, case in enumerate(cases, 1):
        path = raw_dir / f"{case}_T2w.json"
        if path.exists():
            body = path.read_bytes()
            status = 200
        else:
            url = BASE + f"ds007045/{case}/anat/{case}_T2w.json"
            try:
                status, body = get(url)
            except Exception as exc:
                records.append({"case": case, "error": f"{type(exc).__name__}: {exc}"})
                continue
            if status == 200:
                path.write_bytes(body)
        row = {"case": case, "status": status, "bytes": len(body),
               "sha256": hashlib.sha256(body).hexdigest()}
        if status == 200:
            try:
                data = json.loads(body)
                row.update({"acquisition_type": data.get("MRAcquisitionType"),
                            "slice_thickness_mm": numeric(data.get("SliceThickness")),
                            "spacing_between_slices_mm": numeric(data.get("SpacingBetweenSlices")),
                            "image_type": data.get("ImageType"),
                            "site": case.split("-")[1].rstrip("0123456789")})
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
        else:
            row["error"] = f"HTTP {status}"
        records.append(row)
        if index % 25 == 0 or index == len(cases):
            print(f"ds007045 raw T2 sidecars {index}/{len(cases)}", flush=True)
    if not description_matches():
        raise ValueError("Dataset description changed after sidecar audit")
    good = [r for r in records if not r.get("error")]
    counts = Counter(r["acquisition_type"] or "missing" for r in good)
    site = defaultdict(Counter)
    for row in good:
        site[row["site"]][row["acquisition_type"] or "missing"] += 1
    thin_3d = [r["case"] for r in good if r["acquisition_type"] == "3D" and
               r["slice_thickness_mm"] is not None and r["slice_thickness_mm"] <= 1.5]
    thin_2d = [r["case"] for r in good if r["acquisition_type"] == "2D" and
               r["slice_thickness_mm"] is not None and r["slice_thickness_mm"] <= 1.5 and
               r["spacing_between_slices_mm"] is not None and r["spacing_between_slices_mm"] <= 1.5]
    summary = {"attempted": len(cases), "complete_sidecars": len(good),
               "failures": [r for r in records if r.get("error")],
               "acquisition_type_counts": dict(counts),
               "site_type_counts": {k: dict(v) for k, v in sorted(site.items())},
               "missing_slice_thickness": sum(r["slice_thickness_mm"] is None for r in good),
               "missing_spacing_between_slices": sum(r["spacing_between_slices_mm"] is None for r in good),
               "thin_3d_<=1_5mm": thin_3d, "thin_2d_<=1_5mm": thin_2d,
               "records": records, "no_images": True}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("records", "failures", "thin_3d_<=1_5mm", "thin_2d_<=1_5mm")}, indent=2))


if __name__ == "__main__":
    main()
