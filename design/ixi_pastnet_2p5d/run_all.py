from __future__ import annotations

import argparse
import stat
from pathlib import Path

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from ixi_diffusion.common import ensure_dir, write_json
from ixi_diffusion.inference import write_intensity_sanity
from ixi_diffusion.stage_data import prepare_eval_inputs

from .settings import PROFILES, build_paths
from .train import PASTNet2p5DInterpolator, train_pastnet


def _clear_generated_files(paths) -> None:
    for folder in [
        paths.eval_sparse,
        paths.eval_gt,
        paths.model_outputs,
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
    is_ma3 = profile.model_variant in {"ma3", "ma3df"}
    paths = build_paths(profile.name)
    for path in [
        paths.run_dir,
        paths.checkpoints,
        paths.metrics,
        paths.eval_sparse,
        paths.eval_gt,
        paths.model_outputs,
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
            "model_variant": profile.model_variant,
            "sampling": (
                "pastnet_multi_anchor_refined_rich_phase_aware_single_slice_residual"
                if is_ma3
                else "pastnet_phase_aware_single_slice_residual"
            ),
            "source": (
                "ours PAST-Net G07 wide MA3 rich multi-anchor model"
                if is_ma3
                else "ours PAST-Net v1 phase-aware structure-transfer model"
            ),
            "condition": (
                "prev/left/right/next anchors + coarse + phase + differences + validity + sparse curvature"
                if is_ma3
                else "left/right anchors + linear coarse + phase + directional difference + abs difference"
            ),
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "grad_accum_steps": profile.grad_accum_steps,
            "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
            "train_samples_per_epoch": profile.train_samples_per_epoch,
            "val_samples_per_epoch": profile.val_samples_per_epoch,
            "patience": profile.patience,
            "lr": profile.lr,
            "weight_decay": profile.weight_decay,
            "amp": profile.amp,
            "stride": profile.stride,
            "base_channels": profile.base_channels,
            "num_blocks": profile.num_blocks,
            "window_size": profile.window_size,
            "residual_scale": profile.residual_scale,
            "refine_scale": profile.refine_scale,
            "lambda_grad": profile.lambda_grad,
            "lambda_res": profile.lambda_res,
            "lambda_sym": profile.lambda_sym,
            "lambda_edge": profile.lambda_edge,
            "lambda_mse": profile.lambda_mse,
            "lambda_z": profile.lambda_z,
            "lambda_tail": profile.lambda_tail,
            "tail_fraction": profile.tail_fraction,
            "joint_base_guard": profile.joint_base_guard,
            "context_blocks": profile.context_blocks,
            "latent_mixer": profile.latent_mixer,
            "latent_scales": profile.latent_scales,
            "aggressive_mode": profile.aggressive_mode,
            "init_checkpoint": str(profile.init_checkpoint) if profile.init_checkpoint is not None else None,
            "eval_cases": eval_manifest,
            "table_ready": profile.name in {"full", "full_test115", "full_g07_ma3_wide200_test115", "full_g086_dual_interval160_test115", "full_test115_x2", "full_test115_x6"},
            "eval_only_checkpoint": str(eval_only_checkpoint) if eval_only_checkpoint is not None else None,
        },
    )

    if eval_only_checkpoint is not None:
        checkpoint = eval_only_checkpoint
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
    else:
        checkpoint = train_pastnet(paths, profile)
    interpolator = PASTNet2p5DInterpolator(checkpoint)
    interpolator.process_folder(paths.eval_sparse, paths.model_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    method_label = "pastnet_g086" if profile.model_variant == "ma3df" else ("pastnet_ma3" if is_ma3 else "pastnet")
    rows.extend(
        evaluate_method(paths.eval_gt, paths.model_outputs, "diff_", method_label, factor=profile.stride, case_names=eval_names)
    )
    rows.extend(
        evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names)
    )
    rows.extend(
        evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names)
    )
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, paths.model_outputs, paths.baseline_linear, paths.metrics)
    print(f"IXI PAST-Net 2.5D pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument(
        "--eval-only-checkpoint",
        type=Path,
        default=None,
        help="Evaluate an existing PAST-Net checkpoint without training.",
    )
    args = parser.parse_args()
    run(args.profile, eval_only_checkpoint=args.eval_only_checkpoint)


if __name__ == "__main__":
    main()
