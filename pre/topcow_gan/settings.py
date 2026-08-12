from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .common import ROOT


@dataclass(frozen=True)
class Profile:
    name: str
    train_limit: int | None
    val_limit: int | None
    epochs: int
    batch_size: int
    skip_training_if_checkpoint_exists: bool
    case_level: bool = False
    train_fraction: float = 0.8
    patience: int = 8


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_limit=8,
        val_limit=2,
        epochs=1,
        batch_size=1,
        skip_training_if_checkpoint_exists=True,
    ),
    "full": Profile(
        name="full",
        train_limit=None,
        val_limit=None,
        epochs=50,
        batch_size=4,
        skip_training_if_checkpoint_exists=False,
    ),
    "case_smoke": Profile(
        name="case_smoke",
        train_limit=10,
        val_limit=2,
        epochs=1,
        batch_size=1,
        skip_training_if_checkpoint_exists=True,
        case_level=True,
        train_fraction=0.8,
        patience=3,
    ),
    "case_full": Profile(
        name="case_full",
        train_limit=None,
        val_limit=None,
        epochs=50,
        batch_size=4,
        skip_training_if_checkpoint_exists=False,
        case_level=True,
        train_fraction=0.8,
        patience=8,
    ),
    "case_struct_smoke": Profile(
        name="case_struct_smoke",
        train_limit=10,
        val_limit=2,
        epochs=1,
        batch_size=1,
        skip_training_if_checkpoint_exists=True,
        case_level=True,
        train_fraction=0.8,
        patience=3,
    ),
    "case_struct_full": Profile(
        name="case_struct_full",
        train_limit=None,
        val_limit=None,
        epochs=50,
        batch_size=4,
        skip_training_if_checkpoint_exists=False,
        case_level=True,
        train_fraction=0.8,
        patience=8,
    ),
}


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    train_links: Path
    val_links: Path
    checkpoints: Path
    training_plots: Path
    eval_sparse: Path
    eval_gt: Path
    gan_outputs: Path
    baseline_linear: Path
    baseline_cubic: Path
    labeled_sparse: Path
    labeled_gt: Path
    labeled_labels: Path
    labeled_gan_outputs: Path
    labeled_baseline_linear: Path
    labeled_baseline_cubic: Path
    metrics: Path


def build_paths(profile: str) -> RunPaths:
    run_dir = ROOT / "topcow_gan" / "runs" / profile
    return RunPaths(
        run_dir=run_dir,
        train_links=run_dir / "train_mr_links",
        val_links=run_dir / "val_mr_links",
        checkpoints=run_dir / "checkpoints",
        training_plots=run_dir / "training_plots",
        eval_sparse=run_dir / "eval_inputs" / "sparse",
        eval_gt=run_dir / "eval_inputs" / "gt",
        gan_outputs=run_dir / "gan_outputs",
        baseline_linear=run_dir / "baseline_outputs" / "linear",
        baseline_cubic=run_dir / "baseline_outputs" / "cubic",
        labeled_sparse=run_dir / "labeled_eval" / "inputs" / "sparse",
        labeled_gt=run_dir / "labeled_eval" / "inputs" / "gt",
        labeled_labels=run_dir / "labeled_eval" / "labels",
        labeled_gan_outputs=run_dir / "labeled_eval" / "gan_outputs",
        labeled_baseline_linear=run_dir / "labeled_eval" / "baseline_outputs" / "linear",
        labeled_baseline_cubic=run_dir / "labeled_eval" / "baseline_outputs" / "cubic",
        metrics=run_dir / "metrics",
    )
