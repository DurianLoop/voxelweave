from __future__ import annotations

import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from topcow_diffusion.diffusion import DiffusionSchedule
from topcow_diffusion.losses import structural_reconstruction_loss
from topcow_diffusion.model import NoisePredictorUNet

from .common import ensure_dir, write_csv, write_json
from .data import IXIInterpolationDataset
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device) -> bool:
    return device.type == "cuda"


def _validate(model, loader, schedule, device, epoch: int) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"Val {epoch}", leave=False)
        for cond, target in pbar:
            cond = cond.to(device, non_blocking=True)
            target = target.to(device, non_blocking=True)
            t = torch.randint(0, schedule.steps, (target.shape[0],), device=device)
            noise = torch.randn_like(target)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                noisy = schedule.q_sample(target, t, noise)
                pred_noise = model(noisy, cond, t, schedule.steps)
                pred_x0 = schedule.predict_x0(noisy, t, pred_noise).clamp(0, 1)
                loss = torch.mean((pred_noise - noise) ** 2) + 0.2 * structural_reconstruction_loss(pred_x0, target)
            total += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}")
    return total / max(len(loader), 1)


def train_diffusion(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "diffusion_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    train_ds = IXIInterpolationDataset("train", profile.modality, profile.stride, profile.train_cases)
    val_ds = IXIInterpolationDataset("val", profile.modality, profile.stride, profile.val_cases)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader = DataLoader(
        train_ds,
        batch_size=profile.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=device.type == "cuda",
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=profile.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=device.type == "cuda",
    )

    model = NoisePredictorUNet().to(device)
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
    schedule = DiffusionSchedule(profile.diffusion_steps, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4)
    lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=max(2, profile.patience // 3),
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_val = float("inf")
    stale = 0
    rows = []
    print(
        f"IXI diffusion: device={device}, profile={profile.name}, modality={profile.modality}, "
        f"train_pairs={len(train_ds)}, val_pairs={len(val_ds)}, batch={profile.batch_size}, "
        f"diffusion_steps={profile.diffusion_steps}, pure_noise_sampling=True"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        accum = 0.0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{profile.epochs}")
        for cond, target in pbar:
            cond = cond.to(device, non_blocking=True)
            target = target.to(device, non_blocking=True)
            if device.type == "cuda":
                cond = cond.contiguous(memory_format=torch.channels_last)
                target = target.contiguous(memory_format=torch.channels_last)
            t = torch.randint(0, profile.diffusion_steps, (target.shape[0],), device=device)
            noise = torch.randn_like(target)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                noisy = schedule.q_sample(target, t, noise)
                pred_noise = model(noisy, cond, t, profile.diffusion_steps)
                pred_x0 = schedule.predict_x0(noisy, t, pred_noise).clamp(0, 1)
                noise_loss = torch.mean((pred_noise - noise) ** 2)
                struct_loss = structural_reconstruction_loss(pred_x0, target)
                loss = noise_loss + 0.2 * struct_loss
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            accum += float(loss.item())
            pbar.set_postfix(
                loss=f"{loss.item():.4f}",
                noise=f"{noise_loss.item():.4f}",
                struct=f"{struct_loss.item():.4f}",
                lr=f"{optimizer.param_groups[0]['lr']:.1e}",
            )
        train_loss = accum / max(len(train_loader), 1)
        val_loss = _validate(model, val_loader, schedule, device, epoch + 1)
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
                    "sampling": "pure_noise",
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
            f"Epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, val={val_loss:.4f}, "
            f"best={best_val:.4f}, lr={row['lr']:.2e}, seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if epoch % 5 == 0:
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "best_val_loss": best_val,
                    "diffusion_steps": profile.diffusion_steps,
                    "modality": profile.modality,
                    "stride": profile.stride,
                    "sampling": "pure_noise",
                },
                paths.checkpoints / f"diffusion_epoch_{epoch}.pth",
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
            "sampling": "pure_noise",
        },
        paths.checkpoints / "diffusion_epoch_final.pth",
    )
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(paths.run_dir / "training_history.json", {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience})
    return best_path
