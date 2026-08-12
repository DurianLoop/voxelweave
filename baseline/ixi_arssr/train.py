from __future__ import annotations

import time
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, write_csv, write_json

from .data import IXIArSSRDataset, validation_batch
from .model import ArSSRNet
from .settings import Profile, RunPaths


def _device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _validate(model: ArSSRNet, batches: list[dict[str, torch.Tensor]], device: torch.device) -> float:
    model.eval()
    losses = []
    with torch.no_grad():
        for batch in batches:
            volume = batch["volume"].to(device)
            coords = batch["coords"].to(device)
            values = batch["values"].to(device)
            pred = model(volume, coords).clamp(0.0, 1.0)
            losses.append(float(F.l1_loss(pred, values).item()))
    return sum(losses) / max(len(losses), 1)


def train_arssr(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "arssr_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    device = _device()
    train_ds = IXIArSSRDataset(
        "train",
        profile.modality,
        stride=profile.stride,
        case_limit=profile.train_cases,
        chunks_per_volume=profile.chunks_per_volume,
        samples_per_chunk=profile.samples_per_chunk,
    )
    val_batches = validation_batch(
        "val",
        profile.modality,
        stride=profile.stride,
        case_limit=profile.val_cases,
        samples=profile.val_samples,
    )
    loader = DataLoader(
        train_ds,
        batch_size=profile.batch_size,
        shuffle=True,
        num_workers=profile.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=profile.num_workers > 0,
    )
    model = ArSSRNet(feature_channels=profile.feature_channels).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=profile.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=max(1, profile.patience // 3),
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_val = float("inf")
    stale = 0
    rows = []
    print(
        f"IXI ArSSR-style training: device={device}, profile={profile.name}, "
        f"train_items={len(train_ds)}, val_cases={len(val_batches)}, "
        f"samples_per_chunk={profile.samples_per_chunk}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        accum = 0.0
        pbar = tqdm(loader, desc=f"ArSSR-Epoch {epoch + 1}/{profile.epochs}")
        for batch in pbar:
            volume = batch["volume"].to(device, non_blocking=True)
            coords = batch["coords"].to(device, non_blocking=True)
            values = batch["values"].to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
                pred = model(volume, coords).clamp(0.0, 1.0)
                loss = F.l1_loss(pred, values) + 0.25 * F.mse_loss(pred, values)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            accum += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", lr=f"{optimizer.param_groups[0]['lr']:.1e}")
        train_loss = accum / max(len(loader), 1)
        val_loss = _validate(model, val_batches, device)
        scheduler.step(val_loss)
        improved = val_loss < best_val
        if improved:
            best_val = val_loss
            stale = 0
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "best_val_loss": best_val,
                    "modality": profile.modality,
                    "stride": profile.stride,
                    "sampling": "arssr_style_inr",
                    "condition": "linear_densified_sparse_volume_coordinate_residual",
                    "feature_channels": profile.feature_channels,
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
            f"ArSSR epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break
    torch.save(
        {
            "epoch": rows[-1]["epoch"],
            "model_state_dict": model.state_dict(),
            "best_val_loss": best_val,
            "modality": profile.modality,
            "stride": profile.stride,
            "sampling": "arssr_style_inr",
            "condition": "linear_densified_sparse_volume_coordinate_residual",
            "feature_channels": profile.feature_channels,
        },
        paths.checkpoints / "arssr_epoch_final.pth",
    )
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path
