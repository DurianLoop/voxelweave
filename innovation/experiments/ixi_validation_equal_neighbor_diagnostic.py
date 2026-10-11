"""CPU-only IXI validation comparison for frozen x4 interpolators and linear controls."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import torch
from skimage.transform import resize

from remind_native_t2_ixi_pair import MODELS, predict, prepared


PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT / "innovation"
PROTOCOL = ROOT / "IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_PROTOCOL_2026-10-01.md"
SPLIT = PROJECT / "dataset/IXI/splits/seed3407/val_cases.txt"
TRAIN_SPLIT = PROJECT / "dataset/IXI/splits/seed3407/train_cases.txt"
METADATA = PROJECT / "dataset/IXI/metadata/ixi_cases.csv"
IMAGE_DIR = (PROJECT / "dataset/IXI/raw/T2").resolve()
OUT = ROOT / "experiments/ixi_validation_equal_neighbor_diagnostic"
METHODS = ("raw_linear", "pipeline_linear", "hat", "swinir")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_targets(depth: int) -> dict[str, list[int]]:
    anchors = {phase: list(range(phase, depth, 4)) for phase in (0, 2)}
    output = {}
    for residue in (1, 3):
        candidates = [z for z in range(residue, depth, 4)
                      if all(sum(anchor < z for anchor in anchors[phase]) >= 2 and
                             sum(anchor > z for anchor in anchors[phase]) >= 2
                             for phase in (0, 2))]
        if len(candidates) < 2:
            raise ValueError(f"Insufficient targets at depth {depth} residue {residue}")
        m = len(candidates)
        positions = (math.floor((m - 1) / 3), math.ceil(2 * (m - 1) / 3))
        if positions[0] == positions[1]:
            raise ValueError(f"Duplicate target at depth {depth} residue {residue}")
        output[str(residue)] = [candidates[i] for i in positions]
    return output


def source_rows() -> list[dict]:
    ids = [line.strip() for line in SPLIT.read_text(encoding="utf-8").splitlines() if line.strip()]
    train_ids = set(line.strip() for line in TRAIN_SPLIT.read_text(encoding="utf-8").splitlines())
    if len(ids) != 58 or len(set(ids)) != 58 or set(ids) & train_ids:
        raise ValueError("Validation split count/uniqueness/train separation changed")
    with METADATA.open(newline="", encoding="utf-8") as stream:
        indexed = {row["case_id"]: row for row in csv.DictReader(stream)}
    rows = []
    for case in ids:
        record = indexed[case]
        path = Path(record["T2_path"]).resolve()
        if path.parent != IMAGE_DIR or not path.is_file():
            raise FileNotFoundError(f"Validation T2 source missing/outside IXI raw T2: {case}")
        shape = tuple(int(part) for part in record["T2_shape"].split("x"))
        if len(shape) != 3:
            raise ValueError(f"Invalid shape metadata: {case}")
        rows.append({"case": case, "path": path, "shape": shape,
                     "targets": selected_targets(shape[2])})
    return rows


def score(a: np.ndarray, target: np.ndarray, support: np.ndarray) -> tuple[float, float]:
    error = (a - target)[support].astype(np.float64)
    return float(np.mean(error * error)), float(np.mean(np.abs(error)))


def score_case(record: dict, hat: object, swinir: object) -> dict:
    path = record["path"]
    image = nib.load(str(path))
    if image.shape != record["shape"]:
        raise ValueError(f"Validation shape changed: {record['case']}")
    volume = image.get_fdata(dtype=np.float32)
    if not np.isfinite(volume).all():
        raise ValueError(f"Nonfinite validation pixels: {record['case']}")
    anchors = volume[:, :, ::4]
    prep = prepared(anchors)
    planes, lo, hi = prep
    if hi <= lo:
        raise ValueError(f"Constant anchors: {record['case']}")
    rows = []
    for residue in (1, 3):
        for z in record["targets"][str(residue)]:
            index = z // 4
            rel = (z - 4 * index) / 4
            left, right = volume[:, :, 4 * index], volume[:, :, 4 * (index + 1)]
            support = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                       (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
            if not support.any():
                raise ValueError(f"Empty acquired support: {record['case']} z{z}")
            raw = (1 - rel) * left.astype(np.float64) + rel * right.astype(np.float64)
            coarse = ((1 - rel) * planes[index] + rel * planes[index + 1]).astype(np.float32)
            pipeline = (resize(np.clip(coarse, 0, 1), volume.shape[:2], preserve_range=True,
                               anti_aliasing=True) * (hi - lo) + lo).astype(np.float32)
            outputs = {"raw_linear": raw, "pipeline_linear": pipeline,
                       "hat": predict(hat, prep, index, rel, volume.shape[:2]),
                       "swinir": predict(swinir, prep, index, rel, volume.shape[:2])}
            target = volume[:, :, z]
            row = {"z": z, "residue": residue, "support_pixels": int(support.sum())}
            for name, output in outputs.items():
                if not np.isfinite(output).all():
                    raise ValueError(f"Nonfinite prediction: {record['case']} z{z} {name}")
                row[f"{name}_mse"], row[f"{name}_mae"] = score(output, target, support)
            rows.append(row)
    return {"case": record["case"], "complete": True,
            "source_sha256": sha256(path), "targets": record["targets"],
            "rows": rows}


def patient_row(item: dict) -> dict:
    result = {"case": item["case"]}
    rows = item["rows"]
    if len(rows) != 4 or sorted(row["residue"] for row in rows) != [1, 1, 3, 3]:
        raise ValueError(f"Incomplete case: {item['case']}")
    for name in METHODS:
        for metric in ("mse", "mae"):
            field = f"{name}_{metric}"
            result[field] = float(np.mean([
                np.mean([row[field] for row in rows if row["residue"] == residue])
                for residue in (1, 3)]))
    for model in ("hat", "swinir"):
        for baseline in ("raw_linear", "pipeline_linear"):
            result[f"{model}_minus_{baseline}_mse"] = (
                result[f"{model}_mse"] - result[f"{baseline}_mse"])
    return result


def describe(patients: list[dict], field: str, draws: np.ndarray) -> dict:
    values = np.array([row[field] for row in patients], dtype=np.float64)
    means = values[draws].mean(axis=1)
    return {"mean": float(values.mean()),
            "bootstrap_95_percentile": [float(x) for x in np.percentile(means, [2.5, 97.5])],
            "positive_patients": int(np.sum(values > 0)),
            "negative_patients": int(np.sum(values < 0)),
            "tied_patients": int(np.sum(values == 0))}


def save_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    records = source_rows()
    for name, (_, path, expected_hash) in MODELS.items():
        if sha256(path) != expected_hash:
            raise ValueError(f"Frozen {name} checkpoint changed")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    OUT.mkdir(parents=True, exist_ok=True)
    case_dir = OUT / "cases"
    case_dir.mkdir(exist_ok=True)
    contract = {"protocol_sha256": sha256(PROTOCOL),
                "validation_split_sha256": sha256(SPLIT),
                "train_split_sha256": sha256(TRAIN_SPLIT),
                "metadata_sha256": sha256(METADATA),
                "checkpoint_sha256": {name: spec[2] for name, spec in MODELS.items()},
                "attempted_cases": 58, "gpu_used": False}
    contract_path = OUT / "run_contract.json"
    if contract_path.exists():
        if json.loads(contract_path.read_text(encoding="utf-8")) != contract:
            raise ValueError("Existing run contract changed")
    else:
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    cases = []
    for index, record in enumerate(records, 1):
        destination = case_dir / f"{record['case']}.json"
        if destination.exists():
            item = json.loads(destination.read_text(encoding="utf-8"))
            if item["run_contract_sha256"] != sha256(contract_path):
                raise ValueError(f"Case run contract changed: {record['case']}")
        else:
            try:
                item = score_case(record, hat, swinir)
            except Exception as error:
                item = {"case": record["case"], "complete": False,
                        "failure_type": type(error).__name__,
                        "failure_reason": str(error)[:180]}
            item["run_contract_sha256"] = sha256(contract_path)
            destination.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
        cases.append(item)
        if index % 5 == 0 or index == len(records):
            print(f"validation CPU cases {index}/{len(records)}", flush=True)
    patients = [patient_row(item) for item in cases if item["complete"]]
    targets = [{"case": item["case"], **row} for item in cases if item["complete"]
               for row in item["rows"]]
    failures = [{"case": item["case"], "type": item["failure_type"],
                 "reason": item["failure_reason"]} for item in cases if not item["complete"]]
    result = {"status": "checkpoint-selection validation diagnostic",
              "attempted_cases": 58, "completed_cases": len(patients),
              "completed_targets": len(targets), "failures": failures,
              "bootstrap_seed": 20261012, "bootstrap_draws": 5000,
              "run_contract_sha256": sha256(contract_path), "gpu_used": False}
    if patients:
        rng = np.random.default_rng(20261012)
        draws = rng.integers(0, len(patients), size=(5000, len(patients)))
        fields = [f"{method}_mse" for method in METHODS]
        fields += [f"{model}_minus_{baseline}_mse" for model in ("hat", "swinir")
                   for baseline in ("raw_linear", "pipeline_linear")]
        result["results"] = {field: describe(patients, field, draws) for field in fields}
        save_csv(OUT / "per_patient.csv", patients)
        save_csv(OUT / "per_target.csv", targets)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value["mean"] for key, value in result.get("results", {}).items()}, indent=2))


if __name__ == "__main__":
    main()
