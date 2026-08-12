from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from ixi_diffusion.paper_table import _format_float

from .settings import PROFILES, build_paths
from .train import _make_model


def _count_params(model: nn.Module) -> int:
    return int(sum(param.numel() for param in model.parameters()))


def _estimate_forward_macs(model: nn.Module, device: torch.device, size: int = 256) -> int:
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
        lr = torch.zeros((1, size, size, model.args.lr_slice_patch), device=device)
        model(lr)
    for item in hooks:
        item.remove()
    return int(macs)


def _complexity_for_profile(profile) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = _make_model(profile, device)
    params = _count_params(model)
    macs = _estimate_forward_macs(model, device)
    generated_per_window = profile.hr_slice_patch - profile.lr_slice_patch
    return {
        "model": "i3net_inter_intra_slice_window",
        "params": params,
        "params_m": params / 1e6,
        "window_forward_macs_g": macs / 1e9,
        "window_forward_flops_g": 2 * macs / 1e9,
        "generated_slices_per_window": generated_per_window,
        "per_generated_slice_flops_g": 2 * macs / generated_per_window / 1e9,
        "flops_definition": (
            f"one 256x256 I3Net window forward, {profile.lr_slice_patch} sparse slices -> "
            f"{profile.hr_slice_patch} HR slices for x{profile.stride}"
        ),
    }


def _complexity(profile_name: str) -> dict:
    return _complexity_for_profile(PROFILES[profile_name])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    paths = build_paths(args.profile)
    profile = PROFILES[args.profile]
    summary = pd.read_csv(paths.metrics / "summary_metrics.csv")
    complexity = _complexity_for_profile(profile)
    source_note = f"I3Net TMI 2024 official architecture, local IXI-T2 x{profile.stride} reproduction"
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
                "FLOPs(G)": 0.0 if method in {"linear", "cubic"} else float(complexity["per_generated_slice_flops_g"]),
                "Source": "ours rerun" if method in {"linear", "cubic"} else source_note,
            }
        )
    table = pd.DataFrame(rows)
    order = {"linear": 0, "cubic": 1, "i3net": 2}
    table["_order"] = table["method"].map(order).fillna(99)
    table = table.sort_values(["_order", "method"]).drop(columns=["_order"])
    table.to_csv(paths.metrics / "paper_table.csv", index=False)
    simple = table.copy()
    for col in ["PSNR", "SSIM", "MAE", "MSE", "NCC", "Params(M)", "FLOPs(G)"]:
        simple[col] = simple[col].map(_format_float)
    header = list(simple.columns)
    lines = [
        "# IXI-T2 I3Net Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in simple.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.extend(
        [
            "",
            "Note: full profile preserves the official I3Net channel/block configuration. Smoke and mini are only local screening runs and should not be copied into the master table.",
        ]
    )
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
