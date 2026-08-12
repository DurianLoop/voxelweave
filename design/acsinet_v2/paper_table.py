from __future__ import annotations

import argparse
import csv

from .settings import build_paths


def _read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _fmt(value: object, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="smoke")
    args = parser.parse_args()
    paths = build_paths(args.profile)
    metrics = _read_csv(paths.metrics / "summary_metrics.csv")
    consistency = _read_csv(paths.metrics / "summary_3d_consistency.csv")
    complexity = {}
    complexity_path = paths.metrics / "complexity.json"
    if complexity_path.exists():
        import json

        complexity = json.loads(complexity_path.read_text(encoding="utf-8"))

    lines = [
        "# ACSI-Net v2 Paper Table",
        "",
        "## Reconstruction",
        "",
        "| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics:
        lines.append(
            f"| {row['method']} | {row['cases']} | {_fmt(row['psnr_mean'])} | {_fmt(row['ssim_mean'])} | "
            f"{_fmt(row['mae_mean'])} | {_fmt(row['mse_mean'])} | {_fmt(row['ncc_mean'])} |"
        )
    lines.extend(["", "## 3D Consistency", "", "| Method | Cases | ZGE | ZLE | EdgeZ | NCC-z-MAE |", "|---|---:|---:|---:|---:|---:|"])
    for row in consistency:
        lines.append(
            f"| {row['method']} | {row['cases']} | {_fmt(row['zge_mean'])} | {_fmt(row['zle_mean'])} | "
            f"{_fmt(row['edge_z_error_mean'])} | {_fmt(row['interslice_ncc_mae_mean'])} |"
        )
    if complexity:
        lines.extend(
            [
                "",
                "## Lightweight Note",
                "",
                f"- Params: {_fmt(complexity['params_m'], 3)}M",
                f"- FLOPs/window: {_fmt(complexity['window_forward_flops_g'], 3)}G",
                f"- FLOPs/generated slice: {_fmt(complexity['per_generated_slice_flops_g'], 3)}G",
                f"- Definition: {complexity['flops_definition']}",
            ]
        )
    (paths.metrics / "paper_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(paths.metrics / "paper_table.md")


if __name__ == "__main__":
    main()
