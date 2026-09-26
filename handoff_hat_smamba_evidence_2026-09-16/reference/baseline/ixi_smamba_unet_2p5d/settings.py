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
    num_workers: int = 0
    lr: float = 2e-4
    embed_dim: int = 48
    depths: tuple[int, ...] = (2, 2, 2)
    num_heads: tuple[int, ...] = (3, 3, 3)
    window_size: int = 8
    mlp_ratio: float = 2.0
    residual_scale: float = 1.0
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
        embed_dim=24,
        depths=(1, 1),
        num_heads=(3, 3),
        window_size=8,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=5,
        epochs=5,
        batch_size=12,
        patience=3,
        embed_dim=36,
        depths=(2, 2),
        num_heads=(3, 3),
        window_size=8,
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
        embed_dim=48,
        depths=(2, 2, 2),
        num_heads=(3, 3, 3),
        window_size=8,
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
        embed_dim=48,
        depths=(2, 2, 2),
        num_heads=(3, 3, 3),
        window_size=8,
        skip_training_if_checkpoint_exists=True,
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
        embed_dim=48,
        depths=(2, 2, 2),
        num_heads=(3, 3, 3),
        window_size=8,
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
        embed_dim=48,
        depths=(2, 2, 2),
        num_heads=(3, 3, 3),
        window_size=8,
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
    run_dir = ROOT / "ixi_smamba_unet_2p5d" / "runs" / profile
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
