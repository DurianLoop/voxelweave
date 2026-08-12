from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .common import write_csv
from .settings import build_paths


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def run(profile: str = "case_full") -> None:
    paths = build_paths(profile)
    rows = _read_csv(paths.metrics / "per_case_metrics.csv")
    by_case_method = {(row["case"], row["method"]): row for row in rows}
    cases = sorted({row["case"] for row in rows})
    metrics = ["psnr", "ssim", "mae", "mse", "ncc", "mask_psnr", "mask_ssim", "auto_dice", "auto_hd95"]
    deltas: list[dict] = []
    for case in cases:
        diffusion = by_case_method[(case, "diffusion")]
        linear = by_case_method[(case, "linear")]
        cubic = by_case_method[(case, "cubic")]
        row = {"case": case}
        for metric in metrics:
            row[f"diffusion_minus_linear_{metric}"] = float(diffusion[metric]) - float(linear[metric])
            row[f"diffusion_minus_cubic_{metric}"] = float(diffusion[metric]) - float(cubic[metric])
        deltas.append(row)
    write_csv(paths.metrics / "diffusion_delta_vs_baselines.csv", deltas)

    rankings = sorted(
        (
            {
                "case": case,
                "diffusion_psnr": float(by_case_method[(case, "diffusion")]["psnr"]),
                "diffusion_auto_hd95": float(by_case_method[(case, "diffusion")]["auto_hd95"]),
            }
            for case in cases
        ),
        key=lambda row: row["diffusion_psnr"],
    )
    write_csv(paths.metrics / "diffusion_case_rankings.csv", rankings)
    print(f"Wrote result analysis to {paths.metrics}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="case_full")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
