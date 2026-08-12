from __future__ import annotations

import argparse
import stat

from ixi_diffusion.common import ensure_dir, write_json
from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from .inference import StrictHiFiDiffInterpolator, write_intensity_sanity
from .settings import PROFILES, build_paths
from .stage_data import prepare_eval_inputs
from .train import train


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
                        print(f"Warning: locked stale file ignored: {path}")


def run(profile_name: str) -> None:
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
            "method": "strict_hifidiff_gaussian_to_slice",
            "condition": "two_adjacent_slices_plus_relative_offset",
            "intensity_space": "minus_one_to_one",
            "loss": "noise_mse_plus_0.1_x0_l1",
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "diffusion_steps": profile.diffusion_steps,
            "sample_steps": profile.sample_steps,
            "stride": profile.stride,
            "target_size": profile.target_size,
            "base_channels": profile.base_channels,
            "eval_cases": eval_manifest,
        },
    )

    checkpoint = train(paths, profile)
    interpolator = StrictHiFiDiffInterpolator(checkpoint, sample_steps=profile.sample_steps)
    interpolator.process_folder(paths.eval_sparse, paths.diffusion_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(
        evaluate_method(
            paths.eval_gt,
            paths.diffusion_outputs,
            "diff_",
            "strict_hifidiff",
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
    print(f"Strict HiFi-Diff pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
