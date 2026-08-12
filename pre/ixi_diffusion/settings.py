from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
IXI_ROOT = Path(os.environ.get("IXI_DATA_ROOT", str(PROJECT_ROOT / "dataset" / "IXI")))
if not IXI_ROOT.exists():
    IXI_ROOT = ROOT / "dataset" / "IXI"


@dataclass(frozen=True)
class Profile:
    name: str
    modality: str
    train_cases: int | None
    val_cases: int | None
    test_cases: int | None
    epochs: int
    batch_size: int
    diffusion_steps: int
    sample_steps: int
    patience: int
    stride: int = 4
    method: str = "pure_noise"
    num_workers: int = 0
    skip_training_if_checkpoint_exists: bool = False


PROFILES = {
    "smoke": Profile(
        name="smoke",
        modality="PD",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=4,
        diffusion_steps=100,
        sample_steps=10,
        patience=2,
        skip_training_if_checkpoint_exists=True,
    ),
    "mini": Profile(
        name="mini",
        modality="PD",
        train_cases=32,
        val_cases=8,
        test_cases=5,
        epochs=5,
        batch_size=12,
        diffusion_steps=300,
        sample_steps=20,
        patience=3,
    ),
    "full": Profile(
        name="full",
        modality="PD",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=16,
        diffusion_steps=1000,
        sample_steps=30,
        patience=6,
    ),
    "hifidiff_smoke": Profile(
        name="hifidiff_smoke",
        modality="PD",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=2,
        batch_size=8,
        diffusion_steps=100,
        sample_steps=10,
        patience=2,
        method="hifidiff_residual",
    ),
    "hifidiff_mini": Profile(
        name="hifidiff_mini",
        modality="PD",
        train_cases=6,
        val_cases=2,
        test_cases=2,
        epochs=3,
        batch_size=32,
        diffusion_steps=150,
        sample_steps=8,
        patience=4,
        method="hifidiff_residual",
        skip_training_if_checkpoint_exists=True,
    ),
    "hifidiff_mini_eval": Profile(
        name="hifidiff_mini_eval",
        modality="PD",
        train_cases=6,
        val_cases=2,
        test_cases=2,
        epochs=3,
        batch_size=32,
        diffusion_steps=150,
        sample_steps=8,
        patience=4,
        method="hifidiff_residual",
        skip_training_if_checkpoint_exists=True,
    ),
    "hifidiff_full": Profile(
        name="hifidiff_full",
        modality="PD",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=40,
        batch_size=96,
        diffusion_steps=500,
        sample_steps=25,
        patience=8,
        method="hifidiff_residual",
        num_workers=4,
    ),
    "resunet_smoke": Profile(
        name="resunet_smoke",
        modality="PD",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=2,
        batch_size=16,
        diffusion_steps=0,
        sample_steps=0,
        patience=2,
        method="resunet_residual",
    ),
    "resunet_mini": Profile(
        name="resunet_mini",
        modality="PD",
        train_cases=24,
        val_cases=6,
        test_cases=5,
        epochs=8,
        batch_size=64,
        diffusion_steps=0,
        sample_steps=0,
        patience=4,
        method="resunet_residual",
        num_workers=2,
    ),
    "resunet_full": Profile(
        name="resunet_full",
        modality="PD",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=96,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        method="resunet_residual",
        num_workers=4,
    ),
    "resunet_full_t1": Profile(
        name="resunet_full_t1",
        modality="T1",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=96,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        method="resunet_residual",
        num_workers=4,
    ),
    "resunet_full_t2": Profile(
        name="resunet_full_t2",
        modality="T2",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=96,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        method="resunet_residual",
        num_workers=4,
    ),
    "resunet_full_t2_test115": Profile(
        name="resunet_full_t2_test115",
        modality="T2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=96,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        method="resunet_residual",
        num_workers=0,
    ),
    "resunet_full_t2_test115_x2": Profile(
        name="resunet_full_t2_test115_x2",
        modality="T2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=96,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        stride=2,
        method="resunet_residual",
        num_workers=0,
    ),
    "resunet_full_t2_test115_x6": Profile(
        name="resunet_full_t2_test115_x6",
        modality="T2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=96,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        stride=6,
        method="resunet_residual",
        num_workers=0,
    ),
    "saint_smoke": Profile(
        name="saint_smoke",
        modality="PD",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=2,
        batch_size=16,
        diffusion_steps=0,
        sample_steps=0,
        patience=2,
        method="saint_spatial_aware",
        skip_training_if_checkpoint_exists=True,
    ),
    "saint_mini": Profile(
        name="saint_mini",
        modality="PD",
        train_cases=32,
        val_cases=8,
        test_cases=5,
        epochs=8,
        batch_size=48,
        diffusion_steps=0,
        sample_steps=0,
        patience=4,
        method="saint_spatial_aware",
        num_workers=2,
    ),
    "saint_full": Profile(
        name="saint_full",
        modality="PD",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=64,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        method="saint_spatial_aware",
        num_workers=4,
    ),
    "saint_full_t2": Profile(
        name="saint_full_t2",
        modality="T2",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=48,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        method="saint_spatial_aware",
        num_workers=2,
    ),
    "saint_full_t2_test115": Profile(
        name="saint_full_t2_test115",
        modality="T2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=48,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        method="saint_spatial_aware",
        num_workers=0,
    ),
    "saint_full_t2_test115_x2": Profile(
        name="saint_full_t2_test115_x2",
        modality="T2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=48,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        stride=2,
        method="saint_spatial_aware",
        num_workers=0,
    ),
    "saint_full_t2_test115_x6": Profile(
        name="saint_full_t2_test115_x6",
        modality="T2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=48,
        diffusion_steps=0,
        sample_steps=0,
        patience=8,
        stride=6,
        method="saint_spatial_aware",
        num_workers=0,
    ),
}


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    checkpoints: Path
    metrics: Path
    eval_sparse: Path
    eval_gt: Path
    diffusion_outputs: Path
    baseline_linear: Path
    baseline_cubic: Path


def build_paths(profile: str) -> RunPaths:
    run_dir = ROOT / "ixi_diffusion" / "runs" / profile
    return RunPaths(
        run_dir=run_dir,
        checkpoints=run_dir / "checkpoints",
        metrics=run_dir / "metrics",
        eval_sparse=run_dir / "eval_inputs" / "sparse",
        eval_gt=run_dir / "eval_inputs" / "gt",
        diffusion_outputs=run_dir / "diffusion_outputs",
        baseline_linear=run_dir / "baseline_outputs" / "linear",
        baseline_cubic=run_dir / "baseline_outputs" / "cubic",
    )
