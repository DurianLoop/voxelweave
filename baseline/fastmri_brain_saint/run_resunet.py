from __future__ import annotations

import argparse
import stat
from pathlib import Path

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from ixi_diffusion.common import ensure_dir, write_json
from ixi_diffusion.inference import write_intensity_sanity
from ixi_diffusion.resunet import ResUNetResidualInterpolator

from .resunet import train_resunet
from .run_all import _prepare_eval_inputs
from .settings import DATA_ROOT, PROFILES, RUN_ROOT, build_paths


def _clear_generated_files(paths, model_outputs: Path) -> None:
    for folder in [
        paths.eval_sparse,
        paths.eval_gt,
        model_outputs,
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


def _dataset_metadata() -> tuple[str, str, str]:
    data_root_text = str(DATA_ROOT)
    if "NingXiaData" in data_root_text:
        return "NingXia_T2", "T2", "Local external NingXia T2 knee MRI; supervisor-confirmed T2 protocol."
    if "fastMRI_brain_T2" in data_root_text:
        return "fastMRI_brain_T2", "T2", "Strict T2 series selected from readable DICOM sequence labels."
    return (
        "fastMRI_brain_DICOM",
        "unknown_from_local_dicom_header",
        "Do not treat the whole fastMRI brain DICOM subset as T2-only until sequence filtering is confirmed.",
    )


def run(profile_name: str, evaluate_only: bool = False) -> None:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    model_outputs = paths.run_dir / "resunet_outputs"
    dataset_label, modality_label, contrast_note = _dataset_metadata()
    for path in [
        paths.run_dir,
        paths.checkpoints,
        paths.metrics,
        paths.eval_sparse,
        paths.eval_gt,
        model_outputs,
        paths.baseline_linear,
        paths.baseline_cubic,
    ]:
        ensure_dir(path)
    _clear_generated_files(paths, model_outputs)

    eval_manifest = _prepare_eval_inputs(paths, profile)
    eval_names = {row["case"] for row in eval_manifest}
    write_json(
        paths.run_dir / "run_manifest.json",
        {
            "profile": profile.name,
            "dataset": dataset_label,
            "data_root": str(DATA_ROOT),
            "run_root": str(RUN_ROOT),
            "modality": modality_label,
            "contrast_note": contrast_note,
            "sampling": "resunet_residual",
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "stride": profile.stride,
            "eval_cases": eval_manifest,
        },
    )

    checkpoint = paths.checkpoints / "resunet_epoch_best.pth"
    if evaluate_only:
        if not checkpoint.exists():
            raise FileNotFoundError(f"Evaluation-only requested but checkpoint is missing: {checkpoint}")
    else:
        checkpoint = train_resunet(paths, profile)
    interpolator = ResUNetResidualInterpolator(checkpoint)
    interpolator.process_folder(paths.eval_sparse, model_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(evaluate_method(paths.eval_gt, model_outputs, "diff_", "resunet", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names))
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, model_outputs, paths.baseline_linear, paths.metrics)
    print(f"fastMRI brain ResUNet pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument("--evaluate-only", action="store_true", help="Evaluate an existing best checkpoint without retraining.")
    args = parser.parse_args()
    run(args.profile, evaluate_only=args.evaluate_only)


if __name__ == "__main__":
    main()
