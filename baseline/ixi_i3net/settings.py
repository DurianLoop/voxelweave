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
    patience: int = 2
    stride: int = 4
    lr_slice_patch: int = 4
    target_shape: tuple[int, int] = (256, 256)
    window_step: int = 2
    num_workers: int = 0
    lr: float = 2e-4
    weight_decay: float = 1e-4
    amp: bool = True
    kernel_size: int = 3
    n_feats: int = 64
    num_blocks: int = 16
    res_scale: float = 1.0
    head_num: int = 1
    window_size: int = 16
    win_num_sqrt: int = 16
    skip_training_if_checkpoint_exists: bool = True
    shuffle_windows: bool = True
    cache_resized_volumes: bool = False
    cache_items: int = 3

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
        n_feats=16,
        num_blocks=16,
        window_step=8,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=8,
        val_cases=2,
        test_cases=2,
        epochs=3,
        batch_size=1,
        patience=3,
        n_feats=32,
        num_blocks=16,
        window_step=4,
        skip_training_if_checkpoint_exists=False,
    ),
    "full": Profile(
        name="full",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=1,
        patience=8,
        num_workers=0,
        n_feats=64,
        num_blocks=16,
        window_step=2,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=1,
        patience=8,
        num_workers=0,
        n_feats=64,
        num_blocks=16,
        window_step=2,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115_stable": Profile(
        name="full_test115_stable",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=60,
        batch_size=1,
        patience=12,
        num_workers=0,
        lr=5e-5,
        amp=False,
        n_feats=64,
        num_blocks=16,
        window_step=2,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x2": Profile(
        name="full_test115_x2",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=60,
        batch_size=1,
        patience=12,
        stride=2,
        num_workers=0,
        lr=5e-5,
        amp=False,
        n_feats=64,
        num_blocks=16,
        window_step=2,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x2_fast": Profile(
        name="full_test115_x2_fast",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=60,
        batch_size=4,
        patience=12,
        stride=2,
        num_workers=0,
        lr=5e-5,
        amp=False,
        n_feats=64,
        num_blocks=16,
        window_step=2,
        skip_training_if_checkpoint_exists=False,
        shuffle_windows=False,
        cache_resized_volumes=True,
        cache_items=8,
    ),
    "full_test115_x6": Profile(
        name="full_test115_x6",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=60,
        batch_size=1,
        patience=12,
        stride=6,
        num_workers=0,
        lr=5e-5,
        amp=False,
        n_feats=64,
        num_blocks=16,
        window_step=2,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x6_fast": Profile(
        name="full_test115_x6_fast",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=60,
        batch_size=2,
        patience=12,
        stride=6,
        num_workers=0,
        lr=5e-5,
        amp=False,
        n_feats=64,
        num_blocks=16,
        window_step=2,
        skip_training_if_checkpoint_exists=False,
        shuffle_windows=False,
        cache_resized_volumes=True,
        cache_items=8,
    ),
    "stable_smoke_x2": Profile(
        name="stable_smoke_x2",
        train_cases=8,
        val_cases=2,
        test_cases=2,
        epochs=8,
        batch_size=1,
        patience=4,
        stride=2,
        num_workers=0,
        lr=1e-4,
        amp=False,
        n_feats=64,
        num_blocks=16,
        window_step=8,
        skip_training_if_checkpoint_exists=False,
    ),
    "stable_smoke_x6": Profile(
        name="stable_smoke_x6",
        train_cases=8,
        val_cases=2,
        test_cases=2,
        epochs=8,
        batch_size=1,
        patience=4,
        stride=6,
        num_workers=0,
        lr=1e-4,
        amp=False,
        n_feats=64,
        num_blocks=16,
        window_step=8,
        skip_training_if_checkpoint_exists=False,
    ),
    "stable_smoke": Profile(
        name="stable_smoke",
        train_cases=8,
        val_cases=2,
        test_cases=2,
        epochs=8,
        batch_size=1,
        patience=4,
        num_workers=0,
        lr=1e-4,
        amp=False,
        n_feats=64,
        num_blocks=16,
        window_step=8,
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
    run_dir = ROOT / "ixi_i3net" / "runs" / profile
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
