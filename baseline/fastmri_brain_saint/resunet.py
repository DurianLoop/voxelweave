from __future__ import annotations

import time
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from topcow_diffusion.losses import structural_reconstruction_loss

from ixi_diffusion.common import ensure_dir, write_csv, write_json
from ixi_diffusion.resunet import ResidualInterpolationUNet

from .data import FastMRIBrainSAINTDataset
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device) -> bool:
    return device.type == "cuda"


def _make_resunet_condition(batch: dict[str, torch.Tensor], device: torch.device) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    saint_cond = batch["cond"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    left = saint_cond[:, 0:1]
    right = saint_cond[:, 1:2]
    rel = saint_cond[:, 2:3]
    cond = torch.cat([left, right, coarse, rel], dim=1)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)
    return cond, coarse, target


def _batch_loss(model: torch.nn.Module, batch: dict[str, torch.Tensor], device: torch.device) -> tuple[torch.Tensor, dict[str, float]]:
    cond, coarse, target = _make_resunet_condition(batch, device)
    residual = model(cond)
    recon = (coarse + residual).clamp(0.0, 1.0)
    l1 = F.l1_loss(recon, target)
    residual_l1 = F.l1_loss(residual, (target - coarse).clamp(-1.0, 1.0))
    struct = structural_reconstruction_loss(recon, target)
    loss = l1 + 0.25 * residual_l1 + 0.2 * struct
    return loss, {
        "l1": float(l1.detach().item()),
        "residual_l1": float(residual_l1.detach().item()),
        "struct": float(struct.detach().item()),
    }


def _validate(model: torch.nn.Module, loader: DataLoader, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"fastMRI-ResUNet-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                loss, parts = _batch_loss(model, batch, device)
            total += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", l1=f"{parts['l1']:.4f}")
    return total / max(len(loader), 1)


def train_resunet(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "resunet_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    train_ds = FastMRIBrainSAINTDataset("train", profile.stride, profile.train_cases)
    val_ds = FastMRIBrainSAINTDataset("val", profile.stride, profile.val_cases)
    if len(train_ds) == 0 or len(val_ds) == 0:
        raise RuntimeError("Train/val split produced no ResUNet samples; check prepared NIfTI split.")

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

    model = ResidualInterpolationUNet().to(device)
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
        f"fastMRI brain ResUNet residual: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        pbar = tqdm(train_loader, desc=f"fastMRI-ResUNet-Epoch {epoch + 1}/{profile.epochs}")
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
                    "dataset": "fastmri_or_local_t2_prepared_nifti",
                    "stride": profile.stride,
                    "sampling": "resunet_residual",
                    "condition": "left_right_linear_coarse_relative_position",
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
            f"fastMRI ResUNet epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
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
            "dataset": "fastmri_or_local_t2_prepared_nifti",
            "stride": profile.stride,
            "sampling": "resunet_residual",
            "condition": "left_right_linear_coarse_relative_position",
        },
        paths.checkpoints / "resunet_epoch_final.pth",
    )
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path
