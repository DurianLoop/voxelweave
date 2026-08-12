from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .common import ensure_dir, load_nifti
from .settings import build_paths


def _window(slice_: np.ndarray) -> tuple[float, float]:
    foreground = slice_[slice_ > np.percentile(slice_, 5)]
    if foreground.size < 100:
        foreground = slice_.reshape(-1)
    return float(np.percentile(foreground, 1)), float(np.percentile(foreground, 99))


def _candidate_generated_slices(depth: int, factor: int = 4) -> list[int]:
    generated = [idx for idx in range(depth) if idx % factor != 0]
    picks = [0.25, 0.5, 0.75]
    return [generated[min(len(generated) - 1, max(0, int(round((len(generated) - 1) * p))))] for p in picks]


def run(profile: str = "full") -> None:
    paths = build_paths(profile)
    out_dir = ensure_dir(paths.metrics / "visual_qc")
    made = 0
    for gt_path in sorted(paths.eval_gt.glob("*.nii.gz")):
        case = gt_path.name
        volumes = {
            "GT": load_nifti(gt_path)[0],
            "Diffusion": load_nifti(paths.diffusion_outputs / f"diff_{case}")[0],
            "Linear": load_nifti(paths.baseline_linear / f"linear_{case}")[0],
            "Cubic": load_nifti(paths.baseline_cubic / f"cubic_{case}")[0],
        }
        gt = volumes["GT"]
        for idx in _candidate_generated_slices(gt.shape[2]):
            vmin, vmax = _window(gt[:, :, idx])
            fig, axes = plt.subplots(2, 4, figsize=(15, 7), constrained_layout=True)
            for ax, (name, vol) in zip(axes[0], volumes.items()):
                ax.imshow(vol[:, :, idx].T, cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
                ax.set_title(name)
                ax.axis("off")
            axes[1, 0].imshow(gt[:, :, idx].T, cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
            axes[1, 0].set_title(f"GT z={idx}")
            axes[1, 0].axis("off")
            for ax, name in zip(axes[1, 1:], ["Diffusion", "Linear", "Cubic"]):
                err = np.abs(volumes[name][:, :, idx] - gt[:, :, idx])
                ax.imshow(err.T, cmap="magma", origin="lower")
                ax.set_title(f"|{name} - GT|")
                ax.axis("off")
            out = out_dir / f"{Path(case).name.replace('.nii.gz', '')}_z{idx:03d}.png"
            fig.savefig(out, dpi=160)
            plt.close(fig)
            made += 1
    print(f"Wrote {made} visual QC figures to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="full")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
