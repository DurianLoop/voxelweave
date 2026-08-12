from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE_ROOT = ROOT / "pre"
if str(PRE_ROOT) not in sys.path:
    sys.path.insert(0, str(PRE_ROOT))

from gan_2p5d.train import train_gan as train_shared_gan
from ixi_diffusion.common import load_nifti, write_csv, write_json

from .data import case_paths
from .settings import Profile, RunPaths


def _load_volume(path: Path):
    volume, _affine, _header = load_nifti(path)
    return volume


def train_gan(paths: RunPaths, profile: Profile) -> Path:
    train_paths = case_paths("train", profile.modality, profile.train_cases)
    val_paths = case_paths("val", profile.modality, profile.val_cases)

    def write_history(rows: list[dict]) -> None:
        best_row = min(rows, key=lambda row: row["val_loss"]) if rows else None
        final_row = rows[-1] if rows else None
        write_csv(paths.run_dir / "training_history.csv", rows)
        write_json(
            paths.run_dir / "training_history.json",
            {
                "best_val_loss": None if best_row is None else best_row["val_loss"],
                "best_epoch": None if best_row is None else best_row["epoch"],
                "final_val_loss": None if final_row is None else final_row["val_loss"],
                "last_vs_best_pct": None
                if best_row is None or final_row is None or best_row["val_loss"] == 0
                else (final_row["val_loss"] - best_row["val_loss"]) / best_row["val_loss"] * 100.0,
                "epochs_completed": len(rows),
                "checkpoint_selection": "best validation loss",
                "selected_checkpoint": str(paths.checkpoints / "gan_epoch_best.pth"),
                "final_checkpoint": str(paths.checkpoints / "gan_epoch_final.pth"),
            },
        )

    return train_shared_gan(
        train_paths=train_paths,
        val_paths=val_paths,
        loader=_load_volume,
        checkpoints_dir=paths.checkpoints,
        history_writer=write_history,
        epochs=profile.epochs,
        batch_size=profile.batch_size,
        patience=profile.patience,
        lr=profile.lr,
        stride=profile.stride,
        target_shape=profile.target_shape,
        num_workers=profile.num_workers,
        skip_if_checkpoint_exists=profile.skip_training_if_checkpoint_exists,
        meta={
            "dataset": "IXI-T2",
            "method": "gan_2p5d",
            "sampling": "inherited_pix2pix_gan_2p5d",
            "condition": "left/right sparse slices + global z + relative positions",
        },
    )
