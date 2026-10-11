"""CPU-only equal-information linear baseline for original public-source targets."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import zipfile
from collections import defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np
import pydicom


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "UNION_EVEN_LINEAR_CONTROL_PLAN_2026-10-01.md"
OUT = ROOT / "experiments/union_even_linear_control"
ORIGINAL = {
    "msvalid": (ROOT / "experiments/msvalid_ixi_weights_secondary/per_target.csv",
                "ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4"),
    "remind": (ROOT / "experiments/remind_native_t2_ixi_pair/per_target.csv",
               "450def82f8f03261b55c36ffaed952ee865e7c3be83c0c5b77df1f6a8e441e1c"),
}
ENSEMBLE = ROOT / "experiments/two_source_ensemble_error/per_target.csv"
ENSEMBLE_HASH = "2eddfb465c3d1873502dc3171cd502bee709f85f4742ee292ab0ce5ddf53ad88"
MS_MANIFEST = ROOT / "literature/msvalid_extraction_manifest.json"
MS_MANIFEST_HASH = "1ed9c3d417752acb8d111ce258afa190a6fd29aa6a8dbd7802284d953d468384"
MS_GEOMETRY = ROOT / "literature/msvalid_geometry_qualification.json"
REMIND_QUALIFIED = ROOT / "literature/remind_native_t2_qualification.json"
REMIND_QUALIFIED_HASH = "2f93f2849968a07b800ffca8c66ee21c9cdaea9e7152aac9c900d48099991b49"


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def csv_rows(path: Path, expected_hash: str) -> list[dict]:
    if sha256(path) != expected_hash:
        raise ValueError(f"Frozen source changed: {path}")
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def score(source: str, original: dict, ensemble: dict, planes: dict[int, np.ndarray]) -> dict:
    z = int(original["z"])
    left = (z // 4) * 4
    if not {z - 1, z, z + 1, left, left + 4} <= planes.keys():
        raise ValueError(f"Missing required published planes: {source}, {original['patient']}, {z}")
    anchor_l, anchor_r = planes[left], planes[left + 4]
    mask = ((np.abs(anchor_l) > .01 * max(float(np.max(np.abs(anchor_l))), 1e-6)) |
            (np.abs(anchor_r) > .01 * max(float(np.max(np.abs(anchor_r))), 1e-6)))
    if int(mask.sum()) != int(original["support_pixels"]):
        raise ValueError(f"Original support mismatch: {source}, {original['patient']}, {z}")
    prediction = ((planes[z - 1].astype(np.float64) + planes[z + 1].astype(np.float64)) / 2)[mask]
    truth = planes[z][mask].astype(np.float64)
    linear_mse = float(np.mean((prediction - truth) ** 2))
    model_mse = float(ensemble["disjoint_ensemble_mse"])
    if not math.isfinite(linear_mse) or linear_mse <= 0 or not math.isfinite(model_mse):
        raise ValueError(f"Invalid MSE: {source}, {original['patient']}, {z}")
    return {"source": source, "patient": original["patient"], "z": z,
            "residue": int(original["residue"]),
            "stratum": original.get("series_description", "msvalid"),
            "support_pixels": int(mask.sum()),
            "union_linear_mse": linear_mse, "disjoint_ensemble_mse": model_mse,
            "relative_ensemble_gain": (linear_mse - model_mse) / linear_mse}


def read_dicom_plane(archive: zipfile.ZipFile, member: str) -> np.ndarray:
    with archive.open(member) as stream:
        ds = pydicom.dcmread(stream)
    return (ds.pixel_array.astype(np.float32) * float(ds.get("RescaleSlope", 1))
            + float(ds.get("RescaleIntercept", 0)))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    original = {}
    for source, (path, expected_hash) in ORIGINAL.items():
        rows = csv_rows(path, expected_hash)
        assert len(rows) == (479 if source == "msvalid" else 248)
        original[source] = defaultdict(list)
        for row in rows:
            original[source][row["patient"]].append(row)
    ensemble = {(row["source"], row["patient"], row["z"]): row
                for row in csv_rows(ENSEMBLE, ENSEMBLE_HASH)}
    assert len(ensemble) == 727
    if sha256(MS_MANIFEST) != MS_MANIFEST_HASH:
        raise ValueError("MSValid source manifest changed")
    manifest = {row["patient"]: row for row in json.loads(MS_MANIFEST.read_text(encoding="utf-8"))["records"]}
    geometry = {row["patient"]: row for row in json.loads(MS_GEOMETRY.read_text(encoding="utf-8"))["patients"]}
    assert set(original["msvalid"]) == set(manifest) == set(geometry) and len(geometry) == 84
    target_results = []
    for index, patient in enumerate(sorted(geometry), 1):
        record = manifest[patient]
        path = ROOT / record["path"]
        if sha256(path) != record["sha256"]:
            raise ValueError(f"MSValid image hash changed: {patient}")
        volume = nib.load(str(path)).get_fdata(dtype=np.float32)
        if tuple(volume.shape) != tuple(geometry[patient]["shape"]):
            raise ValueError(f"MSValid geometry changed: {patient}")
        expected = {z for r in (1, 3) for z in geometry[patient]["eligible_targets"][f"residue_{r}"]}
        assert expected == {int(row["z"]) for row in original["msvalid"][patient]}
        needed = {q for z in expected for q in (z - 1, z, z + 1, (z // 4) * 4, (z // 4 + 1) * 4)}
        planes = {z: volume[:, :, z] for z in needed}
        for row in original["msvalid"][patient]:
            target_results.append(score("msvalid", row, ensemble[("msvalid", patient, row["z"])], planes))
        print(f"MSValid {index}/84", flush=True)
    if sha256(REMIND_QUALIFIED) != REMIND_QUALIFIED_HASH:
        raise ValueError("ReMIND header qualification changed")
    qualified = json.loads(REMIND_QUALIFIED.read_text(encoding="utf-8"))["records"]
    eligible = [row for row in qualified if row["eligible"]]
    assert len(qualified) == 63 and len(eligible) == 62 and len(original["remind"]) == 62
    for index, record in enumerate(eligible, 1):
        patient = record["patient"]
        path = ROOT / record["path"]
        if sha256(path) != record["zip_sha256"]:
            raise ValueError(f"ReMIND ZIP hash changed: {patient}")
        expected = {z for r in ("1", "3") for z in record["targets"][r]}
        assert expected == {int(row["z"]) for row in original["remind"][patient]}
        needed = {q for z in expected for q in (z - 1, z, z + 1, (z // 4) * 4, (z // 4 + 1) * 4)}
        with zipfile.ZipFile(path) as archive:
            planes = {z: read_dicom_plane(archive, record["ordered_files"][z]) for z in needed}
        for row in original["remind"][patient]:
            target_results.append(score("remind", row, ensemble[("remind", patient, row["z"])], planes))
        print(f"ReMIND {index}/62", flush=True)
    patient_results = []
    for source in ("msvalid", "remind"):
        by_patient = defaultdict(list)
        for row in target_results:
            if row["source"] == source:
                by_patient[row["patient"]].append(row)
        for patient, rows in sorted(by_patient.items()):
            residues = {r: [row for row in rows if row["residue"] == r] for r in (1, 3)}
            if not all(residues.values()):
                raise ValueError(f"Missing residue: {source}, {patient}")
            linear = float(np.mean([np.mean([row["union_linear_mse"] for row in residues[r]]) for r in (1, 3)]))
            model = float(np.mean([np.mean([row["disjoint_ensemble_mse"] for row in residues[r]]) for r in (1, 3)]))
            patient_results.append({"source": source, "patient": patient, "stratum": rows[0]["stratum"],
                                    "targets": len(rows), "union_linear_mse": linear,
                                    "disjoint_ensemble_mse": model,
                                    "relative_ensemble_gain": (linear - model) / linear})
    summary = {}
    for source, seed in (("msvalid", 20261001), ("remind", 20261002)):
        patients = [row for row in patient_results if row["source"] == source]
        targets = [row for row in target_results if row["source"] == source]
        values = np.array([row["relative_ensemble_gain"] for row in patients])
        rng = np.random.default_rng(seed)
        if source == "msvalid":
            draws = values[rng.integers(0, len(values), size=(5000, len(values)))].mean(axis=1)
        else:
            draws = np.zeros(5000)
            for label, expected in (("2D_AX_T2", 35), ("2D_AX_T2_BLADE", 27)):
                group = np.array([row["relative_ensemble_gain"] for row in patients if row["stratum"] == label])
                if len(group) != expected:
                    raise ValueError(f"Wrong ReMIND stratum count: {label}")
                draws += (expected / len(values) *
                          group[rng.integers(0, expected, size=(5000, expected))].mean(axis=1))
        summary[source] = {"patients": len(patients), "targets": len(targets),
                           "mean_patient_relative_ensemble_gain": float(values.mean()),
                           "ci95": np.percentile(draws, [2.5, 97.5]).tolist(),
                           "ensemble_better_patients": int((values > 0).sum()),
                           "linear_better_patients": int((values < 0).sum()),
                           "ensemble_better_targets": sum(row["relative_ensemble_gain"] > 0 for row in targets),
                           "linear_better_targets": sum(row["relative_ensemble_gain"] < 0 for row in targets)}
    OUT.mkdir(parents=True)
    for name, rows in (("per_patient.csv", patient_results), ("per_target.csv", target_results)):
        with (OUT / name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    result = {"plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
              "ensemble_source_sha256": ENSEMBLE_HASH,
              "sources": summary, "model_inference_run": False, "gpu_used": False,
              "status": "post_result_exploratory"}
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
