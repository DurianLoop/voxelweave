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
    patience: int = 2
    stride: int = 4
    target_shape: tuple[int, int] = (256, 256)
    num_workers: int = 0
    lr: float = 2e-4
    skip_training_if_checkpoint_exists: bool = True


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=2,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=1,
        patience=2,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=8,
        val_cases=2,
        test_cases=2,
        epochs=3,
        batch_size=2,
        patience=3,
        skip_training_if_checkpoint_exists=False,
    ),
    "full": Profile(
        name="full",
        train_cases=None,
        val_cases=None,
        test_cases=25,
        epochs=30,
        batch_size=64,
        patience=8,
        num_workers=0,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=64,
        patience=8,
        num_workers=0,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_test115_b64": Profile(
        name="full_test115_b64",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=64,
        patience=8,
        num_workers=0,
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
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x6": Profile(
        name="full_test115_x6",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=30,
        batch_size=64,
        patience=8,
        stride=6,
        num_workers=0,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_stable": Profile(
        name="full_test115_stable",
        train_cases=None,
        val_cases=None,
        test_cases=115,
        epochs=60,
        batch_size=64,
        patience=12,
        num_workers=0,
        lr=1e-4,
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


def build_paths(profile: str) -> RunPaths:
    run_dir = ROOT / "ixi_gan_2p5d" / "runs" / profile
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
