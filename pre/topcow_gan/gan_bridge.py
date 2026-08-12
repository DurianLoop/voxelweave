from __future__ import annotations

import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from .common import ROOT, ensure_dir, set_windows_safe_workers, write_csv, write_json
from .settings import RunPaths


@contextmanager
def _cwd(path: Path):
    previous = Path.cwd()
    ensure_dir(path)
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _import_v4():
    v4_dir = str(ROOT / "v4")
    if v4_dir not in sys.path:
        sys.path.insert(0, v4_dir)
    from inference import MRIInterpolator  # type: ignore
    from train import Pix2PixTrainer  # type: ignore
    return MRIInterpolator, Pix2PixTrainer


def _import_v4_dataset_and_config():
    v4_dir = str(ROOT / "v4")
    if v4_dir not in sys.path:
        sys.path.insert(0, v4_dir)
    from config import MODEL_CONFIG  # type: ignore
    from dataset import MRIDataset  # type: ignore
    from utils import plot_training_progress  # type: ignore
    return MRIDataset, MODEL_CONFIG, plot_training_progress


def train_gan(paths: RunPaths, epochs: int, batch_size: int, skip_if_exists: bool) -> Path:
    best = paths.checkpoints / "pix2pix_epoch_best.pth"
    if skip_if_exists and best.exists():
        return best
    set_windows_safe_workers()
    _, trainer_cls = _import_v4()
    with _cwd(paths.run_dir):
        trainer = trainer_cls(data_folder=str(paths.train_links))
        trainer.train(epochs=epochs, batch_size=batch_size, validation_split=0.2)
    return best


def train_gan_case_level(
    paths: RunPaths,
    epochs: int,
    batch_size: int,
    skip_if_exists: bool,
    patience: int,
) -> Path:
    best = paths.checkpoints / "pix2pix_epoch_best.pth"
    history_path = paths.run_dir / "training_history.csv"
    if skip_if_exists and best.exists():
        return best
    set_windows_safe_workers()
    _, trainer_cls = _import_v4()
    dataset_cls, model_config, plot_training_progress = _import_v4_dataset_and_config()
    num_workers = int(os.environ.get("MRI_NUM_WORKERS", "0"))

    with _cwd(paths.run_dir):
        trainer = trainer_cls(data_folder=str(paths.train_links))
        train_dataset = dataset_cls(str(paths.train_links), target_shape=model_config["input_size"])
        val_dataset = dataset_cls(str(paths.val_links), target_shape=model_config["input_size"])
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        )
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            trainer.g_optimizer,
            mode="min",
            factor=0.5,
            patience=max(2, patience // 3),
        )
        rows = []
        stale_epochs = 0
        for epoch in range(epochs):
            start_time = time.time()
            g_loss, d_loss = trainer.train_epoch(train_loader, epoch, epochs)
            val_loss = trainer.validate(val_loader)
            scheduler.step(val_loss)
            trainer.g_losses.append(g_loss)
            trainer.d_losses.append(d_loss)
            trainer.val_losses.append(val_loss)
            improved = val_loss < trainer.best_val_loss
            if improved:
                prev_best = trainer.best_val_loss
                trainer.best_val_loss = val_loss
                trainer.save_checkpoint("best")
                stale_epochs = 0
                print(f"New case-level best: {prev_best:.4f} -> {val_loss:.4f}")
            else:
                stale_epochs += 1
            epoch_time = time.time() - start_time
            current_lr = trainer.g_optimizer.param_groups[0]["lr"]
            rows.append(
                {
                    "epoch": epoch,
                    "g_loss": g_loss,
                    "d_loss": d_loss,
                    "val_loss": val_loss,
                    "best_val_loss": trainer.best_val_loss,
                    "lr": current_lr,
                    "seconds": epoch_time,
                    "improved": improved,
                }
            )
            print(
                f"Epoch {epoch}/{epochs} ({epoch_time:.1f}s) - "
                f"G: {g_loss:.4f}, D: {d_loss:.4f}, Val(case): {val_loss:.4f}, "
                f"LR: {current_lr:.2e}, stale: {stale_epochs}/{patience}"
            )
            if epoch % 5 == 0:
                trainer.save_checkpoint(epoch)
                plot_training_progress(
                    trainer.generator,
                    trainer.discriminator,
                    trainer.g_losses,
                    trainer.d_losses,
                    str(paths.training_plots / "progress.png"),
                )
            if stale_epochs >= patience:
                print(f"Early stopping at epoch {epoch}: no case-level Val improvement for {patience} epochs.")
                break
        trainer.save_checkpoint("final")
        write_csv(history_path, rows)
        write_json(
            paths.run_dir / "training_history.json",
            {
                "best_val_loss": trainer.best_val_loss,
                "epochs_completed": len(rows),
                "early_stopped": stale_epochs >= patience,
            },
        )
    return best


def run_gan_inference_folders(input_dir: Path, output_dir: Path, checkpoint: Path, run_dir: Path) -> int:
    interpolator_cls, _ = _import_v4()
    ensure_dir(output_dir)
    with _cwd(run_dir):
        interpolator = interpolator_cls(str(checkpoint))
        interpolator.process_folder(str(input_dir), str(output_dir))
    return len(list(output_dir.glob("*.nii.gz")))


def run_gan_inference(paths: RunPaths, checkpoint: Path) -> int:
    return run_gan_inference_folders(paths.eval_sparse, paths.gan_outputs, checkpoint, paths.run_dir)
