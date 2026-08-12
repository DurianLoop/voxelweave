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
    batch_size: int = 4
    grad_accum_steps: int = 1
    patience: int = 2
    stride: int = 4
    num_workers: int = 0
    lr: float = 2e-4
    num_level: int = 3
    num_channel: int = 32
    num_block: int = 1
    transfer_level: tuple[int, ...] = (0, 1, 2)
    block_size_per_level: tuple[int, ...] = (8, 4, 2)
    preload_resized: bool = False
    skip_training_if_checkpoint_exists: bool = True


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=2,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=2,
        patience=2,
        num_channel=16,
        transfer_level=(0, 1),
        block_size_per_level=(8, 4),
        num_level=2,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=5,
        epochs=5,
        batch_size=24,
        grad_accum_steps=1,
        patience=3,
        num_channel=24,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=48,
        grad_accum_steps=1,
        patience=8,
        num_channel=32,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_b64": Profile(
        name="full_test115_b64",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=64,
        grad_accum_steps=1,
        patience=8,
        num_channel=32,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x2": Profile(
        name="full_test115_x2",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=64,
        grad_accum_steps=1,
        patience=8,
        stride=2,
        num_channel=32,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x6": Profile(
        name="full_test115_x6",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=64,
        grad_accum_steps=1,
        patience=8,
        stride=6,
        num_channel=32,
        preload_resized=True,
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
    run_dir = ROOT / "ixi_acvtt_2p5d" / "runs" / profile
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
