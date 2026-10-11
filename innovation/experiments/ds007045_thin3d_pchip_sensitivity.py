"""CPU-only PCHIP sensitivity on frozen, locally cached thin-3D cases."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import nibabel as nib
import numpy as np
from scipy.interpolate import PchipInterpolator
from skimage.transform import resize

from remind_native_t2_ixi_pair import prepared


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "experiments/ds007045_thin3d_model_pilot"
QUALIFICATION = ROOT / "experiments/ds007045_cohort_label_qualification/cases"
PROTOCOL = ROOT / "DS007045_THIN3D_PCHIP_SENSITIVITY_PROTOCOL_2026-10-01.md"
OUT = ROOT / "experiments/ds007045_thin3d_pchip_sensitivity"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def score_case(case_path: Path) -> tuple[list[dict], dict]:
    old = json.loads(case_path.read_text(encoding="utf-8"))
    case = old["case"]
    qualified = json.loads((QUALIFICATION / f"{case}.json").read_text(encoding="utf-8"))
    source = old["source"]
    t2_path = ROOT / source["t2_local_path"]
    mask_path = ROOT / qualified["mask_local_path"]
    if not t2_path.is_file() or not mask_path.is_file():
        raise FileNotFoundError("Frozen local T2 or mask absent")
    if sha256(t2_path) != source["t2_sha256"] or sha256(mask_path) != source["mask_sha256"]:
        raise ValueError("Frozen source SHA-256 differs")
    image, mask_image = nib.load(str(t2_path)), nib.load(str(mask_path))
    if (image.shape != mask_image.shape or tuple(image.shape) != tuple(qualified["shape"]) or
            not np.allclose(image.affine, mask_image.affine, atol=1e-4, rtol=0)):
        raise ValueError("T2/mask geometry differs")
    volume = np.asarray(image.dataobj, dtype=np.float32)
    label = np.asarray(mask_image.dataobj, dtype=np.uint8)
    if not np.isfinite(volume).all() or label.max() > 3 or old["targets"] != qualified["targets"]:
        raise ValueError("Target or pixel qualification differs")
    anchors = volume[:, :, ::4]
    planes, lo, hi = prepared(anchors)
    span = float(hi - lo)
    if abs(span - old["observed_span"]) > 1e-4:
        raise ValueError("Observed intensity span differs")
    rows = []
    prior = {(r["z"], r["residue"]): r for r in old["rows"]}
    for residue in (1, 3):
        for z in old["targets"][str(residue)]:
            i = z // 4
            if i < 1 or i + 2 >= anchors.shape[2]:
                raise ValueError("Four phase-0 anchors do not bracket target")
            indices = np.arange(i - 1, i + 3)
            positions = 4 * indices
            left, right = anchors[:, :, i], anchors[:, :, i + 1]
            support = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                       (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
            tumor = (label[:, :, z] > 0) & support
            original = prior[(z, residue)]
            if int(tumor.sum()) != original["tumor_pixels"] or int(support.sum()) != original["full_pixels"]:
                raise ValueError("Frozen ROI pixel count differs")
            target = volume[:, :, z]
            rel = (z - 4 * i) / 4
            raw_linear = ((1 - rel) * left.astype(np.float64) + rel * right.astype(np.float64)).astype(np.float32)
            raw_pchip = PchipInterpolator(positions, np.moveaxis(anchors[:, :, indices], -1, 0), axis=0)(z)
            pipeline_pchip = PchipInterpolator(positions, np.stack([planes[j] for j in indices]), axis=0)(z)
            pipeline_pchip = (resize(np.clip(pipeline_pchip, 0, 1), volume.shape[:2],
                                     preserve_range=True, anti_aliasing=True) * span + lo).astype(np.float32)
            row = {"case": case, "z": z, "residue": residue}
            for name, roi in (("tumor", tumor), ("full", support)):
                baseline_mse = float(np.mean((raw_linear - target)[roi].astype(np.float64) ** 2))
                if abs(baseline_mse - original[f"{name}_raw_linear_mse"]) > 1e-6:
                    raise ValueError("Original raw-linear arithmetic differs")
                for method, output in (("raw_pchip", raw_pchip), ("pipeline_pchip", pipeline_pchip)):
                    if not np.isfinite(output).all():
                        raise ValueError("Nonfinite PCHIP output")
                    error = (output - target)[roi].astype(np.float64)
                    row[f"{name}_{method}_normalized_mse"] = float(np.mean(error * error) / span ** 2)
                for method in ("hat", "swinir"):
                    row[f"{name}_{method}_normalized_mse"] = original[f"{name}_{method}_normalized_mse"]
            rows.append(row)
    if len(rows) != 4:
        raise ValueError("Incomplete four-target case")
    patient = {"case": case, "site": case.split("-")[1].rstrip("0123456789")}
    for roi in ("tumor", "full"):
        for method in ("raw_pchip", "pipeline_pchip", "hat", "swinir"):
            key = f"{roi}_{method}_normalized_mse"
            patient[key] = float(np.mean([r[key] for r in rows]))
        for model in ("hat", "swinir"):
            for baseline in ("raw_pchip", "pipeline_pchip"):
                patient[f"{roi}_{model}_minus_{baseline}"] = (
                    patient[f"{roi}_{model}_normalized_mse"] -
                    patient[f"{roi}_{baseline}_normalized_mse"])
    return rows, patient


def main() -> None:
    previous = json.loads((PILOT / "summary.json").read_text(encoding="utf-8"))
    case_paths = sorted((PILOT / "cases").glob("*.json"))
    completed = [p for p in case_paths if json.loads(p.read_text(encoding="utf-8")).get("complete")]
    if previous["completed"] != 33 or previous["attempted"] != 34 or len(completed) != 33:
        raise ValueError("Frozen pilot denominator differs")
    if OUT.exists():
        prior_path = OUT / "summary.json"
        prior = json.loads(prior_path.read_text(encoding="utf-8")) if prior_path.exists() else {}
        if not (prior.get("completed") == 0 and len(prior.get("failures", [])) == 33 and
                all(f["type"] == "TypeError" and
                    f["reason"] == "only integer scalar arrays can be converted to a scalar index"
                    for f in prior["failures"])):
            raise FileExistsError(OUT)
        prior_path.rename(OUT / "software_failure_before_fix.json")
    else:
        OUT.mkdir(parents=True)
    targets, patients, failures = [], [], []
    for path in completed:
        try:
            rows, patient = score_case(path)
            targets.extend(rows)
            patients.append(patient)
        except Exception as exc:
            failures.append({"case": path.stem, "type": type(exc).__name__, "reason": str(exc)[:200]})
        print(f"PCHIP {len(patients) + len(failures)}/{len(completed)} {path.stem}", flush=True)
    summary = {"attempted_original": 34, "attempted_cached": len(completed),
               "completed": len(patients), "failures": failures, "no_gpu": True,
               "protocol_sha256": sha256(PROTOCOL), "script_sha256": sha256(Path(__file__)),
               "prior_summary_sha256": sha256(PILOT / "summary.json"),
               "bootstrap_seed": 20261005, "bootstrap_draws": 5000}
    if patients:
        write_csv(OUT / "per_target.csv", targets)
        write_csv(OUT / "per_patient.csv", patients)
        draws = np.random.default_rng(20261005).integers(0, len(patients), (5000, len(patients)))
        summary["differences"] = {}
        for roi in ("tumor", "full"):
            for model in ("hat", "swinir"):
                for baseline in ("raw_pchip", "pipeline_pchip"):
                    key = f"{roi}_{model}_minus_{baseline}"
                    values = np.array([p[key] for p in patients])
                    means = values[draws].mean(axis=1)
                    summary["differences"][key] = {
                        "mean": float(values.mean()),
                        "ci95": [float(x) for x in np.percentile(means, [2.5, 97.5])],
                        "positive_patients": int((values > 0).sum())}
        summary["sign_discordance"] = {
            f"{model}_vs_{baseline}": sum(
                p[f"tumor_{model}_minus_{baseline}"] > 0 and
                p[f"full_{model}_minus_{baseline}"] < 0 for p in patients)
            for model in ("hat", "swinir") for baseline in ("raw_pchip", "pipeline_pchip")}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "differences"}, indent=2))


if __name__ == "__main__":
    main()
