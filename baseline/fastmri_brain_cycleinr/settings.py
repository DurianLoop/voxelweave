from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path


ROOT = Path(os.environ.get("MRI_PROJECT_ROOT", str(Path(__file__).resolve().parents[2])))
DATA_ROOT = Path(
    os.environ.get(
        "FASTMRI_BRAIN_CYCLEINR_DATA_ROOT",
        str(ROOT / "dataset" / "fastMRI_brain_T2" / "processed"),
    )
)
INDEX_PATH = DATA_ROOT / "metadata" / "fastmri_brain_nifti_cases.csv"
SPLIT_ROOT = DATA_ROOT / "splits" / "nifti_seed3407"
RUN_ROOT = Path(os.environ.get("FASTMRI_BRAIN_CYCLEINR_RUN_ROOT", str(ROOT / "fastmri_brain_cycleinr" / "runs")))


@dataclass(frozen=True)
class Profile:
    name: str
    train_cases: int | None
    val_cases: int | None
    test_cases: int | None
    epochs: int
    batch_size: int
    chunks_per_volume: int
    samples_per_chunk: int
    cycle_samples_per_chunk: int
    val_samples: int
    patience: int
    stride: int = 4
    num_workers: int = 0
    lr: float = 2e-4
    feature_channels: int = 24
    cycle_weight: float = 0.5
    skip_training_if_checkpoint_exists: bool = False


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=8,
        val_cases=2,
        test_cases=2,
        epochs=1,
        batch_size=1,
        chunks_per_volume=1,
        samples_per_chunk=1024,
        cycle_samples_per_chunk=512,
        val_samples=2048,
        patience=2,
        feature_channels=16,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=4,
        epochs=3,
        batch_size=1,
        chunks_per_volume=1,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=4096,
        patience=3,
        feature_channels=24,
    ),
    "full": Profile(
        name="full",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=1,
        chunks_per_volume=1,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=16384,
        patience=8,
        feature_channels=24,
        cycle_weight=0.5,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_x2": Profile(
        name="full_x2",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=1,
        chunks_per_volume=1,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=16384,
        patience=8,
        stride=2,
        feature_channels=24,
        cycle_weight=0.5,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_x6": Profile(
        name="full_x6",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        batch_size=1,
        chunks_per_volume=1,
        samples_per_chunk=2048,
        cycle_samples_per_chunk=1024,
        val_samples=16384,
        patience=8,
        stride=6,
        feature_channels=24,
        cycle_weight=0.5,
        skip_training_if_checkpoint_exists=False,
    ),
}

# Independent 60-epoch reruns used by the convergence audit; original runs remain intact.
PROFILES.update(
    {
        "full_extend60": replace(PROFILES["full"], name="full_extend60", epochs=60, patience=12, skip_training_if_checkpoint_exists=False),
        "full_x2_extend60": replace(PROFILES["full_x2"], name="full_x2_extend60", epochs=60, patience=12, skip_training_if_checkpoint_exists=False),
        "full_x6_extend60": replace(PROFILES["full_x6"], name="full_x6_extend60", epochs=60, patience=12, skip_training_if_checkpoint_exists=False),
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
