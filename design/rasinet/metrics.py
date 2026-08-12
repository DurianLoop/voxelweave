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


def _generated_indices(depth: int, factor: int) -> list[int]:
    return [idx for idx in range(depth) if idx % factor != 0]


def _safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    b = np.asarray(b, dtype=np.float64).reshape(-1)
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 2:
        return float("nan")
    a = a[mask]
    b = b[mask]
    if float(np.std(a)) <= 1e-12 or float(np.std(b)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _edge_mask(volume: np.ndarray) -> np.ndarray:
    dx = np.diff(volume, axis=0, append=volume[-1:, :, :])
    dy = np.diff(volume, axis=1, append=volume[:, -1:, :])
    mag = np.sqrt(dx * dx + dy * dy)
    threshold = float(np.percentile(mag[np.isfinite(mag)], 75)) if np.any(np.isfinite(mag)) else 0.0
    return mag >= threshold


def _risk_coverage(error: np.ndarray, uncertainty: np.ndarray, bins: int = 10) -> tuple[list[dict], float]:
    error = np.asarray(error, dtype=np.float64).reshape(-1)
    uncertainty = np.asarray(uncertainty, dtype=np.float64).reshape(-1)
    mask = np.isfinite(error) & np.isfinite(uncertainty)
    error = error[mask]
    uncertainty = uncertainty[mask]
    if error.size == 0:
        return [], float("nan")
    order = np.argsort(uncertainty)
    sorted_error = error[order]
    rows = []
    coverages = np.linspace(1.0, 0.1, bins)
    risks = []
    for coverage in coverages:
        keep = max(1, int(round(error.size * float(coverage))))
        retained = sorted_error[:keep]
        risk = float(np.mean(retained))
        rows.append({"coverage": float(coverage), "retained_mae": risk, "retained_pixels": int(keep)})
        risks.append(risk)
    risk_values = np.asarray(risks, dtype=np.float64)
    if hasattr(np, "trapezoid"):
        aurc = float(np.trapezoid(risk_values, coverages))
    else:
        aurc = float(np.trapz(risk_values, coverages))
    return rows, abs(aurc)


def _calibration_bins(error: np.ndarray, uncertainty: np.ndarray, bins: int = 10) -> list[dict]:
    error = np.asarray(error, dtype=np.float64).reshape(-1)
    uncertainty = np.asarray(uncertainty, dtype=np.float64).reshape(-1)
    mask = np.isfinite(error) & np.isfinite(uncertainty)
    error = error[mask]
    uncertainty = uncertainty[mask]
    if error.size == 0:
        return []
    edges = np.quantile(uncertainty, np.linspace(0.0, 1.0, bins + 1))
    rows = []
    for idx in range(bins):
        lo = edges[idx]
        hi = edges[idx + 1]
        if idx == bins - 1:
            selected = (uncertainty >= lo) & (uncertainty <= hi)
        else:
            selected = (uncertainty >= lo) & (uncertainty < hi)
        if not np.any(selected):
            continue
        rows.append(
            {
                "bin": idx,
                "uncertainty_min": float(lo),
                "uncertainty_max": float(hi),
                "pixels": int(selected.sum()),
                "mean_uncertainty": float(np.mean(uncertainty[selected])),
                "mean_abs_error": float(np.mean(error[selected])),
            }
        )
    return rows


def _binary_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=np.int32)
    scores = np.asarray(scores, dtype=np.float64)
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    wins = 0.0
    for value in pos:
        wins += float(np.sum(value > neg)) + 0.5 * float(np.sum(value == neg))
    return float(wins / (pos.size * neg.size))


def _average_precision(labels: np.ndarray, scores: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=np.int32)
    scores = np.asarray(scores, dtype=np.float64)
    positives = int(labels.sum())
    if positives == 0:
        return float("nan")
    order = np.argsort(-scores)
    sorted_labels = labels[order]
    tp = np.cumsum(sorted_labels)
    precision = tp / (np.arange(labels.size) + 1)
    return float(np.sum(precision * sorted_labels) / positives)


def _failure_detection(rows: list[dict]) -> dict:
    if not rows:
        return {}
    maes = np.asarray([row["mean_abs_error"] for row in rows], dtype=np.float64)
    scores = np.asarray([row["mean_uncertainty"] for row in rows], dtype=np.float64)
    k = max(1, int(np.ceil(0.1 * len(rows))))
    worst = np.argsort(-maes)[:k]
    labels = np.zeros(len(rows), dtype=np.int32)
    labels[worst] = 1
    top_score = np.argsort(-scores)[:k]
    auroc = _binary_auc(labels, scores)
    auprc = _average_precision(labels, scores)
    return {
        "cases": len(rows),
        "failure_cases": int(k),
        "auroc": None if not np.isfinite(auroc) else auroc,
        "auprc": None if not np.isfinite(auprc) else auprc,
        "top_k_failure_recall": float(labels[top_score].sum() / max(k, 1)),
    }


