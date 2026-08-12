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
    grad_accum_steps: int = 1
    patience: int = 2
    stride: int = 4
    lr_slice_patch: int = 4
    target_shape: tuple[int, int] = (256, 256)
    window_step: int = 4
    num_workers: int = 0
    lr: float = 2e-4
    weight_decay: float = 1e-4
    amp: bool = True
    base_channels: int = 32
    num_blocks: int = 6
    z_refine_channels: int = 8
    mlp_ratio: float = 2.0
    residual_scale: float = 0.5
    lambda_grad_xy: float = 0.05
    lambda_zgrad: float = 0.08
    lambda_zlap: float = 0.04
    lambda_edge_z: float = 0.08
    lambda_z_ncc: float = 0.0
    lambda_anat: float = 0.05
    lambda_res: float = 0.001
    cache_resized_volumes: bool = False
    cache_items: int = 3
    skip_training_if_checkpoint_exists: bool = True

    @property
    def hr_slice_patch(self) -> int:
        return self.stride * (self.lr_slice_patch - 1) + 1


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=2,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=1,
        patience=2,
        target_shape=(128, 128),
        window_step=8,
        base_channels=16,
        num_blocks=3,
        z_refine_channels=4,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=8,
        val_cases=2,
        test_cases=2,
        epochs=3,
        batch_size=1,
        grad_accum_steps=2,
        patience=3,
        target_shape=(192, 192),
        window_step=4,
        base_channels=24,
        num_blocks=5,
        z_refine_channels=6,
        cache_resized_volumes=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini_consistency": Profile(
        name="mini_consistency",
        train_cases=8,
        val_cases=2,
        test_cases=2,
        epochs=8,
        batch_size=1,
        grad_accum_steps=2,
        patience=4,
        target_shape=(192, 192),
        window_step=4,
        base_channels=24,
        num_blocks=5,
        z_refine_channels=6,
        lambda_zgrad=0.14,
        lambda_zlap=0.06,
        lambda_edge_z=0.14,
        lambda_z_ncc=0.12,
        cache_resized_volumes=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=40,
        batch_size=1,
        grad_accum_steps=4,
        patience=10,
        num_workers=0,
        lr=1e-4,
        base_channels=32,
        num_blocks=8,
        z_refine_channels=8,
        window_step=2,
        cache_resized_volumes=True,
        cache_items=6,
        skip_training_if_checkpoint_exists=True,
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
    run_dir = ROOT / "acsinet_v2" / "runs" / profile
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
