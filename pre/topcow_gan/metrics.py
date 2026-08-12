from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import ndimage
from skimage.filters import threshold_otsu
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

from .common import load_nifti, write_csv, write_json


def _generated_indices(depth: int, factor: int) -> list[int]:
    return [idx for idx in range(depth) if idx % factor != 0]


def _safe_data_range(gt: np.ndarray) -> float:
    data_range = float(np.max(gt) - np.min(gt))
    return data_range if data_range > 0 else 1.0


def _auto_mask(slice_: np.ndarray) -> np.ndarray:
    values = slice_.astype(np.float32)
    if np.all(values == values.flat[0]):
        return np.ones_like(values, dtype=bool)
    try:
        thresh = threshold_otsu(values)
    except ValueError:
        thresh = float(np.percentile(values, 10))
    mask = values > thresh
    if int(mask.sum()) < 100:
        mask = values > np.percentile(values, 5)
    return mask


def _bbox(mask: np.ndarray) -> tuple[slice, slice] | None:
    coords = np.argwhere(mask)
    if coords.size == 0:
        return None
    lo = coords.min(axis=0)
    hi = coords.max(axis=0) + 1
    return slice(int(lo[0]), int(hi[0])), slice(int(lo[1]), int(hi[1]))


def _masked_psnr(gt: np.ndarray, pred: np.ndarray, mask: np.ndarray) -> float:
    if not np.any(mask):
        return float("nan")
    mse = float(np.mean((gt[mask] - pred[mask]) ** 2))
    if mse == 0:
        return float("inf")
    data_range = _safe_data_range(gt)
    return float(20 * np.log10(data_range / np.sqrt(mse)))


def _masked_ssim(gt: np.ndarray, pred: np.ndarray, mask: np.ndarray) -> float:
    box = _bbox(mask)
    if box is None:
        return float("nan")
    gt_crop = gt[box]
    pred_crop = pred[box]
    mask_crop = mask[box].astype(np.float32)
    if min(gt_crop.shape) < 7:
        return float("nan")
    return float(
        structural_similarity(
            gt_crop * mask_crop,
            pred_crop * mask_crop,
            data_range=_safe_data_range(gt_crop),
        )
    )


