from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from ixi_diffusion.paper_table import _format_float
from ixi_pastnet_2p5d.model import PASTNet2p5D

from .data import MA4_MISSING_OFFSETS
from .model_ma import PASTNetMultiAnchor2p5D
from .model_ma3aggressive import PASTNetMA3Aggressive2p5D
from .model_ma3j import PASTNetMA3Joint2p5D
from .model_ma3latent import PASTNetMA3LatentInterval2p5D
from .model_ma4 import PASTNetMA4Window2p5D
from .model_sparse_window import PASTNetSparseWindow2p5D
from .settings import DATASET_NAME, PROFILES, build_paths


MA3_SINGLE_VARIANTS = {"ma3", "ma3af", "ma3ms", "ma3afms"}
MA3_JOINT_VARIANTS = {"ma3j", "ma3ir"}
MA3_LATENT_VARIANTS = {"ma3lc", "ma3la", "ma3lms", "ma3lt", "ma3lh"}
MA3_AGGRESSIVE_VARIANTS = {"ma3ad", "ma3ci", "ma3ur", "ma3df", "ma3vs"}
SPARSE_WINDOW_VARIANTS = {"ma3sw", "ma3sf", "ma3sd", "ma3sh"}
MA3_INTERVAL_VARIANTS = {
    *MA3_JOINT_VARIANTS,
    *MA3_LATENT_VARIANTS,
    *MA3_AGGRESSIVE_VARIANTS,
    *SPARSE_WINDOW_VARIANTS,
}


def _count_params(model: nn.Module) -> int:
    return int(sum(param.numel() for param in model.parameters()))


