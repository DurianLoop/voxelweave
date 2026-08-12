from __future__ import annotations

import argparse
import stat

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from ixi_diffusion.common import ensure_dir, write_json
from ixi_diffusion.inference import write_intensity_sanity
from ixi_diffusion.stage_data import prepare_eval_inputs

from .settings import PROFILES, build_paths
from .train import ResSRDiff2p5DInterpolator, train_ressrdiff


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
                        print(f"Warning: could not delete locked file, will ignore stale metrics if possible: {path}")


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
            "dataset": "IXI",
            "modality": profile.modality,
            "sampling": "ressrdiff_2p5d_refinement",
            "source": f"official mosaf/Res-SRDiff diffusion core adapted to this project's IXI-T2 x{profile.stride} protocol",
            "condition": "linear coarse slice as low-quality condition; no intermediate GT as input",
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "grad_accum_steps": profile.grad_accum_steps,
            "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
            "use_amp": profile.use_amp,
            "preload_resized": profile.preload_resized,
            "stride": profile.stride,
            "model_channels": profile.model_channels,
            "steps": profile.steps,
            "eval_cases": eval_manifest,
        },
    )

    checkpoint = train_ressrdiff(paths, profile)
    interpolator = ResSRDiff2p5DInterpolator(checkpoint)
    interpolator.process_folder(paths.eval_sparse, paths.model_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(
        evaluate_method(paths.eval_gt, paths.model_outputs, "diff_", "ressrdiff", factor=profile.stride, case_names=eval_names)
    )
    rows.extend(
        evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names)
    )
    rows.extend(
        evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names)
    )
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, paths.model_outputs, paths.baseline_linear, paths.metrics)
    print(f"IXI Res-SRDiff 2.5D pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
