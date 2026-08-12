from __future__ import annotations

import argparse
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE_ROOT = ROOT / "pre"
if str(PRE_ROOT) not in sys.path:
    sys.path.insert(0, str(PRE_ROOT))

from gan_2p5d.inference import GAN2p5DInterpolator
from ixi_diffusion.common import ensure_dir, load_nifti, save_nifti, write_json
from ixi_diffusion.inference import write_intensity_sanity
from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from .data import prepare_eval_inputs
from .settings import PROFILES, build_paths
from .train import train_gan


def _clear_generated_files(paths) -> None:
    for folder in [
        paths.eval_sparse,
        paths.eval_gt,
        paths.model_outputs,
        paths.baseline_linear,
        paths.baseline_cubic,
        paths.metrics,
    ]:
        if not folder.exists():
            continue
        for pattern in ["*.nii.gz", "*.csv", "*.json"]:
            for path in folder.glob(pattern):
                if path.is_file():
                    try:
                        path.chmod(stat.S_IWRITE)
                        path.unlink()
                    except PermissionError:
                        print(f"Warning: could not delete locked file: {path}")


def run(profile_name: str) -> None:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    for path in [
        paths.run_dir,
        paths.checkpoints,
        paths.metrics,
        paths.eval_sparse,
        paths.eval_gt,
        paths.model_outputs,
        paths.baseline_linear,
        paths.baseline_cubic,
    ]:
        ensure_dir(path)
    _clear_generated_files(paths)

    eval_manifest = prepare_eval_inputs(paths, profile)
    eval_names = {row["case"] for row in eval_manifest}
    write_json(
        paths.run_dir / "run_manifest.json",
        {
            "profile": profile.name,
            "dataset": "IXI-T2",
            "modality": profile.modality,
            "sampling": "inherited_pix2pix_gan_2p5d",
            "source": f"Inherited pix2pix/GAN baseline from pre/v4 adapted to current T2-only x{profile.stride} through-plane protocol",
            "condition": "left/right sparse slices + global z + relative positions",
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "patience": profile.patience,
            "lr": profile.lr,
            "stride": profile.stride,
            "target_shape": profile.target_shape,
            "eval_cases": eval_manifest,
            "table_ready": profile.name in {"full", "full_test115", "full_test115_b64", "full_test115_stable"},
        },
    )

    checkpoint = train_gan(paths, profile)
    interpolator = GAN2p5DInterpolator(checkpoint, target_shape=profile.target_shape, stride=profile.stride)
    interpolator.process_folder(paths.eval_sparse, paths.model_outputs, load_nifti, save_nifti, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(evaluate_method(paths.eval_gt, paths.model_outputs, "diff_", "gan_2p5d", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names))
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, paths.model_outputs, paths.baseline_linear, paths.metrics)
    print(f"IXI GAN 2.5D pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
