from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Profile:
    name: str
    modality: str = "T2"
    train_cases: int | None = None
    val_cases: int | None = None
    test_cases: int | None = None
    epochs: int = 1
    batch_size: int = 1
    chunks_per_volume: int = 2
    samples_per_chunk: int = 2048
    cycle_samples_per_chunk: int = 1024
    val_samples: int = 8192
    patience: int = 2
    stride: int = 4
    num_workers: int = 0
    lr: float = 2e-4
    feature_channels: int = 24
    cycle_weight: float = 0.5
    skip_training_if_checkpoint_exists: bool = True


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=2,
        val_cases=1,
        test_cases=1,
        epochs=1,
        chunks_per_volume=1,
        samples_per_chunk=1024,
        cycle_samples_per_chunk=512,
        val_samples=2048,
        patience=2,
        feature_channels=16,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=5,
        epochs=8,
        chunks_per_volume=2,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=4096,
        patience=4,
        feature_channels=24,
        skip_training_if_checkpoint_exists=False,
    ),
    "full": Profile(
        name="full",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        chunks_per_volume=1,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=16384,
        patience=8,
        feature_channels=24,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        chunks_per_volume=1,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=16384,
        patience=8,
        feature_channels=24,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115_x2": Profile(
        name="full_test115_x2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        chunks_per_volume=1,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=16384,
        patience=8,
        stride=2,
        feature_channels=24,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x6": Profile(
        name="full_test115_x6",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        chunks_per_volume=1,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=16384,
        patience=8,
        stride=6,
        feature_channels=24,
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

    @property
    def diffusion_outputs(self) -> Path:
        return self.model_outputs


def build_paths(profile: str) -> RunPaths:
    run_dir = ROOT / "ixi_cycleinr" / "runs" / profile
    return RunPaths(
        run_dir=run_dir,
        checkpoints=run_dir / "checkpoints",
        metrics=run_dir / "metrics",
        eval_sparse=run_dir / "eval_inputs" / "sparse",
        eval_gt=run_dir / "eval_inputs" / "gt",
        model_outputs=run_dir / "model_outputs",
        baseline_linear=run_dir / "baseline_outputs" / "linear",
        baseline_cubic=run_dir / "baseline_outputs" / "cubic",
    )
