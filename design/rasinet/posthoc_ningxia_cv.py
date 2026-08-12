from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ixi_diffusion.common import ensure_dir, load_nifti, write_csv, write_json

from .metrics import _failure_detection, evaluate_reliability_volume, summarize_reliability
from .posthoc_qc import _safe_corr


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FoldSource:
    name: str
    root: Path

    def run_dir(self, fold: str) -> Path:
        return self.root / "runs" / fold / "full"

    def pred_dir(self, fold: str) -> Path:
        return self.run_dir(fold) / "model_outputs"


SOURCES = (
    FoldSource("i3net", ROOT / "ningxia_t2_i3net_cv"),
    FoldSource("hat", ROOT / "ningxia_t2_hat_2p5d_cv"),
    FoldSource("swinir", ROOT / "ningxia_t2_swinir_2p5d_cv"),
)


def _fold_names() -> list[str]:
    run_root = SOURCES[0].root / "runs"
    return [path.name for path in sorted(run_root.glob("fold_*")) if path.is_dir()]


def _case_name_from_prediction(path: Path) -> str:
    name = path.name
    if not name.startswith("diff_"):
        raise ValueError(f"Unexpected prediction file name: {name}")
    return name[len("diff_") :]


def _case_names(fold: str) -> list[str]:
    return [_case_name_from_prediction(path) for path in sorted(SOURCES[0].pred_dir(fold).glob("diff_*.nii.gz"))]


def _gt_path(fold: str, case_name: str) -> Path:
    return SOURCES[0].run_dir(fold) / "eval_gt" / case_name


def _baseline_path(fold: str, baseline: str, case_name: str) -> Path:
    return SOURCES[0].run_dir(fold) / "baseline_outputs" / baseline / f"{baseline}_{case_name}"


def _pred_path(source: FoldSource, fold: str, case_name: str) -> Path:
    return source.pred_dir(fold) / f"diff_{case_name}"


def _generated_indices(depth: int, factor: int) -> list[int]:
    return [idx for idx in range(depth) if idx % factor != 0]


def _safe_std(volumes: list[np.ndarray]) -> np.ndarray:
    return np.std(np.stack([volume.astype(np.float32) for volume in volumes], axis=0), axis=0).astype(np.float32)


def _proxy_arrays(pred: np.ndarray, linear: np.ndarray, cubic: np.ndarray, disagreement: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "residual_linear": np.abs(pred.astype(np.float32) - linear.astype(np.float32)),
        "residual_cubic": np.abs(pred.astype(np.float32) - cubic.astype(np.float32)),
        "baseline_disagreement": disagreement,
    }


