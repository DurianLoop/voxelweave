from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path


ROOT = Path(os.environ.get("MRI_PROJECT_ROOT", str(Path(__file__).resolve().parents[2])))
DATA_ROOT = Path(
    os.environ.get(
        "FASTMRI_BRAIN_RESSRDIFF_DATA_ROOT",
        str(ROOT / "dataset" / "fastMRI_brain_T2" / "processed"),
    )
)
INDEX_PATH = DATA_ROOT / "metadata" / "fastmri_brain_nifti_cases.csv"
SPLIT_ROOT = DATA_ROOT / "splits" / "nifti_seed3407"
RUN_ROOT = Path(os.environ.get("FASTMRI_BRAIN_RESSRDIFF_RUN_ROOT", str(ROOT / "fastmri_brain_ressrdiff_2p5d" / "runs")))
DATASET_NAME = os.environ.get("FASTMRI_BRAIN_RESSRDIFF_DATASET_NAME", "fastMRI-brain-T2 expanded")
SOURCE_NOTE = os.environ.get(
    "FASTMRI_BRAIN_RESSRDIFF_SOURCE_NOTE",
    "Official Res-SRDiff diffusion core adapted as coarse-to-target slice refinement",
)


@dataclass(frozen=True)
class Profile:
    name: str
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
    preload_resized: bool = True
    skip_training_if_checkpoint_exists: bool = True


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=1,
        batch_size=2,
        model_channels=32,
        attention_resolutions=(16,),
        steps=2,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=4,
        epochs=5,
        batch_size=4,
        grad_accum_steps=3,
        patience=3,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_safe": Profile(
        name="full_safe",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=4,
        grad_accum_steps=6,
        patience=8,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_tiny": Profile(
        name="full_tiny",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=2,
        grad_accum_steps=12,
        patience=8,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        skip_training_if_checkpoint_exists=False,
    ),
    "full": Profile(
        name="full",
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
        skip_training_if_checkpoint_exists=False,
    ),
    "full_x2": Profile(
        name="full_x2",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=2,
        grad_accum_steps=12,
        patience=8,
        stride=2,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_x6": Profile(
        name="full_x6",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=2,
        grad_accum_steps=12,
        patience=8,
        stride=6,
        model_channels=32,
        attention_resolutions=(32, 16),
        steps=4,
        skip_training_if_checkpoint_exists=False,
    ),
}

# Independent 60-epoch reruns used by the convergence audit; original runs remain intact.
PROFILES.update(
    {
        "full_extend60": replace(PROFILES["full"], name="full_extend60", epochs=60, patience=12, skip_training_if_checkpoint_exists=False),
        "full_x2_extend60": replace(PROFILES["full_x2"], name="full_x2_extend60", epochs=60, patience=12, skip_training_if_checkpoint_exists=False),
        "full_x6_extend60": replace(PROFILES["full_x6"], name="full_x6_extend60", epochs=60, patience=12, skip_training_if_checkpoint_exists=False),
        "full_x2_extend90": replace(PROFILES["full_x2"], name="full_x2_extend90", epochs=90, patience=16, skip_training_if_checkpoint_exists=False),
    }
)


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


def build_paths(profile_name: str) -> RunPaths:
    run_dir = RUN_ROOT / profile_name
    return RunPaths(
        run_dir=run_dir,
        checkpoints=run_dir / "checkpoints",
        metrics=run_dir / "metrics",
        eval_sparse=run_dir / "eval_sparse",
        eval_gt=run_dir / "eval_gt",
        model_outputs=run_dir / "model_outputs",
        baseline_linear=run_dir / "baseline_outputs" / "linear",
        baseline_cubic=run_dir / "baseline_outputs" / "cubic",
    )
