from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(os.environ.get("MRI_PROJECT_ROOT", str(Path(__file__).resolve().parents[2])))
DATA_ROOT = Path(
    os.environ.get(
        "FASTMRI_BRAIN_GAN_DATA_ROOT",
        str(ROOT / "dataset" / "fastMRI_brain_T2" / "processed"),
    )
)
INDEX_PATH = DATA_ROOT / "metadata" / "fastmri_brain_nifti_cases.csv"
SPLIT_ROOT = DATA_ROOT / "splits" / "nifti_seed3407"
RUN_ROOT = Path(os.environ.get("FASTMRI_BRAIN_GAN_RUN_ROOT", str(ROOT / "fastmri_brain_gan_2p5d" / "runs")))
DATASET_NAME = os.environ.get("FASTMRI_BRAIN_GAN_DATASET_NAME", "fastMRI-brain-T2 expanded")
SOURCE_NOTE = os.environ.get(
    "FASTMRI_BRAIN_GAN_SOURCE_NOTE",
    "Inherited pix2pix/GAN baseline adapted to current T2-only through-plane protocol",
)


@dataclass(frozen=True)
class Profile:
    name: str
    train_cases: int | None = None
    val_cases: int | None = None
    test_cases: int | None = None
    epochs: int = 1
    batch_size: int = 2
    patience: int = 2
    stride: int = 4
    target_shape: tuple[int, int] = (256, 256)
    num_workers: int = 0
    lr: float = 2e-4
    skip_training_if_checkpoint_exists: bool = True


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=1,
        patience=2,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=4,
        epochs=3,
        batch_size=2,
        patience=3,
        skip_training_if_checkpoint_exists=False,
    ),
    "full": Profile(
        name="full",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=4,
        patience=8,
        num_workers=0,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_x2": Profile(
        name="full_x2",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=4,
        patience=8,
        stride=2,
        num_workers=0,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_x6": Profile(
        name="full_x6",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=4,
        patience=8,
        stride=6,
        num_workers=0,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_stable": Profile(
        name="full_stable",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=60,
        batch_size=4,
        patience=12,
        num_workers=0,
        lr=1e-4,
        skip_training_if_checkpoint_exists=False,
    ),
}


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    checkpoints: Path
    metrics: Path
    eval_sparse: Path
    eval_gt: Path
    model_outputs: Path
    baseline_linear: Path
    baseline_cubic: Path


def build_paths(profile: str) -> RunPaths:
    run_dir = RUN_ROOT / profile
    return RunPaths(
        run_dir=run_dir,
        checkpoints=run_dir / "checkpoints",
        metrics=run_dir / "metrics",
        eval_sparse=run_dir / "eval_sparse",
        eval_gt=run_dir / "eval_gt",
        model_outputs=run_dir / "model_outputs",
        baseline_linear=run_dir / "baseline_outputs" / "linear",
        baseline_cubic=run_dir / "baseline_outputs" / "cubic",
    )
