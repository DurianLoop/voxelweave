from __future__ import annotations

import argparse
import stat

import numpy as np

from topcow_diffusion.baselines import run_baseline_folder
from topcow_diffusion.metrics import evaluate_method, write_metric_outputs

from ixi_diffusion.common import ensure_dir, load_nifti, save_nifti, write_json
from ixi_diffusion.inference import write_intensity_sanity
from ixi_diffusion.saint import SAINTInterpolator

from .data import case_paths
from .settings import DATA_ROOT, PROFILES, RUN_ROOT, build_paths
from .train import train_saint


def _clear_generated_files(paths) -> None:
    for folder in [
        paths.eval_sparse,
        paths.eval_gt,
        paths.saint_outputs,
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
        sparse_name = f"{src.name.removesuffix('.nii.gz')}.nii.gz"
        save_nifti(sparse.astype(np.float32), affine, header, paths.eval_sparse / sparse_name)
        save_nifti(gt.astype(np.float32), affine, header, paths.eval_gt / sparse_name)
        manifest.append(
            {
                "case": sparse_name,
                "source": str(src),
                "source_depth": int(volume.shape[2]),
                "sparse_depth": int(sparse.shape[2]),
                "target_depth": int(gt.shape[2]),
                "stride": profile.stride,
            }
        )
    if not manifest:
        raise RuntimeError("No fastMRI brain test cases available for evaluation.")
    return manifest


def run(profile_name: str) -> None:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    data_root_text = str(DATA_ROOT)
    is_strict_t2 = "fastMRI_brain_T2" in data_root_text
    is_ningxia_t2 = "NingXiaData" in data_root_text
    if is_ningxia_t2:
        dataset_label = "NingXia_T2"
        modality_label = "T2"
        contrast_note = "Local external NingXia T2 knee MRI; supervisor-confirmed T2 protocol."
    elif is_strict_t2:
        dataset_label = "fastMRI_brain_T2"
        modality_label = "T2"
        contrast_note = "Strict T2 series selected from readable DICOM sequence labels."
    else:
        dataset_label = "fastMRI_brain_DICOM"
        modality_label = "unknown_from_local_dicom_header"
        contrast_note = "Do not treat the whole fastMRI brain DICOM subset as T2-only until sequence filtering is confirmed."
    for path in [
        paths.run_dir,
        paths.checkpoints,
        paths.metrics,
        paths.eval_sparse,
        paths.eval_gt,
        paths.saint_outputs,
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
            "dataset": dataset_label,
            "data_root": str(DATA_ROOT),
            "run_root": str(RUN_ROOT),
            "modality": modality_label,
            "contrast_note": contrast_note,
            "sampling": "saint_spatial_aware",
            "train_cases": profile.train_cases,
            "val_cases": profile.val_cases,
            "test_cases": profile.test_cases,
            "epochs": profile.epochs,
            "batch_size": profile.batch_size,
            "stride": profile.stride,
            "eval_cases": eval_manifest,
        },
    )

    checkpoint = train_saint(paths, profile)
    interpolator = SAINTInterpolator(checkpoint)
    interpolator.process_folder(paths.eval_sparse, paths.saint_outputs, stride=profile.stride)
    run_baseline_folder(paths.eval_sparse, paths.baseline_linear, factor=profile.stride, kind="linear")
    run_baseline_folder(paths.eval_sparse, paths.baseline_cubic, factor=profile.stride, kind="cubic")

    rows = []
    rows.extend(evaluate_method(paths.eval_gt, paths.saint_outputs, "diff_", "saint", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_linear, "linear_", "linear", factor=profile.stride, case_names=eval_names))
    rows.extend(evaluate_method(paths.eval_gt, paths.baseline_cubic, "cubic_", "cubic", factor=profile.stride, case_names=eval_names))
    write_metric_outputs(paths.metrics, rows)
    write_intensity_sanity(paths.eval_gt, paths.saint_outputs, paths.baseline_linear, paths.metrics)
    print(f"fastMRI brain SAINT pipeline finished: {paths.run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    args = parser.parse_args()
    run(args.profile)


if __name__ == "__main__":
    main()
