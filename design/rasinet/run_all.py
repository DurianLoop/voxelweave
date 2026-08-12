from __future__ import annotations

import argparse
import stat
from pathlib import Path

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from ixi_diffusion.common import ensure_dir, write_json
from ixi_diffusion.inference import write_intensity_sanity
from ixi_diffusion.stage_data import prepare_eval_inputs

from .metrics import (
    evaluate_consistency_method,
    evaluate_reliability_method,
    write_consistency_outputs,
    write_reliability_outputs,
)
from .settings import PROFILES, build_paths
from .train import RASINet2p5DInterpolator, train_rasinet


def _clear_generated_files(paths) -> None:
    for folder in [
        paths.eval_sparse,
        paths.eval_gt,
        paths.model_outputs,
        paths.uncertainty_outputs,
        paths.confidence_outputs,
        paths.residual_outputs,
        paths.baseline_linear,
        paths.baseline_cubic,
        paths.metrics,
    ]:
        if not folder.exists():
            continue
        for pattern in ["*.nii.gz", "*.csv", "*.json"]:
            for path in folder.glob(pattern):
                if path.is_file():
                    try:
                        path.chmod(stat.S_IWRITE)
                        path.unlink()
                    except PermissionError:
                        print(f"Warning: could not delete locked file, will ignore stale metrics if possible: {path}")


def run(profile_name: str, eval_only_checkpoint: Path | None = None) -> None:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    for path in [
        paths.run_dir,
        paths.checkpoints,
        paths.metrics,
        paths.eval_sparse,
        paths.eval_gt,
        paths.model_outputs,
        paths.uncertainty_outputs,
        paths.confidence_outputs,
        paths.residual_outputs,
        paths.baseline_linear,
        paths.baseline_cubic,
    ]:
        ensure_dir(path)
    _clear_generated_files(paths)

    eval_manifest = prepare_eval_inputs(paths, profile)
    eval_names = {row["case"] for row in eval_manifest}
    write_json(
        paths.run_dir / "run_manifest.json",
        {
            "profile": profile.name,
            "dataset": "IXI",
            "modality": profile.modality,
            "sampling": "rasinet_reliability_aware_group",
            "source": "ours RASI-Net v1 reliability-aware group interpolation model",
            "condition": "S0/S_end anchors + all linear coarse phase slices + phase maps + directional difference + abs difference",
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "grad_accum_steps": profile.grad_accum_steps,
            "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
            "patience": profile.patience,
            "lr": profile.lr,
            "weight_decay": profile.weight_decay,
            "amp": profile.amp,
            "stride": profile.stride,
            "target_shape": profile.target_shape,
            "window_step": profile.window_step,
            "base_channels": profile.base_channels,
            "num_blocks": profile.num_blocks,
            "loss": {
                "lambda_unc": profile.lambda_unc,
                "lambda_logvar": profile.lambda_logvar,
                "lambda_grad_xy": profile.lambda_grad_xy,
                "lambda_res": profile.lambda_res,
                "lambda_cal": profile.lambda_cal,
            },
            "reliability_outputs": {
                "uncertainty": str(paths.uncertainty_outputs),
                "confidence": str(paths.confidence_outputs),
                "residual": str(paths.residual_outputs),
            },
            "eval_cases": eval_manifest,
            "table_ready": profile.name in {"full_test115", "full_test115_x2", "full_test115_x6"},
            "eval_only_checkpoint": str(eval_only_checkpoint) if eval_only_checkpoint is not None else None,
        },
    )

    if eval_only_checkpoint is not None:
        checkpoint = eval_only_checkpoint
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
    else:
        checkpoint = train_rasinet(paths, profile)
    interpolator = RASINet2p5DInterpolator(checkpoint)
    interpolator.process_folder(
        paths.eval_sparse,
        paths.model_outputs,
        stride=profile.stride,
        uncertainty_dir=paths.uncertainty_outputs,
        confidence_dir=paths.confidence_outputs,
        residual_dir=paths.residual_outputs,
    )
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(
        evaluate_method(paths.eval_gt, paths.model_outputs, "diff_", "rasinet", factor=profile.stride, case_names=eval_names)
    )
    rows.extend(
        evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names)
    )
    rows.extend(
        evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names)
    )
    write_metric_outputs(paths.metrics, rows)

    consistency_rows = []
    consistency_rows.extend(evaluate_consistency_method(paths.eval_gt, paths.model_outputs, "diff_", "rasinet", eval_names))
    consistency_rows.extend(evaluate_consistency_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", eval_names))
    consistency_rows.extend(evaluate_consistency_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", eval_names))
    write_consistency_outputs(paths.metrics, consistency_rows)

    reliability_rows, risk_rows, calibration_rows, failure_detection = evaluate_reliability_method(
        paths.eval_gt,
        paths.model_outputs,
        paths.uncertainty_outputs,
        "diff_",
        "uncertainty_",
        "rasinet",
        factor=profile.stride,
        case_names=eval_names,
    )
    write_reliability_outputs(paths.metrics, reliability_rows, risk_rows, calibration_rows, failure_detection)

    write_intensity_sanity(paths.eval_gt, paths.model_outputs, paths.baseline_linear, paths.metrics)
    print(f"IXI RASI-Net 2.5D pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument(
        "--eval-only-checkpoint",
        type=Path,
        default=None,
        help="Evaluate an existing RASI-Net checkpoint without training.",
    )
    args = parser.parse_args()
    run(args.profile, eval_only_checkpoint=args.eval_only_checkpoint)


if __name__ == "__main__":
    main()
