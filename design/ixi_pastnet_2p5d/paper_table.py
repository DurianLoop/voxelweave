from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from ixi_diffusion.paper_table import _format_float
from fastmri_brain_pastnet_2p5d.model_ma import PASTNetMultiAnchor2p5D
from fastmri_brain_pastnet_2p5d.model_ma3aggressive import PASTNetMA3Aggressive2p5D

from .model import PASTNet2p5D
from .settings import PROFILES, build_paths


def _count_params(model: nn.Module) -> int:
    return int(sum(param.numel() for param in model.parameters()))


def _estimate_forward_macs(model: nn.Module, device: torch.device, channels: int, size: int = 256, offsets: int = 1) -> int:
    macs = 0
    hooks = []

    def hook(module: nn.Module, _inputs: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        if isinstance(module, nn.Conv2d):
            batch, out_channels, out_h, out_w = [int(v) for v in output.shape]
            kh, kw = module.kernel_size
            macs += batch * out_channels * out_h * out_w * module.in_channels * kh * kw // module.groups
        elif isinstance(module, nn.Linear):
            batch = int(np.prod(output.shape[:-1])) if output.ndim > 1 else 1
            macs += batch * module.in_features * module.out_features
        elif isinstance(module, nn.Conv3d):
            batch, out_channels, out_d, out_h, out_w = [int(v) for v in output.shape]
            kd, kh, kw = module.kernel_size
            macs += batch * out_channels * out_d * out_h * out_w * module.in_channels * kd * kh * kw // module.groups

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.Conv3d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model.eval()
    with torch.no_grad():
        cond = torch.zeros((1, offsets, channels, size, size), device=device) if offsets > 1 else torch.zeros((1, channels, size, size), device=device)
        model(cond)
    for item in hooks:
        item.remove()
    return int(macs)


def _complexity(profile_name: str) -> dict:
    profile = PROFILES[profile_name]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if profile.model_variant == "ma3df":
        model = PASTNetMA3Aggressive2p5D(
            input_channels=13,
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
            aggressive_scale=profile.aggressive_scale,
        ).to(device)
        channels = 13
        offsets = 3
        model_name = "pastnet_g086_dual_domain_interval"
    elif profile.model_variant == "ma3":
        model = PASTNetMultiAnchor2p5D(
            input_channels=13,
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
            temporal_refine=True,
            refine_scale=profile.refine_scale,
        ).to(device)
        channels = 13
        offsets = 1
        model_name = "pastnet_g07_wide_ma3_rich_multi_anchor"
    else:
        model = PASTNet2p5D(
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
        ).to(device)
        channels = 6
        offsets = 1
        model_name = "pastnet_phase_aware_single_slice_residual"
    params = _count_params(model)
    macs = _estimate_forward_macs(model, device, channels, offsets=offsets)
    return {
        "model": model_name,
        "params": params,
        "params_m": params / 1e6,
        "single_forward_macs_g": macs / 1e9,
        "single_forward_flops_g": 2 * macs / 1e9,
        "sample_steps": 1,
        "per_slice_sampling_flops_g": 2 * macs / 1e9 / offsets,
        "flops_definition": "one 256x256 generated slice, one deterministic PAST-Net 2.5D forward",
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
                "dataset": f"IXI-{profile.modality}",
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
                    "ours PAST-Net G086 dual-domain interval"
                    if profile.model_variant == "ma3df"
                    else ("ours PAST-Net G07 wide MA3" if profile.model_variant == "ma3" else "ours PAST-Net v1")
                ),
            }
        )
    table = pd.DataFrame(rows)
    reference_path = (
        Path(__file__).resolve().parents[2]
        / "baseline"
        / "ixi_i3net"
        / "runs"
        / "full_test115_stable"
        / "metrics"
        / "paper_table.csv"
    )
    if profile.test_cases is None and profile.stride == 4 and reference_path.exists():
        reference = pd.read_csv(reference_path)
        reference = reference[reference["method"] == "i3net"]
        if not reference.empty:
            reference = reference.copy()
            reference["profile"] = args.profile
            table = pd.concat([table, reference[table.columns]], ignore_index=True)
    order = {"linear": 0, "cubic": 1, "i3net": 2, "pastnet": 3, "pastnet_ma3": 4, "pastnet_g086": 5}
    table["_order"] = table["method"].map(order).fillna(99)
    table = table.sort_values(["_order", "method"]).drop(columns=["_order"])
    table.to_csv(paths.metrics / "paper_table.csv", index=False)
    simple = table.copy()
    for col in ["PSNR", "SSIM", "MAE", "MSE", "NCC", "Params(M)", "FLOPs(G)"]:
        simple[col] = simple[col].map(_format_float)
    header = list(simple.columns)
    lines = [
        "# IXI-T2 PAST-Net Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in simple.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.extend(
        [
            "",
            "Note: G07 uses the same wide rich multi-anchor MA3 architecture as the fastMRI experiment. G086 is frozen from fastMRI evidence and warm-started only from the IXI G07 checkpoint; IXI test-115 is not used for architecture selection. I3Net is the local official-architecture reproduction on the identical IXI-T2 x4 test-115 protocol; it is the comparison target, not an automatic universal SOTA claim.",
        ]
    )
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
