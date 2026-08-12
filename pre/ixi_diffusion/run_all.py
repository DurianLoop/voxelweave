from __future__ import annotations

import argparse
import stat
from pathlib import Path

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from .common import ensure_dir, write_json
from .hifidiff import HiFiDiffResidualInterpolator, train_hifidiff
from .inference import PureNoiseDiffusionInterpolator, write_intensity_sanity
from .resunet import ResUNetResidualInterpolator, train_resunet
from .saint import SAINTInterpolator, train_saint
from .settings import PROFILES, build_paths
from .stage_data import prepare_eval_inputs
from .train import train_diffusion


def _clear_generated_files(paths) -> None:
    for folder in [
        paths.eval_sparse,
        paths.eval_gt,
        paths.diffusion_outputs,
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
                        print(f"Warning: could not delete locked file, will ignore stale metrics if possible: {path}")


def run(profile_name: str, eval_only_checkpoint: Path | None = None) -> None:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    for path in [
        paths.run_dir,
        paths.checkpoints,
        paths.metrics,
        paths.eval_sparse,
        paths.eval_gt,
        paths.diffusion_outputs,
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
            "dataset": "IXI",
            "modality": profile.modality,
            "sampling": profile.method,
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "diffusion_steps": profile.diffusion_steps,
            "sample_steps": profile.sample_steps,
            "stride": profile.stride,
            "eval_cases": eval_manifest,
        },
    )

    if profile.method == "hifidiff_residual":
        checkpoint = eval_only_checkpoint if eval_only_checkpoint is not None else train_hifidiff(paths, profile)
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
        interpolator = HiFiDiffResidualInterpolator(checkpoint, sample_steps=profile.sample_steps)
        method_name = "diffusion"
    elif profile.method == "resunet_residual":
        checkpoint = eval_only_checkpoint if eval_only_checkpoint is not None else train_resunet(paths, profile)
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
        interpolator = ResUNetResidualInterpolator(checkpoint)
        method_name = "resunet"
    elif profile.method == "saint_spatial_aware":
        checkpoint = eval_only_checkpoint if eval_only_checkpoint is not None else train_saint(paths, profile)
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
        interpolator = SAINTInterpolator(checkpoint)
        method_name = "saint"
    else:
        checkpoint = eval_only_checkpoint if eval_only_checkpoint is not None else train_diffusion(paths, profile)
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
        interpolator = PureNoiseDiffusionInterpolator(checkpoint, sample_steps=profile.sample_steps)
        method_name = "diffusion"
    interpolator.process_folder(paths.eval_sparse, paths.diffusion_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(
        evaluate_method(
            paths.eval_gt,
            paths.diffusion_outputs,
            "diff_",
            method_name,
            factor=profile.stride,
            case_names=eval_names,
        )
    )
    rows.extend(
        evaluate_method(
            paths.eval_gt,
            paths.baseline_linear,
            "linear_",
            "linear",
            factor=profile.stride,
            case_names=eval_names,
        )
    )
    rows.extend(
        evaluate_method(
            paths.eval_gt,
            paths.baseline_cubic,
            "cubic_",
            "cubic",
            factor=profile.stride,
            case_names=eval_names,
        )
    )
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, paths.diffusion_outputs, paths.baseline_linear, paths.metrics)
    print(f"IXI diffusion pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument("--eval-only-checkpoint", type=Path, default=None)
    args = parser.parse_args()
    run(args.profile, eval_only_checkpoint=args.eval_only_checkpoint)


if __name__ == "__main__":
    main()
