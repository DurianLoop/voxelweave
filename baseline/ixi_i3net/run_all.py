from __future__ import annotations

import argparse
import stat
from pathlib import Path

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from ixi_diffusion.common import ensure_dir, write_json
from ixi_diffusion.inference import write_intensity_sanity
from ixi_diffusion.stage_data import prepare_eval_inputs

from .settings import PROFILES, build_paths
from .train import I3NetInterpolator, train_i3net


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


def run(profile_name: str, eval_only_checkpoint: Path | None = None) -> None:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    condition = f"{profile.lr_slice_patch} sparse through-plane slices -> {profile.hr_slice_patch} HR slices for x{profile.stride}"
    source_note = f"I3Net TMI 2024 official architecture, local IXI-T2 x{profile.stride} reproduction"
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
            "sampling": "i3net_inter_intra_slice_window",
            "source": source_note,
            "paper": "I3Net: Inter-Intra-slice Interpolation Network for Medical Slice Synthesis",
            "paper_url": "https://doi.org/10.1109/TMI.2024.3394033",
            "code_url": "https://github.com/DeepMed-Lab-ECNU/Medical-Image-Reconstruction",
            "condition": condition,
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "patience": profile.patience,
            "lr": profile.lr,
            "weight_decay": profile.weight_decay,
            "amp": profile.amp,
            "stride": profile.stride,
            "lr_slice_patch": profile.lr_slice_patch,
            "hr_slice_patch": profile.hr_slice_patch,
            "n_feats": profile.n_feats,
            "num_blocks": profile.num_blocks,
            "window_step": profile.window_step,
            "shuffle_windows": profile.shuffle_windows,
            "cache_resized_volumes": profile.cache_resized_volumes,
            "cache_items": profile.cache_items,
            "eval_cases": eval_manifest,
            "table_ready": profile.name
            in {
                "full",
                "full_test115",
                "full_test115_stable",
                "full_test115_x2",
                "full_test115_x2_fast",
                "full_test115_x6",
                "full_test115_x6_fast",
            },
            "eval_only_checkpoint": str(eval_only_checkpoint) if eval_only_checkpoint is not None else None,
        },
    )

    if eval_only_checkpoint is not None:
        checkpoint = eval_only_checkpoint
        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)
    else:
        checkpoint = train_i3net(paths, profile)
    interpolator = I3NetInterpolator(checkpoint)
    interpolator.process_folder(paths.eval_sparse, paths.model_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(evaluate_method(paths.eval_gt, paths.model_outputs, "diff_", "i3net", factor=profile.stride, case_names=eval_names))
    rows.extend(
        evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names)
    )
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names))
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, paths.model_outputs, paths.baseline_linear, paths.metrics)
    print(f"IXI I3Net pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument(
        "--eval-only-checkpoint",
        type=Path,
        default=None,
        help="Evaluate an existing I3Net checkpoint without training.",
    )
    args = parser.parse_args()
    run(args.profile, eval_only_checkpoint=args.eval_only_checkpoint)


if __name__ == "__main__":
    main()