def _dice(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(bool)
    b = b.astype(bool)
    denom = int(a.sum() + b.sum())
    if denom == 0:
        return 1.0
    return float(2 * np.logical_and(a, b).sum() / denom)


def _hd95(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(bool)
    b = b.astype(bool)
    if not np.any(a) and not np.any(b):
        return 0.0
    if not np.any(a) or not np.any(b):
        return float("nan")
    dt_b = ndimage.distance_transform_edt(~b)
    dt_a = ndimage.distance_transform_edt(~a)
    distances = np.concatenate([dt_b[a], dt_a[b]])
    return float(np.percentile(distances, 95))


def _boundary_band(mask: np.ndarray, iterations: int = 2) -> np.ndarray:
    mask = mask.astype(bool)
    dilated = ndimage.binary_dilation(mask, iterations=iterations)
    eroded = ndimage.binary_erosion(mask, iterations=iterations)
    return np.logical_xor(dilated, eroded)


def _evaluate_volume(gt: np.ndarray, pred: np.ndarray, factor: int) -> dict:
    if gt.shape != pred.shape:
        raise ValueError(f"Shape mismatch: gt={gt.shape}, pred={pred.shape}")
    indices = _generated_indices(gt.shape[2], factor)
    if not indices:
        raise ValueError("No generated slices found for evaluation.")
    psnr_values = []
    ssim_values = []
    mae_values = []
    mse_values = []
    ncc_values = []
    pearson_values = []
    mask_psnr_values = []
    mask_ssim_values = []
    auto_dice_values = []
    auto_hd95_values = []
    for idx in indices:
        g = gt[:, :, idx].astype(np.float32)
        p = pred[:, :, idx].astype(np.float32)
        dr = _safe_data_range(g)
        psnr_values.append(float(peak_signal_noise_ratio(g, p, data_range=dr)))
        ssim_values.append(float(structural_similarity(g, p, data_range=dr)))
        gt_mask = _auto_mask(g)
        pred_mask = _auto_mask(p)
        mask_psnr_values.append(_masked_psnr(g, p, gt_mask))
        mask_ssim_values.append(_masked_ssim(g, p, gt_mask))
        auto_dice_values.append(_dice(gt_mask, pred_mask))
        auto_hd95_values.append(_hd95(gt_mask, pred_mask))
        diff = p - g
        mae_values.append(float(np.mean(np.abs(diff))))
        mse_values.append(float(np.mean(diff ** 2)))
        g_flat = g.reshape(-1)
        p_flat = p.reshape(-1)
        if np.std(g_flat) > 0 and np.std(p_flat) > 0:
            corr = float(np.corrcoef(g_flat, p_flat)[0, 1])
        else:
            corr = 0.0
        ncc_values.append(corr)
        pearson_values.append(corr)
    return {
        "generated_slices": len(indices),
        "psnr": float(np.mean(psnr_values)),
        "ssim": float(np.mean(ssim_values)),
        "mae": float(np.mean(mae_values)),
        "mse": float(np.mean(mse_values)),
        "ncc": float(np.mean(ncc_values)),
        "pearson": float(np.mean(pearson_values)),
        "mask_psnr": float(np.nanmean(mask_psnr_values)),
        "mask_ssim": float(np.nanmean(mask_ssim_values)),
        "auto_dice": float(np.nanmean(auto_dice_values)),
        "auto_hd95": float(np.nanmean(auto_hd95_values)),
    }


def _evaluate_labeled_volume(gt: np.ndarray, pred: np.ndarray, label: np.ndarray, factor: int) -> dict:
    if gt.shape != pred.shape or gt.shape != label.shape:
        raise ValueError(f"Shape mismatch: gt={gt.shape}, pred={pred.shape}, label={label.shape}")
    indices = _generated_indices(gt.shape[2], factor)
    vessel_psnr_values = []
    vessel_ssim_values = []
    vessel_mae_values = []
    vessel_mse_values = []
    boundary_mae_values = []
    vessel_voxels = 0
    for idx in indices:
        g = gt[:, :, idx].astype(np.float32)
        p = pred[:, :, idx].astype(np.float32)
        vessel_mask = label[:, :, idx] > 0
        vessel_voxels += int(vessel_mask.sum())
        if not np.any(vessel_mask):
            continue
        vessel_psnr_values.append(_masked_psnr(g, p, vessel_mask))
        vessel_ssim_values.append(_masked_ssim(g, p, vessel_mask))
        diff = p - g
        vessel_mae_values.append(float(np.mean(np.abs(diff[vessel_mask]))))
        vessel_mse_values.append(float(np.mean(diff[vessel_mask] ** 2)))
        boundary = _boundary_band(vessel_mask)
        if np.any(boundary):
            boundary_mae_values.append(float(np.mean(np.abs(diff[boundary]))))
    return {
        "generated_slices": len(indices),
        "vessel_voxels": vessel_voxels,
        "vessel_psnr": float(np.nanmean(vessel_psnr_values)),
        "vessel_ssim": float(np.nanmean(vessel_ssim_values)),
        "vessel_mae": float(np.nanmean(vessel_mae_values)),
        "vessel_mse": float(np.nanmean(vessel_mse_values)),
        "vessel_boundary_mae": float(np.nanmean(boundary_mae_values)),
    }


def evaluate_method(gt_dir: Path, pred_dir: Path, prefix: str, method: str, factor: int = 4) -> list[dict]:
    rows: list[dict] = []
    for gt_path in sorted(gt_dir.glob("*.nii.gz")):
        pred_path = pred_dir / f"{prefix}{gt_path.name}"
        if not pred_path.exists():
            raise FileNotFoundError(pred_path)
        gt, _, _ = load_nifti(gt_path)
        pred, _, _ = load_nifti(pred_path)
        metrics = _evaluate_volume(gt, pred, factor=factor)
        rows.append({"method": method, "case": gt_path.name, **metrics})
    return rows


def evaluate_labeled_method(
    gt_dir: Path,
    pred_dir: Path,
    label_dir: Path,
    prefix: str,
    method: str,
    factor: int = 4,
) -> list[dict]:
    rows: list[dict] = []
    for gt_path in sorted(gt_dir.glob("*.nii.gz")):
        pred_path = pred_dir / f"{prefix}{gt_path.name}"
        label_path = label_dir / gt_path.name
        if not pred_path.exists():
            raise FileNotFoundError(pred_path)
        if not label_path.exists():
            raise FileNotFoundError(label_path)
        gt, _, _ = load_nifti(gt_path)
        pred, _, _ = load_nifti(pred_path)
        label, _, _ = load_nifti(label_path)
        metrics = _evaluate_labeled_volume(gt, pred, label, factor=factor)
        rows.append({"method": method, "case": gt_path.name, **metrics})
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    methods = sorted({row["method"] for row in rows})
    summaries: list[dict] = []
    metric_names = [
        "psnr",
        "ssim",
        "mae",
        "mse",
        "ncc",
        "pearson",
        "mask_psnr",
        "mask_ssim",
        "auto_dice",
        "auto_hd95",
    ]
    for method in methods:
        selected = [row for row in rows if row["method"] == method]
        summary = {"method": method, "cases": len(selected)}
        for name in metric_names:
            values = np.array([row[name] for row in selected], dtype=np.float64)
            summary[f"{name}_mean"] = float(values.mean())
            summary[f"{name}_std"] = float(values.std(ddof=0))
        summaries.append(summary)
    return summaries


def write_metric_outputs(metrics_dir: Path, rows: list[dict]) -> None:
    summaries = summarize(rows)
    write_csv(metrics_dir / "per_case_metrics.csv", rows)
    write_csv(metrics_dir / "summary_metrics.csv", summaries)
    write_json(metrics_dir / "summary_metrics.json", {"summary": summaries})


def summarize_labeled(rows: list[dict]) -> list[dict]:
    methods = sorted({row["method"] for row in rows})
    metric_names = [
        "vessel_psnr",
        "vessel_ssim",
        "vessel_mae",
        "vessel_mse",
        "vessel_boundary_mae",
    ]
    summaries: list[dict] = []
    for method in methods:
        selected = [row for row in rows if row["method"] == method]
        summary = {"method": method, "cases": len(selected)}
        for name in metric_names:
            values = np.array([row[name] for row in selected], dtype=np.float64)
            summary[f"{name}_mean"] = float(np.nanmean(values))
            summary[f"{name}_std"] = float(np.nanstd(values))
        summaries.append(summary)
    return summaries


def write_labeled_metric_outputs(metrics_dir: Path, rows: list[dict]) -> None:
    summaries = summarize_labeled(rows)
    write_csv(metrics_dir / "labeled_holdout_per_case_metrics.csv", rows)
    write_csv(metrics_dir / "labeled_holdout_summary_metrics.csv", summaries)
    write_json(metrics_dir / "labeled_holdout_summary_metrics.json", {"summary": summaries})
