"""CPU-only MSValid controls for the public-IXI-trained HAT/SwinIR pair."""
from __future__ import annotations

import csv
import json
import os
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import torch
from skimage.transform import resize

from msvalid_ixi_weights_secondary import (DATA, INNOVATION, MODELS, QUALIFIED,
                                          SOURCE_MANIFEST, predict, sha256, write_csv)


PLAN = INNOVATION / "MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_PLAN_2026-10-01.md"
ORIGINAL = INNOVATION / "experiments/msvalid_ixi_weights_secondary/per_patient.csv"
MAIN = INNOVATION / "experiments/msvalid_ixi_weights_secondary/summary.json"
OUT = INNOVATION / "experiments/msvalid_ixi_weight_postresult_controls"


def prepare(anchors: np.ndarray, lo: float, hi: float):
    normalized = ((anchors - lo) / (hi - lo + 1e-8)).astype(np.float32)
    planes = [resize(normalized[:, :, j], (256, 256), preserve_range=True,
                     anti_aliasing=True).astype(np.float32)
              for j in range(anchors.shape[2])]
    return planes, lo, hi


def score(a: np.ndarray, b: np.ndarray, y: np.ndarray, mask: np.ndarray) -> dict:
    ea = (a - y)[mask].astype(np.float64)
    eb = (b - y)[mask].astype(np.float64)
    am = float(np.mean(ea * ea))
    bm = float(np.mean(eb * eb))
    pair = (am + bm) / 2
    if not np.isfinite(pair) or pair <= 0:
        raise ValueError("nonpositive_or_nonfinite_pair_error")
    disagreement = float(np.mean((ea - eb) ** 2))
    return {"observable": disagreement / (4 * pair),
            "a_mae": float(np.mean(np.abs(ea))), "b_mae": float(np.mean(np.abs(eb))),
            "a_mse": am, "b_mse": bm, "paired_mse": pair,
            "disagreement_mse": disagreement}


def balanced(rows: list[dict], key: str) -> float:
    return float(np.mean([np.mean([r[key] for r in rows if r["residue"] == residue])
                          for residue in (1, 3)]))


