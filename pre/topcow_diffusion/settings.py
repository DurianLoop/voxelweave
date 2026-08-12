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
    diffusion_steps: int
    sample_steps: int
    skip_training_if_checkpoint_exists: bool
    train_fraction: float = 0.8
    patience: int = 8


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_limit=10,
        val_limit=2,
        epochs=1,
        batch_size=1,
        diffusion_steps=100,
        sample_steps=10,
        skip_training_if_checkpoint_exists=True,
        train_fraction=0.8,
        patience=3,
    ),
    "quick_smoke": Profile(
        name="quick_smoke",
        train_limit=4,
        val_limit=1,
        epochs=1,
        batch_size=1,
        diffusion_steps=20,
        sample_steps=2,
        skip_training_if_checkpoint_exists=True,
        train_fraction=0.75,
        patience=2,
    ),
    "full": Profile(
        name="full",
        train_limit=None,
        val_limit=None,
        epochs=30,
        batch_size=16,
        diffusion_steps=1000,
        sample_steps=20,
        skip_training_if_checkpoint_exists=False,
        train_fraction=0.8,
        patience=5,
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
    diffusion_outputs: Path
    baseline_linear: Path
    baseline_cubic: Path
    labeled_sparse: Path
    labeled_gt: Path
    labeled_labels: Path
    labeled_diffusion_outputs: Path
    labeled_baseline_linear: Path
    labeled_baseline_cubic: Path
    metrics: Path


def build_paths(profile: str) -> RunPaths:
    run_dir = ROOT / "topcow_diffusion" / "runs" / profile
    return RunPaths(
        run_dir=run_dir,
        train_links=run_dir / "train_mr_links",
        val_links=run_dir / "val_mr_links",
        checkpoints=run_dir / "checkpoints",
        training_plots=run_dir / "training_plots",
        eval_sparse=run_dir / "eval_inputs" / "sparse",
        eval_gt=run_dir / "eval_inputs" / "gt",
        diffusion_outputs=run_dir / "diffusion_outputs",
        baseline_linear=run_dir / "baseline_outputs" / "linear",
        baseline_cubic=run_dir / "baseline_outputs" / "cubic",
        labeled_sparse=run_dir / "labeled_eval" / "inputs" / "sparse",
        labeled_gt=run_dir / "labeled_eval" / "inputs" / "gt",
        labeled_labels=run_dir / "labeled_eval" / "labels",
        labeled_diffusion_outputs=run_dir / "labeled_eval" / "diffusion_outputs",
        labeled_baseline_linear=run_dir / "labeled_eval" / "baseline_outputs" / "linear",
        labeled_baseline_cubic=run_dir / "labeled_eval" / "baseline_outputs" / "cubic",
        metrics=run_dir / "metrics",
    )
