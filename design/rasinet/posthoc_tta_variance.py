from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRE_ROOT = ROOT / "pre"
if PRE_ROOT.exists() and str(PRE_ROOT) not in sys.path:
    sys.path.insert(0, str(PRE_ROOT))

from fastmri_brain_swinir_2p5d.settings import build_paths as build_fastmri_paths
from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator
from ixi_diffusion.common import ensure_dir, load_nifti, save_nifti, write_csv, write_json
from ixi_swinir_2p5d.settings import build_paths as build_ixi_paths
from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator

from .metrics import _failure_detection, evaluate_reliability_volume, summarize_reliability


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _case_name_from_prediction(path: Path) -> str:
    if not path.name.startswith("diff_"):
        raise ValueError(f"Unexpected prediction file name: {path.name}")
    return path.name[len("diff_") :]


def _flip_axes(name: str) -> tuple[int, ...]:
    if name == "identity":
        return ()
    if name == "flip_x":
        return (0,)
    if name == "flip_y":
        return (1,)
    if name == "flip_xy":
        return (0, 1)
    raise ValueError(f"Unknown TTA view: {name}")


def _transform(volume: np.ndarray, view: str) -> np.ndarray:
    axes = _flip_axes(view)
    if not axes:
        return np.ascontiguousarray(volume)
    return np.ascontiguousarray(np.flip(volume, axis=axes))


def _inverse_transform(volume: np.ndarray, view: str) -> np.ndarray:
    return _transform(volume, view)


def _safe_std(volumes: list[np.ndarray]) -> np.ndarray:
    return np.std(np.stack([v.astype(np.float32) for v in volumes], axis=0), axis=0).astype(np.float32)


