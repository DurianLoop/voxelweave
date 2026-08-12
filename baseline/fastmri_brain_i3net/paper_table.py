from __future__ import annotations

import argparse
import json

import pandas as pd

from ixi_diffusion.paper_table import _format_float
from ixi_i3net.paper_table import _complexity_for_profile

from .settings import DATASET_NAME, PROFILES, SOURCE_NOTE, build_paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    paths = build_paths(args.profile)
    profile = PROFILES[args.profile]
    summary = pd.read_csv(paths.metrics / "summary_metrics.csv")
    complexity = _complexity_for_profile(profile)
    source_note = f"{SOURCE_NOTE}, x{profile.stride}"
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
        "# fastMRI-brain-T2 I3Net Paper Table",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in simple.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    lines.append("")
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (paths.metrics / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    print(f"Wrote {paths.metrics / 'paper_table.csv'}")
    print(f"Wrote {paths.metrics / 'paper_table.md'}")


if __name__ == "__main__":
    main()
