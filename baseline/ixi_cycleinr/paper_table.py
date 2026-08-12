from __future__ import annotations

import argparse

import pandas as pd

from ixi_arssr.paper_table import _complexity
from ixi_diffusion.paper_table import _format_float

from .settings import PROFILES, build_paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="mini")
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
                "dataset": "IXI-T2",
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
        "# IXI-T2 CycleINR-style Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in display.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.append("")
    lines.append("说明：本结果为 CycleINR-style reproduction，使用 IXI-T2 x4/split/metrics 口径。")
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
