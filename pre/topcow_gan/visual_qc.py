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
    if len(generated) <= 3:
        return generated
    picks = [0.25, 0.5, 0.75]
    return [generated[min(len(generated) - 1, max(0, int(round((len(generated) - 1) * p))))] for p in picks]


def _load_methods(paths, case: str) -> dict[str, np.ndarray]:
    return {
        "GT": load_nifti(paths.eval_gt / case)[0],
        "GAN": load_nifti(paths.gan_outputs / f"up_{case}")[0],
        "Linear": load_nifti(paths.baseline_linear / f"linear_{case}")[0],
        "Cubic": load_nifti(paths.baseline_cubic / f"cubic_{case}")[0],
    }


def make_case_qc(paths, case: str, out_dir: Path) -> list[Path]:
    volumes = _load_methods(paths, case)
    gt = volumes["GT"]
    indices = _candidate_generated_slices(gt.shape[2])
    outputs: list[Path] = []
    for idx in indices:
        gt_slice = gt[:, :, idx]
        vmin, vmax = _window(gt_slice)
        errors = {
            name: np.abs(vol[:, :, idx] - gt_slice)
            for name, vol in volumes.items()
            if name != "GT"
        }
        err_vmax = float(np.percentile(np.concatenate([e.reshape(-1) for e in errors.values()]), 99))
        fig, axes = plt.subplots(2, 4, figsize=(15, 7), constrained_layout=True)
        for ax, (name, vol) in zip(axes[0], volumes.items()):
            ax.imshow(vol[:, :, idx].T, cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
            ax.set_title(name)
            ax.axis("off")
        axes[1, 0].imshow(gt_slice.T, cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
        axes[1, 0].set_title(f"GT z={idx}")
        axes[1, 0].axis("off")
        for ax, name in zip(axes[1, 1:], ["GAN", "Linear", "Cubic"]):
            im = ax.imshow(errors[name].T, cmap="magma", origin="lower", vmin=0, vmax=err_vmax)
            ax.set_title(f"|{name} - GT|")
            ax.axis("off")
        fig.colorbar(im, ax=axes[1, 1:].ravel().tolist(), shrink=0.85)
        out_path = out_dir / f"{Path(case).name.replace('.nii.gz', '')}_z{idx:03d}.png"
        fig.suptitle(case)
        fig.savefig(out_path, dpi=160)
        plt.close(fig)
        outputs.append(out_path)
    return outputs


def run(profile: str = "full") -> None:
    paths = build_paths(profile)
    out_dir = ensure_dir(paths.metrics / "visual_qc")
    made: list[Path] = []
    for gt_path in sorted(paths.eval_gt.glob("*.nii.gz")):
        made.extend(make_case_qc(paths, gt_path.name, out_dir))
    print(f"Wrote {len(made)} visual QC figures to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="full")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