def run_ningxia_cv(factor: int, progress_every: int) -> Path:
    started = time.time()
    profile = "ningxia_cv"
    metrics_dir = ensure_dir(ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / profile / "metrics")
    report_dir = ensure_dir(ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / profile)
    rows: list[dict] = []
    risk_rows: list[dict] = []
    calibration_rows: list[dict] = []
    manifest_rows: list[dict] = []
    mask_rows: list[dict] = []
    inventory_rows: list[dict] = []

    folds = _fold_names()
    total_cases = sum(len(_case_names(fold)) for fold in folds)
    print(f"[ningxia-cv] folds={len(folds)} cases={total_cases}", flush=True)
    completed = 0
    for fold in folds:
        cases = _case_names(fold)
        for source in SOURCES:
            available = sum(1 for case_name in cases if _pred_path(source, fold, case_name).exists())
            inventory_rows.append(
                {
                    "fold": fold,
                    "method": source.name,
                    "run_dir": str(source.run_dir(fold)),
                    "available_cases_in_fold": available,
                    "requested_cases": len(cases),
                }
            )
        for case_name in cases:
            completed += 1
            if progress_every > 0 and (completed == 1 or completed % progress_every == 0):
                print(f"[ningxia-cv] case {completed}/{total_cases} {fold}/{case_name} elapsed={time.time() - started:.1f}s", flush=True)
            gt_path = _gt_path(fold, case_name)
            linear_path = _baseline_path(fold, "linear", case_name)
            cubic_path = _baseline_path(fold, "cubic", case_name)
            gt, _, _ = load_nifti(gt_path)
            linear, _, _ = load_nifti(linear_path)
            cubic, _, _ = load_nifti(cubic_path)
            predictions: dict[str, np.ndarray] = {}
            for source in SOURCES:
                pred, _, _ = load_nifti(_pred_path(source, fold, case_name))
                predictions[source.name] = pred
            disagreement = _safe_std([linear, cubic, *predictions.values()])
            indices = _generated_indices(gt.shape[2], factor)
            gt_eval = gt[:, :, indices].astype(np.float32)
            data_max = float(np.nanmax(np.abs(gt_eval))) if np.any(np.isfinite(gt_eval)) else 0.0
            threshold = max(1e-6, 0.01 * data_max)
            nonzero_mask = np.abs(gt_eval) > threshold
            case_key = f"{fold}/{case_name}"
            manifest_rows.append(
                {
                    "fold": fold,
                    "case": case_name,
                    "case_key": case_key,
                    "gt_path": str(gt_path),
                    "linear_path": str(linear_path),
                    "cubic_path": str(cubic_path),
                    "generated_slices_expected": len(indices),
                    "shape": str(tuple(gt.shape)),
                    "nonzero_fraction": float(np.mean(nonzero_mask)),
                }
            )
            for method, pred in predictions.items():
                error = np.abs(pred[:, :, indices].astype(np.float32) - gt_eval)
                for proxy_name, uncertainty_full in _proxy_arrays(pred, linear, cubic, disagreement).items():
                    method_name = f"{method}__{proxy_name}"
                    metrics, case_risk, case_calibration = evaluate_reliability_volume(gt, pred, uncertainty_full, factor)
                    rows.append({"method": method_name, "case": case_key, "fold": fold, "proxy": proxy_name, **metrics})
                    uncertainty = uncertainty_full[:, :, indices].astype(np.float32)
                    all_corr = _safe_corr(error, uncertainty)
                    nonzero_corr = _safe_corr(error[nonzero_mask], uncertainty[nonzero_mask]) if np.any(nonzero_mask) else float("nan")
                    background_corr = _safe_corr(error[~nonzero_mask], uncertainty[~nonzero_mask]) if np.any(~nonzero_mask) else float("nan")
                    mask_rows.append(
                        {
                            "profile": profile,
                            "method": method_name,
                            "case": case_key,
                            "proxy": proxy_name,
                            "mask_threshold": threshold,
                            "nonzero_fraction": float(np.mean(nonzero_mask)),
                            "background_fraction": float(1.0 - np.mean(nonzero_mask)),
                            "pixel_corr_all": all_corr,
                            "pixel_corr_nonzero": nonzero_corr,
                            "pixel_corr_background": background_corr,
                            "corr_drop_nonzero_minus_all": nonzero_corr - all_corr if np.isfinite(nonzero_corr) and np.isfinite(all_corr) else float("nan"),
                        }
                    )
                    for risk in case_risk:
                        risk_rows.append({"method": method_name, "case": case_key, "fold": fold, "proxy": proxy_name, **risk})
                    for calibration in case_calibration:
                        calibration_rows.append({"method": method_name, "case": case_key, "fold": fold, "proxy": proxy_name, **calibration})

    failure_rows = []
    for method in sorted({row["method"] for row in rows}):
        selected = [row for row in rows if row["method"] == method]
        failure_rows.append({"method": method, **_failure_detection(selected)})

    summary_rows = summarize_reliability(rows)
    write_csv(metrics_dir / "method_inventory.csv", inventory_rows)
    write_csv(metrics_dir / "per_case_posthoc_reliability.csv", rows)
    write_csv(metrics_dir / "summary_posthoc_reliability.csv", summary_rows)
    write_csv(metrics_dir / "risk_coverage_posthoc.csv", risk_rows)
    write_csv(metrics_dir / "calibration_bins_posthoc.csv", calibration_rows)
    write_csv(metrics_dir / "failure_detection_posthoc.csv", failure_rows)
    write_json(metrics_dir / "summary_posthoc_reliability.json", {"profile": profile, "summary": summary_rows, "failure_detection": failure_rows})

    grouped: dict[str, list[dict]] = {}
    for row in mask_rows:
        grouped.setdefault(row["method"], []).append(row)
    mask_summary = []
    for method, selected in sorted(grouped.items()):
        for key in [
            "nonzero_fraction",
            "background_fraction",
            "pixel_corr_all",
            "pixel_corr_nonzero",
            "pixel_corr_background",
            "corr_drop_nonzero_minus_all",
        ]:
            values = np.asarray([float(row[key]) for row in selected], dtype=np.float64)
            values = values[np.isfinite(values)]
            mask_summary.append(
                {
                    "method": method,
                    "metric": key,
                    "cases": len(selected),
                    "mean": float(np.mean(values)) if values.size else float("nan"),
                    "std": float(np.std(values)) if values.size else float("nan"),
                }
            )
    write_csv(report_dir / "qc_manifest.csv", manifest_rows)
    write_csv(report_dir / "qc_mask_background_per_case.csv", mask_rows)
    write_csv(report_dir / "qc_mask_background_summary.csv", mask_summary)
    print(f"[ningxia-cv] done rows={len(rows)} output={metrics_dir}", flush=True)
    return metrics_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-hoc RASI uncertainty analysis for NingXia 8-fold CV outputs.")
    parser.add_argument("--factor", type=int, default=4)
    parser.add_argument("--progress-every", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_ningxia_cv(factor=args.factor, progress_every=args.progress_every)


if __name__ == "__main__":
    main()
