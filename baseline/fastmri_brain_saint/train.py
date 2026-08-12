from __future__ import annotations

import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, write_csv, write_json
from ixi_diffusion.saint import SAINTInterpolationNet, _autocast_enabled, _batch_loss

from .data import FastMRIBrainSAINTDataset
from .settings import Profile, RunPaths


def _validate(model: torch.nn.Module, loader: DataLoader, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"fastMRI-SAINT-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                loss, parts = _batch_loss(model, batch, device)
            total += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", l1=f"{parts['l1']:.4f}")
    return total / max(len(loader), 1)


def train_saint(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "saint_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path
    ensure_dir(paths.checkpoints)
    train_ds = FastMRIBrainSAINTDataset("train", profile.stride, profile.train_cases)
    val_ds = FastMRIBrainSAINTDataset("val", profile.stride, profile.val_cases)
    if len(train_ds) == 0 or len(val_ds) == 0:
        raise RuntimeError("Train/val split produced no SAINT samples; convert more fastMRI brain DICOM cases first.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader = DataLoader(
        train_ds,
        batch_size=profile.batch_size,
        shuffle=True,
        num_workers=profile.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=profile.num_workers > 0,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=profile.batch_size,
        shuffle=False,
        num_workers=profile.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=profile.num_workers > 0,
    )
    model = SAINTInterpolationNet().to(device)
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
    lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=max(2, profile.patience // 3),
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    rows = []
    best_val = float("inf")
    stale = 0
    print(
        f"fastMRI brain SAINT: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        pbar = tqdm(train_loader, desc=f"fastMRI-SAINT-Epoch {epoch + 1}/{profile.epochs}")
        for batch in pbar:
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                loss, parts = _batch_loss(model, batch, device)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", l1=f"{parts['l1']:.4f}", lr=f"{optimizer.param_groups[0]['lr']:.1e}")
        train_loss = total / max(len(train_loader), 1)
        val_loss = _validate(model, val_loader, device, epoch + 1)
        lr_scheduler.step(val_loss)
        improved = val_loss < best_val
        if improved:
            best_val = val_loss
            stale = 0
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "best_val_loss": best_val,
                    "dataset": "fastMRI_brain_DICOM_prepared_nifti",
                    "modality": "unknown",
                    "stride": profile.stride,
                    "sampling": "saint_spatial_aware",
                    "condition": "left_right_relative_zabs_yx",
                },
                best_path,
            )
        else:
            stale += 1
        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "best_val_loss": best_val,
            "lr": optimizer.param_groups[0]["lr"],
            "seconds": time.time() - start,
            "improved": improved,
        }
        rows.append(row)
        print(
            f"fastMRI SAINT epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(
        {
            "epoch": rows[-1]["epoch"],
            "model_state_dict": model.state_dict(),
            "best_val_loss": best_val,
            "dataset": "fastMRI_brain_DICOM_prepared_nifti",
            "modality": "unknown",
            "stride": profile.stride,
            "sampling": "saint_spatial_aware",
            "condition": "left_right_relative_zabs_yx",
        },
        paths.checkpoints / "saint_epoch_final.pth",
    )
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path
