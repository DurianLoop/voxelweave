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
    num_workers: int = 0
    lr: float = 5e-5
    model_channels: int = 32
    num_res_blocks: tuple[int, ...] = (1, 1, 1, 1)
    attention_resolutions: tuple[int, ...] = (32, 16)
    steps: int = 4
    use_amp: bool = True
    preload_resized: bool = False
    skip_training_if_checkpoint_exists: bool = True


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=2,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=1,
        model_channels=32,
        attention_resolutions=(16,),
        steps=2,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=5,
        epochs=5,
        batch_size=2,
        grad_accum_steps=6,
        patience=3,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_safe": Profile(
        name="full_test115_safe",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=8,
        grad_accum_steps=3,
        patience=8,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        use_amp=True,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115": Profile(
        name="full_test115",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=24,
        grad_accum_steps=1,
        patience=8,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        use_amp=True,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_fast": Profile(
        name="full_test115_fast",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=32,
        grad_accum_steps=1,
        patience=8,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        use_amp=True,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x2": Profile(
        name="full_test115_x2",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=24,
        grad_accum_steps=1,
        patience=8,
        stride=2,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        use_amp=True,
        preload_resized=True,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_test115_x6": Profile(
        name="full_test115_x6",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=24,
        grad_accum_steps=1,
        patience=8,
        stride=6,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        use_amp=True,
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
    run_dir = ROOT / "ixi_ressrdiff_2p5d" / "runs" / profile
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
