"""Frozen CPU-only IXI model versus pipeline-linear replication on ds007045."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import torch
from skimage.transform import resize

from remind_native_t2_ixi_pair import MODELS, predict, prepared


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "DS007045_MODEL_REPLICATION_PROTOCOL_2026-10-01.md"
QUALIFICATION = ROOT / "experiments/ds007045_cohort_label_qualification"
SOURCE = ROOT / "literature/source_cache/ds007045_current_pair_audit_2026-10-01/result.json"
DESCRIPTION = ROOT / "literature/source_cache/ds007045_pair_inventory_2026-10-01/dataset_description.json"
OUT = ROOT / "experiments/ds007045_model_replication"
DATA = ROOT / "data/ds007045_model_replication"
BASE = "https://s3.amazonaws.com/openneuro.org/"
DESCRIPTION_SHA256 = "748fb52a1d943c6f50bb6e4795082e973c4a8694e01a287383a9bf1f20fff763"
MIN_FREE = 15_000_000_000
METHODS = ("pipeline_linear", "raw_linear", "hat", "swinir")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(url: str, cap: int) -> tuple[bytes, int, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for attempt in range(2):
        try:
            with opener.open(request, timeout=60) as response:
                body = response.read(cap + 1)
                if len(body) > cap:
                    raise ValueError("Response exceeded 10 MB cap")
                return body, response.status, dict(response.headers)
        except (urllib.error.URLError, TimeoutError):
            if attempt:
                raise
            time.sleep(2)
    raise AssertionError("unreachable")


def live_description_matches() -> bool:
    body, status, _ = fetch(BASE + "ds007045/dataset_description.json", 10_000)
    return status == 200 and hashlib.sha256(body).hexdigest() == DESCRIPTION_SHA256


def source_pair(record: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    case = record["case"]
    destination = DATA / f"{case}_t2.nii.gz"
    if not destination.exists():
        if shutil.disk_usage(DATA).free < MIN_FREE:
            raise OSError("15 GB free-space floor reached")
        body, status, headers = fetch(BASE + record["t2_key"], 10_000_000)
        if (status != 200 or len(body) != record["t2_listed_bytes"] or
                int(headers.get("Content-Length", -1)) != len(body)):
            raise ValueError("Unexpected T2 response size/status")
        if hashlib.sha256(body[:65_536]).hexdigest() != record["t2_prefix_65536_sha256"]:
            raise ValueError("T2 bytes changed since label qualification")
        destination.write_bytes(body)
    if destination.stat().st_size != record["t2_listed_bytes"]:
        raise ValueError("Local T2 size differs from qualification")
    with destination.open("rb") as stream:
        if hashlib.sha256(stream.read(65_536)).hexdigest() != record["t2_prefix_65536_sha256"]:
            raise ValueError("Local T2 prefix differs from qualification")
    mask_path = ROOT / record["mask_local_path"]
    if sha256(mask_path) != record["mask_sha256"]:
        raise ValueError("Mask bytes differ from qualification")
    t2_image = nib.load(str(destination))
    mask_image = nib.load(str(mask_path))
    if (tuple(t2_image.shape) != tuple(record["shape"]) or
            t2_image.shape != mask_image.shape or
            not np.allclose(t2_image.affine, mask_image.affine, atol=1e-4, rtol=0)):
        raise ValueError("Full T2/mask geometry differs from qualification")
    t2 = np.asarray(t2_image.dataobj, dtype=np.float32)
    mask = np.asarray(mask_image.dataobj, dtype=np.uint8)
    if not np.isfinite(t2).all() or mask.max() > 3:
        raise ValueError("Nonfinite T2 or unexpected mask labels")
    return t2, mask, {"t2_sha256": sha256(destination),
                      "mask_sha256": record["mask_sha256"],
                      "t2_local_path": destination.relative_to(ROOT).as_posix()}


def mse_and_mae(output: np.ndarray, target: np.ndarray, roi: np.ndarray, span: float) -> dict:
    errors = (output - target)[roi].astype(np.float64)
    return {"mse": float(np.mean(errors * errors)),
            "normalized_mse": float(np.mean(errors * errors) / (span * span)),
            "mae": float(np.mean(np.abs(errors)))}


def score_case(record: dict, hat: object, swinir: object) -> dict:
    volume, label, source = source_pair(record)
    anchors = volume[:, :, ::4]
    prep = prepared(anchors)
    planes, lo, hi = prep
    span = hi - lo
    if not np.isfinite(span) or span <= 0:
        raise ValueError("Invalid observed-only intensity span")
    rows = []
    for residue in (1, 3):
        for z in record["targets"][str(residue)]:
            index = z // 4
            rel = (z - 4 * index) / 4
            left, right = anchors[:, :, index], anchors[:, :, index + 1]
            support = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                       (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
            lesion = (label[:, :, z] > 0) & support
            if lesion.sum() < 64 or not support.any():
                raise ValueError(f"Insufficient lesion/support pixels z{z}")
            raw = ((1 - rel) * left.astype(np.float64) +
                   rel * right.astype(np.float64)).astype(np.float32)
            coarse = ((1 - rel) * planes[index] + rel * planes[index + 1]).astype(np.float32)
            pipeline = (resize(np.clip(coarse, 0, 1), volume.shape[:2],
                               preserve_range=True, anti_aliasing=True) * span + lo).astype(np.float32)
            outputs = {"pipeline_linear": pipeline, "raw_linear": raw,
                       "hat": predict(hat, prep, index, rel, volume.shape[:2]),
                       "swinir": predict(swinir, prep, index, rel, volume.shape[:2])}
            target = volume[:, :, z]
            row = {"z": int(z), "residue": residue,
                   "tumor_pixels": int(lesion.sum()), "full_pixels": int(support.sum())}
            for method, output in outputs.items():
                if not np.isfinite(output).all():
                    raise ValueError(f"Nonfinite {method} output z{z}")
                for name, roi in (("tumor", lesion), ("full", support)):
                    for metric, value in mse_and_mae(output, target, roi, span).items():
                        row[f"{name}_{method}_{metric}"] = value
            rows.append(row)
    if len(rows) != 4:
        raise ValueError("Four frozen targets not completed")
    patient = {"case": record["case"], "site": record["case"].split("-")[1].rstrip("0123456789")}
    for name in ("tumor", "full"):
        for method in METHODS:
            for metric in ("normalized_mse", "mse", "mae"):
                field = f"{name}_{method}_{metric}"
                patient[field] = float(np.mean([row[field] for row in rows]))
        for model in ("swinir", "hat"):
            for baseline in ("pipeline_linear", "raw_linear"):
                field = f"{name}_{model}_minus_{baseline}_normalized_mse"
                patient[field] = (patient[f"{name}_{model}_normalized_mse"] -
                                  patient[f"{name}_{baseline}_normalized_mse"])
    patient["swinir_pipeline_sign_discordance"] = bool(
        patient["tumor_swinir_minus_pipeline_linear_normalized_mse"] > 0 and
        patient["full_swinir_minus_pipeline_linear_normalized_mse"] < 0)
    return {"case": record["case"], "complete": True, "targets": record["targets"],
            "source": source, "observed_span": span, "rows": rows, "patient": patient}


def interval(values: np.ndarray, draws: np.ndarray) -> dict:
    means = values[draws].mean(axis=1)
    return {"mean": float(values.mean()),
            "ci95": [float(x) for x in np.percentile(means, [2.5, 97.5])],
            "positive_patients": int((values > 0).sum()),
            "negative_patients": int((values < 0).sum())}


def wilson_lower(positive: int, n: int) -> float:
    z = 1.959963984540054
    p = positive / n
    return (p + z * z / (2 * n) - z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / (1 + z * z / n)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--preflight-one"):
        raise ValueError("Supported: full run or --preflight-one")
    preflight = len(sys.argv) == 2
    qualification = json.loads((QUALIFICATION / "summary.json").read_text(encoding="utf-8"))
    if qualification["attempted"] != 363 or not qualification["complete_cohort"]:
        raise ValueError("Full outcome-independent qualification not complete")
    cases = json.loads(SOURCE.read_text(encoding="utf-8"))["paired_subjects_list"]
    if not live_description_matches() or sha256(DESCRIPTION) != DESCRIPTION_SHA256:
        raise ValueError("Current v2.0.1 dataset description changed")
    for name, (_, path, expected_hash) in MODELS.items():
        if sha256(path) != expected_hash:
            raise ValueError(f"Frozen {name} checkpoint hash changed")
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    contract = {"protocol_sha256": sha256(PROTOCOL),
                "qualification_summary_sha256": sha256(QUALIFICATION / "summary.json"),
                "source_inventory_sha256": sha256(SOURCE),
                "script_sha256": sha256(Path(__file__)),
                "checkpoint_sha256": {name: spec[2] for name, spec in MODELS.items()},
                "gpu_used": False, "attempted_cases": 363}
    contract_path = OUT / "run_contract.json"
    if contract_path.exists():
        if json.loads(contract_path.read_text(encoding="utf-8")) != contract:
            raise ValueError("Existing run contract differs")
    else:
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    case_dir = OUT / "cases"
    case_dir.mkdir(exist_ok=True)
    selected = cases[:1] if preflight else cases
    completed, failed = [], []
    for index, case in enumerate(selected, 1):
        qualification_record = json.loads((QUALIFICATION / "cases" / f"{case}.json").read_text(encoding="utf-8"))
        if not qualification_record["eligible"]:
            failed.append({"case": case, "stage": "label_qualification",
                           "reason": qualification_record["failure_reason"]})
            continue
        path = case_dir / f"{case}.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
            if result.get("run_contract_sha256") != sha256(contract_path):
                raise ValueError(f"Existing case contract differs: {case}")
        else:
            try:
                result = score_case(qualification_record, hat, swinir)
            except Exception as exc:
                result = {"case": case, "complete": False,
                          "failure_type": type(exc).__name__, "failure_reason": str(exc)[:200]}
            result["run_contract_sha256"] = sha256(contract_path)
            path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        if result["complete"]:
            completed.append(result)
        else:
            failed.append({"case": case, "stage": "pixel_or_inference",
                           "reason": result["failure_reason"]})
        if index % 10 == 0 or index == len(selected):
            print(f"ds007045 CPU model {index}/{len(selected)} completed={len(completed)}", flush=True)
    if not live_description_matches():
        raise ValueError("Current dataset description changed after model run")
    patients = [result["patient"] for result in completed]
    targets = [{"case": result["case"], **row} for result in completed for row in result["rows"]]
    write_csv(OUT / ("preflight_per_patient.csv" if preflight else "per_patient.csv"), patients)
    write_csv(OUT / ("preflight_per_target.csv" if preflight else "per_target.csv"), targets)
    summary = {"protocol_sha256": sha256(PROTOCOL),
               "run_contract_sha256": sha256(contract_path),
               "attempted": len(selected), "completed": len(patients), "failures": failed,
               "gpu_used": False, "complete_cohort": not preflight,
               "bootstrap_seed": 20261003, "bootstrap_draws": 5000}
    if patients:
        rng = np.random.default_rng(20261003)
        draws = rng.integers(0, len(patients), (5000, len(patients)))
        fields = [f"{roi}_{model}_minus_{baseline}_normalized_mse"
                  for roi in ("tumor", "full") for model in ("swinir", "hat")
                  for baseline in ("pipeline_linear", "raw_linear")]
        summary["differences"] = {field: interval(np.array([p[field] for p in patients]), draws)
                                  for field in fields}
        discordance = sum(p["swinir_pipeline_sign_discordance"] for p in patients)
        summary["swinir_pipeline_sign_discordance"] = {
            "patients": discordance, "fraction": discordance / len(patients),
            "wilson_95_lower": wilson_lower(discordance, len(patients))}
        summary["sites_completed"] = dict(sorted(Counter(p["site"] for p in patients).items()))
        summary["site_sensitivity"] = {
            site: {
                "patients": sum(p["site"] == site for p in patients),
                "mean_tumor_difference": float(np.mean([
                    p["tumor_swinir_minus_pipeline_linear_normalized_mse"]
                    for p in patients if p["site"] == site])),
                "mean_full_difference": float(np.mean([
                    p["full_swinir_minus_pipeline_linear_normalized_mse"]
                    for p in patients if p["site"] == site])),
                "discordant_patients": sum(
                    p["swinir_pipeline_sign_discordance"] for p in patients if p["site"] == site),
            }
            for site in sorted(summary["sites_completed"])
        }
        tumor = summary["differences"]["tumor_swinir_minus_pipeline_linear_normalized_mse"]["ci95"]
        full = summary["differences"]["full_swinir_minus_pipeline_linear_normalized_mse"]["ci95"]
        summary["primary_replication_pass"] = bool(
            not preflight and len(patients) >= 250 and len(summary["sites_completed"]) >= 6 and
            tumor[0] > 0 and full[1] < 0 and
            summary["swinir_pipeline_sign_discordance"]["wilson_95_lower"] > .20)
    (OUT / ("preflight_summary.json" if preflight else "summary.json")).write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("failures", "differences")}, indent=2))


if __name__ == "__main__":
    main()
