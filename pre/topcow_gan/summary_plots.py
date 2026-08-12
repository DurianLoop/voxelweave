from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt

from .common import ensure_dir
from .settings import build_paths


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _plot_grouped(rows: list[dict], metrics: list[tuple[str, str]], out_path: Path, title: str) -> None:
    x = list(range(len(metrics)))
    width = 0.22
    fig, ax = plt.subplots(figsize=(11, 5), constrained_layout=True)
    for offset_idx, row in enumerate(rows):
        offset = (offset_idx - (len(rows) - 1) / 2) * width
        values = [float(row[key]) for key, _ in metrics]
        ax.bar([idx + offset for idx in x], values, width=width, label=row["method"])
    ax.set_xticks(x, [label for _, label in metrics])
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def run(profile: str = "case_full") -> None:
    paths = build_paths(profile)
    out_dir = ensure_dir(paths.metrics / "summary_plots")
    summary = _read_csv(paths.metrics / "summary_metrics.csv")
    _plot_grouped(
        summary,
        [
            ("psnr_mean", "PSNR"),
            ("ssim_mean", "SSIM"),
            ("mask_psnr_mean", "mask-PSNR"),
            ("mask_ssim_mean", "mask-SSIM"),
        ],
        out_dir / "intensity_and_mask_metrics.png",
        f"{profile}: intensity and mask metrics",
    )
    labeled_path = paths.metrics / "labeled_holdout_summary_metrics.csv"
    if labeled_path.exists():
        labeled = _read_csv(labeled_path)
        _plot_grouped(
            labeled,
            [
                ("vessel_psnr_mean", "vessel-PSNR"),
                ("vessel_ssim_mean", "vessel-SSIM"),
                ("vessel_boundary_mae_mean", "boundary-MAE"),
            ],
            out_dir / "labeled_holdout_metrics.png",
            f"{profile}: labeled holdout metrics",
        )
    print(f"Wrote summary plots to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="case_full")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
