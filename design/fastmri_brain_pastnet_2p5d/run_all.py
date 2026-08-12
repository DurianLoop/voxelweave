from __future__ import annotations

import argparse
import stat
from pathlib import Path

import numpy as np

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from ixi_diffusion.common import ensure_dir, load_nifti, save_nifti, write_json
from ixi_diffusion.inference import write_intensity_sanity

from .data import case_paths
from .settings import DATA_ROOT, DATASET_NAME, PROFILES, RUN_ROOT, build_paths
from .train import FastMRIPASTNet2p5DInterpolator, train_pastnet


MA3_SINGLE_VARIANTS = {"ma3", "ma3af", "ma3ms", "ma3afms"}
MA3_JOINT_VARIANTS = {"ma3j", "ma3ir"}


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
                        print(f"Warning: could not delete locked file, will overwrite or ignore if possible: {path}")


def _prepare_eval_inputs(paths, profile) -> list[dict]:
    ensure_dir(paths.eval_sparse)
    ensure_dir(paths.eval_gt)
    manifest = []
    for src in case_paths("test", profile.test_cases):
        volume, affine, header = load_nifti(src)
        sparse = volume[:, :, :: profile.stride]
        full_depth = (sparse.shape[2] - 1) * profile.stride + 1
        gt = volume[:, :, :full_depth]
        name = f"{src.name.removesuffix('.nii.gz')}.nii.gz"
        save_nifti(sparse.astype(np.float32), affine, header, paths.eval_sparse / name)
        save_nifti(gt.astype(np.float32), affine, header, paths.eval_gt / name)
        manifest.append(
            {
                "case": name,
                "source": str(src),
                "source_depth": int(volume.shape[2]),
                "sparse_depth": int(sparse.shape[2]),
                "target_depth": int(gt.shape[2]),
                "stride": profile.stride,
            }
        )
    if not manifest:
        raise RuntimeError("No fastMRI-brain-T2 test cases available for evaluation.")
    return manifest