def _estimate_forward_macs(
    model: nn.Module,
    device: torch.device,
    channels: int,
    size: int = 256,
    joint_offsets: int = 1,
) -> int:
    macs = 0
    hooks = []

    def hook(module: nn.Module, _inputs: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        if isinstance(module, nn.Conv2d):
            batch, out_channels, out_h, out_w = [int(v) for v in output.shape]
            kh, kw = module.kernel_size
            macs += batch * out_channels * out_h * out_w * module.in_channels * kh * kw // module.groups
        elif isinstance(module, nn.Conv3d):
            batch, out_channels, out_d, out_h, out_w = [int(v) for v in output.shape]
            kd, kh, kw = module.kernel_size
            macs += (
                batch
                * out_channels
                * out_d
                * out_h
                * out_w
                * module.in_channels
                * kd
                * kh
                * kw
                // module.groups
            )
        elif isinstance(module, nn.Linear):
            batch = int(np.prod(output.shape[:-1])) if output.ndim > 1 else 1
            macs += batch * module.in_features * module.out_features

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.Conv3d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model.eval()
    with torch.no_grad():
        if joint_offsets > 1:
            cond = torch.zeros((1, joint_offsets, channels, size, size), device=device)
        else:
            cond = torch.zeros((1, channels, size, size), device=device)
        model(cond)
    for item in hooks:
        item.remove()
    return int(macs)


def _complexity(profile_name: str) -> dict:
    profile = PROFILES[profile_name]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if profile.model_variant == "ma4w":
        channels = 22
        model = PASTNetMA4Window2p5D(
            input_channels=channels,
            output_channels=len(MA4_MISSING_OFFSETS),
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
        ).to(device)
        model_name = "pastnet_ma4_window_residual_psnr_aligned"
    elif profile.model_variant in {"ma", "ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg", *MA3_INTERVAL_VARIANTS}:
        channels = 13 if profile.model_variant in {"ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg", *MA3_INTERVAL_VARIANTS} else 10
        if profile.model_variant in SPARSE_WINDOW_VARIANTS:
            model = PASTNetSparseWindow2p5D(
                input_channels=channels,
                base_channels=profile.base_channels,
                num_blocks=profile.num_blocks,
                window_size=profile.window_size,
                mlp_ratio=profile.mlp_ratio,
                residual_scale=profile.residual_scale,
                temporal_refine=True,
                refine_scale=profile.refine_scale,
                sparse_mode=profile.sparse_mode,
                flow_channels=profile.flow_channels,
            ).to(device)
        elif profile.model_variant in MA3_AGGRESSIVE_VARIANTS:
            model = PASTNetMA3Aggressive2p5D(
                input_channels=channels,
                base_channels=profile.base_channels,
                num_blocks=profile.num_blocks,
                window_size=profile.window_size,
                mlp_ratio=profile.mlp_ratio,
                residual_scale=profile.residual_scale,
                temporal_refine=True,
                refine_scale=profile.refine_scale,
                context_blocks=profile.context_blocks,
                latent_mixer=profile.latent_mixer,
                latent_scales=profile.latent_scales,
                latent_scale=profile.latent_scale,
                aggressive_mode=profile.aggressive_mode,
                aggressive_channels=profile.aggressive_channels,
                aggressive_steps=profile.aggressive_steps,
                aggressive_scale=profile.aggressive_scale,
            ).to(device)
        elif profile.model_variant in MA3_LATENT_VARIANTS:
            model = PASTNetMA3LatentInterval2p5D(
                input_channels=channels,
                base_channels=profile.base_channels,
                num_blocks=profile.num_blocks,
                window_size=profile.window_size,
                mlp_ratio=profile.mlp_ratio,
                residual_scale=profile.residual_scale,
                temporal_refine=True,
                refine_scale=profile.refine_scale,
                context_blocks=profile.context_blocks,
                latent_mixer=profile.latent_mixer,
                latent_scales=profile.latent_scales,
                latent_scale=profile.latent_scale,
            ).to(device)
        elif profile.model_variant in MA3_JOINT_VARIANTS:
            model = PASTNetMA3Joint2p5D(
                input_channels=channels,
                base_channels=profile.base_channels,
                num_blocks=profile.num_blocks,
                window_size=profile.window_size,
                mlp_ratio=profile.mlp_ratio,
                residual_scale=profile.residual_scale,
                temporal_refine=True,
                refine_scale=profile.refine_scale,
                joint_scale=profile.joint_scale,
                anchor_reliability=profile.anchor_reliability,
                context_blocks=profile.context_blocks,
                interval_refine=profile.model_variant == "ma3ir",
            ).to(device)
        else:
            model = PASTNetMultiAnchor2p5D(
                input_channels=channels,
                base_channels=profile.base_channels,
                num_blocks=profile.num_blocks,
                window_size=profile.window_size,
                mlp_ratio=profile.mlp_ratio,
                residual_scale=profile.residual_scale,
                temporal_refine=profile.model_variant in {*MA3_SINGLE_VARIANTS, "ma3c", "ma3cg"},
                refine_scale=profile.refine_scale,
                anchor_reliability=profile.anchor_reliability,
                context_blocks=profile.context_blocks,
            ).to(device)
        model_name = (
            f"pastnet_{profile.sparse_mode}_independent_sparse_window"
            if profile.model_variant in SPARSE_WINDOW_VARIANTS
            else
            f"pastnet_{profile.aggressive_mode}_aggressive_interval"
            if profile.model_variant in MA3_AGGRESSIVE_VARIANTS
            else
            f"pastnet_{profile.latent_mixer}_latent_interval_rich_phase_aware_residual"
            if profile.model_variant in MA3_LATENT_VARIANTS
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
        )
    else:
        model = PASTNet2p5D(
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
        ).to(device)
        model_name = "pastnet_phase_aware_single_slice_residual"
        channels = 6
    params = _count_params(model)
    joint_offsets = 3 if profile.model_variant in MA3_INTERVAL_VARIANTS else 1
    macs = _estimate_forward_macs(model, device, channels, joint_offsets=joint_offsets)
    output_slices = len(MA4_MISSING_OFFSETS) if profile.model_variant == "ma4w" else (3 if profile.model_variant in MA3_INTERVAL_VARIANTS else 1)
    return {
        "model": model_name,
        "params": params,
        "params_m": params / 1e6,
        "single_forward_macs_g": macs / 1e9,
        "single_forward_flops_g": 2 * macs / 1e9,
        "sample_steps": 1,
        "output_slices_per_forward": output_slices,
        "per_slice_sampling_flops_g": (2 * macs / 1e9) / output_slices,
        "flops_definition": "one deterministic PAST-Net forward divided by generated slices per forward",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    paths = build_paths(args.profile)
    profile = PROFILES[args.profile]
    summary = pd.read_csv(paths.metrics / "summary_metrics.csv")
    complexity = _complexity(args.profile)
    rows = []
    for _, row in summary.iterrows():
        method = str(row["method"])
        rows.append(
            {
                "dataset": DATASET_NAME,
                "scale": f"x{profile.stride}",
                "profile": args.profile,
                "method": method,
                "cases": int(row["cases"]),
                "PSNR": float(row["psnr_mean"]),
                "SSIM": float(row["ssim_mean"]),
                "MAE": float(row["mae_mean"]),
                "MSE": float(row["mse_mean"]),
                "NCC": float(row["ncc_mean"]),
                "Params(M)": 0.0 if method in {"linear", "cubic"} else float(complexity["params_m"]),
                "FLOPs(G)": 0.0 if method in {"linear", "cubic"} else float(complexity["per_slice_sampling_flops_g"]),
                "Source": "ours rerun"
                if method in {"linear", "cubic"}
                else (
                    "ours PAST-Net-MA4 window"
                    if profile.model_variant == "ma4w"
                    else
                    f"ours PAST-Net independent {profile.sparse_mode} sparse window"
                    if profile.model_variant in SPARSE_WINDOW_VARIANTS
                    else
                    f"ours PAST-Net G079 + {profile.aggressive_mode}"
                    if profile.model_variant in MA3_AGGRESSIVE_VARIANTS
                    else
                    f"ours PAST-Net {profile.latent_mixer} latent interval"
                    if profile.model_variant in MA3_LATENT_VARIANTS
                    else
                    "ours PAST-Net-MA3IR 3D interval"
                    if profile.model_variant == "ma3ir"
                    else
                    "ours PAST-Net-MA3J joint"
                    if profile.model_variant == "ma3j"
                    else
                    "ours PAST-Net-MA3CG guarded"
                    if profile.model_variant == "ma3cg"
                    else
                    "ours PAST-Net-MA3C interval"
                    if profile.model_variant == "ma3c"
                    else
                    "ours PAST-Net-MA3 adaptive fusion + multi-scale"
                    if profile.model_variant == "ma3afms"
                    else
                    "ours PAST-Net-MA3 multi-scale"
                    if profile.model_variant == "ma3ms"
                    else
                    "ours PAST-Net-MA3 anchor reliability"
                    if profile.model_variant == "ma3af"
                    else
                    "ours PAST-Net-MA3 v3"
                    if profile.model_variant == "ma3"
                    else
                    "ours PAST-Net-MA2 v2"
                    if profile.model_variant == "ma2"
                    else ("ours PAST-Net-MA v2" if profile.model_variant == "ma" else "ours PAST-Net v1")
                ),
            }
        )
    table = pd.DataFrame(rows)
    order = {"linear": 0, "cubic": 1, "pastnet": 2, "pastnet_ma": 3, "pastnet_ma2": 4, "pastnet_ma3": 5, "pastnet_ma3c": 6, "pastnet_ma3cg": 7, "pastnet_ma3j": 8, "pastnet_ma3ir": 9, "pastnet_ma3lc": 10, "pastnet_ma3la": 11, "pastnet_ma3lms": 12, "pastnet_ma3lt": 13, "pastnet_ma3lh": 14, "pastnet_ma4w": 15}
    table["_order"] = table["method"].map(order).fillna(99)
    table = table.sort_values(["_order", "method"]).drop(columns=["_order"])
    table.to_csv(paths.metrics / "paper_table.csv", index=False)
    simple = table.copy()
    for col in ["PSNR", "SSIM", "MAE", "MSE", "NCC", "Params(M)", "FLOPs(G)"]:
        simple[col] = simple[col].map(_format_float)
    header = list(simple.columns)
    lines = [
        "# fastMRI-brain-T2 PAST-Net Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in simple.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.extend(
        [
            "",
            "Note: PAST-Net v1/MA are project-specific phase-aware deterministic residual interpolation models. Smoke and mini runs are screening evidence only and should not be copied into the master table.",
        ]
    )
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
