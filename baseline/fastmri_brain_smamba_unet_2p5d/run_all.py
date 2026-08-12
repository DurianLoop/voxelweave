from __future__ import annotations

import argparse
import stat

import numpy as np

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from ixi_diffusion.common import ensure_dir, load_nifti, save_nifti, write_json
from ixi_diffusion.inference import write_intensity_sanity

from .data import case_paths
from .settings import DATA_ROOT, PROFILES, RUN_ROOT, build_paths
from .train import FastMRISMambaUNet2p5DInterpolator, train_smamba_unet


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
                        print(f"Warning: could not delete locked file, will overwrite or ignore if possible: {path}")


def _prepare_eval_inputs(paths, profile) -> list[dict]:
    ensure_dir(paths.eval_sparse)
    ensure_dir(paths.eval_gt)
    manifest = []
    for src in case_paths("test", profile.test_cases):
        volume, affine, header = load_nifti(src)
        sparse = volume[:, :, :: profile.stride]
        full_depth = (sparse.shape[2] - 1) * profile.stride + 1
        gt = volume[:, :, :full_depth]
        name = f"{src.name.removesuffix('.nii.gz')}.nii.gz"
        save_nifti(sparse.astype(np.float32), affine, header, paths.eval_sparse / name)
        save_nifti(gt.astype(np.float32), affine, header, paths.eval_gt / name)
        manifest.append(
            {
                "case": name,
                "source": str(src),
                "source_depth": int(volume.shape[2]),
                "sparse_depth": int(sparse.shape[2]),
                "target_depth": int(gt.shape[2]),
                "stride": profile.stride,
            }
        )
    if not manifest:
        raise RuntimeError("No fastMRI-brain-T2 test cases available for evaluation.")
    return manifest


def run(profile_name: str, evaluate_only: bool = False) -> None:
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

    eval_manifest = _prepare_eval_inputs(paths, profile)
    eval_names = {row["case"] for row in eval_manifest}
    write_json(
        paths.run_dir / "run_manifest.json",
        {
            "profile": profile.name,
            "dataset": "fastMRI-brain-T2 expanded",
            "data_root": str(DATA_ROOT),
            "run_root": str(RUN_ROOT),
            "modality": "T2",
            "sampling": "smamba_unet_2p5d_residual",
            "source": "ours SMamba-UNet/MambaIR-style 2.5D reproduction",
            "condition": "left/right adjacent sparse slices + linear coarse + relative position",
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "grad_accum_steps": profile.grad_accum_steps,
            "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
            "stride": profile.stride,
            "embed_dim": profile.embed_dim,
            "depths": profile.depths,
            "num_heads": profile.num_heads,
            "window_size": profile.window_size,
            "eval_cases": eval_manifest,
        },
    )

    checkpoint = paths.checkpoints / "smamba_unet_epoch_best.pth"
    if evaluate_only:
        if not checkpoint.exists():
            raise FileNotFoundError(f"Evaluation-only requested but checkpoint is missing: {checkpoint}")
    else:
        checkpoint = train_smamba_unet(paths, profile)
    interpolator = FastMRISMambaUNet2p5DInterpolator(checkpoint)
    interpolator.process_folder(paths.eval_sparse, paths.model_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(evaluate_method(paths.eval_gt, paths.model_outputs, "diff_", "smamba_unet", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names))
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, paths.model_outputs, paths.baseline_linear, paths.metrics)
    print(f"fastMRI brain SMamba-UNet/MambaIR-style 2.5D pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument("--evaluate-only", action="store_true", help="Evaluate an existing best checkpoint without retraining.")
    args = parser.parse_args()
    run(args.profile, evaluate_only=args.evaluate_only)


if __name__ == "__main__":
    main()