def run(profile_name: str, eval_only_checkpoint: Path | None = None) -> None:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    is_window = profile.model_variant == "ma4w"
    is_multi_anchor = profile.model_variant in {"ma", "ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg", *MA3_JOINT_VARIANTS}
    sampling = (
        "pastnet_ma4_window_residual_psnr_aligned"
        if is_window
        else
        "pastnet_ma3ir_lowres_3d_interval_refined_rich_phase_aware_residual"
        if profile.model_variant == "ma3ir"
        else
        "pastnet_ma3j_joint_interval_refined_rich_phase_aware_residual"
        if profile.model_variant == "ma3j"
        else
        "pastnet_ma3cg_guarded_interval_consistency_refined_rich_phase_aware_single_slice_residual"
        if profile.model_variant == "ma3cg"
        else
        "pastnet_ma3c_interval_consistency_refined_rich_phase_aware_single_slice_residual"
        if profile.model_variant == "ma3c"
        else
        "pastnet_multi_anchor_reliability_multiscale_residual"
        if profile.model_variant == "ma3afms"
        else
        "pastnet_multi_anchor_multiscale_residual"
        if profile.model_variant == "ma3ms"
        else
        "pastnet_multi_anchor_reliability_residual"
        if profile.model_variant == "ma3af"
        else
        "pastnet_multi_anchor_refined_rich_phase_aware_single_slice_residual"
        if profile.model_variant == "ma3"
        else
        "pastnet_multi_anchor_rich_phase_aware_single_slice_residual"
        if profile.model_variant == "ma2"
        else "pastnet_multi_anchor_phase_aware_single_slice_residual"
        if is_multi_anchor
        else "pastnet_phase_aware_single_slice_residual"
    )
    source = (
        "ours PAST-Net-MA4 window residual PSNR-aligned model"
        if is_window
        else
        "ours PAST-Net-MA3IR low-resolution 3D interval refinement model"
        if profile.model_variant == "ma3ir"
        else
        "ours PAST-Net-MA3J joint interval multi-anchor model"
        if profile.model_variant == "ma3j"
        else
        "ours PAST-Net-MA3CG guarded interval-consistency calibrated multi-anchor model"
        if profile.model_variant == "ma3cg"
        else
        "ours PAST-Net-MA3C interval-consistency refined multi-anchor phase-aware model"
        if profile.model_variant == "ma3c"
        else
        "ours PAST-Net-MA3 adaptive-fusion multi-scale model"
        if profile.model_variant == "ma3afms"
        else
        "ours PAST-Net-MA3 multi-scale context model"
        if profile.model_variant == "ma3ms"
        else
        "ours PAST-Net-MA3 anchor-reliability model"
        if profile.model_variant == "ma3af"
        else
        "ours PAST-Net-MA3 refined rich multi-anchor phase-aware structure-transfer model"
        if profile.model_variant == "ma3"
        else
        "ours PAST-Net-MA2 rich multi-anchor phase-aware structure-transfer model"
        if profile.model_variant == "ma2"
        else "ours PAST-Net-MA v2 multi-anchor phase-aware structure-transfer model"
        if is_multi_anchor
        else "ours PAST-Net v1 phase-aware structure-transfer model"
    )
    condition = (
        "4 sparse anchors + 9 linear coarse missing slices + 9 phase maps + window residual prediction + normalized MSE PSNR tuning"
        if is_window
        else
        "prev/left/right/next anchors + linear coarse + phase + directional difference + abs difference + outer-anchor validity masks"
        + (" + outer-anchor deltas + sparse curvature" if profile.model_variant in {"ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg", *MA3_JOINT_VARIANTS} else "")
        + (" + temporal local residual refinement + Laplacian edge loss" if profile.model_variant in {*MA3_SINGLE_VARIANTS, "ma3c", "ma3cg", *MA3_JOINT_VARIANTS} else "")
        + (" + learned anchor reliability correction" if profile.anchor_reliability else "")
        + (f" + {profile.context_blocks} multi-scale context adapters" if profile.context_blocks > 0 else "")
        + (" + interval z-curvature consistency" if profile.model_variant in {"ma3c", "ma3cg", *MA3_JOINT_VARIANTS} else "")
        + (" + low-resolution 3D interval residual refiner" if profile.model_variant == "ma3ir" else "")
        + (" + joint three-offset residual head" if profile.model_variant == "ma3j" else "")
        + (" + frozen-backbone teacher trust region" if profile.model_variant == "ma3cg" else "")
        + (" + MSE PSNR tuning" if profile.lambda_mse > 0 else "")
        if is_multi_anchor
        else "left/right anchors + linear coarse + phase + directional difference + abs difference"
    )
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

    eval_manifest = _prepare_eval_inputs(paths, profile)
    eval_names = {row["case"] for row in eval_manifest}
    write_json(
        paths.run_dir / "run_manifest.json",
        {
            "profile": profile.name,
            "dataset": DATASET_NAME,
            "data_root": str(DATA_ROOT),
            "run_root": str(RUN_ROOT),
            "modality": "T2",
            "model_variant": profile.model_variant,
            "sampling": sampling,
            "source": source,
            "condition": condition,
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
            "optimizer_name": profile.optimizer_name,
            "optimizer_betas": profile.optimizer_betas,
            "scheduler_name": profile.scheduler_name,
            "warmup_epochs": profile.warmup_epochs,
            "min_lr_ratio": profile.min_lr_ratio,
            "backbone_lr_scale": profile.backbone_lr_scale,
            "head_lr_scale": profile.head_lr_scale,
            "adapter_lr_scale": profile.adapter_lr_scale,
            "adapter_only_epochs": profile.adapter_only_epochs,
            "ema_decay": profile.ema_decay,
            "grad_clip_norm": profile.grad_clip_norm,
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
            "lambda_teacher": profile.lambda_teacher,
            "joint_scale": profile.joint_scale,
            "anchor_reliability": profile.anchor_reliability,
            "context_blocks": profile.context_blocks,
            "freeze_backbone": profile.freeze_backbone,
            "window_step": profile.window_step,
            "init_checkpoint": str(profile.init_checkpoint) if profile.init_checkpoint is not None else None,
            "pretrained_epochs": profile.pretrained_epochs,
            "total_epoch_budget": profile.pretrained_epochs + profile.epochs,
            "eval_cases": eval_manifest,
            "table_ready": profile.name in {"full", "full_extend60", "full_extend90", "full_ma90", "full_ma2_90", "full_ma3_90", "full_ma3_warm90", "full_ma3_psnr_ft30", "full_ma3_psnr_ft60", "full_ma3c_150", "full_ma3cg_150", "full_ma3j_150", "full_ma3jf_150", "full_ma4w_150", "full_x2", "full_x6"},
            "eval_only_checkpoint": str(eval_only_checkpoint) if eval_only_checkpoint is not None else None,
        },
    )

    if eval_only_checkpoint is not None:
        checkpoint = eval_only_checkpoint
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
    else:
        checkpoint = train_pastnet(paths, profile)
    interpolator = FastMRIPASTNet2p5DInterpolator(checkpoint)
    interpolator.process_folder(paths.eval_sparse, paths.model_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    method_label = (
        "pastnet_ma4w"
        if is_window
        else
        "pastnet_ma3ir"
        if profile.model_variant == "ma3ir"
        else
        "pastnet_ma3j"
        if profile.model_variant == "ma3j"
        else
        "pastnet_ma3cg"
        if profile.model_variant == "ma3cg"
        else
        "pastnet_ma3c"
        if profile.model_variant == "ma3c"
        else
        f"pastnet_{profile.model_variant}"
        if profile.model_variant in MA3_SINGLE_VARIANTS
        else "pastnet_ma2"
        if profile.model_variant == "ma2"
        else "pastnet_ma"
        if is_multi_anchor
        else "pastnet"
    )
    rows.extend(evaluate_method(paths.eval_gt, paths.model_outputs, "diff_", method_label, factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names))
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, paths.model_outputs, paths.baseline_linear, paths.metrics)
    print(f"fastMRI brain PAST-Net 2.5D pipeline finished: {paths.run_dir}")


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
