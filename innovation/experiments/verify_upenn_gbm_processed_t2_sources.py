"""Independent read-only verification of UPENN official selection and DICOM headers."""
from __future__ import annotations

import hashlib
import json
import math
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "literature/source_cache/upenn_gbm_getSeries_2026-10-01.json"
INVENTORY = ROOT / "literature/upenn_gbm_processed_t2_inventory.json"
DOWNLOADS = ROOT / "literature/upenn_gbm_processed_t2_download_manifest.json"
QUALIFIED = ROOT / "literature/upenn_gbm_processed_t2_qualification.json"
PROTOCOL = ROOT / "UPENN_GBM_PROCESSED_T2_CONTEXT_PROTOCOL_2026-10-01.md"
DESCRIPTION = "Axial T2 tse: Processed_CaPTk"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def target_positions(depth: int) -> dict[str, list[int]]:
    phases = [range(0, depth, 4), range(2, depth, 4)]
    selected = {}
    for residue in (1, 3):
        pool = [z for z in range(depth) if z % 4 == residue and
                all(sum(a < z for a in phase) >= 2 and
                    sum(a > z for a in phase) >= 2 for phase in phases)]
        assert len(pool) >= 2
        selected[str(residue)] = [pool[math.floor((len(pool) - 1) / 3)],
                                  pool[math.ceil(2 * (len(pool) - 1) / 3)]]
    return selected


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    downloads = json.loads(DOWNLOADS.read_text(encoding="utf-8"))
    qualified = json.loads(QUALIFIED.read_text(encoding="utf-8"))
    assert inventory["source_sha256"] == sha256(SOURCE)
    assert inventory["protocol_sha256"] == sha256(PROTOCOL)
    assert downloads["inventory_sha256"] == sha256(INVENTORY)
    assert qualified["download_manifest_sha256"] == sha256(DOWNLOADS)
    assert qualified["inventory_sha256"] == sha256(INVENTORY)
    assert qualified["protocol_sha256"] == sha256(PROTOCOL)
    all_rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    groups = defaultdict(list)
    for row in all_rows:
        if (row.get("Modality") == "MR" and row.get("SeriesDescription") == DESCRIPTION
                and int(row.get("ImageCount", 0)) >= 24):
            groups[row["PatientID"]].append(row)
    assert sum(map(len, groups.values())) == 402 and len(groups) == 374
    expected = {
        patient: min(rows, key=lambda r: (r.get("StudyDate", ""), r["SeriesInstanceUID"]))
        for patient, rows in groups.items()}
    items = inventory["series"]
    assert len(items) == 374 and [x["patient"] for x in items] == sorted(expected)
    for item in items:
        official = expected[item["patient"]]
        assert item["series_uid"] == official["SeriesInstanceUID"]
        assert item["study_uid"] == official["StudyInstanceUID"]
        assert item["image_count"] == int(official["ImageCount"])
    downloaded = {row["patient"]: row for row in downloads["records"]}
    records = {row["patient"]: row for row in qualified["records"]}
    assert len(downloaded) == len(records) == 374
    assert not downloads["failures"]
    image_types, physical_steps, nominal_steps, depths = Counter(), Counter(), Counter(), Counter()
    headers_read = 0
    for index, item in enumerate(items, 1):
        patient = item["patient"]
        archive_record, qualification = downloaded[patient], records[patient]
        path = ROOT / archive_record["path"]
        assert path.stat().st_size == archive_record["bytes"]
        assert sha256(path) == archive_record["zip_sha256"] == qualification["zip_sha256"]
        positions, orientations, pixel_spacings, types, tag_spacing, sop, filenames = [], [], [], [], [], set(), []
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            names = [name for name in archive.namelist() if name.lower().endswith(".dcm")]
            assert len(names) == item["image_count"] == archive_record["dicom_files"]
            for name in names:
                with archive.open(name) as stream:
                    ds = pydicom.dcmread(stream, stop_before_pixels=True)
                assert "PixelData" not in ds
                assert str(ds.PatientID) == patient
                assert str(ds.StudyInstanceUID) == item["study_uid"]
                assert str(ds.SeriesInstanceUID) == item["series_uid"]
                assert str(ds.SeriesDescription) == DESCRIPTION
                assert str(ds.MRAcquisitionType) == "2D"
                assert str(ds.PhotometricInterpretation) == "MONOCHROME2"
                assert int(ds.SamplesPerPixel) == 1
                assert [int(ds.Rows), int(ds.Columns)] == qualification["shape"]
                sop.add(str(ds.SOPInstanceUID))
                filenames.append(name)
                positions.append(np.asarray(ds.ImagePositionPatient, dtype=float))
                orientations.append(np.asarray(ds.ImageOrientationPatient, dtype=float))
                pixel_spacings.append(np.asarray(ds.PixelSpacing, dtype=float))
                types.append("/".join(map(str, ds.ImageType)))
                tag_spacing.append(float(ds.SpacingBetweenSlices))
        assert len(sop) == len(filenames)
        direction = np.asarray(orientations)
        assert np.max(np.abs(direction - direction[0])) <= 1e-4
        spacing = np.asarray(pixel_spacings)
        assert np.max(np.abs(spacing / spacing[0] - 1)) <= .005
        assert np.allclose(spacing[0], qualification["pixel_spacing_mm"], rtol=0, atol=1e-5)
        normal = np.cross(direction[0, :3], direction[0, 3:])
        normal /= np.linalg.norm(normal)
        projected = np.asarray(positions) @ normal
        order = np.argsort(projected)
        distances = np.diff(projected[order])
        median = float(np.median(distances))
        assert np.all(distances > 0)
        assert np.max(np.abs(distances / median - 1)) <= .02
        assert math.isclose(median, qualification["z_spacing_mm"], abs_tol=1e-5)
        assert [filenames[i] for i in order] == qualification["ordered_files"]
        assert qualification["targets"] == target_positions(len(filenames))
        assert qualification["eligible"]
        assert set(types) == set(qualification["image_types"])
        image_types.update(set(types))
        physical_steps[round(median, 3)] += 1
        nominal_steps.update(set(tag_spacing))
        depths[len(filenames)] += 1
        headers_read += len(filenames)
        if index % 50 == 0 or index == 374:
            print(f"verified {index}/374", flush=True)
    assert headers_read == 23702
    assert image_types == {"DERIVED/SECONDARY/OTHER": 374}
    assert physical_steps == {3.0: 367, 4.8: 7}
    assert nominal_steps == {1.0: 374}
    print(json.dumps({"status": "PASS", "series": 374, "dicom_headers": headers_read,
                      "derived_secondary_series": image_types["DERIVED/SECONDARY/OTHER"],
                      "physical_step_mm": dict(physical_steps),
                      "tag_spacing_mm": dict(nominal_steps),
                      "depths": dict(depths), "pixel_data_read": False}, indent=2))


if __name__ == "__main__":
    main()
