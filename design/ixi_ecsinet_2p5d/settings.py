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
    batch_size: int = 16
    patience: int = 2
    stride: int = 4
    target_shape: tuple[int, int] = (256, 256)
    num_workers: int = 0
    lr: float = 2e-4
    weight_decay: float = 1e-4
    amp: bool = True
    channels: int = 48
    num_blocks: int = 8
    expansion: int = 2
    kernel_size: int = 5
    residual_scale: float = 1.0
    mask_bias: float = -2.0
    lambda_grad: float = 0.05
    lambda_residual: float = 0.001
    lambda_mask: float = 0.001
    lambda_prior: float = 0.01
    skip_training_if_checkpoint_exists: bool = True


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=2,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=8,
        patience=2,
        channels=32,
        num_blocks=4,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=5,
        epochs=5,
        batch_size=32,
        patience=3,
        channels=48,
        num_blocks=8,
        skip_training_if_checkpoint_exists=False,
    ),
    "profile32_b6": Profile(
        name="profile32_b6",
        train_cases=16,
        val_cases=4,
        test_cases=5,
        epochs=3,
        batch_size=64,
        patience=3,
        channels=32,
        num_blocks=6,
        skip_training_if_checkpoint_exists=False,
    ),
    "profile48_b8": Profile(
        name="profile48_b8",
        train_cases=16,
        val_cases=4,
        test_cases=5,
        epochs=3,
        batch_size=32,
        patience=3,
        channels=48,
        num_blocks=8,
        skip_training_if_checkpoint_exists=False,
    ),
    "full": Profile(
        name="full",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=48,
        patience=8,
        num_workers=2,
        channels=48,
        num_blocks=8,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=48,
        patience=8,
        num_workers=0,
        channels=48,
        num_blocks=8,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115_x2": Profile(
        name="full_test115_x2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=64,
        patience=8,
        stride=2,
        num_workers=0,
        channels=48,
        num_blocks=8,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x6": Profile(
        name="full_test115_x6",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=32,
        patience=8,
        stride=6,
        num_workers=0,
        channels=48,
        num_blocks=8,
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
    run_dir = ROOT / "ixi_ecsinet_2p5d" / "runs" / profile
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

