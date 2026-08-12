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
    batch_size: int = 2
    grad_accum_steps: int = 1
    patience: int = 2
    stride: int = 4
    target_shape: tuple[int, int] = (256, 256)
    window_step: int = 1
    num_workers: int = 0
    lr: float = 2e-4
    weight_decay: float = 1e-4
    amp: bool = True
    base_channels: int = 40
    num_blocks: int = 6
    mlp_ratio: float = 2.0
    residual_scale: float = 0.75
    lambda_unc: float = 0.5
    lambda_logvar: float = 0.02
    lambda_grad_xy: float = 0.05
    lambda_res: float = 0.001
    lambda_cal: float = 0.05
    preload_resized: bool = False
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
        target_shape=(128, 128),
        window_step=16,
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
        batch_size=4,
        grad_accum_steps=2,
        patience=3,
        window_step=2,
        base_channels=40,
        num_blocks=6,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=6,
        grad_accum_steps=4,
        patience=8,
        num_workers=0,
        base_channels=48,
        num_blocks=8,
        preload_resized=True,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115_x2": Profile(
        name="full_test115_x2",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=12,
        grad_accum_steps=2,
        patience=8,
        stride=2,
        num_workers=0,
        base_channels=48,
        num_blocks=8,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x6": Profile(
        name="full_test115_x6",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=4,
        grad_accum_steps=6,
        patience=8,
        stride=6,
        num_workers=0,
        base_channels=48,
        num_blocks=8,
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
    uncertainty_outputs: Path
    confidence_outputs: Path
    residual_outputs: Path
    baseline_linear: Path
    baseline_cubic: Path

    @property
    def diffusion_outputs(self) -> Path:
        return self.model_outputs


def build_paths(profile: str) -> RunPaths:
    run_dir = ROOT / "rasinet" / "runs" / profile
    return RunPaths(
        run_dir=run_dir,
        checkpoints=run_dir / "checkpoints",
        metrics=run_dir / "metrics",
        eval_sparse=run_dir / "eval_inputs" / "sparse",
        eval_gt=run_dir / "eval_inputs" / "gt",
        model_outputs=run_dir / "model_outputs",
        uncertainty_outputs=run_dir / "reliability_outputs" / "uncertainty",
        confidence_outputs=run_dir / "reliability_outputs" / "confidence",
        residual_outputs=run_dir / "reliability_outputs" / "residual",
        baseline_linear=run_dir / "baseline_outputs" / "linear",
        baseline_cubic=run_dir / "baseline_outputs" / "cubic",
    )
