"""Post-result native-linear companion control for the public IXI-weight pair."""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
import zipfile
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import pydicom
import torch

import msvalid_ixi_weights_secondary as msvalid
import remind_native_t2_ixi_pair as remind


ROOT = Path(__file__).resolve().parents[2]
INNOVATION = ROOT / "innovation"
PLAN = INNOVATION / "PUBLIC_LINEAR_PARTNER_CONTROL_PLAN_2026-10-01.md"
OUT = INNOVATION / "experiments/public_linear_partner_control"
EXPECTED_MAIN = {
    "msvalid": "ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4",
    "remind": "450def82f8f03261b55c36ffaed952ee865e7c3be83c0c5b77df1f6a8e441e1c",
}


def original_rows(source: str) -> dict[tuple[str, int], dict[str, str]]:
    folder = ("msvalid_ixi_weights_secondary" if source == "msvalid"
              else "remind_native_t2_ixi_pair")
    path = INNOVATION / "experiments" / folder / "per_target.csv"
    if msvalid.sha256(path) != EXPECTED_MAIN[source]:
        raise ValueError(f"original {source} target results changed")
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return {(row["patient"], int(row["z"])): row for row in rows}


def mask_from_phase0(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
            (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))


def linear(planes: dict[int, np.ndarray], z: int, phase: int) -> np.ndarray:
    left = phase + ((z - phase) // 4) * 4
    rel = (z - left) / 4
    return ((1 - rel) * planes[left] + rel * planes[left + 4]).astype(np.float32)


def score(patient: str, z: int, residue: int, group: str, spacing: float,
          planes: dict[int, np.ndarray], prepared: tuple,
          hat: object, original: dict[tuple[str, int], dict[str, str]]) -> dict:
    i0 = z // 4
    left, right = planes[4 * i0], planes[4 * (i0 + 1)]
    mask = mask_from_phase0(left, right)
    if not mask.any():
        raise ValueError(f"empty support: {patient} z{z}")
    a = msvalid.predict(hat, prepared, i0, (z - 4 * i0) / 4, left.shape)
    y = planes[z]
    shared = msvalid.metrics(a, linear(planes, z, 0), y, mask)
    disjoint = msvalid.metrics(a, linear(planes, z, 2), y, mask)
    prior = original[(patient, z)]
    if (int(prior["support_pixels"]) != int(mask.sum()) or
            abs(float(prior["shared_a_mae"]) - shared["a_mae"]) > 1e-5):
        raise ValueError(f"fixed reference replay mismatch: {patient} z{z}")
    return {"patient": patient, "z": z, "residue": residue, "group": group,
            "z_spacing_mm": spacing, "support_pixels": int(mask.sum()),
            "a_mae": shared["a_mae"],
            "shared_o": shared["observable"], "disjoint_o": disjoint["observable"],
            "delta_o": disjoint["observable"] - shared["observable"],
            "shared_b_mae": shared["b_mae"], "disjoint_b_mae": disjoint["b_mae"],
            "shared_b_mse": shared["b_mse"], "disjoint_b_mse": disjoint["b_mse"]}


def score_msvalid(hat: object, original: dict) -> list[dict]:
    cohort = json.loads(msvalid.QUALIFIED.read_text(encoding="utf-8"))["patients"]
    source = json.loads(msvalid.SOURCE_MANIFEST.read_text(encoding="utf-8"))["records"]
    hashes = {row["patient"]: row["sha256"] for row in source}
    if len(cohort) != 84 or set(hashes) != {row["patient"] for row in cohort}:
        raise ValueError("MSValid cohort/source mismatch")
    rows = []
    for index, patient in enumerate(cohort, 1):
        pid = patient["patient"]
        path = msvalid.DATA / f"{pid}.nii.gz"
        if msvalid.sha256(path) != hashes[pid]:
            raise ValueError(f"MSValid source changed: {pid}")
        volume = nib.load(str(path)).get_fdata(dtype=np.float32)
        if tuple(volume.shape) != tuple(patient["shape"]) or not np.isfinite(volume).all():
            raise ValueError(f"MSValid geometry/pixels changed: {pid}")
        planes = {z: volume[:, :, z] for z in range(volume.shape[2])}
        phase0 = np.ascontiguousarray(volume[:, :, list(range(0, volume.shape[2], 4))])
        prepared = msvalid.prepared(phase0)
        for residue in (1, 3):
            for z in patient["eligible_targets"][f"residue_{residue}"]:
                rows.append(score(pid, z, residue, "MSValid", patient["zooms_mm"][2],
                                  planes, prepared, hat, original))
        print(f"MSValid {index}/84 {pid}", flush=True)
    return rows


def score_remind(hat: object, original: dict) -> list[dict]:
    cohort = json.loads(remind.QUALIFIED.read_text(encoding="utf-8"))
    if len(cohort["records"]) != 63 or cohort["patients_header_eligible"] != 62:
        raise ValueError("ReMIND qualification mismatch")
    if (cohort["inventory_sha256"] != remind.sha256(remind.INVENTORY) or
            cohort["download_manifest_sha256"] != remind.sha256(remind.DOWNLOADS) or
            cohort["protocol_sha256"] != remind.sha256(remind.PROTOCOL)):
        raise ValueError("ReMIND frozen inputs changed")
    rows = []
    for index, patient in enumerate(cohort["records"], 1):
        if not patient["eligible"]:
            print(f"ReMIND {index}/63 {patient['patient']} header exclusion", flush=True)
            continue
        pid = patient["patient"]
        path = INNOVATION / patient["path"]
        if remind.sha256(path) != patient["zip_sha256"]:
            raise ValueError(f"ReMIND source changed: {pid}")
        depth = patient["depth"]
        selected = set(range(0, depth, 2))
        selected.update(z for targets in patient["targets"].values() for z in targets)
        planes = {}
        with zipfile.ZipFile(path) as archive:
            for z in sorted(selected):
                with archive.open(patient["ordered_files"][z]) as stream:
                    ds = pydicom.dcmread(stream)
                plane = ds.pixel_array.astype(np.float32)
                if tuple(plane.shape) != tuple(patient["shape"]):
                    raise ValueError(f"ReMIND shape changed: {pid} z{z}")
                plane = plane * float(ds.get("RescaleSlope", 1)) + float(ds.get("RescaleIntercept", 0))
                if not np.isfinite(plane).all():
                    raise ValueError(f"ReMIND nonfinite plane: {pid} z{z}")
                planes[z] = plane
        phase0 = np.stack([planes[z] for z in range(0, depth, 4)], axis=2)
        prepared = remind.prepared(phase0)
        for residue in (1, 3):
            for z in patient["targets"][str(residue)]:
                rows.append(score(pid, z, residue, patient["series_description"],
                                  patient["z_spacing_mm"], planes, prepared, hat, original))
        print(f"ReMIND {index}/63 {pid}", flush=True)
    return rows


def aggregate(rows: list[dict], source: str) -> tuple[list[dict], dict]:
    by_patient: dict[str, list[dict]] = {}
    for row in rows:
        by_patient.setdefault(row["patient"], []).append(row)
    keys = ("shared_o", "disjoint_o", "delta_o", "a_mae", "shared_b_mae",
            "disjoint_b_mae", "shared_b_mse", "disjoint_b_mse")
    patients = []
    for pid, targets in by_patient.items():
        residue = {r: [row for row in targets if row["residue"] == r] for r in (1, 3)}
        if not residue[1] or not residue[3]:
            raise ValueError(f"missing residue: {pid}")
        values = {key: float(np.mean([np.mean([row[key] for row in residue[r]])
                                      for r in (1, 3)])) for key in keys}
        patients.append({"patient": pid, "group": targets[0]["group"],
                         "targets": len(targets), **values})
    values = np.array([row["delta_o"] for row in patients])
    rng = np.random.default_rng(20261001 if source == "msvalid" else 20261002)
    if source == "msvalid":
        indices = rng.integers(0, len(values), (5000, len(values)))
        draws = values[indices].mean(axis=1)
        groups = {"MSValid": len(patients)}
    else:
        draws = np.zeros(5000)
        groups = {}
        for group in ("2D_AX_T2", "2D_AX_T2_BLADE"):
            stratum = np.array([row["delta_o"] for row in patients if row["group"] == group])
            groups[group] = len(stratum)
            indices = rng.integers(0, len(stratum), (5000, len(stratum)))
            draws += stratum[indices].mean(axis=1) * len(stratum) / len(values)
    expected = (84, 479) if source == "msvalid" else (62, 248)
    if (len(patients), len(rows)) != expected or len(original_rows(source)) != len(rows):
        raise ValueError(f"incomplete {source} patient/target set")
    summary = {"source": source, "status": "post-result exploratory control",
               "plan_sha256": msvalid.sha256(PLAN), "script_sha256": msvalid.sha256(Path(__file__)),
               "original_per_target_sha256": EXPECTED_MAIN[source],
               "hat_checkpoint_sha256": msvalid.MODELS["hat"][2],
               "patients": len(patients), "targets": len(rows), "groups": groups,
               "shared_o": float(np.mean([row["shared_o"] for row in patients])),
               "disjoint_o": float(np.mean([row["disjoint_o"] for row in patients])),
               "delta_o": float(values.mean()),
               "ci95": np.percentile(draws, [2.5, 97.5]).tolist(),
               "positive_patients": int((values > 0).sum()),
               "negative_patients": int((values < 0).sum()),
               "shared_b_mae": float(np.mean([row["shared_b_mae"] for row in patients])),
               "disjoint_b_mae": float(np.mean([row["disjoint_b_mae"] for row in patients]))}
    return patients, summary


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", choices=("msvalid", "remind"))
    source = parser.parse_args().source
    destination = OUT / source
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite {destination}")
    if msvalid.sha256(msvalid.MODELS["hat"][1]) != msvalid.MODELS["hat"][2]:
        raise ValueError("IXI HAT checkpoint changed")
    original = original_rows(source)
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = msvalid.MODELS["hat"][0](msvalid.MODELS["hat"][1], device="cpu")
    start = time.perf_counter()
    rows = score_msvalid(hat, original) if source == "msvalid" else score_remind(hat, original)
    patients, summary = aggregate(rows, source)
    summary["elapsed_seconds"] = time.perf_counter() - start
    destination.mkdir(parents=True)
    write_csv(destination / "per_target.csv", rows)
    write_csv(destination / "per_patient.csv", patients)
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
