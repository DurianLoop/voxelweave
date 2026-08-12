from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(os.environ.get("MRI_PROJECT_ROOT", str(Path(__file__).resolve().parents[2])))
DATA_ROOT = Path(
    os.environ.get(
        "FASTMRI_BRAIN_I3NET_DATA_ROOT",
        str(ROOT / "dataset" / "fastMRI_brain_T2" / "processed"),
    )
)
INDEX_PATH = DATA_ROOT / "metadata" / "fastmri_brain_nifti_cases.csv"
SPLIT_ROOT = DATA_ROOT / "splits" / "nifti_seed3407"
RUN_ROOT = Path(os.environ.get("FASTMRI_BRAIN_I3NET_RUN_ROOT", str(ROOT / "fastmri_brain_i3net" / "runs")))
DATASET_NAME = os.environ.get("FASTMRI_BRAIN_I3NET_DATASET_NAME", "fastMRI-brain-T2 expanded")
SOURCE_NOTE = os.environ.get(
    "FASTMRI_BRAIN_I3NET_SOURCE_NOTE",
    "I3Net TMI 2024 official architecture, local fastMRI-brain-T2 reproduction",
)


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
    window_step: int = 1
    num_workers: int = 0
    lr: float = 1e-4
    weight_decay: float = 1e-4
    amp: bool = False
    kernel_size: int = 3
    n_feats: int = 64
    num_blocks: int = 16
    res_scale: float = 1.0
    head_num: int = 1
    window_size: int = 16
    win_num_sqrt: int = 16
    skip_training_if_checkpoint_exists: bool = True

    @property
    def hr_slice_patch(self) -> int:
        return self.stride * (self.lr_slice_patch - 1) + 1


PROFILES = {
    "smoke": Profile(
        name="smoke",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=1,
        n_feats=16,
        window_step=1,
        skip_training_if_checkpoint_exists=False,
    ),
    "mini": Profile(
        name="mini",
        train_cases=16,
        val_cases=4,
        test_cases=4,
        epochs=5,
        patience=3,
        n_feats=32,
        window_step=1,
        skip_training_if_checkpoint_exists=False,
    ),
    "full": Profile(
        name="full",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        patience=8,
        n_feats=64,
        window_step=1,
        skip_training_if_checkpoint_exists=True,
    ),
    "full_x2": Profile(
        name="full_x2",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        patience=8,
        stride=2,
        n_feats=64,
        window_step=1,
        skip_training_if_checkpoint_exists=False,
    ),
    "full_x6": Profile(
        name="full_x6",
        train_cases=None,
        val_cases=None,
        test_cases=None,
        epochs=30,
        patience=8,
        stride=6,
        # fastMRI volumes are predominantly 16 slices: three sparse anchors yield the valid 13-slice x6 interval.
        lr_slice_patch=3,
        n_feats=64,
        window_step=1,
        skip_training_if_checkpoint_exists=False,
    ),
    "smoke_x2": Profile(
        name="smoke_x2",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=1,
        stride=2,
        n_feats=16,
        window_step=1,
        skip_training_if_checkpoint_exists=False,
    ),
    "smoke_x6": Profile(
        name="smoke_x6",
        train_cases=4,
        val_cases=1,
        test_cases=1,
        epochs=1,
        stride=6,
        n_feats=16,
        window_step=1,
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
