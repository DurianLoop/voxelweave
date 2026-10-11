"""Screen all 15 public QIN repeat-T2 pairs without reading PixelData."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pydicom

from qin_repeat_t2_header_pilot import read_series, sha256


ROOT = Path(__file__).resolve().parents[2] / "innovation"
PLAN = ROOT / "QIN_REPEAT_T2_ALL_HEADER_PLAN_2026-10-01.md"
SOURCE = ROOT / "literature/source_cache/qin_repeat_t2_getSeries_2026-10-01.json"
PILOT = ROOT / "literature/qin_repeat_t2_pilot_download_manifest.json"
DATA = ROOT / "data/qin_prostate_repeat_t2"
OUT = ROOT / "literature/qin_repeat_t2_all_header_screen.json"
EXPECTED_SOURCE_SHA256 = "2aa9a41cd2871ac16f1cea588cf2970c32cd8152aab7e3bfd465cd0d5f2f88b5"
API = "https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?"


def download(opener: urllib.request.OpenerDirector, row: dict,
             pilot_hashes: dict) -> dict:
    patient = row["PatientID"]
    path = DATA / f"{patient}_repeat_{row['repeat']}.zip"
    if path.is_file():
        if row["SeriesInstanceUID"] in pilot_hashes:
            if sha256(path) != pilot_hashes[row["SeriesInstanceUID"]]:
                raise ValueError("Frozen pilot ZIP hash changed")
            status = "pilot_reuse"
        else:
            if not zipfile.is_zipfile(path):
                raise ValueError("Existing ZIP is invalid")
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None or sum(name.lower().endswith(".dcm") for name in archive.namelist()) != int(row["ImageCount"]):
                    raise ValueError("Existing ZIP integrity or DICOM count failed")
            status = "verified_resume"
    else:
        partial = path.with_suffix(".zip.part")
        if partial.exists():
            raise FileExistsError(f"Incomplete prior download: {partial}")
        url = API + urllib.parse.urlencode({"SeriesInstanceUID": row["SeriesInstanceUID"]})
        for attempt in range(1, 4):
            try:
                with opener.open(url, timeout=90) as response, partial.open("wb") as target:
                    for block in iter(lambda: response.read(1024 * 1024), b""):
                        target.write(block)
                if not zipfile.is_zipfile(partial):
                    raise ValueError("NBIA response was not a ZIP")
                partial.rename(path)
                break
            except (OSError, ValueError):
                if partial.exists():
                    partial.unlink()
                if attempt == 3:
                    raise
                time.sleep(2 * attempt)
        status = "downloaded"
    with zipfile.ZipFile(path) as archive:
        dicoms = sum(name.lower().endswith(".dcm") for name in archive.namelist())
    return {"patient": patient, "repeat": row["repeat"],
            "series_uid": row["SeriesInstanceUID"],
            "study_uid": row["StudyInstanceUID"],
            "study_date": row.get("StudyDate"),
            "expected_images": int(row["ImageCount"]),
            "archive_path": path.relative_to(ROOT).as_posix(),
            "zip_bytes": path.stat().st_size, "zip_sha256": sha256(path),
            "dicom_members": dicoms, "status": status}


def validate_within_series(record: dict) -> None:
    path = ROOT / record["archive_path"]
    values = set()
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.lower().endswith(".dcm"):
                with archive.open(name) as stream:
                    ds = pydicom.dcmread(stream, stop_before_pixels=True)
                if "PixelData" in ds:
                    raise AssertionError("PixelData unexpectedly decoded")
                values.add((int(ds.Rows), int(ds.Columns),
                            float(ds.get("RepetitionTime", 0)), float(ds.get("EchoTime", 0)),
                            float(ds.get("SliceThickness", 0)),
                            float(ds.get("SpacingBetweenSlices", 0))))
    if len(values) != 1:
        raise ValueError(f"Technical protocol varies within series: {len(values)} values")


def compare(first: dict, centers1: np.ndarray, orientation1: np.ndarray,
            second: dict, centers2: np.ndarray, orientation2: np.ndarray) -> tuple[dict, list[str]]:
    normal1, normal2 = np.array(first["normal"]), np.array(second["normal"])
    normal_angle = float(np.degrees(np.arccos(np.clip(np.dot(normal1, normal2), -1, 1))))
    orientation_diff = float(np.max(np.abs(orientation1 - orientation2)))
    spacing_diff = float(np.max(np.abs(np.array(first["pixel_spacing_mm"]) -
                                       np.array(second["pixel_spacing_mm"]))))
    tr1, tr2 = first["repetition_time_ms"], second["repetition_time_ms"]
    te1, te2 = first["echo_time_ms"], second["echo_time_ms"]
    tr_diff = abs(tr1 - tr2) / max(tr1, tr2) if tr1 and tr2 else None
    te_diff = abs(te1 - te2) / max(te1, te2) if te1 and te2 else None
    if len(centers1) == len(centers2):
        distances = np.linalg.norm(centers1 - centers2, axis=1)
        max_distance, median_distance = float(np.max(distances)), float(np.median(distances))
    else:
        max_distance = median_distance = None
    failures = []
    if first["study_dates"] == second["study_dates"] or first["acquisition_dates"] == second["acquisition_dates"]:
        failures.append("no_distinct_study_and_acquisition_dates")
    if not first["acquisition_times_present"] or not second["acquisition_times_present"]:
        failures.append("missing_acquisition_time")
    if any(info["acquisition_types"] != ["2D"] or
           not all(t.startswith("ORIGINAL/PRIMARY") for t in info["image_types"])
           for info in (first, second)):
        failures.append("not_original_primary_2d")
    if (first["rows"], first["columns"]) != (second["rows"], second["columns"]):
        failures.append("matrix_mismatch")
    if spacing_diff > 1e-3:
        failures.append("pixel_spacing_mismatch")
    if orientation_diff > 1e-4:
        failures.append("orientation_mismatch")
    if tr_diff is None or tr_diff > 0.05:
        failures.append("TR_mismatch")
    if te_diff is None or te_diff > 0.05:
        failures.append("TE_mismatch")
    if max_distance is None or max_distance > 0.5:
        failures.append("center_grid_mismatch")
    metrics = {"normal_angle_degrees": normal_angle,
               "max_abs_orientation_component_difference": orientation_diff,
               "max_pixel_spacing_difference_mm": spacing_diff,
               "relative_TR_difference": tr_diff, "relative_TE_difference": te_diff,
               "max_matched_center_distance_mm": max_distance,
               "median_matched_center_distance_mm": median_distance}
    return metrics, failures


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise ValueError("Frozen official source response changed")
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    groups = defaultdict(list)
    for row in records:
        if row.get("Modality") == "MR" and row.get("SeriesDescription") == "T2 Weighted Axial" and int(row.get("ImageCount", 0)) >= 24:
            if row.get("LicenseURI", "").rstrip("/") != "https://creativecommons.org/licenses/by/4.0":
                raise ValueError("T2 series license metadata changed")
            groups[row["PatientID"]].append(row)
    if len(groups) != 15 or sum(map(len, groups.values())) != 30 or any(len(v) != 2 for v in groups.values()):
        raise ValueError("Frozen 15-patient/30-series cohort changed")
    for rows in groups.values():
        rows.sort(key=lambda row: (row.get("StudyDate", ""), row["SeriesInstanceUID"]))
        for repeat, row in enumerate(rows, 1):
            row["repeat"] = repeat
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    pilot_hashes = {row["series_uid"]: row["zip_sha256"] for row in pilot["records"]}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    DATA.mkdir(parents=True, exist_ok=True)
    results, all_downloads, failures = [], [], []
    started = time.perf_counter()
    for index, patient in enumerate(sorted(groups), 1):
        pair = []
        for row in groups[patient]:
            try:
                record = download(opener, row, pilot_hashes)
                all_downloads.append(record)
                header, centers, orientation = read_series(record)
                validate_within_series(record)
                pair.append((header, centers, orientation))
            except Exception as error:
                failures.append({"patient": patient, "repeat": row["repeat"],
                                 "error": f"{type(error).__name__}: {error}"})
        if len(pair) == 2:
            metrics, reasons = compare(*pair[0], *pair[1])
            results.append({"patient": patient, "image_counts": [p[0]["dicom_headers"] for p in pair],
                            "study_dates": [p[0]["study_dates"][0] for p in pair],
                            "image_types": [p[0]["image_types"] for p in pair],
                            "acquisition_types": [p[0]["acquisition_types"] for p in pair],
                            **metrics, "strict_header_eligible": not reasons,
                            "failed_conditions": reasons})
            print(f"{index}/15 {patient}: eligible={not reasons} reasons={','.join(reasons)} elapsed={time.perf_counter()-started:.1f}s", flush=True)
        else:
            print(f"{index}/15 {patient}: incomplete header pair elapsed={time.perf_counter()-started:.1f}s", flush=True)
    summary = {"plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
               "pilot_script_sha256": sha256(Path(__file__).with_name("qin_repeat_t2_header_pilot.py")),
               "official_source_sha256": sha256(SOURCE), "pilot_manifest_sha256": sha256(PILOT),
               "patients_expected": 15, "series_expected": 30,
               "series_downloaded_or_reused": len(all_downloads), "pairs_scored": len(results),
               "pairs_strict_eligible": sum(r["strict_header_eligible"] for r in results),
               "download_or_parse_failures": failures,
               "failure_condition_counts": {reason: sum(reason in r["failed_conditions"] for r in results)
                                            for reason in sorted({reason for r in results for reason in r["failed_conditions"]})},
               "pixel_data_read": False, "elapsed_seconds": time.perf_counter() - started,
               "downloads": all_downloads, "pairs": results}
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("patients_expected", "series_expected",
                                                  "series_downloaded_or_reused", "pairs_scored",
                                                  "pairs_strict_eligible", "download_or_parse_failures",
                                                  "failure_condition_counts", "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    main()
