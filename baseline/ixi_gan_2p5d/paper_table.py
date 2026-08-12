from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from gan_2p5d.model import GeneratorUNet

from .settings import PROFILES, build_paths


def _format_float(value: float) -> str:
    if pd.isna(value):
        return "nan"
    return f"{float(value):.4f}"


def _count_params(model: nn.Module) -> int:
    return int(sum(param.numel() for param in model.parameters()))


def _estimate_forward_macs(model: nn.Module, device: torch.device, channels: int, size: int = 256) -> int:
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

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model.eval()
    with torch.no_grad():
        cond = torch.zeros((1, channels, size, size), device=device)
        model(cond)
    for item in hooks:
        item.remove()
    return int(macs)


def _complexity(profile) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    target_slices = profile.stride - 1
    condition_channels = target_slices + 3
    model = GeneratorUNet(in_channels=condition_channels, out_channels=target_slices).to(device)
    params = _count_params(model)
    macs = _estimate_forward_macs(model, device, condition_channels)
    return {
        "model": "gan_2p5d",
        "params": params,
        "params_m": params / 1e6,
        "single_forward_macs_g": macs / 1e9,
        "single_forward_flops_g": 2 * macs / 1e9,
        "per_slice_sampling_flops_g": (2 * macs / 1e9) / target_slices,
        "flops_definition": f"one 256x256 x{profile.stride} interval forward over generated intermediate slices",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    paths = build_paths(args.profile)
    profile = PROFILES[args.profile]
    summary = pd.read_csv(paths.metrics / "summary_metrics.csv")
    complexity = _complexity(profile)
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
                "Source": "ours rerun" if method in {"linear", "cubic"} else "inherited pix2pix/GAN-style 2.5D adapted to current protocol",
            }
        )
    table = pd.DataFrame(rows)
    order = {"linear": 0, "cubic": 1, "gan_2p5d": 2}
    table["_order"] = table["method"].map(order).fillna(99)
    table = table.sort_values(["_order", "method"]).drop(columns=["_order"])
    table.to_csv(paths.metrics / "paper_table.csv", index=False)
    simple = table.copy()
    for col in ["PSNR", "SSIM", "MAE", "MSE", "NCC", "Params(M)", "FLOPs(G)"]:
        simple[col] = simple[col].map(_format_float)
    header = list(simple.columns)
    lines = [
        "# IXI-T2 Pix2Pix/GAN-style 2.5D Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in simple.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.append("")
    lines.append(f"Note: this adapts the inherited pix2pix/GAN code to the project IXI-T2/x{profile.stride}/split/metrics protocol.")
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
