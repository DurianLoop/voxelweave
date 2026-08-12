from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from ixi_diffusion.paper_table import _format_float

from .model import ACVTT2p5D
from .settings import PROFILES, build_paths


def _count_params(model: nn.Module) -> int:
    return int(sum(param.numel() for param in model.parameters()))


def _estimate_forward_macs(model: nn.Module, device: torch.device, size: int = 256) -> int:
    macs = 0
    hooks = []

    def hook(module: nn.Module, _inputs: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        if isinstance(output, dict):
            output = output["out"]
        if isinstance(module, nn.Conv2d):
            batch, out_channels, out_h, out_w = [int(v) for v in output.shape]
            kh, kw = module.kernel_size
            macs += batch * out_channels * out_h * out_w * module.in_channels * kh * kw // module.groups
        elif isinstance(module, nn.Linear):
            batch = int(np.prod(output.shape[:-1])) if output.ndim > 1 else 1
            macs += batch * module.in_features * module.out_features

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model.eval()
    with torch.no_grad():
        cond = torch.zeros((1, 4, size, size), device=device)
        model(cond)
    for item in hooks:
        item.remove()
    return int(macs)


def _complexity(profile_name: str) -> dict:
    profile = PROFILES[profile_name]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ACVTT2p5D(
        num_level=profile.num_level,
        num_ref_enc_level=profile.num_level,
        num_channel=profile.num_channel,
        num_ref_channel=profile.num_channel,
        num_block=profile.num_block,
        num_block_ref=profile.num_block,
        scale=profile.stride,
        transfer_level=profile.transfer_level,
        block_size_per_level=profile.block_size_per_level,
        win_block_size_per_level=tuple([2] * profile.num_level),
    ).to(device)
    params = _count_params(model)
    macs = _estimate_forward_macs(model, device)
    return {
        "model": "acvtt_2p5d",
        "params": params,
        "params_m": params / 1e6,
        "single_forward_macs_g": macs / 1e9,
        "single_forward_flops_g": 2 * macs / 1e9,
        "sample_steps": 1,
        "per_slice_sampling_flops_g": 2 * macs / 1e9,
        "flops_definition": "one 256x256 generated slice, one deterministic ACVTT forward",
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
                "Source": "ours rerun" if method in {"linear", "cubic"} else "official ACVTT adapted",
            }
        )
    table = pd.DataFrame(rows)
    order = {"linear": 0, "cubic": 1, "acvtt": 2}
    table["_order"] = table["method"].map(order).fillna(99)
    table = table.sort_values(["_order", "method"]).drop(columns=["_order"])
    table.to_csv(paths.metrics / "paper_table.csv", index=False)
    simple = table.copy()
    for col in ["PSNR", "SSIM", "MAE", "MSE", "NCC", "Params(M)", "FLOPs(G)"]:
        simple[col] = simple[col].map(_format_float)
    header = list(simple.columns)
    lines = [
        "# IXI-T2 ACVTT Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in simple.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.extend(
        [
            "",
            f"Note: official ACVTT public architecture adapted to this project's IXI-T2/x{profile.stride}/split/metrics protocol.",
        ]
    )
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
