from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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
    target_size: int = 256
    base_channels: int = 48
    num_workers: int = 0
    skip_training_if_checkpoint_exists: bool = False


PROFILES = {
    "smoke": Profile(
        name="smoke",
        modality="PD",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=2,
        batch_size=8,
        diffusion_steps=100,
        sample_steps=12,
        patience=2,
        base_channels=32,
    ),
    "mini": Profile(
        name="mini",
        modality="PD",
        train_cases=24,
        val_cases=6,
        test_cases=5,
        epochs=8,
        batch_size=32,
        diffusion_steps=300,
        sample_steps=25,
        patience=4,
        base_channels=48,
        num_workers=2,
    ),
    "fixed_mini": Profile(
        name="fixed_mini",
        modality="PD",
        train_cases=24,
        val_cases=6,
        test_cases=5,
        epochs=8,
        batch_size=32,
        diffusion_steps=1000,
        sample_steps=50,
        patience=4,
        base_channels=48,
        num_workers=2,
    ),
    "fixed_debug": Profile(
        name="fixed_debug",
        modality="PD",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=3,
        batch_size=32,
        diffusion_steps=1000,
        sample_steps=50,
        patience=2,
        base_channels=32,
        num_workers=0,
    ),
    "full": Profile(
        name="full",
        modality="PD",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=40,
        batch_size=64,
        diffusion_steps=1000,
        sample_steps=50,
        patience=8,
        base_channels=64,
        num_workers=4,
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
    run_dir = ROOT / "ixi_hifidiff_strict" / "runs" / profile
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