def evaluate_reliability_volume(gt: np.ndarray, pred: np.ndarray, uncertainty: np.ndarray, factor: int) -> tuple[dict, list[dict], list[dict]]:
    if gt.shape != pred.shape or gt.shape != uncertainty.shape:
        raise ValueError(f"Shape mismatch: gt={gt.shape}, pred={pred.shape}, uncertainty={uncertainty.shape}")
    indices = _generated_indices(gt.shape[2], factor)
    if not indices:
        raise ValueError("No generated slices found for reliability evaluation.")
    error = np.abs(pred[:, :, indices].astype(np.float32) - gt[:, :, indices].astype(np.float32))
    unc = uncertainty[:, :, indices].astype(np.float32)
    edges = _edge_mask(gt[:, :, indices].astype(np.float32))
    slice_error = error.mean(axis=(0, 1))
    slice_unc = unc.mean(axis=(0, 1))
    risk_rows, aurc = _risk_coverage(error, unc)
    cal_rows = _calibration_bins(error, unc)
    non_edges = ~edges
    metrics = {
        "generated_slices": len(indices),
        "mean_abs_error": float(np.mean(error)),
        "mean_uncertainty": float(np.mean(unc)),
        "std_uncertainty": float(np.std(unc)),
        "pixel_error_uncertainty_corr": _safe_corr(error, unc),
        "slice_error_uncertainty_corr": _safe_corr(slice_error, slice_unc),
        "edge_error_uncertainty_corr": _safe_corr(error[edges], unc[edges]) if np.any(edges) else float("nan"),
        "nonedge_error_uncertainty_corr": _safe_corr(error[non_edges], unc[non_edges]) if np.any(non_edges) else float("nan"),
        "risk_coverage_aurc": aurc,
        "retained_mae_50pct_low_uncertainty": next(
            (row["retained_mae"] for row in risk_rows if abs(row["coverage"] - 0.5) < 1e-6),
            float("nan"),
        ),
    }
    return metrics, risk_rows, cal_rows


def evaluate_reliability_method(
    gt_dir: Path,
    pred_dir: Path,
    uncertainty_dir: Path,
    pred_prefix: str,
    uncertainty_prefix: str,
    method: str,
    factor: int = 4,
    case_names: set[str] | None = None,
) -> tuple[list[dict], list[dict], list[dict], dict]:
    rows: list[dict] = []
    risk_rows: list[dict] = []
    cal_rows: list[dict] = []
    for gt_path in sorted(gt_dir.glob("*.nii.gz")):
        if case_names is not None and gt_path.name not in case_names:
            continue
        pred_path = pred_dir / f"{pred_prefix}{gt_path.name}"
        unc_path = uncertainty_dir / f"{uncertainty_prefix}{gt_path.name}"
        if not pred_path.exists():
            raise FileNotFoundError(pred_path)
        if not unc_path.exists():
            raise FileNotFoundError(unc_path)
        gt, _, _ = load_nifti(gt_path)
        pred, _, _ = load_nifti(pred_path)
        uncertainty, _, _ = load_nifti(unc_path)
        metrics, case_risk, case_cal = evaluate_reliability_volume(gt, pred, uncertainty, factor)
        rows.append({"method": method, "case": gt_path.name, **metrics})
        for row in case_risk:
            risk_rows.append({"method": method, "case": gt_path.name, **row})
        for row in case_cal:
            cal_rows.append({"method": method, "case": gt_path.name, **row})
    return rows, risk_rows, cal_rows, _failure_detection(rows)


def summarize_reliability(rows: list[dict]) -> list[dict]:
    metric_names = [
        "mean_abs_error",
        "mean_uncertainty",
        "std_uncertainty",
        "pixel_error_uncertainty_corr",
        "slice_error_uncertainty_corr",
        "edge_error_uncertainty_corr",
        "nonedge_error_uncertainty_corr",
        "risk_coverage_aurc",
        "retained_mae_50pct_low_uncertainty",
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


def write_reliability_outputs(
    metrics_dir: Path,
    rows: list[dict],
    risk_rows: list[dict],
    calibration_rows: list[dict],
    failure_detection: dict,
) -> None:
    summaries = summarize_reliability(rows)
    write_csv(metrics_dir / "per_case_reliability.csv", rows)
    write_csv(metrics_dir / "summary_reliability.csv", summaries)
    write_csv(metrics_dir / "risk_coverage.csv", risk_rows)
    write_csv(metrics_dir / "calibration_bins.csv", calibration_rows)
    write_json(
        metrics_dir / "summary_reliability.json",
        {"summary": summaries, "failure_detection": failure_detection},
    )
