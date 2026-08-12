from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ixi_diffusion.common import ensure_dir, load_nifti, write_csv, write_json

from .metrics import (
    _failure_detection,
    evaluate_reliability_volume,
    summarize_reliability,
)


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class MethodSource:
    name: str
    run_dir: Path
    pred_prefix: str = "diff_"
    gt_parts: tuple[str, ...] = ("eval_inputs", "gt")

    @property
    def pred_dir(self) -> Path:
        return self.run_dir / "model_outputs"


IXI_SOURCES = (
    MethodSource("i3net", ROOT / "ixi_i3net" / "runs" / "full_test115_stable"),
    MethodSource("hat", ROOT / "ixi_hat_2p5d" / "runs" / "full_test115"),
    MethodSource("swinir", ROOT / "ixi_swinir_2p5d" / "runs" / "full_test115"),
    MethodSource("acsinet", ROOT / "acsinet" / "runs" / "full_test115"),
)

FASTMRI_SOURCES = (
    MethodSource("i3net", ROOT / "fastmri_brain_i3net" / "runs" / "full", gt_parts=("eval_gt",)),
    MethodSource("hat", ROOT / "fastmri_brain_hat_2p5d" / "runs" / "full", gt_parts=("eval_gt",)),
    MethodSource("swinir", ROOT / "fastmri_brain_swinir_2p5d" / "runs" / "full", gt_parts=("eval_gt",)),
)

SOURCE_SETS = {
    "ixi": IXI_SOURCES,
    "fastmri": FASTMRI_SOURCES,
}


PROFILE_CASE_LIMITS = {
    "smoke": 1,
    "mini": 5,
    "full_test115": None,
    "fastmri_full": None,
}


def _case_name_from_prediction(path: Path, prefix: str) -> str:
    name = path.name
    if not name.startswith(prefix):
        raise ValueError(f"Unexpected prediction file name for prefix {prefix!r}: {name}")
    return name[len(prefix) :]


def _available_cases(reference: MethodSource, max_cases: int | None) -> list[str]:
    cases = [
        _case_name_from_prediction(path, reference.pred_prefix)
        for path in sorted(reference.pred_dir.glob(f"{reference.pred_prefix}*.nii.gz"))
    ]
    return cases[:max_cases] if max_cases is not None else cases


def _existing_sources(sources: tuple[MethodSource, ...]) -> tuple[MethodSource, ...]:
    return tuple(source for source in sources if source.pred_dir.exists())


def _prediction_path(source: MethodSource, case_name: str) -> Path:
    return source.pred_dir / f"{source.pred_prefix}{case_name}"


def _baseline_path(reference: MethodSource, baseline: str, case_name: str) -> Path:
    return reference.run_dir / "baseline_outputs" / baseline / f"{baseline}_{case_name}"


def _gt_path(reference: MethodSource, case_name: str) -> Path:
    return reference.run_dir.joinpath(*reference.gt_parts) / case_name


def _safe_std(volumes: list[np.ndarray]) -> np.ndarray:
    stacked = np.stack([volume.astype(np.float32) for volume in volumes], axis=0)
    return np.std(stacked, axis=0).astype(np.float32)


def _method_inventory(sources: tuple[MethodSource, ...], cases: list[str]) -> list[dict]:
    rows = []
    for source in sources:
        available = sum(1 for case_name in cases if _prediction_path(source, case_name).exists())
        rows.append(
            {
                "method": source.name,
                "run_dir": str(source.run_dir),
                "available_cases_in_profile": available,
                "requested_cases": len(cases),
            }
        )
    return rows


