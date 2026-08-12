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
        elif isinstance(module, nn.Conv3d):
            batch, out_channels, out_d, out_h, out_w = [int(v) for v in output.shape]
            kd, kh, kw = module.kernel_size
            macs += batch * out_channels * out_d * out_h * out_w * module.in_channels * kd * kh * kw // module.groups
        elif isinstance(module, nn.Linear):
            batch = int(np.prod(output.shape[:-1])) if output.ndim > 1 else 1
            macs += batch * module.in_features * module.out_features

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.Conv3d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model.eval()
    with torch.no_grad():
        cond = torch.zeros((1, model.input_channels, size, size), device=device)
        model(cond)
    for item in hooks:
        item.remove()
    return int(macs)


def _complexity_for_profile(profile) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = _make_model(profile, device)
    params = _count_params(model)
    macs = _estimate_forward_macs(model, device)
    generated_slices = profile.stride - 1
    return {
        "model": "rasinet_reliability_aware_group",
        "params": params,
        "params_m": params / 1e6,
        "group_forward_macs_g": macs / 1e9,
        "group_forward_flops_g": 2 * macs / 1e9,
        "generated_slices_per_forward": generated_slices,
        "per_generated_slice_flops_g": 2 * macs / generated_slices / 1e9,
        "flops_definition": f"one 256x256 RASI-Net group forward, predicts {generated_slices} intermediate slices for x{profile.stride}",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    paths = build_paths(args.profile)
    profile = PROFILES[args.profile]
    summary = pd.read_csv(paths.metrics / "summary_metrics.csv")
    consistency_path = paths.metrics / "summary_3d_consistency.csv"
    consistency = pd.read_csv(consistency_path) if consistency_path.exists() else pd.DataFrame()
    reliability_path = paths.metrics / "summary_reliability.csv"
    reliability = pd.read_csv(reliability_path) if reliability_path.exists() else pd.DataFrame()
    reliability_json_path = paths.metrics / "summary_reliability.json"
    failure_detection = {}
    if reliability_json_path.exists():
        payload = json.loads(reliability_json_path.read_text(encoding="utf-8"))
        failure_detection = payload.get("failure_detection", {})
    complexity = _complexity_for_profile(profile)
    rows = []
    for _, row in summary.iterrows():
        method = str(row["method"])
        extra = {}
        if not consistency.empty:
            hit = consistency[consistency["method"] == method]
            if len(hit):
                c_row = hit.iloc[0]
                extra = {
                    "ZGE": float(c_row["zge_mean"]),
                    "ZLE": float(c_row["zle_mean"]),
                    "EdgeZ": float(c_row["edge_z_error_mean"]),
                    "NCC-z-MAE": float(c_row["interslice_ncc_mae_mean"]),
                }
        if not reliability.empty:
            hit = reliability[reliability["method"] == method]
            if len(hit):
                r_row = hit.iloc[0]
                extra.update(
                    {
                        "Err-U-Corr": float(r_row["pixel_error_uncertainty_corr_mean"]),
                        "Slice-Err-U-Corr": float(r_row["slice_error_uncertainty_corr_mean"]),
                        "Risk-AURC": float(r_row["risk_coverage_aurc_mean"]),
                        "Mean-U": float(r_row["mean_uncertainty_mean"]),
                    }
                )
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
                **extra,
                "Params(M)": 0.0 if method in {"linear", "cubic"} else float(complexity["params_m"]),
                "FLOPs(G)": 0.0 if method in {"linear", "cubic"} else float(complexity["per_generated_slice_flops_g"]),
                "Source": "ours rerun" if method in {"linear", "cubic"} else "ours RASI-Net reliability-aware group model",
            }
        )
    table = pd.DataFrame(rows)
    order = {"linear": 0, "cubic": 1, "rasinet": 2}
    table["_order"] = table["method"].map(order).fillna(99)
    table = table.sort_values(["_order", "method"]).drop(columns=["_order"])
    table.to_csv(paths.metrics / "paper_table.csv", index=False)

    simple = table.copy()
    for col in [
        "PSNR",
        "SSIM",
        "MAE",
        "MSE",
        "NCC",
        "ZGE",
        "ZLE",
        "EdgeZ",
        "NCC-z-MAE",
        "Err-U-Corr",
        "Slice-Err-U-Corr",
        "Risk-AURC",
        "Mean-U",
        "Params(M)",
        "FLOPs(G)",
    ]:
        if col in simple.columns:
            simple[col] = simple[col].map(_format_float)
    header = list(simple.columns)
    lines = [
        "# IXI-T2 RASI-Net Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in simple.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.extend(
        [
            "",
            "Note: RASI-Net v1 predicts the whole intermediate slice group and reports uncertainty-aware reliability metrics. Smoke and mini runs are screening evidence only.",
        ]
    )
    if failure_detection:
        lines.extend(
            [
                "",
                "## Failure Detection",
                "",
                f"- AUROC: {_format_float(failure_detection.get('auroc'))}",
                f"- AUPRC: {_format_float(failure_detection.get('auprc'))}",
                f"- Top-k failure recall: {_format_float(failure_detection.get('top_k_failure_recall'))}",
            ]
        )
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
