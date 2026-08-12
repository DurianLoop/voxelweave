from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd

from .common import ensure_dir
from .settings import build_paths


def _load(path: Path) -> np.ndarray:
    return nib.load(str(path)).get_fdata(dtype=np.float32)


def _generated_indices(depth: int, factor: int) -> list[int]:
    return [idx for idx in range(depth) if idx % factor != 0]


def _window(values: np.ndarray) -> tuple[float, float]:
    finite = values[np.isfinite(values)]
    return float(np.percentile(finite, 1)), float(np.percentile(finite, 99.5))


def _run_context(run_dir: Path, factor: int) -> str:
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.exists():
        return f"x{factor}"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dataset = str(manifest.get("dataset", "dataset"))
    modality = str(manifest.get("modality", ""))
    stride = int(manifest.get("stride", factor))
    profile = str(manifest.get("profile", run_dir.name))
    dataset_label = f"{dataset}-{modality}" if modality else dataset
    return f"{dataset_label} {profile} x{stride}"


def _plot_training(run_dir: Path, out_dir: Path) -> None:
    history_path = run_dir / "training_history.csv"
    if not history_path.exists():
        return
    history = pd.read_csv(history_path)
    fig, ax = plt.subplots(figsize=(7, 4), dpi=160)
    ax.plot(history["epoch"] + 1, history["train_loss"], label="train")
    ax.plot(history["epoch"] + 1, history["val_loss"], label="val")
    ax.set_xlabel("epoch")
    ax.set_ylabel("loss")
    ax.set_title("HiFiDiff Training Curve")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "training_curve.png")
    plt.close(fig)


def _plot_summary(metrics_dir: Path, out_dir: Path, context: str) -> None:
    summary = pd.read_csv(metrics_dir / "summary_metrics.csv")
    methods = list(summary["method"])
    metric_names = ["psnr_mean", "ssim_mean", "mae_mean", "ncc_mean", "mask_psnr_mean", "auto_dice_mean"]
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), dpi=160)
    for ax, metric in zip(axes.ravel(), metric_names):
        values = summary[metric].to_numpy()
        ax.bar(methods, values, color=["#6c7a89", "#d96c4a", "#4b8bbe"])
        ax.set_title(metric.replace("_mean", ""))
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle(f"Full Evaluation Summary ({context})", y=1.02)
    fig.tight_layout()
    fig.savefig(out_dir / "summary_metrics.png")
    plt.close(fig)


def _generated_method(metrics_dir: Path) -> str:
    rows = pd.read_csv(metrics_dir / "summary_metrics.csv")
    for method in rows["method"].tolist():
        if method not in {"linear", "cubic"}:
            return str(method)
    return "diffusion"


def _plot_intensity(metrics_dir: Path, out_dir: Path) -> None:
    generated_name = _generated_method(metrics_dir)
    rows = pd.read_csv(metrics_dir / "intensity_sanity.csv")
    pivot = rows.pivot(index="case", columns="source", values="median")
    p99 = rows.pivot(index="case", columns="source", values="p99")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), dpi=160)
    axes[0].scatter(pivot["gt"], pivot["linear"], label="linear", alpha=0.8)
    axes[0].scatter(pivot["gt"], pivot["diffusion"], label=generated_name, alpha=0.8)
    axes[0].set_xlabel("GT median")
    axes[0].set_ylabel("prediction median")
    axes[0].set_title("Median Intensity")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].scatter(p99["gt"], p99["linear"], label="linear", alpha=0.8)
    axes[1].scatter(p99["gt"], p99["diffusion"], label=generated_name, alpha=0.8)
    axes[1].set_xlabel("GT p99")
    axes[1].set_ylabel("prediction p99")
    axes[1].set_title("P99 Intensity")
    axes[1].legend()
    axes[1].grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "intensity_sanity.png")
    plt.close(fig)


def _choose_cases(metrics_dir: Path, limit: int) -> list[str]:
    rows = pd.read_csv(metrics_dir / "per_case_metrics.csv")
    pivot = rows.pivot(index="case", columns="method", values="psnr")
    generated_name = _generated_method(metrics_dir)
    pivot["delta_vs_linear"] = pivot[generated_name] - pivot["linear"]
    ordered = []
    ordered.extend(pivot.sort_values("delta_vs_linear", ascending=False).head(limit).index.tolist())
    ordered.extend(pivot.iloc[(pivot["delta_vs_linear"].abs()).argsort()].head(limit).index.tolist())
    ordered.extend(pivot.sort_values("delta_vs_linear", ascending=True).head(limit).index.tolist())
    deduped: list[str] = []
    for case in ordered:
        if case not in deduped:
            deduped.append(case)
    return deduped


def _plot_case(paths, out_dir: Path, case: str, factor: int, context: str) -> None:
    generated_name = _generated_method(paths.metrics)
    gt = _load(paths.eval_gt / case)
    linear = _load(paths.baseline_linear / f"linear_{case}")
    cubic = _load(paths.baseline_cubic / f"cubic_{case}")
    diff = _load(paths.diffusion_outputs / f"diff_{case}")
    indices = _generated_indices(gt.shape[2], factor)
    if not indices:
        return
    err = np.array([np.mean(np.abs(diff[:, :, idx] - gt[:, :, idx])) for idx in indices])
    z = int(indices[int(np.argmax(err))])
    lo, hi = _window(gt[:, :, z])
    panels = [
        ("GT", gt[:, :, z]),
        ("linear", linear[:, :, z]),
        ("cubic", cubic[:, :, z]),
        (generated_name, diff[:, :, z]),
        (f"|{generated_name}-GT|", np.abs(diff[:, :, z] - gt[:, :, z])),
        ("|linear-GT|", np.abs(linear[:, :, z] - gt[:, :, z])),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(12, 8), dpi=160)
    for ax, (title, data) in zip(axes.ravel(), panels):
        if title.startswith("|"):
            vmax = float(np.percentile(data, 99))
            ax.imshow(np.rot90(data), cmap="magma", vmin=0, vmax=max(vmax, 1e-6))
        else:
            ax.imshow(np.rot90(data), cmap="gray", vmin=lo, vmax=hi)
        ax.set_title(title)
        ax.axis("off")
    fig.suptitle(f"{case} generated slice z={z} ({context})", y=0.98)
    fig.tight_layout()
    safe = case.replace(".nii.gz", "")
    fig.savefig(out_dir / f"{safe}_z{z:03d}.png")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="hifidiff_full")
    parser.add_argument("--factor", type=int, default=4)
    parser.add_argument("--case-limit", type=int, default=3)
    args = parser.parse_args()

    paths = build_paths(args.profile)
    context = _run_context(paths.run_dir, args.factor)
    out_dir = ensure_dir(paths.metrics / "visual_qc")
    _plot_training(paths.run_dir, out_dir)
    _plot_summary(paths.metrics, out_dir, context)
    _plot_intensity(paths.metrics, out_dir)
    for case in _choose_cases(paths.metrics, args.case_limit):
        _plot_case(paths, out_dir, case, args.factor, context)
    print(f"Visual QC written to {out_dir}")


if __name__ == "__main__":
    main()