def _write_markdown_table(path: Path, summary_rows: list[dict], failure_rows: list[dict]) -> None:
    ensure_dir(path.parent)
    failure_by_method = {row["method"]: row for row in failure_rows}
    lines = [
        "# RASI Post-hoc Uncertainty Summary",
        "",
        "This table uses existing predictions only. No RASI-Net training is involved.",
        "",
        "| Method / proxy | Cases | Pixel Err-U Corr | Slice Err-U Corr | AURC | MAE@50% low-U | Failure AUROC | Top-k Recall |",
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
                auroc=_format_optional(failure.get("auroc")),
                recall=_format_optional(failure.get("top_k_failure_recall")),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_optional(value: object) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not np.isfinite(number):
        return ""
    return f"{number:.4f}"


def evaluate_posthoc(
    profile: str,
    source_set: str,
    factor: int,
    target_methods: set[str] | None,
    max_cases: int | None,
    progress_every: int,
) -> Path:
    started_at = time.time()
    sources = _existing_sources(SOURCE_SETS[source_set])
    if not sources:
        raise FileNotFoundError("No default method output directories were found.")
    reference = sources[0]
    if max_cases is None:
        max_cases = PROFILE_CASE_LIMITS.get(profile)
    cases = _available_cases(reference, max_cases)
    selected_sources = tuple(source for source in sources if target_methods is None or source.name in target_methods)
    if not selected_sources:
        raise ValueError(f"No target methods matched: {sorted(target_methods or [])}")

    out_dir = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / profile
    metrics_dir = ensure_dir(out_dir / "metrics")
    rows: list[dict] = []
    risk_rows: list[dict] = []
    calibration_rows: list[dict] = []

    print(
        f"[posthoc] profile={profile} cases={len(cases)} "
        f"source_set={source_set} "
        f"methods={','.join(source.name for source in selected_sources)} "
        f"available_sources={','.join(source.name for source in sources)}",
        flush=True,
    )

    completed_cases = 0
    skipped_cases = 0
    for index, case_name in enumerate(cases, start=1):
        if progress_every > 0 and (index == 1 or index % progress_every == 0):
            elapsed = time.time() - started_at
            print(f"[posthoc] case {index}/{len(cases)} {case_name} elapsed={elapsed:.1f}s", flush=True)
        gt_path = _gt_path(reference, case_name)
        linear_path = _baseline_path(reference, "linear", case_name)
        cubic_path = _baseline_path(reference, "cubic", case_name)
        if not gt_path.exists() or not linear_path.exists() or not cubic_path.exists():
            skipped_cases += 1
            print(f"[posthoc] skip missing gt/linear/cubic: {case_name}", flush=True)
            continue
        gt, _, _ = load_nifti(gt_path)
        linear, _, _ = load_nifti(linear_path)
        cubic, _, _ = load_nifti(cubic_path)

        available_predictions: dict[str, np.ndarray] = {}
        for source in sources:
            pred_path = _prediction_path(source, case_name)
            if pred_path.exists():
                pred, _, _ = load_nifti(pred_path)
                if pred.shape == gt.shape:
                    available_predictions[source.name] = pred
        disagreement = _safe_std([linear, cubic, *available_predictions.values()])

        for source in selected_sources:
            pred = available_predictions.get(source.name)
            if pred is None:
                continue
            proxies = {
                "residual_linear": np.abs(pred.astype(np.float32) - linear.astype(np.float32)),
                "residual_cubic": np.abs(pred.astype(np.float32) - cubic.astype(np.float32)),
                "baseline_disagreement": disagreement,
            }
            for proxy_name, uncertainty in proxies.items():
                method_name = f"{source.name}__{proxy_name}"
                metrics, case_risk, case_calibration = evaluate_reliability_volume(gt, pred, uncertainty, factor)
                rows.append({"method": method_name, "case": case_name, "proxy": proxy_name, **metrics})
                for risk in case_risk:
                    risk_rows.append({"method": method_name, "case": case_name, "proxy": proxy_name, **risk})
                for calibration in case_calibration:
                    calibration_rows.append({"method": method_name, "case": case_name, "proxy": proxy_name, **calibration})
        completed_cases += 1

    failure_rows = []
    for method in sorted({row["method"] for row in rows}):
        selected = [row for row in rows if row["method"] == method]
        failure_rows.append({"method": method, **_failure_detection(selected)})

    summary_rows = summarize_reliability(rows)
    write_csv(metrics_dir / "method_inventory.csv", _method_inventory(sources, cases))
    write_csv(metrics_dir / "per_case_posthoc_reliability.csv", rows)
    write_csv(metrics_dir / "summary_posthoc_reliability.csv", summary_rows)
    write_csv(metrics_dir / "risk_coverage_posthoc.csv", risk_rows)
    write_csv(metrics_dir / "calibration_bins_posthoc.csv", calibration_rows)
    write_csv(metrics_dir / "failure_detection_posthoc.csv", failure_rows)
    write_json(
        metrics_dir / "summary_posthoc_reliability.json",
        {
            "profile": profile,
            "cases": cases,
            "factor": factor,
            "summary": summary_rows,
            "failure_detection": failure_rows,
        },
    )
    _write_markdown_table(metrics_dir / "paper_table_posthoc.md", summary_rows, failure_rows)
    elapsed = time.time() - started_at
    print(
        f"[posthoc] done completed_cases={completed_cases} skipped_cases={skipped_cases} "
        f"rows={len(rows)} elapsed={elapsed:.1f}s output={metrics_dir}",
        flush=True,
    )
    return metrics_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-hoc RASI uncertainty analysis using existing predictions.")
    parser.add_argument("--profile", choices=sorted(PROFILE_CASE_LIMITS), default="mini")
    parser.add_argument("--source-set", choices=sorted(SOURCE_SETS), default="ixi")
    parser.add_argument("--factor", type=int, default=4)
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument(
        "--methods",
        default="i3net,hat,swinir,acsinet",
        help="Comma-separated target methods to evaluate.",
    )
    parser.add_argument("--progress-every", type=int, default=1, help="Print progress every N cases; 0 disables progress.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    methods = {item.strip() for item in args.methods.split(",") if item.strip()}
    metrics_dir = evaluate_posthoc(
        profile=args.profile,
        source_set=args.source_set,
        factor=args.factor,
        target_methods=methods or None,
        max_cases=args.max_cases,
        progress_every=args.progress_every,
    )
    print(f"Wrote post-hoc RASI uncertainty metrics to {metrics_dir}")


if __name__ == "__main__":
    main()
