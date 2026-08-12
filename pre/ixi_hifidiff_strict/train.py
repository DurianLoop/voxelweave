from __future__ import annotations

import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, write_csv, write_json
from topcow_diffusion.diffusion import DiffusionSchedule

from .data import IXIHiFiSliceDataset
from .model import StrictHiFiDiffUNet
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device) -> bool:
    return device.type == "cuda"


def _make_model(profile: Profile, device: torch.device) -> StrictHiFiDiffUNet:
    model = StrictHiFiDiffUNet(base_channels=profile.base_channels).to(device)
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
    return model


def _batch_loss(model, schedule, batch, device, diffusion_steps: int) -> torch.Tensor:
    cond = batch["cond"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    offset = batch["offset"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)
    t = torch.randint(0, diffusion_steps, (target.shape[0],), device=device)
    noise = torch.randn_like(target)
    noisy = schedule.q_sample(target, t, noise)
    pred_noise = model(noisy, cond, offset, t, diffusion_steps)
    noise_loss = torch.mean((pred_noise - noise) ** 2)
    pred_x0 = schedule.predict_x0(noisy, t, pred_noise).clamp(-1.0, 1.0)
    x0_loss = torch.mean(torch.abs(pred_x0 - target))
    return noise_loss + 0.1 * x0_loss


def _validate(model, loader, schedule, device, profile: Profile, epoch: int) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"Strict-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                loss = _batch_loss(model, schedule, batch, device, profile.diffusion_steps)
            total += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}")
    return total / max(len(loader), 1)


def train(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "hifidiff_strict_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path
    ensure_dir(paths.checkpoints)
    train_ds = IXIHiFiSliceDataset(
        "train", profile.modality, profile.stride, profile.target_size, profile.train_cases
    )
    val_ds = IXIHiFiSliceDataset("val", profile.modality, profile.stride, profile.target_size, profile.val_cases)
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
    model = _make_model(profile, device)
    schedule = DiffusionSchedule(profile.diffusion_steps, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4)
    lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=max(2, profile.patience // 3)
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_val = float("inf")
    stale = 0
    rows = []
    print(
        f"Strict HiFi-Diff: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}, "
        f"base={profile.base_channels}, diffusion_steps={profile.diffusion_steps}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        accum = 0.0
        pbar = tqdm(train_loader, desc=f"Strict-Epoch {epoch + 1}/{profile.epochs}")
        for batch in pbar:
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                loss = _batch_loss(model, schedule, batch, device, profile.diffusion_steps)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            accum += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", lr=f"{optimizer.param_groups[0]['lr']:.1e}")
        train_loss = accum / max(len(train_loader), 1)
        val_loss = _validate(model, val_loader, schedule, device, profile, epoch + 1)
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
                    "diffusion_steps": profile.diffusion_steps,
                    "modality": profile.modality,
                    "stride": profile.stride,
                    "target_size": profile.target_size,
                    "base_channels": profile.base_channels,
                    "sampling": "strict_hifidiff_gaussian_to_slice",
                    "intensity_space": "minus_one_to_one",
                    "loss": "noise_mse_plus_0.1_x0_l1",
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
            f"Strict epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
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
            "diffusion_steps": profile.diffusion_steps,
            "modality": profile.modality,
            "stride": profile.stride,
            "target_size": profile.target_size,
            "base_channels": profile.base_channels,
            "sampling": "strict_hifidiff_gaussian_to_slice",
            "intensity_space": "minus_one_to_one",
            "loss": "noise_mse_plus_0.1_x0_l1",
        },
        paths.checkpoints / "hifidiff_strict_epoch_final.pth",
    )
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path
