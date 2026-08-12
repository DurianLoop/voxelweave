from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from .hifidiff import _build_model
from .resunet import ResidualInterpolationUNet
from .saint import SAINTInterpolationNet
from .settings import PROFILES, build_paths


def _count_params(model: nn.Module) -> int:
    return int(sum(param.numel() for param in model.parameters()))


def _conv_macs(module: nn.Module, output: torch.Tensor) -> int:
    if not isinstance(output, torch.Tensor):
        return 0
    batch = int(output.shape[0])
    out_channels = int(output.shape[1])
    out_h = int(output.shape[2])
    out_w = int(output.shape[3])
    if isinstance(module, nn.Conv2d):
        kernel_h, kernel_w = module.kernel_size
        in_channels = module.in_channels
        groups = module.groups
    elif isinstance(module, nn.ConvTranspose2d):
        kernel_h, kernel_w = module.kernel_size
        in_channels = module.in_channels
        groups = module.groups
    else:
        return 0
    return batch * out_channels * out_h * out_w * (in_channels // groups) * kernel_h * kernel_w


def _linear_macs(module: nn.Linear, output: torch.Tensor) -> int:
    if not isinstance(output, torch.Tensor):
        return 0
    batch = int(np.prod(output.shape[:-1])) if output.ndim > 1 else 1
    return batch * module.in_features * module.out_features


def _estimate_forward_macs(model: nn.Module, device: torch.device, size: int = 256) -> int:
    macs = 0
    hooks = []

    def hook(module: nn.Module, _inputs: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        if isinstance(module, (nn.Conv2d, nn.ConvTranspose2d)):
            macs += _conv_macs(module, output)
        elif isinstance(module, nn.Linear):
            macs += _linear_macs(module, output)

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.ConvTranspose2d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model.eval()
    with torch.no_grad():
        cond_channels = 6 if isinstance(model, SAINTInterpolationNet) else 4
        cond = torch.zeros((1, cond_channels, size, size), device=device)
        if isinstance(model, (ResidualInterpolationUNet, SAINTInterpolationNet)):
            model(cond)
        else:
            noisy = torch.zeros((1, 1, size, size), device=device)
            t = torch.zeros((1,), dtype=torch.long, device=device)
            model(noisy, cond, t, 500)
    for item in hooks:
        item.remove()
    return int(macs)


def _complexity(profile_name: str) -> dict[str, float | int | str]:
    profile = PROFILES[profile_name]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if profile.method == "resunet_residual":
        model_name = "resunet_residual"
        model = ResidualInterpolationUNet().to(device)
        sample_steps = 1
        flops_definition = "one 256x256 generated slice, one deterministic ResUNet forward"
    elif profile.method == "saint_spatial_aware":
        model_name = "saint_spatial_aware"
        model = SAINTInterpolationNet().to(device)
        sample_steps = 1
        flops_definition = "one 256x256 generated slice, one deterministic SAINT-style forward"
    else:
        model_name = "hifidiff_residual"
        model = _build_model().to(device)
        sample_steps = int(profile.sample_steps)
        flops_definition = "one 256x256 generated slice, denoising UNet forward FLOPs x sample_steps"
    params = _count_params(model)
    forward_macs = _estimate_forward_macs(model, device)
    forward_flops = 2 * forward_macs
    sampling_flops = forward_flops * sample_steps
    return {
        "model": model_name,
        "params": params,
        "params_m": params / 1e6,
        "single_forward_macs_g": forward_macs / 1e9,
        "single_forward_flops_g": forward_flops / 1e9,
        "sample_steps": sample_steps,
        "per_slice_sampling_flops_g": sampling_flops / 1e9,
        "flops_definition": flops_definition,
    }


def _format_float(value: object, digits: int = 4) -> str:
    if value == "" or pd.isna(value):
        return "NA"
    numeric = float(value)
    if not np.isfinite(numeric):
        return "NA"
    return f"{numeric:.{digits}f}"


def build_table(profile_name: str) -> tuple[pd.DataFrame, dict[str, float | int | str]]:
    paths = build_paths(profile_name)
    profile = PROFILES[profile_name]
    summary_path = paths.metrics / "summary_metrics.csv"
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    summary = pd.read_csv(summary_path)
    ext_path = paths.metrics / "extended_summary_metrics.csv"
    if ext_path.exists():
        ext = pd.read_csv(ext_path)
        summary = summary.merge(ext, on="method", how="left", suffixes=("", "_ext"))
    complexity = _complexity(profile_name)

    rows = []
    linear = summary[summary["method"] == "linear"].iloc[0]
    for _, row in summary.iterrows():
        method = str(row["method"])
        mse = float(row["mse_mean"])
        params_m = 0.0 if method in {"linear", "cubic"} else float(complexity["params_m"])
        flops_g = 0.0 if method in {"linear", "cubic"} else float(complexity["per_slice_sampling_flops_g"])
        rows.append(
            {
                "dataset": f"IXI-{profile.modality}",
                "scale": f"x{profile.stride}",
                "stride": int(profile.stride),
                "profile": profile_name,
                "method": method,
                "cases": int(row["cases"]),
                "PSNR": float(row["psnr_mean"]),
                "SSIM": float(row["ssim_mean"]),
                "SSIMa": row.get("ssim_a_mean", np.nan),
                "SSIMc": row.get("ssim_c_mean", np.nan),
                "SSIMs": row.get("ssim_s_mean", np.nan),
                "RMSE": float(row.get("rmse_mean", np.sqrt(mse))),
                "MSE": mse,
                "NMSE": row.get("nmse_mean", np.nan),
                "NRMSE": row.get("nrmse_mean", np.nan),
                "MAE": float(row["mae_mean"]),
                "NCC": float(row["ncc_mean"]),
                "SNLI": row.get("snli_mean", np.nan),
                "Gradient-MAE": row.get("gradient_mae_mean", np.nan),
                "LPIPS": row.get("lpips_mean", np.nan),
                "Mask-PSNR": float(row["mask_psnr_mean"]),
                "Mask-SSIM": float(row["mask_ssim_mean"]),
                "Auto-Dice": float(row["auto_dice_mean"]),
                "Auto-HD95": float(row["auto_hd95_mean"]),
                "Params(M)": params_m,
                "FLOPs(G)": flops_g,
                "PSNR_vs_linear": float(row["psnr_mean"] - linear["psnr_mean"]),
                "SSIM_vs_linear": float(row["ssim_mean"] - linear["ssim_mean"]),
                "MAE_vs_linear": float(row["mae_mean"] - linear["mae_mean"]),
            }
        )
    table = pd.DataFrame(rows)
    order = ["linear", "cubic", "resunet", "saint", "diffusion"]
    table["_order"] = table["method"].map({name: idx for idx, name in enumerate(order)}).fillna(99)
    table = table.sort_values(["_order", "method"]).drop(columns=["_order"])
    return table, complexity


def write_markdown(table: pd.DataFrame, complexity: dict[str, float | int | str], out_path: Path) -> None:
    method_label = {
        "linear": "Linear",
        "cubic": "Cubic",
        "resunet": "ResUNet residual",
        "saint": "SAINT-style",
        "diffusion": "HiFiDiff residual",
    }
    simple = table[["scale", "method", "PSNR", "SSIM", "MAE", "MSE", "NCC"]].copy()
    simple["Method"] = simple["method"].map(method_label).fillna(simple["method"])
    simple = simple.rename(columns={"scale": "Scale"})
    simple = simple[["Scale", "Method", "PSNR", "SSIM", "MAE", "MSE", "NCC"]]
    simple = simple.rename(
        columns={
            "PSNR": "PSNR mean",
            "SSIM": "SSIM mean",
            "MAE": "MAE mean",
            "MSE": "MSE mean",
            "NCC": "NCC mean",
        }
    )
    for col in ["PSNR mean", "SSIM mean", "MAE mean", "MSE mean", "NCC mean"]:
        simple[col] = simple[col].map(_format_float)
    simple_header = list(simple.columns)
    simple_rows = [
        "| " + " | ".join(simple_header) + " |",
        "| " + " | ".join(["---", "---"] + ["---:"] * (len(simple_header) - 2)) + " |",
    ]
    for _, row in simple.iterrows():
        simple_rows.append("| " + " | ".join(str(row[col]) for col in simple_header) + " |")

    representative_cols = [
        "scale",
        "method",
        "PSNR",
        "SSIM",
        "SSIMa",
        "SSIMc",
        "SSIMs",
        "MSE",
        "RMSE",
        "NMSE",
        "NRMSE",
        "NCC",
        "SNLI",
        "Gradient-MAE",
        "LPIPS",
        "Params(M)",
        "FLOPs(G)",
    ]
    representative = table[representative_cols].copy()
    representative["method"] = representative["method"].map(method_label).fillna(representative["method"])
    for col in [
        "PSNR",
        "SSIM",
        "SSIMa",
        "SSIMc",
        "SSIMs",
        "MSE",
        "RMSE",
        "NMSE",
        "NRMSE",
        "NCC",
        "SNLI",
        "Gradient-MAE",
        "LPIPS",
        "Params(M)",
        "FLOPs(G)",
    ]:
        representative[col] = representative[col].map(_format_float)
    representative_header = list(representative.columns)
    representative_rows = [
        "| " + " | ".join(representative_header) + " |",
        "| " + " | ".join(["---"] * len(representative_header)) + " |",
    ]
    for _, row in representative.iterrows():
        representative_rows.append("| " + " | ".join(str(row[col]) for col in representative_header) + " |")

    display = table.copy()
    display["method"] = display["method"].map(method_label).fillna(display["method"])
    for col in [
        "PSNR",
        "SSIM",
        "SSIMa",
        "SSIMc",
        "SSIMs",
        "MSE",
        "RMSE",
        "NMSE",
        "NRMSE",
        "MAE",
        "NCC",
        "SNLI",
        "Gradient-MAE",
        "LPIPS",
        "Mask-PSNR",
        "Mask-SSIM",
        "Auto-Dice",
        "Auto-HD95",
        "Params(M)",
        "FLOPs(G)",
        "PSNR_vs_linear",
        "SSIM_vs_linear",
        "MAE_vs_linear",
    ]:
        display[col] = display[col].map(_format_float)
    header = list(display.columns)
    markdown_rows = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in display.iterrows():
        markdown_rows.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    model_label = str(complexity["model"])
    forward_label = "Single forward"
    sampling_label = "Effective forwards"
    if "hifidiff" in model_label:
        forward_label = "Single denoising forward"
        sampling_label = "Sampling"
    lines = [
        "# IXI Interpolation Paper Table",
        "",
        "This table is generated from existing evaluation outputs. It does not rerun training or inference.",
        "",
        f"- Dataset: `{table['dataset'].iloc[0]}`",
        f"- Scale: `{table['scale'].iloc[0]}` / stride `{int(table['stride'].iloc[0])}`",
        "",
        "## Main Metrics",
        "",
        "\n".join(simple_rows),
        "",
        "## Representative Metrics",
        "",
        "\n".join(representative_rows),
        "",
        "## Detailed Metrics",
        "",
        "\n".join(markdown_rows),
        "",
        "## Complexity Definition",
        "",
        f"- Model: `{model_label}`.",
        f"- Params: `{int(complexity['params'])}` trainable parameters.",
        f"- {forward_label}: `{float(complexity['single_forward_flops_g']):.4f}` GFLOPs at 256x256.",
        f"- {sampling_label}: `{int(complexity['sample_steps'])}` step(s).",
        f"- Reported FLOPs: `{float(complexity['per_slice_sampling_flops_g']):.4f}` GFLOPs per generated 256x256 slice.",
        "- Linear/cubic are deterministic interpolation baselines and have no trainable parameters.",
        "",
        "## Pending Optional Metrics",
        "",
        "- LPIPS: not computed yet. It needs an additional perceptual network package and should be reported only after confirming the 2D slice normalization convention.",
        "- FID: not computed yet. In medical MRI, vanilla ImageNet-Inception FID is debatable; if used, report it as slice-level FID and keep PSNR/SSIM/RMSE as primary metrics.",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="hifidiff_full")
    args = parser.parse_args()

    paths = build_paths(args.profile)
    table, complexity = build_table(args.profile)
    out_csv = paths.metrics / "paper_table.csv"
    out_md = paths.metrics / "paper_table.md"
    out_json = paths.metrics / "complexity.json"
    table.to_csv(out_csv, index=False)
    write_markdown(table, complexity, out_md)
    out_json.write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")


if __name__ == "__main__":
    main()
