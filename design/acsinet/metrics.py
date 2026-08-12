from __future__ import annotations

from pathlib import Path

import numpy as np

from ixi_diffusion.common import load_nifti, write_csv, write_json


def _safe_data_range(volume: np.ndarray) -> float:
    data_range = float(np.nanmax(volume) - np.nanmin(volume))
    return data_range if data_range > 0 else 1.0


def _edge_magnitude(volume: np.ndarray) -> np.ndarray:
    dx = np.diff(volume, axis=0, append=volume[-1:, :, :])
    dy = np.diff(volume, axis=1, append=volume[:, -1:, :])
    return np.sqrt(dx * dx + dy * dy + 1e-8).astype(np.float32)


def _adjacent_ncc(volume: np.ndarray) -> np.ndarray:
    values = []
    for idx in range(volume.shape[2] - 1):
        a = volume[:, :, idx].astype(np.float32).reshape(-1)
        b = volume[:, :, idx + 1].astype(np.float32).reshape(-1)
        if float(a.std()) > 0 and float(b.std()) > 0:
            values.append(float(np.corrcoef(a, b)[0, 1]))
        else:
            values.append(0.0)
    return np.asarray(values, dtype=np.float32)


def evaluate_volume_consistency(gt: np.ndarray, pred: np.ndarray) -> dict:
    if gt.shape != pred.shape:
        raise ValueError(f"Shape mismatch: gt={gt.shape}, pred={pred.shape}")
    data_range = _safe_data_range(gt)
    gt_z = np.diff(gt.astype(np.float32), axis=2)
    pred_z = np.diff(pred.astype(np.float32), axis=2)
    gt_lap = gt[:, :, :-2] - 2.0 * gt[:, :, 1:-1] + gt[:, :, 2:]
    pred_lap = pred[:, :, :-2] - 2.0 * pred[:, :, 1:-1] + pred[:, :, 2:]
    gt_edge_z = np.diff(_edge_magnitude(gt), axis=2)
    pred_edge_z = np.diff(_edge_magnitude(pred), axis=2)
    gt_ncc = _adjacent_ncc(gt)
    pred_ncc = _adjacent_ncc(pred)
    return {
        "zge": float(np.mean(np.abs(pred_z - gt_z)) / data_range),
        "zle": float(np.mean(np.abs(pred_lap - gt_lap)) / data_range),
        "edge_z_error": float(np.mean(np.abs(pred_edge_z - gt_edge_z)) / data_range),
        "interslice_ncc_mae": float(np.mean(np.abs(pred_ncc - gt_ncc))),
        "interslice_ncc_pred": float(np.mean(pred_ncc)),
        "interslice_ncc_gt": float(np.mean(gt_ncc)),
    }


def evaluate_consistency_method(
    gt_dir: Path,
    pred_dir: Path,
    prefix: str,
    method: str,
    case_names: set[str] | None = None,
) -> list[dict]:
    rows: list[dict] = []
    for gt_path in sorted(gt_dir.glob("*.nii.gz")):
        if case_names is not None and gt_path.name not in case_names:
            continue
        pred_path = pred_dir / f"{prefix}{gt_path.name}"
        if not pred_path.exists():
            raise FileNotFoundError(pred_path)
        gt, _, _ = load_nifti(gt_path)
        pred, _, _ = load_nifti(pred_path)
        rows.append({"method": method, "case": gt_path.name, **evaluate_volume_consistency(gt, pred)})
    return rows


def summarize_consistency(rows: list[dict]) -> list[dict]:
    metric_names = [
        "zge",
        "zle",
        "edge_z_error",
        "interslice_ncc_mae",
        "interslice_ncc_pred",
        "interslice_ncc_gt",
    ]
    summaries: list[dict] = []
    for method in sorted({row["method"] for row in rows}):
        selected = [row for row in rows if row["method"] == method]
        summary = {"method": method, "cases": len(selected)}
        for name in metric_names:
            values = np.asarray([row[name] for row in selected], dtype=np.float64)
            summary[f"{name}_mean"] = float(np.nanmean(values))
            summary[f"{name}_std"] = float(np.nanstd(values))
        summaries.append(summary)
    return summaries


def write_consistency_outputs(metrics_dir: Path, rows: list[dict]) -> None:
    summaries = summarize_consistency(rows)
    write_csv(metrics_dir / "per_case_3d_consistency.csv", rows)
    write_csv(metrics_dir / "summary_3d_consistency.csv", summaries)
    write_json(metrics_dir / "summary_3d_consistency.json", {"summary": summaries})
