from __future__ import annotations

import argparse

from .baselines import run_baseline_folder
from .common import ensure_dir, write_json
from .inference import DiffusionInterpolator
from .metrics import evaluate_labeled_method, evaluate_method, write_labeled_metric_outputs, write_metric_outputs
from .settings import PROFILES, build_paths
from .stage_data import prepare_eval_inputs, prepare_labeled_eval_inputs, stage_case_level_training
from .train import train_diffusion


def _run_inference(input_dir, output_dir, checkpoint, sample_steps) -> int:
    interpolator = DiffusionInterpolator(checkpoint, sample_steps=sample_steps)
    return interpolator.process_folder(input_dir, output_dir)


def run(profile_name: str) -> None:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    for path in [paths.run_dir, paths.checkpoints, paths.training_plots, paths.metrics]:
        ensure_dir(path)
    split_info = stage_case_level_training(paths, profile.train_limit, profile.train_fraction)
    eval_manifest = prepare_eval_inputs(paths, profile.val_limit, stride=4)
    labeled_manifest = prepare_labeled_eval_inputs(paths, stride=4)
    write_json(
        paths.run_dir / "run_manifest.json",
        {
            "profile": profile.name,
            "train_cases": len(split_info["train_cases"]),
            "case_level": True,
            "split": split_info,
            "eval_cases": eval_manifest,
            "labeled_eval_cases": labeled_manifest,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "diffusion_steps": profile.diffusion_steps,
            "sample_steps": profile.sample_steps,
        },
    )
    checkpoint = train_diffusion(paths, profile.epochs, profile.batch_size, profile.diffusion_steps, profile.patience, profile.skip_training_if_checkpoint_exists)
    _run_inference(paths.eval_sparse, paths.diffusion_outputs, checkpoint, profile.sample_steps)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=4, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=4, kind="cubic")
    rows = []
    rows.extend(evaluate_method(paths.eval_gt, paths.diffusion_outputs, "diff_", "diffusion", factor=4))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=4))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=4))
    write_metric_outputs(paths.metrics, rows)
    _run_inference(paths.labeled_sparse, paths.labeled_diffusion_outputs, checkpoint, profile.sample_steps)
    run_baseline_folder(paths.labeled_sparse, paths.labeled_baseline_linear, factor=4, kind="linear")
    run_baseline_folder(paths.labeled_sparse, paths.labeled_baseline_cubic, factor=4, kind="cubic")
    labeled_rows = []
    labeled_rows.extend(evaluate_labeled_method(paths.labeled_gt, paths.labeled_diffusion_outputs, paths.labeled_labels, "diff_", "diffusion", factor=4))
    labeled_rows.extend(evaluate_labeled_method(paths.labeled_gt, paths.labeled_baseline_linear, paths.labeled_labels, "linear_", "linear", factor=4))
    labeled_rows.extend(evaluate_labeled_method(paths.labeled_gt, paths.labeled_baseline_cubic, paths.labeled_labels, "cubic_", "cubic", factor=4))
    write_labeled_metric_outputs(paths.metrics, labeled_rows)
    print(f"Diffusion pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
