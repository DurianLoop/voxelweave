from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, write_csv, write_json
from ixi_i3net.train import I3NetInterpolator, _autocast_enabled, _checkpoint_payload, _make_model

from .data import FastMRII3NetWindowDataset
from .settings import DATASET_NAME, Profile, RunPaths


def _batch_loss(model: torch.nn.Module, hr: torch.Tensor, profile: Profile, device: torch.device) -> torch.Tensor:
    gt = hr.to(device, non_blocking=True)
    lr = gt[..., :: profile.stride]
    sr = model(lr).clamp(0.0, 1.0)
    return F.l1_loss(sr, gt)


def _validate(model: torch.nn.Module, loader: DataLoader, profile: Profile, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"FastMRI-I3Net-Val {epoch}", leave=False)
        for hr in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss = _batch_loss(model, hr, profile, device)
            if not torch.isfinite(loss):
                continue
            total += float(loss.item())
            count += 1
            pbar.set_postfix(loss=f"{loss.item():.4f}")
    return total / max(count, 1) if count else float("nan")


def train_i3net(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "i3net_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    train_ds = FastMRII3NetWindowDataset("train", profile)
    val_ds = FastMRII3NetWindowDataset("val", profile)
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
    optimizer = torch.optim.AdamW(model.parameters(), lr=profile.lr, weight_decay=profile.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=max(1, profile.patience // 3),
    )
    scaler = torch.amp.GradScaler("cuda", enabled=_autocast_enabled(device, profile))
    rows = []
    best_val = float("inf")
    stale = 0
    print(
        f"{DATASET_NAME} I3Net: device={device}, profile={profile.name}, "
        f"train_windows={len(train_ds)}, val_windows={len(val_ds)}, batch={profile.batch_size}, "
        f"n_feats={profile.n_feats}, blocks={profile.num_blocks}, amp={profile.amp}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        count = 0
        skipped_nonfinite = 0
        pbar = tqdm(train_loader, desc=f"FastMRI-I3Net-Epoch {epoch + 1}/{profile.epochs}")
        for hr in pbar:
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss = _batch_loss(model, hr, profile, device)
            if not torch.isfinite(loss):
                skipped_nonfinite += 1
                pbar.set_postfix(loss="nonfinite", skipped=skipped_nonfinite)
                continue
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            if not torch.isfinite(grad_norm):
                skipped_nonfinite += 1
                optimizer.zero_grad(set_to_none=True)
                pbar.set_postfix(loss="bad_grad", skipped=skipped_nonfinite)
                continue
            scaler.step(optimizer)
            scaler.update()
            total += float(loss.item())
            count += 1
            pbar.set_postfix(loss=f"{loss.item():.4f}", lr=f"{optimizer.param_groups[0]['lr']:.1e}", skipped=skipped_nonfinite)
        train_loss = total / max(count, 1) if count else float("nan")
        val_loss = _validate(model, val_loader, profile, device, epoch + 1)
        if np.isfinite(val_loss):
            scheduler.step(val_loss)
        improved = np.isfinite(val_loss) and val_loss < best_val
        if improved:
            best_val = val_loss
            stale = 0
            torch.save(_checkpoint_payload(model, profile, epoch, best_val), best_path)
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
            "finite_train_batches": count,
            "skipped_nonfinite": skipped_nonfinite,
        }
        rows.append(row)
        print(
            f"{DATASET_NAME} I3Net epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, skipped={skipped_nonfinite}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "i3net_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path
