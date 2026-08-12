from __future__ import annotations

import argparse
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import ndimage

from .optimization_protocol import (
    ANALYTICAL, REPO_ROOT, UNIVERSAL_NEURAL, analytical_path, case_names,
    folds, gt_path, prediction_path, profile_sources, sparse_path,
)
from .cross_scale_protocol import ningxia_case_group, ningxia_test_group


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "nested_optimization"
PROFILES = (("ixi", 4), ("fastmri", 2), ("fastmri", 4), ("fastmri", 6),
            ("ningxia", 2), ("ningxia", 4), ("ningxia", 6))
TARGETS = UNIVERSAL_NEURAL


def load_image(path: Path) -> tuple[np.ndarray, np.ndarray]:
    image = nib.load(str(path))
    data = image.get_fdata(dtype=np.float32)
    if data.ndim != 3 or not np.isfinite(data).all():
        raise ValueError(f"invalid NIfTI: {path}")
    return data, image.affine


def generated(depth: int, scale: int) -> np.ndarray:
    return np.asarray([z for z in range(depth) if z % scale], dtype=int)


def threshold_mask(volume: np.ndarray, indices: np.ndarray, fraction: float = .01) -> np.ndarray:
    mask = np.zeros(volume.shape, dtype=bool)
    values = np.abs(volume[:, :, indices])
    threshold = fraction * float(np.max(values)) if values.size else 0.0
    mask[:, :, indices] = values > threshold
    return mask


def input_mask(sparse: np.ndarray, target_shape: tuple[int, int, int], indices: np.ndarray, scale: int) -> np.ndarray:
    observed = np.asarray([z for z in range(target_shape[2]) if z % scale == 0], dtype=int)
    sparse_indices = np.arange(sparse.shape[2], dtype=int)
    base = threshold_mask(sparse, sparse_indices)
    result = np.zeros(target_shape, dtype=bool)
    for z in indices:
        nearest_position = int(np.argmin(np.abs(observed - z)))
        nearest_sparse = min(nearest_position, sparse.shape[2]-1)
        result[:, :, z] = base[:, :, nearest_sparse]
    return result


def common_metrics(pred: np.ndarray, gt: np.ndarray, support: np.ndarray, indices: np.ndarray) -> dict[str, float]:
    p = pred[:, :, indices][support[:, :, indices]].astype(np.float64)
    y = gt[:, :, indices][support[:, :, indices]].astype(np.float64)
    if not p.size:
        raise ValueError("empty common support")
    diff = p - y
    mae = float(np.mean(np.abs(diff)))
    mse = float(np.mean(diff * diff))
    data_range = max(float(np.quantile(y, .99) - np.quantile(y, .01)), 1e-6)
    psnr = float(20 * np.log10(data_range) - 10 * np.log10(max(mse, 1e-12)))
    p0, y0 = p - p.mean(), y - y.mean()
    ncc = float(np.dot(p0, y0) / max(np.linalg.norm(p0) * np.linalg.norm(y0), 1e-12))
    c1, c2 = (.01 * data_range) ** 2, (.03 * data_range) ** 2
    vx, vy, cov = float(np.var(p)), float(np.var(y)), float(np.mean(p0 * y0))
    ssim = float(((2*p.mean()*y.mean()+c1)*(2*cov+c2)) /
                 ((p.mean()**2+y.mean()**2+c1)*(vx+vy+c2)))
    return {"mae": mae, "mse": mse, "psnr": psnr, "ssim": ssim, "ncc": ncc}


def pool_map(values: np.ndarray, mask: np.ndarray, indices: np.ndarray) -> dict[str, float]:
    slice_mean, slice_q90, slice_top = [], [], []
    for z in indices:
        v = values[:, :, z][mask[:, :, z]]
        if not v.size:
            continue
        slice_mean.append(float(np.mean(v)))
        slice_q90.append(float(np.quantile(v, .90)))
        k = max(1, int(math.ceil(.10 * v.size)))
        slice_top.append(float(np.mean(np.partition(v, v.size-k)[-k:])))
    if not slice_mean:
        return {name: float("nan") for name in
                ("mean", "q90", "top10", "slice_max", "slice_q90", "top2")}
    means = np.asarray(slice_mean)
    return {
        "mean": float(np.mean(means)), "q90": float(np.mean(slice_q90)),
        "top10": float(np.mean(slice_top)), "slice_max": float(np.max(means)),
        "slice_q90": float(np.quantile(means, .90)),
        "top2": float(np.mean(np.sort(means)[-min(2, len(means)):])),
    }


def pool_basic(values: np.ndarray, mask: np.ndarray, indices: np.ndarray, with_q90: bool = True) -> dict[str, float]:
    means, quantiles = [], []
    for z in indices:
        v = values[:, :, z][mask[:, :, z]]
        if not v.size: continue
        means.append(float(np.mean(v)))
        if with_q90: quantiles.append(float(np.quantile(v, .90)))
    return {"mean": float(np.mean(means)) if means else float("nan"),
            "q90": float(np.mean(quantiles)) if quantiles else float("nan")}


