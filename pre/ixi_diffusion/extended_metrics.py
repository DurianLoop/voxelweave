from __future__ import annotations

import argparse
from pathlib import Path
import time

import numpy as np
import pandas as pd
from skimage.metrics import structural_similarity
import torch

from .common import load_nifti, write_csv, write_json
from .settings import build_paths


def _safe_range(a: np.ndarray) -> float:
    value = float(np.nanmax(a) - np.nanmin(a))
    return value if value > 0 else 1.0


def _safe_energy(a: np.ndarray) -> float:
    value = float(np.mean(a.astype(np.float32) ** 2))
    return value if value > 1e-8 else 1.0


def _mean_ssim_for_axis(gt: np.ndarray, pred: np.ndarray, axis: int, max_slices: int | None = None) -> float:
    gt_axis = np.moveaxis(gt, axis, 0)
    pred_axis = np.moveaxis(pred, axis, 0)
    indices = list(range(gt_axis.shape[0]))
    if max_slices is not None and len(indices) > max_slices:
        step = len(indices) / float(max_slices)
        indices = [int(round(i * step)) for i in range(max_slices)]
        indices = sorted(set(min(i, gt_axis.shape[0] - 1) for i in indices))
    values = []
    for idx in indices:
        g = gt_axis[idx].astype(np.float32)
        p = pred_axis[idx].astype(np.float32)
        if min(g.shape) < 7:
            continue
        values.append(float(structural_similarity(g, p, data_range=_safe_range(g))))
    return float(np.mean(values)) if values else float("nan")


def _prepare_lpips_slice(slice_: np.ndarray, data_range: float) -> torch.Tensor:
    arr = slice_.astype(np.float32)
    arr = (arr - float(np.min(arr))) / max(data_range, 1e-8)
    arr = arr * 2.0 - 1.0
    tensor = torch.from_numpy(arr[None, None, :, :]).float()
    return tensor.repeat(1, 3, 1, 1)


def _lpips_volume(gt: np.ndarray, pred: np.ndarray, indices: list[int], max_slices: int | None) -> float | None:
    if max_slices is not None and max_slices <= 0:
        return None
    try:
        import lpips  # type: ignore
    except Exception:
        return None
    if max_slices is not None and len(indices) > max_slices:
        step = len(indices) / float(max_slices)
        indices = [indices[int(i * step)] for i in range(max_slices)]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        model = lpips.LPIPS(net="alex").to(device).eval()
    except Exception:
        return None
    values = []
    with torch.no_grad():
        for idx in indices:
            g = gt[:, :, idx].astype(np.float32)
            p = pred[:, :, idx].astype(np.float32)
            dr = _safe_range(g)
            gx = _prepare_lpips_slice(g, dr).to(device)
            px = _prepare_lpips_slice(p, dr).to(device)
            values.append(float(model(gx, px).item()))
    return float(np.mean(values)) if values else float("nan")


def _generated_indices(depth: int, factor: int) -> list[int]:
    return [idx for idx in range(depth) if idx % factor != 0]


def _generated_error_metrics(gt: np.ndarray, pred: np.ndarray, indices: list[int]) -> dict[str, float]:
    nmse_values = []
    nrmse_values = []
    snli_values = []
    grad_mae_values = []
    for idx in indices:
        g = gt[:, :, idx].astype(np.float32)
        p = pred[:, :, idx].astype(np.float32)
        diff = p - g
        mse = float(np.mean(diff ** 2))
        rmse = float(np.sqrt(mse))
        nmse_values.append(float(mse / _safe_energy(g)))
        nrmse_values.append(float(rmse / _safe_range(g)))
        gy, gx = np.gradient(g)
        py, px = np.gradient(p)
        grad_gt = np.sqrt(gx ** 2 + gy ** 2)
        grad_pred = np.sqrt(px ** 2 + py ** 2)
        grad_mae_values.append(float(np.mean(np.abs(grad_pred - grad_gt))))
        if 0 < idx < gt.shape[2] - 1:
            gt_curvature = (
                gt[:, :, idx + 1].astype(np.float32)
                - 2.0 * gt[:, :, idx].astype(np.float32)
                + gt[:, :, idx - 1].astype(np.float32)
            )
            pred_curvature = (
                pred[:, :, idx + 1].astype(np.float32)
                - 2.0 * pred[:, :, idx].astype(np.float32)
                + pred[:, :, idx - 1].astype(np.float32)
            )
            snli_values.append(float(np.mean(np.abs(pred_curvature - gt_curvature)) / _safe_range(g)))
    return {
        "nmse": float(np.nanmean(nmse_values)) if nmse_values else float("nan"),
        "nrmse": float(np.nanmean(nrmse_values)) if nrmse_values else float("nan"),
        "snli": float(np.nanmean(snli_values)) if snli_values else float("nan"),
        "gradient_mae": float(np.nanmean(grad_mae_values)) if grad_mae_values else float("nan"),
    }


