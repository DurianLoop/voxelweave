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
    batch_size: int = 8
    grad_accum_steps: int = 1
    patience: int = 2
    stride: int = 4
    target_shape: tuple[int, int] = (256, 256)
    num_workers: int = 0
    lr: float = 2e-4
    weight_decay: float = 1e-4
    amp: bool = True
    base_channels: int = 48
    num_blocks: int = 8
    window_size: int = 8
    mlp_ratio: float = 2.0
    residual_scale: float = 1.0
    refine_scale: float = 0.5
    lambda_grad: float = 0.05
    lambda_res: float = 0.001
    lambda_sym: float = 0.01
    lambda_edge: float = 0.0
    lambda_mse: float = 0.0
    model_variant: str = "v1"
    train_samples_per_epoch: int | None = None
    val_samples_per_epoch: int | None = None
    skip_training_if_checkpoint_exists: bool = True


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=2,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=4,
        patience=2,
        base_channels=24,
        num_blocks=3,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=5,
        epochs=5,
        batch_size=8,
        patience=3,
        base_channels=40,
        num_blocks=6,
        skip_training_if_checkpoint_exists=False,
    ),
    "smoke_g07_ma3_wide": Profile(
        name="smoke_g07_ma3_wide",
        train_cases=2,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=2,
        grad_accum_steps=2,
        patience=2,
        lr=1.5e-4,
        base_channels=64,
        num_blocks=10,
        refine_scale=0.35,
        lambda_grad=0.04,
        lambda_res=0.0008,
        lambda_sym=0.004,
        lambda_edge=0.003,
        lambda_mse=0.25,
        model_variant="ma3",
        skip_training_if_checkpoint_exists=False,
    ),
    "full": Profile(
        name="full",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=8,
        grad_accum_steps=3,
        patience=8,
        num_workers=0,
        base_channels=48,
        num_blocks=8,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=8,
        grad_accum_steps=3,
        patience=8,
        num_workers=0,
        base_channels=48,
        num_blocks=8,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_g07_ma3_wide200_test115": Profile(
        name="full_g07_ma3_wide200_test115",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=200,
        batch_size=4,
        grad_accum_steps=4,
        patience=45,
        num_workers=0,
        lr=1.5e-4,
        weight_decay=1e-4,
        base_channels=64,
        num_blocks=10,
        refine_scale=0.35,
        lambda_grad=0.04,
        lambda_res=0.0008,
        lambda_sym=0.004,
        lambda_edge=0.003,
        lambda_mse=0.25,
        model_variant="ma3",
        train_samples_per_epoch=12000,
        val_samples_per_epoch=4096,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x2": Profile(
        name="full_test115_x2",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=8,
        grad_accum_steps=3,
        patience=8,
        stride=2,
        num_workers=0,
        base_channels=48,
        num_blocks=8,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x6": Profile(
        name="full_test115_x6",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=8,
        grad_accum_steps=3,
        patience=8,
        stride=6,
        num_workers=0,
        base_channels=48,
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
    run_dir = ROOT / "ixi_pastnet_2p5d" / "runs" / profile
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
