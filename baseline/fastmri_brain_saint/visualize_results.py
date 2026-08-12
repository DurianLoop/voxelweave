from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ixi_diffusion.common import ensure_dir, load_nifti

from .settings import RUN_ROOT, build_paths


MAIN_METRICS = ["psnr", "ssim", "mae", "mse", "ncc"]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in {"", None} else float("nan")


def _load_prefixed(folder: Path, prefix: str, case: str) -> np.ndarray:
    data, _, _ = load_nifti(folder / f"{prefix}{case}")
    return data.astype(np.float32)


def _plot_summary(summary_rows: list[dict[str, str]], out_path: Path, highlight: str) -> None:
    methods = [row["method"] for row in summary_rows]
    fig, axes = plt.subplots(1, len(MAIN_METRICS), figsize=(18, 3.8))
    for ax, metric in zip(axes, MAIN_METRICS):
        vals = [_float(row, f"{metric}_mean") for row in summary_rows]
        colors = ["#3f6fb5" if m == highlight else "#8a8f98" for m in methods]
        ax.bar(methods, vals, color=colors)
        ax.set_title(metric.upper())
        ax.tick_params(axis="x", rotation=35)
        if metric in {"mae", "mse"}:
            ax.set_ylabel("lower is better")
        else:
            ax.set_ylabel("higher is better")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def _plot_case(paths, case: str, out_path: Path, prediction_dir: Path, method: str, prefix: str) -> None:
    gt, _, _ = load_nifti(paths.eval_gt / case)
    linear = _load_prefixed(paths.baseline_linear, "linear_", case)
    cubic = _load_prefixed(paths.baseline_cubic, "cubic_", case)
    pred = _load_prefixed(prediction_dir, prefix, case)

    z = gt.shape[2] // 2
    gt_slice = gt[:, :, z].astype(np.float32)
    panels = [
        ("GT", gt_slice),
        ("Linear", linear[:, :, z]),
        ("Cubic", cubic[:, :, z]),
        (method, pred[:, :, z]),
        (f"|{method}-GT|", np.abs(pred[:, :, z] - gt_slice)),
    ]
    vmin, vmax = np.percentile(gt_slice, [1, 99])
    err_vmax = max(float(np.percentile(panels[-1][1], 99)), 1.0)

    fig, axes = plt.subplots(1, len(panels), figsize=(16, 3.5))
    for ax, (title, image) in zip(axes, panels):
        if title.startswith("|"):
            ax.imshow(np.rot90(image), cmap="magma", vmin=0, vmax=err_vmax)
        else:
            ax.imshow(np.rot90(image), cmap="gray", vmin=vmin, vmax=vmax)
        ax.set_title(f"{title}\nz={z}")
        ax.axis("off")
    fig.suptitle(case, y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run(profile: str, case_limit: int, method: str, prediction_dir_name: str, prediction_prefix: str) -> None:
    paths = build_paths(profile)
    out_dir = ensure_dir(paths.metrics / "visual_qc")
    prediction_dir = paths.run_dir / prediction_dir_name
    summary_rows = _read_csv(paths.metrics / "summary_metrics.csv")
    per_case_rows = _read_csv(paths.metrics / "per_case_metrics.csv")
    method_rows = [row for row in per_case_rows if row["method"] == method]
    method_rows.sort(key=lambda row: _float(row, "psnr"))

    _plot_summary(summary_rows, out_dir / "summary_metrics.png", method)
    selected = []
    if method_rows:
        selected.append(method_rows[0])
        selected.append(method_rows[len(method_rows) // 2])
        selected.append(method_rows[-1])
    seen: set[str] = set()
    for row in selected[:case_limit]:
        case = row["case"]
        if case in seen:
            continue
        seen.add(case)
        _plot_case(paths, case, out_dir / f"{Path(case).stem}_qc.png", prediction_dir, method, prediction_prefix)
    print(f"fastMRI brain visual QC written to: {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="full")
    parser.add_argument("--case-limit", type=int, default=3)
    parser.add_argument("--method", default="saint")
    parser.add_argument("--prediction-dir-name", default="saint_outputs")
    parser.add_argument("--prediction-prefix", default="diff_")
    args = parser.parse_args()
    run(args.profile, args.case_limit, args.method, args.prediction_dir_name, args.prediction_prefix)


if __name__ == "__main__":
    main()
