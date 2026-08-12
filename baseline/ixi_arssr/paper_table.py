from __future__ import annotations

import argparse
import json

import pandas as pd
import torch
import torch.nn as nn

from ixi_diffusion.paper_table import _count_params, _format_float

from .model import ArSSRNet
from .settings import PROFILES, build_paths


def _complexity(profile_name: str) -> dict:
    profile = PROFILES[profile_name]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ArSSRNet(feature_channels=profile.feature_channels).to(device)
    params = _count_params(model)
    macs = _estimate_arssr_macs(model, device)
    return {
        "model": "arssr_style_inr",
        "params": params,
        "params_m": params / 1e6,
        "single_forward_flops_g": 2 * macs / 1e9,
        "sample_steps": 1,
        "per_slice_sampling_flops_g": 2 * macs / 1e9,
        "flops_definition": "proxy: 256x256xD feature encoder plus one generated slice of coordinate queries; coordinate MLP cost depends on queried voxels",
    }


def _estimate_arssr_macs(model: ArSSRNet, device: torch.device) -> int:
    macs = 0
    hooks = []

    def hook(module: nn.Module, _inputs: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        if isinstance(module, nn.Conv3d):
            batch, out_channels, out_d, out_h, out_w = [int(v) for v in output.shape]
            kd, kh, kw = module.kernel_size
            macs += batch * out_channels * out_d * out_h * out_w * (module.in_channels // module.groups) * kd * kh * kw
        elif isinstance(module, nn.Linear):
            batch = int(torch.tensor(output.shape[:-1]).prod().item()) if output.ndim > 1 else 1
            macs += batch * module.in_features * module.out_features

    for module in model.modules():
        if isinstance(module, (nn.Conv3d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model.eval()
    with torch.no_grad():
        volume = torch.zeros((1, 1, 32, 256, 256), device=device)
        coords = torch.zeros((1, 256 * 256, 3), device=device)
        model(volume, coords)
    for item in hooks:
        item.remove()
    return int(macs)


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
                "Source": "ours rerun" if method in {"linear", "cubic"} else "ours ArSSR-style reproduction",
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(paths.metrics / "paper_table.csv", index=False)
    simple = table.copy()
    for col in ["PSNR", "SSIM", "MAE", "MSE", "NCC", "Params(M)", "FLOPs(G)"]:
        simple[col] = simple[col].map(_format_float)
    header = list(simple.columns)
    lines = [
        "# IXI-T2 ArSSR-style Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in simple.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.extend(
        [
            "",
            "说明：本结果为 ArSSR-style reproduction，使用本项目 IXI-T2/x4/split/metrics 口径；不是官方 HCP-1200 protocol 的 reported result。",
        ]
    )
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