def patient_result(patient: dict, hat: object, swinir: object):
    path = DATA / f"{patient['patient']}.nii.gz"
    volume = nib.load(str(path)).get_fdata(dtype=np.float32)
    if tuple(volume.shape) != tuple(patient["shape"]) or not np.isfinite(volume).all():
        raise ValueError("changed shape or nonfinite volume")
    phase = {j: np.ascontiguousarray(volume[:, :, list(range(j, volume.shape[2], 4))])
             for j in (0, 2)}
    lo = min(float(x.min()) for x in phase.values())
    hi = max(float(x.max()) for x in phase.values())
    if hi <= lo:
        raise ValueError("constant common anchor range")
    prep = {j: prepare(phase[j], lo, hi) for j in (0, 2)}
    rows = []
    for residue in (1, 3):
        for z in patient["eligible_targets"][f"residue_{residue}"]:
            i0, i2 = z // 4, (z - 2) // 4
            shape = volume.shape[:2]
            h0 = predict(hat, prep[0], i0, (z - 4 * i0) / 4, shape)
            h2 = predict(hat, prep[2], i2, (z - (2 + 4 * i2)) / 4, shape)
            s0 = predict(swinir, prep[0], i0, (z - 4 * i0) / 4, shape)
            s2 = predict(swinir, prep[2], i2, (z - (2 + 4 * i2)) / 4, shape)
            masks = {}
            for j, i in ((0, i0), (2, i2)):
                left, right = phase[j][:, :, i], phase[j][:, :, i + 1]
                masks[j] = ((np.abs(left) > .01 * max(float(np.abs(left).max()), 1e-6)) |
                            (np.abs(right) > .01 * max(float(np.abs(right).max()), 1e-6)))
                if not masks[j].any():
                    raise ValueError(f"empty phase-{j} support z{z}")
            y = volume[:, :, z]
            fs, fd = score(h0, s0, y, masks[0]), score(h0, s2, y, masks[0])
            rs, rd = score(h2, s2, y, masks[2]), score(h2, s0, y, masks[2])
            rows.append({"patient": patient["patient"], "z": z, "residue": residue,
                         "common_lo": lo, "common_hi": hi,
                         "forward_support_pixels": int(masks[0].sum()),
                         "reverse_support_pixels": int(masks[2].sum()),
                         **{f"forward_shared_{k}": v for k, v in fs.items()},
                         **{f"forward_disjoint_{k}": v for k, v in fd.items()},
                         **{f"reverse_shared_{k}": v for k, v in rs.items()},
                         **{f"reverse_disjoint_{k}": v for k, v in rd.items()},
                         "forward_delta_o": fd["observable"] - fs["observable"],
                         "reverse_delta_o": rd["observable"] - rs["observable"]})
    if not rows or {r["residue"] for r in rows} != {1, 3}:
        raise ValueError("incomplete target set")
    keys = ("forward_shared_observable", "forward_disjoint_observable", "forward_delta_o",
            "reverse_shared_observable", "reverse_disjoint_observable", "reverse_delta_o",
            "forward_shared_b_mae", "forward_disjoint_b_mae",
            "reverse_shared_b_mae", "reverse_disjoint_b_mae")
    summary = {key: balanced(rows, key) for key in keys}
    summary.update({"patient": patient["patient"], "targets": len(rows),
                    "common_lo": lo, "common_hi": hi})
    for direction in ("forward", "reverse"):
        for residue in (1, 3):
            summary[f"{direction}_residue_{residue}_delta_o"] = float(np.mean([
                r[f"{direction}_delta_o"] for r in rows if r["residue"] == residue]))
    return rows, summary


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite: {OUT}")
    cohort = json.loads(QUALIFIED.read_text(encoding="utf-8"))["patients"]
    main = json.loads(MAIN.read_text(encoding="utf-8"))
    if len(cohort) != 84 or not all(p["geometry_eligible"] for p in cohort):
        raise RuntimeError("frozen cohort mismatch")
    if main["patients_scored"] != 84 or main["targets_scored"] != 479:
        raise RuntimeError("original outcome sample mismatch")
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    source_hashes = {r["patient"]: r["sha256"] for r in manifest["records"]}
    if set(source_hashes) != {p["patient"] for p in cohort}:
        raise ValueError("source manifest patient set mismatch")
    for p in cohort:
        if sha256(DATA / f"{p['patient']}.nii.gz") != source_hashes[p["patient"]]:
            raise ValueError(f"source image hash mismatch: {p['patient']}")
    with ORIGINAL.open(newline="", encoding="utf-8") as stream:
        old = {r["patient"]: float(r["delta_o"]) for r in csv.DictReader(stream)}
    if len(old) != 84:
        raise RuntimeError("original patient count mismatch")
    for name, (_, path, expected) in MODELS.items():
        if sha256(path) != expected or main["checkpoint_sha256"][name] != expected:
            raise ValueError(f"{name} checkpoint hash mismatch")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    OUT.mkdir(parents=True)
    target, patient_rows, failures = [], [], []
    started = time.perf_counter()
    for i, p in enumerate(cohort, 1):
        try:
            rows, result = patient_result(p, hat, swinir)
            result["original_delta_o"] = old[result["patient"]]
            result["change_vs_original"] = result["forward_delta_o"] - result["original_delta_o"]
            target.extend(rows)
            patient_rows.append(result)
            print(f"{i}/84 {p['patient']} targets={len(rows)} elapsed={time.perf_counter()-started:.1f}s", flush=True)
        except (OSError, ValueError, RuntimeError, KeyError, AttributeError) as error:
            failures.append({"patient": p["patient"], "error": f"{type(error).__name__}: {error}"})
            print(f"{i}/84 {p['patient']} FAIL {error}", flush=True)
    write_csv(OUT / "per_target.csv", target)
    write_csv(OUT / "per_patient.csv", patient_rows)
    values = np.array([[p["forward_delta_o"], p["reverse_delta_o"]] for p in patient_rows])
    if len(values):
        rng = np.random.default_rng(20261005)
        draws = values[rng.integers(0, len(values), (5000, len(values)))].mean(axis=1)
        forward_ci = np.percentile(draws[:, 0], [2.5, 97.5]).tolist()
        reverse_ci = np.percentile(draws[:, 1], [2.5, 97.5]).tolist()
    else:
        forward_ci = reverse_ci = [None, None]
    sensitivity = (len(patient_rows) == 84 and len(target) == 479 and forward_ci[0] is not None
                   and forward_ci[0] > 0 and values[:, 0].mean() >= main["mean_delta_o"] / 2)
    report = {"status": "post-result exploratory; same MSValid patient source",
              "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
              "qualification_sha256": sha256(QUALIFIED), "source_manifest_sha256": sha256(SOURCE_MANIFEST),
              "original_summary_sha256": sha256(MAIN), "original_per_patient_sha256": sha256(ORIGINAL),
              "checkpoint_sha256": {k: v[2] for k, v in MODELS.items()},
              "patients_expected": 84, "patients_scored": len(patient_rows), "targets_scored": len(target),
              "failures": failures,
              "mean_forward_delta_o": float(values[:, 0].mean()) if len(values) else None,
              "mean_reverse_delta_o": float(values[:, 1].mean()) if len(values) else None,
              "ci95_forward": forward_ci, "ci95_reverse": reverse_ci,
              "positive_forward": int((values[:, 0] > 0).sum()) if len(values) else 0,
              "positive_reverse": int((values[:, 1] > 0).sum()) if len(values) else 0,
              "mean_change_vs_original": float(np.mean([p["change_vs_original"] for p in patient_rows])) if len(values) else None,
              "exploratory_normalization_sensitivity_pass": bool(sensitivity),
              "elapsed_seconds": time.perf_counter() - started}
    (OUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
