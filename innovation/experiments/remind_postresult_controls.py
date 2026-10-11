"""CPU-only post-result ReMIND common-scale and reverse-phase controls."""
from __future__ import annotations

import json
import os
import time
import zipfile
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import numpy as np
import pydicom
import torch
from skimage.transform import resize

from remind_native_t2_ixi_pair import (INNOVATION, MODELS, QUALIFIED, metrics,
                                       predict, sha256, write_csv)


PLAN = INNOVATION / "REMIND_POSTRESULT_CONTROLS_PLAN_2026-10-01.md"
ORIGINAL = INNOVATION / "experiments/remind_native_t2_ixi_pair/per_patient.csv"
MAIN = INNOVATION / "experiments/remind_native_t2_ixi_pair/summary.json"
OUT = INNOVATION / "experiments/remind_postresult_controls"


def prepare(anchors: np.ndarray, lo: float, hi: float):
    normalized = ((anchors - lo) / (hi - lo + 1e-8)).astype(np.float32)
    planes = [resize(normalized[:, :, j], (256, 256), preserve_range=True,
                     anti_aliasing=True).astype(np.float32)
              for j in range(anchors.shape[2])]
    return planes, lo, hi


def balanced(rows: list[dict], key: str) -> float:
    return float(np.mean([np.mean([r[key] for r in rows if r["residue"] == residue])
                          for residue in (1, 3)]))