def run(profile: str, max_view_slices: int, max_lpips_slices: int) -> None:
    paths = build_paths(profile)
    summary_path = paths.metrics / "summary_metrics.csv"
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    summary = pd.read_csv(summary_path)
    rows = []
    method_specs = [
        ("linear", paths.baseline_linear, "linear_"),
        ("cubic", paths.baseline_cubic, "cubic_"),
        ("resunet", paths.diffusion_outputs, "diff_"),
        ("saint", paths.diffusion_outputs, "diff_"),
        ("diffusion", paths.diffusion_outputs, "diff_"),
    ]
    existing_methods = set(summary["method"].astype(str))
    for method, pred_dir, prefix in method_specs:
        if method not in existing_methods:
            continue
        start = time.perf_counter()
        case_rows = []
        for gt_path in sorted(paths.eval_gt.glob("*.nii.gz")):
            pred_path = pred_dir / f"{prefix}{gt_path.name}"
            if not pred_path.exists():
                continue
            gt, _, _ = load_nifti(gt_path)
            pred, _, _ = load_nifti(pred_path)
            indices = _generated_indices(gt.shape[2], factor=int(summary.iloc[0].get("stride", 4)) if "stride" in summary else 4)
            lpips_value = _lpips_volume(gt, pred, indices, max_lpips_slices)
            generated_metrics = _generated_error_metrics(gt, pred, indices)
            case_rows.append(
                {
                    "method": method,
                    "case": gt_path.name,
                    "ssim_a": _mean_ssim_for_axis(gt, pred, axis=2, max_slices=max_view_slices),
                    "ssim_c": _mean_ssim_for_axis(gt, pred, axis=1, max_slices=max_view_slices),
                    "ssim_s": _mean_ssim_for_axis(gt, pred, axis=0, max_slices=max_view_slices),
                    "nmse": generated_metrics["nmse"],
                    "nrmse": generated_metrics["nrmse"],
                    "snli": generated_metrics["snli"],
                    "gradient_mae": generated_metrics["gradient_mae"],
                    "lpips": "" if lpips_value is None else lpips_value,
                }
            )
        elapsed = time.perf_counter() - start
        for row in case_rows:
            row["metric_seconds_total"] = elapsed
            row["metric_seconds_per_case"] = elapsed / max(len(case_rows), 1)
        rows.extend(case_rows)
    write_csv(paths.metrics / "extended_per_case_metrics.csv", rows)

    summary_rows = []
    for method in sorted({row["method"] for row in rows}):
        selected = [row for row in rows if row["method"] == method]
        out = {"method": method, "cases": len(selected)}
        for key in ["ssim_a", "ssim_c", "ssim_s", "nmse", "nrmse", "snli", "gradient_mae"]:
            values = np.array([float(row[key]) for row in selected], dtype=np.float64)
            out[f"{key}_mean"] = float(np.nanmean(values))
            out[f"{key}_std"] = float(np.nanstd(values))
        lpips_values = [row["lpips"] for row in selected if row["lpips"] != ""]
        out["lpips_mean"] = "" if not lpips_values else float(np.mean([float(v) for v in lpips_values]))
        out["metric_seconds_per_case"] = (
            float(np.mean([float(row["metric_seconds_per_case"]) for row in selected])) if selected else 0.0
        )
        summary_rows.append(out)
    write_csv(paths.metrics / "extended_summary_metrics.csv", summary_rows)
    write_json(paths.metrics / "extended_summary_metrics.json", {"summary": summary_rows, "lpips_available": any(row["lpips"] != "" for row in rows)})
    print(f"Wrote extended metrics to {paths.metrics}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--max-view-slices", type=int, default=96)
    parser.add_argument("--max-lpips-slices", type=int, default=32)
    args = parser.parse_args()
    run(args.profile, args.max_view_slices, args.max_lpips_slices)


if __name__ == "__main__":
    main()
