from __future__ import annotations

import argparse
import json

import pandas as pd
import torch

from ixi_arssr.model import ArSSRNet
from ixi_arssr.paper_table import _estimate_arssr_macs
from ixi_diffusion.paper_table import _count_params, _format_float

from .settings import DATA_ROOT, PROFILES, build_paths


def _complexity(profile_name: str) -> dict:
    profile = PROFILES[profile_name]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ArSSRNet(feature_channels=profile.feature_channels).to(device)
    params = _count_params(model)
    macs = _estimate_arssr_macs(model, device)
    return {
        "model": "cycleinr_style_inr",
        "params": params,
        "params_m": params / 1e6,
        "single_forward_flops_g": 2 * macs / 1e9,
        "sample_steps": 1,
        "per_slice_sampling_flops_g": 2 * macs / 1e9,
        "flops_definition": "proxy: 256x256xD feature encoder plus one generated slice of coordinate queries",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="full")
    args = parser.parse_args()
    paths = build_paths(args.profile)
    profile = PROFILES[args.profile]
    dataset = "NingXia-T2" if "NingXiaData" in str(DATA_ROOT) else "fastMRI-brain-T2 expanded"
    summary = pd.read_csv(paths.metrics / "summary_metrics.csv")
    complexity = _complexity(args.profile)
    rows = []
    for _, row in summary.iterrows():
        method = str(row["method"])
        rows.append(
            {
                "dataset": dataset,
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
                "Source": "ours rerun" if method in {"linear", "cubic"} else "ours CycleINR-style reproduction",
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(paths.metrics / "paper_table.csv", index=False)
    display = table.copy()
    for col in ["PSNR", "SSIM", "MAE", "MSE", "NCC", "Params(M)", "FLOPs(G)"]:
        display[col] = display[col].map(_format_float)
    header = list(display.columns)
    lines = [
        f"# {dataset} CycleINR-style Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in display.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.append("")
    lines.append(
        f"Note: this is an ours CycleINR-style reproduction using the project {dataset} x4/split/metrics protocol."
    )
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