def _write_summary_note(path: Path, dataset_label: str, summary_rows: list[dict], failure_rows: list[dict], compare_rows: list[dict]) -> None:
    failure_by_method = {row["method"]: row for row in failure_rows}
    lines = [
        f"# {dataset_label} SwinIR TTA variance experiment",
        "",
        f"This experiment evaluates 4-view flip TTA variance as an uncertainty proxy for {dataset_label} SwinIR.",
        "",
        "| Method / proxy | Cases | Pixel Corr | Slice Corr | AURC | MAE@50% low-U | Failure AUROC | Top-k Recall |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        failure = failure_by_method.get(row["method"], {})
        lines.append(
            "| {method} | {cases} | {pixel:.4f} | {slice:.4f} | {aurc:.4f} | {mae50:.4f} | {auroc} | {recall} |".format(
                method=row["method"],
                cases=int(row["cases"]),
                pixel=float(row["pixel_error_uncertainty_corr_mean"]),
                slice=float(row["slice_error_uncertainty_corr_mean"]),
                aurc=float(row["risk_coverage_aurc_mean"]),
                mae50=float(row["retained_mae_50pct_low_uncertainty_mean"]),
                auroc=_fmt_optional(failure.get("auroc")),
                recall=_fmt_optional(failure.get("top_k_failure_recall")),
            )
        )
    if compare_rows:
        lines.extend(
            [
                "",
                "## Baseline disagreement comparison",
                "",
                "| Metric | TTA variance | Baseline disagreement | Delta |",
                "|---|---:|---:|---:|",
            ]
        )
        for row in compare_rows:
            lines.append(
                "| {metric} | {tta_value:.4f} | {baseline_value:.4f} | {delta:.4f} |".format(
                    metric=row["metric"],
                    tta_value=float(row["tta_value"]),
                    baseline_value=float(row["baseline_value"]),
                    delta=float(row["delta"]),
                )
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt_optional(value: object) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not np.isfinite(number):
        return ""
    return f"{number:.4f}"


def _compare_with_baseline(summary_rows: list[dict], failure_rows: list[dict], baseline_profile: str) -> list[dict]:
    baseline_path = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / baseline_profile / "metrics" / "summary_posthoc_reliability.csv"
    baseline_failure_path = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / baseline_profile / "metrics" / "failure_detection_posthoc.csv"
    if not baseline_path.exists():
        return []
    baseline_rows = _read_csv(baseline_path)
    selected_baseline = next((row for row in baseline_rows if row.get("method") == "swinir__baseline_disagreement"), None)
    if selected_baseline is None:
        return []
    baseline_failure = {}
    if baseline_failure_path.exists():
        baseline_failure = next((row for row in _read_csv(baseline_failure_path) if row.get("method") == "swinir__baseline_disagreement"), {})
    tta_row = next((row for row in summary_rows if row.get("method") == "swinir_tta_mean__tta_variance"), None)
    tta_failure = next((row for row in failure_rows if row.get("method") == "swinir_tta_mean__tta_variance"), {})
    if tta_row is None:
        return []
    pairs = [
        ("pixel_error_uncertainty_corr_mean", "pixel_corr"),
        ("slice_error_uncertainty_corr_mean", "slice_corr"),
        ("risk_coverage_aurc_mean", "risk_coverage_aurc"),
        ("retained_mae_50pct_low_uncertainty_mean", "mae_50pct_low_u"),
    ]
    rows = []
    for source_key, metric in pairs:
        tta_value = float(tta_row[source_key])
        baseline_value = float(selected_baseline[source_key])
        rows.append({"metric": metric, "tta_value": tta_value, "baseline_value": baseline_value, "delta": tta_value - baseline_value})
    if baseline_failure and tta_failure:
        for key, metric in [("auroc", "failure_auroc"), ("top_k_failure_recall", "top_k_failure_recall")]:
            if tta_failure.get(key) in ("", None) or baseline_failure.get(key) in ("", None):
                continue
            tta_value = float(tta_failure[key])
            baseline_value = float(baseline_failure[key])
            rows.append({"metric": metric, "tta_value": tta_value, "baseline_value": baseline_value, "delta": tta_value - baseline_value})
    return rows


def run_fastmri_swinir_tta(
    dataset: str,
    checkpoint: Path | None,
    output_profile: str,
    max_cases: int | None,
    views: tuple[str, ...],
    stride: int,
    progress_every: int,
    save_maps: bool,
) -> Path:
    started = time.time()
    fold_interpolators = {}
    if dataset == "fastmri":
        if checkpoint is None:
            raise ValueError("fastmri requires a checkpoint")
        source_paths = build_fastmri_paths("full")
        baseline_profile = "fastmri_full"
        dataset_label = "fastMRI-brain T2"
        source_profile = "fastmri_brain_swinir_2p5d/full"
        interpolator = FastMRISwinIR2p5DInterpolator(checkpoint)
        case_entries = [
            {
                "case_name": path.name,
                "sparse_path": path,
                "gt_path": source_paths.eval_gt / path.name,
                "original_pred_path": source_paths.model_outputs / f"diff_{path.name}",
                "checkpoint": checkpoint,
            }
            for path in sorted(source_paths.eval_sparse.glob("*.nii.gz"))
        ]
    elif dataset == "ixi":
        if checkpoint is None:
            raise ValueError("ixi requires a checkpoint")
        source_paths = build_ixi_paths("full_test115")
        baseline_profile = "full_test115"
        dataset_label = "IXI T2 full_test115"
        source_profile = "ixi_swinir_2p5d/full_test115"
        interpolator = SwinIR2p5DInterpolator(checkpoint)
        case_entries = [
            {
                "case_name": path.name,
                "sparse_path": path,
                "gt_path": source_paths.eval_gt / path.name,
                "original_pred_path": source_paths.model_outputs / f"diff_{path.name}",
                "checkpoint": checkpoint,
            }
            for path in sorted(source_paths.eval_sparse.glob("*.nii.gz"))
        ]
    elif dataset == "ningxia":
        baseline_profile = "ningxia_cv"
        dataset_label = "NingXia T2 CV"
        source_profile = "ningxia_t2_swinir_2p5d_cv/fold_*/full"
        interpolator = None
        case_entries = []
        for fold_dir in sorted((ROOT / "ningxia_t2_swinir_2p5d_cv" / "runs").glob("fold_*")):
            run_dir = fold_dir / "full"
            fold_checkpoint = run_dir / "checkpoints" / "swinir_epoch_best.pth"
            for path in sorted((run_dir / "eval_sparse").glob("*.nii.gz")):
                case_entries.append(
                    {
                        "case_name": path.name,
                        "sparse_path": path,
                        "gt_path": run_dir / "eval_gt" / path.name,
                        "original_pred_path": run_dir / "model_outputs" / f"diff_{path.name}",
                        "checkpoint": fold_checkpoint,
                    }
                )
    else:
        raise ValueError(f"Unsupported dataset: {dataset}")
    if max_cases is not None:
        case_entries = case_entries[:max_cases]
    if not case_entries:
        raise FileNotFoundError(f"No cases found for dataset={dataset}")
    missing_checkpoints = sorted({str(entry["checkpoint"]) for entry in case_entries if not Path(entry["checkpoint"]).exists()})
    if missing_checkpoints:
        raise FileNotFoundError(missing_checkpoints[0])
    if checkpoint is not None and not checkpoint.exists():
        raise FileNotFoundError(checkpoint)

    run_dir = ensure_dir(ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / output_profile)
    metrics_dir = ensure_dir(run_dir / "metrics")
    maps_dir = ensure_dir(run_dir / "tta_maps")
    report_dir = ensure_dir(ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / output_profile)

    rows: list[dict] = []
    risk_rows: list[dict] = []
    calibration_rows: list[dict] = []
    runtime_rows: list[dict] = []

    print(
        f"[tta] dataset={dataset} profile={output_profile} cases={len(case_entries)} views={','.join(views)} checkpoint={checkpoint or 'fold-specific'}",
        flush=True,
    )
    for index, entry in enumerate(case_entries, start=1):
        case_started = time.time()
        sparse_path = Path(entry["sparse_path"])
        gt_path = Path(entry["gt_path"])
        original_pred_path = Path(entry["original_pred_path"])
        case_checkpoint = Path(entry["checkpoint"])
        case_name = str(entry["case_name"])
        if progress_every > 0 and (index == 1 or index % progress_every == 0):
            print(f"[tta] case {index}/{len(case_entries)} {case_name}", flush=True)
        if dataset == "ningxia":
            if case_checkpoint not in fold_interpolators:
                fold_interpolators[case_checkpoint] = SwinIR2p5DInterpolator(case_checkpoint)
            case_interpolator = fold_interpolators[case_checkpoint]
        else:
            case_interpolator = interpolator
        sparse, affine, header = load_nifti(sparse_path)
        gt, _, _ = load_nifti(gt_path)
        original_pred, _, _ = load_nifti(original_pred_path)

        preds = []
        for view in views:
            transformed = _transform(sparse, view)
            pred = case_interpolator.interpolate_volume(transformed, stride=stride)
            preds.append(_inverse_transform(pred, view))
        mean_pred = np.mean(np.stack(preds, axis=0), axis=0).astype(np.float32)
        uncertainty = _safe_std(preds)

        for method_name, pred in [
            ("swinir_tta_mean__tta_variance", mean_pred),
            ("swinir_original__tta_variance", original_pred),
        ]:
            metrics, case_risk, case_calibration = evaluate_reliability_volume(gt, pred, uncertainty, stride)
            rows.append({"method": method_name, "case": case_name, "proxy": "tta_variance", **metrics})
            for risk in case_risk:
                risk_rows.append({"method": method_name, "case": case_name, "proxy": "tta_variance", **risk})
            for calibration in case_calibration:
                calibration_rows.append({"method": method_name, "case": case_name, "proxy": "tta_variance", **calibration})

        if save_maps:
            save_nifti(mean_pred, affine, header, maps_dir / f"tta_mean_{case_name}")
            save_nifti(uncertainty, affine, header, maps_dir / f"tta_std_{case_name}")
        runtime_rows.append(
            {
                "case": case_name,
                "views": len(views),
                "seconds": time.time() - case_started,
                "generated_slices": int((sparse.shape[2] - 1) * (stride - 1)),
            }
        )

    failure_rows = []
    for method in sorted({row["method"] for row in rows}):
        selected = [row for row in rows if row["method"] == method]
        failure_rows.append({"method": method, **_failure_detection(selected)})
    summary_rows = summarize_reliability(rows)
    compare_rows = _compare_with_baseline(summary_rows, failure_rows, baseline_profile)

    write_csv(metrics_dir / "per_case_tta_reliability.csv", rows)
    write_csv(metrics_dir / "summary_tta_reliability.csv", summary_rows)
    write_csv(metrics_dir / "risk_coverage_tta.csv", risk_rows)
    write_csv(metrics_dir / "calibration_bins_tta.csv", calibration_rows)
    write_csv(metrics_dir / "failure_detection_tta.csv", failure_rows)
    write_csv(metrics_dir / "runtime_tta.csv", runtime_rows)
    write_csv(metrics_dir / "comparison_tta_vs_baseline_disagreement.csv", compare_rows)
    write_json(
        metrics_dir / "summary_tta_reliability.json",
        {
            "output_profile": output_profile,
            "dataset": dataset,
            "source_profile": source_profile,
            "cases": [str(entry["case_name"]) for entry in case_entries],
            "checkpoint": str(checkpoint or "fold-specific"),
            "views": views,
            "stride": stride,
            "summary": summary_rows,
            "failure_detection": failure_rows,
            "elapsed_seconds": time.time() - started,
        },
    )
    _write_summary_note(report_dir / "tta_variance_summary.md", dataset_label, summary_rows, failure_rows, compare_rows)
    print(f"[tta] done rows={len(rows)} elapsed={time.time() - started:.1f}s output={metrics_dir}", flush=True)
    return metrics_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TTA variance post-hoc reliability experiments.")
    parser.add_argument("--dataset", choices=("fastmri", "ixi", "ningxia"), default="fastmri")
    parser.add_argument("--output-profile", default=None)
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
    )
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument("--stride", type=int, default=4)
    parser.add_argument("--views", default="identity,flip_x,flip_y,flip_xy")
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--no-save-maps", action="store_true")
    args = parser.parse_args()
    views = tuple(view.strip() for view in args.views.split(",") if view.strip())
    default_checkpoints = {
        "fastmri": ROOT / "fastmri_brain_swinir_2p5d" / "runs" / "full" / "checkpoints" / "swinir_epoch_best.pth",
        "ixi": ROOT / "ixi_swinir_2p5d" / "runs" / "full" / "checkpoints" / "swinir_epoch_best.pth",
        "ningxia": None,
    }
    default_profiles = {
        "fastmri": "fastmri_swinir_tta",
        "ixi": "ixi_swinir_tta",
        "ningxia": "ningxia_swinir_tta",
    }
    run_fastmri_swinir_tta(
        dataset=args.dataset,
        checkpoint=args.checkpoint or default_checkpoints[args.dataset],
        output_profile=args.output_profile or default_profiles[args.dataset],
        max_cases=args.max_cases,
        views=views,
        stride=args.stride,
        progress_every=args.progress_every,
        save_maps=not args.no_save_maps,
    )


if __name__ == "__main__":
    main()