def patient_result(patient: dict, hat: object, swinir: object):
    path = INNOVATION / patient["path"]
    if sha256(path) != patient["zip_sha256"]:
        raise ValueError("source ZIP hash changed")
    depth = patient["depth"]
    selected = set(range(0, depth, 2))
    selected.update(z for positions in patient["targets"].values() for z in positions)
    decoded = {}
    with zipfile.ZipFile(path) as archive:
        for z in sorted(selected):
            with archive.open(patient["ordered_files"][z]) as stream:
                ds = pydicom.dcmread(stream)
            plane = ds.pixel_array.astype(np.float32)
            if tuple(plane.shape) != tuple(patient["shape"]):
                raise ValueError(f"pixel shape changed z{z}")
            plane = plane * float(ds.get("RescaleSlope", 1)) + float(ds.get("RescaleIntercept", 0))
            if not np.isfinite(plane).all():
                raise ValueError(f"nonfinite pixels z{z}")
            decoded[z] = plane
    anchors = {phase: np.stack([decoded[z] for z in range(phase, depth, 4)], axis=2)
               for phase in (0, 2)}
    lo = min(float(a.min()) for a in anchors.values())
    hi = max(float(a.max()) for a in anchors.values())
    if hi <= lo:
        raise ValueError("constant common anchor range")
    prep = {phase: prepare(anchors[phase], lo, hi) for phase in (0, 2)}
    rows = []
    for residue in (1, 3):
        for z in patient["targets"][str(residue)]:
            i0, i2 = z // 4, (z - 2) // 4
            shape = tuple(patient["shape"])
            h0 = predict(hat, prep[0], i0, (z - 4 * i0) / 4, shape)
            h2 = predict(hat, prep[2], i2, (z - (2 + 4 * i2)) / 4, shape)
            s0 = predict(swinir, prep[0], i0, (z - 4 * i0) / 4, shape)
            s2 = predict(swinir, prep[2], i2, (z - (2 + 4 * i2)) / 4, shape)
            masks = {}
            for phase, index in ((0, i0), (2, i2)):
                left = anchors[phase][:, :, index]
                right = anchors[phase][:, :, index + 1]
                masks[phase] = ((np.abs(left) > .01 * max(float(np.abs(left).max()), 1e-6)) |
                                (np.abs(right) > .01 * max(float(np.abs(right).max()), 1e-6)))
                if not masks[phase].any():
                    raise ValueError(f"empty phase-{phase} support z{z}")
            y = decoded[z]
            fs = metrics(h0, s0, y, masks[0])
            fd = metrics(h0, s2, y, masks[0])
            rs = metrics(h2, s2, y, masks[2])
            rd = metrics(h2, s0, y, masks[2])
            rows.append({"patient": patient["patient"], "z": z, "residue": residue,
                         "series_description": patient["series_description"],
                         "common_lo": lo, "common_hi": hi,
                         "forward_support_pixels": int(masks[0].sum()),
                         "reverse_support_pixels": int(masks[2].sum()),
                         **{f"forward_shared_{k}": v for k, v in fs.items()},
                         **{f"forward_disjoint_{k}": v for k, v in fd.items()},
                         **{f"reverse_shared_{k}": v for k, v in rs.items()},
                         **{f"reverse_disjoint_{k}": v for k, v in rd.items()},
                         "forward_delta_o": fd["observable"] - fs["observable"],
                         "reverse_delta_o": rd["observable"] - rs["observable"]})
    if len(rows) != 4 or {r["residue"] for r in rows} != {1, 3}:
        raise ValueError("incomplete target set")
    keys = ("forward_shared_observable", "forward_disjoint_observable", "forward_delta_o",
            "reverse_shared_observable", "reverse_disjoint_observable", "reverse_delta_o",
            "forward_shared_b_mae", "forward_disjoint_b_mae",
            "reverse_shared_b_mae", "reverse_disjoint_b_mae")
    summary = {key: balanced(rows, key) for key in keys}
    summary.update({"patient": patient["patient"], "series_description": patient["series_description"],
                    "targets": len(rows), "common_lo": lo, "common_hi": hi,
                    "forward_residue_1_delta_o": float(np.mean([r["forward_delta_o"] for r in rows if r["residue"] == 1])),
                    "forward_residue_3_delta_o": float(np.mean([r["forward_delta_o"] for r in rows if r["residue"] == 3])),
                    "reverse_residue_1_delta_o": float(np.mean([r["reverse_delta_o"] for r in rows if r["residue"] == 1])),
                    "reverse_residue_3_delta_o": float(np.mean([r["reverse_delta_o"] for r in rows if r["residue"] == 3]))})
    return rows, summary


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite: {OUT}")
    cohort = json.loads(QUALIFIED.read_text(encoding="utf-8"))
    main = json.loads(MAIN.read_text(encoding="utf-8"))
    if len(cohort["records"]) != 63 or main["patients_scored"] != 62 or main["targets_scored"] != 248:
        raise RuntimeError("frozen sample mismatch")
    import csv
    with ORIGINAL.open(newline="", encoding="utf-8") as stream:
        old = {r["patient"]: float(r["delta_o"]) for r in csv.DictReader(stream)}
    if len(old) != 62:
        raise RuntimeError("original patient contract mismatch")
    for name, (_, path, expected) in MODELS.items():
        if sha256(path) != expected or main["checkpoint_sha256"][name] != expected:
            raise ValueError(f"{name} checkpoint hash mismatch")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    OUT.mkdir(parents=True)
    targets, patients, failures = [], [], []
    started = time.perf_counter()
    for i, patient in enumerate(cohort["records"], 1):
        if not patient["eligible"]:
            failures.append({"patient": patient["patient"], "stage": "header", "error": patient["reason"]})
            print(f"{i}/63 {patient['patient']} HEADER_FAIL", flush=True)
            continue
        try:
            rows, result = patient_result(patient, hat, swinir)
            result["original_delta_o"] = old[result["patient"]]
            result["change_vs_original"] = result["forward_delta_o"] - result["original_delta_o"]
            targets.extend(rows)
            patients.append(result)
            print(f"{i}/63 {patient['patient']} targets={len(rows)} elapsed={time.perf_counter()-started:.1f}s", flush=True)
        except (OSError, ValueError, RuntimeError, KeyError, AttributeError,
                pydicom.errors.InvalidDicomError) as error:
            failures.append({"patient": patient["patient"], "stage": "pixel_or_inference",
                             "error": f"{type(error).__name__}: {error}"})
            print(f"{i}/63 {patient['patient']} FAIL {error}", flush=True)
    write_csv(OUT / "per_target.csv", targets)
    write_csv(OUT / "per_patient.csv", patients)
    rng = np.random.default_rng(20261003)
    draws = {}
    strata = {}
    for name in ("2D_AX_T2", "2D_AX_T2_BLADE"):
        group = [p for p in patients if p["series_description"] == name]
        values = np.array([[p["forward_delta_o"], p["reverse_delta_o"]] for p in group])
        if len(values):
            resampled = values[rng.integers(0, len(values), (5000, len(values)))].mean(axis=1)
            draws[name] = resampled
            strata[name] = {"patients": len(values), "mean_forward_delta_o": float(values[:, 0].mean()),
                            "mean_reverse_delta_o": float(values[:, 1].mean()),
                            "ci95_forward": np.percentile(resampled[:, 0], [2.5, 97.5]).tolist(),
                            "ci95_reverse": np.percentile(resampled[:, 1], [2.5, 97.5]).tolist(),
                            "positive_forward": int((values[:, 0] > 0).sum()),
                            "positive_reverse": int((values[:, 1] > 0).sum())}
        else:
            strata[name] = {"patients": 0, "mean_forward_delta_o": None,
                            "mean_reverse_delta_o": None, "ci95_forward": [None, None],
                            "ci95_reverse": [None, None], "positive_forward": 0, "positive_reverse": 0}
    n = len(patients)
    pooled = sum(draws[name] * strata[name]["patients"] / n for name in draws) if n else None
    values = np.array([[p["forward_delta_o"], p["reverse_delta_o"]] for p in patients])
    forward_ci = np.percentile(pooled[:, 0], [2.5, 97.5]).tolist() if n else [None, None]
    original_mean = main["mean_delta_o"]
    sensitivity = (n == 62 and len(targets) == 248 and forward_ci[0] is not None
                   and forward_ci[0] > 0 and float(values[:, 0].mean()) >= original_mean / 2
                   and all(strata[g]["ci95_forward"][0] is not None
                           and strata[g]["ci95_forward"][0] > 0 for g in strata))
    report = {"status": "post-result exploratory; not independent confirmation",
              "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
              "qualification_sha256": sha256(QUALIFIED), "original_summary_sha256": sha256(MAIN),
              "original_per_patient_sha256": sha256(ORIGINAL),
              "checkpoint_sha256": {k: v[2] for k, v in MODELS.items()},
              "patients_expected": 63, "patients_scored": n, "targets_scored": len(targets),
              "failures": failures, "strata": strata,
              "mean_forward_delta_o": float(values[:, 0].mean()) if n else None,
              "mean_reverse_delta_o": float(values[:, 1].mean()) if n else None,
              "ci95_forward": forward_ci,
              "ci95_reverse": np.percentile(pooled[:, 1], [2.5, 97.5]).tolist() if n else [None, None],
              "positive_forward": int((values[:, 0] > 0).sum()) if n else 0,
              "positive_reverse": int((values[:, 1] > 0).sum()) if n else 0,
              "mean_change_vs_original": float(np.mean([p["change_vs_original"] for p in patients])) if n else None,
              "exploratory_normalization_sensitivity_pass": sensitivity,
              "elapsed_seconds": time.perf_counter() - started}
    (OUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