def case_job(job: tuple[str, int, str | None, str]) -> tuple[list[dict], list[dict], list[dict]]:
    dataset, scale, fold, case = job
    sources = profile_sources(dataset, scale)
    ref = sources["i3net"]
    outputs = {name: load_image(prediction_path(src, fold, case))[0] for name, src in sources.items()}
    outputs.update({name: load_image(analytical_path(ref, fold, name, case))[0] for name in ANALYTICAL})
    gt, affine = load_image(gt_path(ref, fold, case))
    sparse, _ = load_image(sparse_path(ref, fold, case))
    indices = generated(gt.shape[2], scale)
    common = threshold_mask(gt, indices)
    bank_union = np.logical_or.reduce([threshold_mask(v, indices) for v in outputs.values()])
    inp = input_mask(sparse, gt.shape, indices, scale)
    masks = {"bank_union": bank_union, "input_derived": inp}
    fidelity, errors, pair_rows = [], [], []
    for model, pred in outputs.items():
        metric = common_metrics(pred, gt, common, indices)
        record = {"dataset": dataset, "scale": scale, "fold": fold or "none", "case": case,
                  "model": model, "support": "gt_0.01_common", **metric}
        fidelity.append(record)
        errors.append({"dataset": dataset, "scale": scale, "fold": fold or "none", "case": case,
                       "target_model": model, "common_error": metric["mae"]})
    gradients = {name: np.sqrt(sum(g*g for g in np.gradient(value, edge_order=1))).astype(np.float32)
                 for name, value in outputs.items()}
    laplacians = {name: ndimage.laplace(value, mode="nearest") for name, value in outputs.items()}
    energies = {name: np.sqrt(ndimage.uniform_filter(value*value, size=(5,5,1), mode="nearest") + 1e-6)
                for name, value in outputs.items()}
    for target in TARGETS:
        if target not in outputs:
            continue
        target_masks = {**masks, "target_0.01": threshold_mask(outputs[target], indices)}
        for member in sorted(set(outputs) - {target}):
            absolute = np.abs(outputs[target] - outputs[member])
            relative = absolute / (np.abs(outputs[target]) + np.abs(outputs[member]) + 1e-3)
            grad = np.abs(gradients[target] - gradients[member])
            lap = np.abs(laplacians[target] - laplacians[member])
            energy = absolute / (energies[target] + energies[member] + 1e-3)
            row = {"dataset": dataset, "scale": scale, "fold": fold or "none", "case": case,
                   "target_model": target, "member": member}
            for mask_name, mask in target_masks.items():
                p = pool_map(absolute, mask, indices)
                for key, value in p.items(): row[f"intensity_{key}__{mask_name}"] = value
            bank = target_masks["bank_union"]
            for domain, values, with_q90 in (("relative",relative,True),("gradient",grad,True),
                                              ("laplacian",lap,False),("local_energy",energy,False)):
                p2=pool_basic(values,bank,indices,with_q90)
                row[f"{domain}_mean__bank_union"]=p2["mean"]
                if with_q90: row[f"{domain}_q90__bank_union"]=p2["q90"]
            pair_rows.append(row)
    return fidelity, errors, pair_rows


def jobs_for(profiles) -> list[tuple[str, int, str | None, str]]:
    jobs = []
    for dataset, scale in profiles:
        sources = profile_sources(dataset, scale); ref = sources["i3net"]
        for fold in folds(dataset):
            held = ningxia_test_group(REPO_ROOT, fold) if fold else None
            for case in case_names(ref, fold):
                if held and ningxia_case_group(case) != held:
                    raise ValueError(f"OOF mismatch {fold}/{case}")
                jobs.append((dataset, scale, fold, case))
    return jobs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("development", "ningxia", "all"), default="all")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    profiles = PROFILES if args.scope == "all" else (PROFILES[:4] if args.scope == "development" else PROFILES[4:])
    jobs = jobs_for(profiles)
    fidelity, errors, pairs = [], [], []
    start = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for index, (f, e, p) in enumerate(executor.map(case_job, jobs), 1):
            fidelity.extend(f); errors.extend(e); pairs.extend(p)
            print(f"nested precompute {index}/{len(jobs)} pairs={len(pairs)} elapsed={time.time()-start:.1f}s", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    suffix = args.scope
    pd.DataFrame(fidelity).to_csv(OUT / f"common_fidelity_per_case_{suffix}.csv", index=False)
    pd.DataFrame(errors).to_csv(OUT / f"common_errors_per_case_{suffix}.csv", index=False)
    pd.DataFrame(pairs).to_csv(OUT / f"pair_features_per_case_{suffix}.csv", index=False)


if __name__ == "__main__":
    main()
