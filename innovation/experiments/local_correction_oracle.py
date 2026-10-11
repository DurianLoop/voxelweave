"""CPU-only, target-assisted local mixing diagnostic on old fastMRI validation.

The oracle sees target images. It measures action-space headroom, not a deployable
selector or independent evaluation of the previously validation-selected models.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "design"))

from pastnet_v2.data import IntervalDataset
from pastnet_v2.metrics import quality
from pastnet_v2.run import load_model as load_control
from pastnet_orientation.run import load_model as load_orientation
from pastnet_series_integrity.run import load_model as load_repair
from pastnet_wavelet_trunk.run import load_model as load_wavelet

PAIRS = {
    "old_orientation": dict(
        manifest=ROOT / "design/pastnet_v2/manifests/fastmri/fold_00.json",
        base=("control", load_control, ROOT / "design/pastnet_v2/runs/full_control_seed3407_vram20/best.pth",
              ROOT / "design/pastnet_v2/runs/full_control_seed3407_vram20/validation/per_slice.csv"),
        candidate=("orientation", load_orientation,
                   ROOT / "design/pastnet_orientation/runs/full_orientation_seed3407_vram20/best.pth",
                   ROOT / "design/pastnet_orientation/runs/full_orientation_seed3407_vram20/validation/per_slice.csv")),
    "repaired_wavelet": dict(
        manifest=ROOT / "design/pastnet_series_integrity/manifests/fastmri_repaired.json",
        base=("repair", load_repair,
              ROOT / "design/pastnet_series_integrity/runs/full_repair_seed3407_vram20/best.pth",
              ROOT / "design/pastnet_series_integrity/runs/full_repair_seed3407_vram20/validation/per_slice.csv"),
        candidate=("wavelet3", load_wavelet,
                   ROOT / "design/pastnet_wavelet_trunk/runs/full_wavelet3_seed3407_vram20/best.pth",
                   ROOT / "design/pastnet_wavelet_trunk/runs/full_wavelet3_seed3407_vram20/validation/per_slice.csv")),
}
METRICS = ("psnr", "ssim", "mae", "mse", "ncc", "dice_proxy", "hd95_proxy", "tail10_mse")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def history(path: Path) -> dict[tuple[str, int, float], dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {(row["case_id"], int(row["z"]), float(row["phase"])): row
                for row in csv.DictReader(stream)}


def patch_oracle(base: np.ndarray, candidate: np.ndarray, target: np.ndarray,
                 size: int = 32, stride: int = 16) -> tuple[np.ndarray, np.ndarray]:
    if base.shape != (256, 256):
        raise ValueError(f"Unexpected image shape: {base.shape}")
    delta = candidate - base
    residual = target - base
    taper = 0.05 + 0.95 * np.hanning(size)
    window = np.outer(taper, taper).astype(np.float32)
    numerator = np.zeros_like(base)
    denominator = np.zeros_like(base)
    for y in range(0, base.shape[0] - size + 1, stride):
        for x in range(0, base.shape[1] - size + 1, stride):
            d = delta[y:y+size, x:x+size]
            e = residual[y:y+size, x:x+size]
            energy = float(np.mean(d * d))
            alignment = float(np.mean(d * e))
            alpha = float(np.clip(alignment / max(energy, 1e-12), 0, 1))
            numerator[y:y+size, x:x+size] += alpha * window
            denominator[y:y+size, x:x+size] += window
    if np.any(denominator <= 0):
        raise AssertionError("Patch windows do not cover the image")
    alpha_map = numerator / denominator
    return base + alpha_map * delta, alpha_map


def aggregate(rows: list[dict], metric: str) -> float:
    cases: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        cases[(row["patient_id"], row["case_id"])].append(float(row[metric]))
    patients: dict[str, list[float]] = defaultdict(list)
    for (patient, _), values in cases.items():
        patients[patient].append(float(np.mean(values)))
    return float(np.mean([np.mean(values) for values in patients.values()]))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_predictions(path: Path, records: list[dict]) -> str:
    np.savez_compressed(path,
                        base=np.stack([r["base"] for r in records]),
                        candidate=np.stack([r["candidate"] for r in records]),
                        target=np.stack([r["target"] for r in records]),
                        spacing=np.stack([r["spacing"] for r in records]),
                        case_id=np.asarray([r["case_id"] for r in records]),
                        patient_id=np.asarray([r["patient_id"] for r in records]),
                        z=np.asarray([r["z"] for r in records]),
                        phase=np.asarray([r["phase"] for r in records]))
    return sha256(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit-cases", type=int)
    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--save-predictions", action="store_true")
    parser.add_argument("--pair", choices=PAIRS, default="old_orientation")
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    pair = PAIRS[args.pair]
    manifest = pair["manifest"]
    base_name, base_loader, base_checkpoint, base_csv = pair["base"]
    candidate_name, candidate_loader, candidate_checkpoint, candidate_csv = pair["candidate"]
    source_paths = (manifest, base_checkpoint, candidate_checkpoint, base_csv, candidate_csv)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    device = torch.device("cpu")
    models = (base_loader(base_name, base_checkpoint).to(device).eval(),
              candidate_loader(candidate_name, candidate_checkpoint).to(device).eval())
    dataset = IntervalDataset(manifest, "val", anchors=4, limit=args.limit_cases)
    old = (history(base_csv), history(candidate_csv))
    records = []
    parity_differences: dict[str, list[float]] = defaultdict(list)
    case_seen = set()
    for index in range(len(dataset)):
        sample = dataset[index]
        batch = {key: value[None] for key, value in sample.items()
                 if isinstance(value, torch.Tensor) and key != "target"}
        with torch.inference_mode():
            base, candidate = (model(batch).float()[0, :, 0].numpy()
                               for model in models)
        target = sample["target"][:, 0].numpy()
        for j, phase in enumerate((0.25, 0.5, 0.75)):
            key = (sample["case_id"], sample["z"] + j + 1, phase)
            b, c, y = base[j], candidate[j], target[j]
            b_mse = float(np.mean((b.astype(np.float64) - y) ** 2))
            c_mse = float(np.mean((c.astype(np.float64) - y) ** 2))
            for model_name, actual, reference in ((base_name, b_mse, old[0]),
                                                   (candidate_name, c_mse, old[1])):
                expected = float(reference[key]["psnr"])
                recomputed = -10 * np.log10(max(actual, 1e-12))
                parity_differences[model_name].append(float(recomputed - expected))
                if abs(recomputed - expected) > 0.02:
                    raise AssertionError(f"Historical metric mismatch for {model_name} {key}: "
                                         f"CPU={recomputed:.8f}, historical={expected:.8f}, "
                                         f"difference={recomputed-expected:+.8f} dB")
            delta = c - b
            residual = y - b
            m = float(np.mean(delta.astype(np.float64) * residual))
            d = float(np.mean(delta.astype(np.float64) ** 2))
            alpha_slice = float(np.clip(m / max(d, 1e-12), 0, 1))
            patch, alpha_map = patch_oracle(b, c, y)
            records.append(dict(case_id=key[0], patient_id=sample["patient_id"],
                                z=key[1], phase=phase, base=b.copy(), candidate=c.copy(),
                                target=y.copy(), patch=patch, m=m, d=d, b_mse=b_mse,
                                alpha_slice=alpha_slice,
                                patch_alpha_mean=float(alpha_map.mean()),
                                patch_alpha_std=float(alpha_map.std()),
                                spacing=np.exp2(sample["physical"][j, :2].numpy())))
        if sample["case_id"] not in case_seen:
            case_seen.add(sample["case_id"])
            print(f"CPU inference case {len(case_seen)}/{len(dataset.records)}: {sample['case_id']}", flush=True)

    if args.export_only:
        args.out.mkdir(parents=True)
        archive_hash = save_predictions(args.out / "paired_predictions.npz", records)
        export = dict(scope="fastmri_validation_paired_cpu_predictions", pair=args.pair,
                      patients=len(case_seen), slices=len(records),
                      paired_predictions_sha256=archive_hash,
                      cpu_vs_historical_psnr_difference_db={name: {
                          "mean": float(np.mean(values)),
                          "max_absolute": float(np.max(np.abs(values)))}
                          for name, values in parity_differences.items()},
                      sources=[dict(path=str(path.relative_to(ROOT)).replace("\\", "/"),
                                    sha256=sha256(path)) for path in source_paths],
                      limitations=["Targets are withheld at deployment; this archive is for development diagnostics only.",
                                   "Both checkpoints were previously selected on this validation cohort.",
                                   "CPU float32 output differs slightly from historical GPU autocast output."])
        (args.out / "manifest.json").write_text(
            json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"patients": len(case_seen), "slices": len(records),
                          "sha256": export["paired_predictions_sha256"]}, indent=2), flush=True)
        return

    grid = np.linspace(0.0, 1.0, 101)
    scores = []
    for alpha in grid:
        rows = [dict(patient_id=r["patient_id"], case_id=r["case_id"],
                     psnr=-10 * np.log10(max(r["b_mse"] - 2*alpha*r["m"] + alpha*alpha*r["d"], 1e-12)))
                for r in records]
        scores.append(aggregate(rows, "psnr"))
    best_alpha = float(grid[int(np.argmax(scores))])

    rows = []
    for r in records:
        for policy, pred in (("base", r["base"]), (candidate_name, r["candidate"]),
                             ("best_fixed", r["base"] + best_alpha * (r["candidate"] - r["base"])),
                             ("oracle_slice", r["base"] + r["alpha_slice"] * (r["candidate"] - r["base"])),
                             ("oracle_patch32", r["patch"])):
            measured = quality(pred, r["target"], r["spacing"])
            rows.append(dict(case_id=r["case_id"], patient_id=r["patient_id"],
                             z=r["z"], phase=r["phase"], policy=policy,
                             alpha_slice=r["alpha_slice"],
                             patch_alpha_mean=r["patch_alpha_mean"],
                             patch_alpha_std=r["patch_alpha_std"], **measured))

    summaries = {}
    for policy in ("base", candidate_name, "best_fixed", "oracle_slice", "oracle_patch32"):
        selected = [r for r in rows if r["policy"] == policy]
        summaries[policy] = {metric: aggregate(selected, metric) for metric in METRICS}
    patients = sorted({r["patient_id"] for r in rows})
    per_patient = []
    for patient in patients:
        for policy in summaries:
            selected = [r for r in rows if r["patient_id"] == patient and r["policy"] == policy]
            per_patient.append(dict(patient_id=patient, policy=policy,
                                    **{metric: float(np.mean([r[metric] for r in selected]))
                                       for metric in METRICS}))
    result = dict(scope="historical_fastmri_validation_target_assisted_oracle", pair=args.pair,
                  complete_validation=args.limit_cases is None,
                  patients=len(patients), slices=len(records), patch_size=32, stride=16,
                  patch_window="0.05 + 0.95*hanning", best_fixed_alpha=best_alpha,
                  best_fixed_alpha_grid_step=0.01, summary=summaries,
                  cpu_vs_historical_psnr_difference_db={name: {
                      "mean": float(np.mean(values)),
                      "max_absolute": float(np.max(np.abs(values)))}
                      for name, values in parity_differences.items()},
                  limitations=["Oracle alpha uses withheld target pixels and is not deployable.",
                               "CPU float32 inference can differ slightly from historical GPU autocast metrics.",
                               "Both checkpoints were selected using this historical validation cohort.",
                               "Best fixed alpha is also selected on the same validation cohort.",
                               "Historical validation selected both checkpoints; this is exploratory only.",
                               "HD95 and Dice are intensity-threshold proxies, not segmentation outcomes."],
                  sources=[dict(path=str(path.relative_to(ROOT)).replace("\\", "/"), sha256=sha256(path))
                           for path in source_paths])
    args.out.mkdir(parents=True)
    if args.save_predictions:
        result["paired_predictions_sha256"] = save_predictions(
            args.out / "paired_predictions.npz", records)
    write_csv(args.out / "per_slice.csv", rows)
    write_csv(args.out / "per_patient.csv", per_patient)
    (args.out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    print(json.dumps({"patients": len(patients), "slices": len(records),
                      "best_fixed_alpha": best_alpha,
                      "psnr": {key: value["psnr"] for key, value in summaries.items()},
                      "hd95_proxy": {key: value["hd95_proxy"] for key, value in summaries.items()}},
                     indent=2), flush=True)


if __name__ == "__main__":
    main()
