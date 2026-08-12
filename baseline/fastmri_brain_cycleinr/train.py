from __future__ import annotations

import time

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_arssr.model import ArSSRNet
from ixi_diffusion.common import ensure_dir, write_csv, write_json

from .data import FastMRICycleINRDataset, validation_batches
from .settings import Profile, RunPaths


def _validate(model: ArSSRNet, batches: list[dict[str, torch.Tensor]], device: torch.device) -> float:
    model.eval()
    losses = []
    with torch.no_grad():
        for batch in batches:
            pred = model(batch["volume"].to(device), batch["coords"].to(device)).clamp(0.0, 1.0)
            losses.append(float(F.l1_loss(pred, batch["values"].to(device)).item()))
    return sum(losses) / max(len(losses), 1)


def train_cycleinr(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "cycleinr_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_ds = FastMRICycleINRDataset(
        "train",
        stride=profile.stride,
        case_limit=profile.train_cases,
        chunks_per_volume=profile.chunks_per_volume,
        samples_per_chunk=profile.samples_per_chunk,
        cycle_samples_per_chunk=profile.cycle_samples_per_chunk,
    )
    val_batches = validation_batches("val", profile.stride, profile.val_cases, profile.val_samples)
    if len(train_ds) == 0 or not val_batches:
        raise RuntimeError("fastMRI CycleINR train/val split produced no samples.")

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
    rows = []
    best_val = float("inf")
    stale = 0
    print(
        f"fastMRI CycleINR-style: device={device}, profile={profile.name}, "
        f"train_items={len(train_ds)}, val_cases={len(val_batches)}, samples={profile.samples_per_chunk}, "
        f"cycle={profile.cycle_samples_per_chunk}, cycle_weight={profile.cycle_weight}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        accum = 0.0
        pbar = tqdm(loader, desc=f"fastMRI-CycleINR-Epoch {epoch + 1}/{profile.epochs}")
        for batch in pbar:
            volume = batch["volume"].to(device, non_blocking=True)
            coords = batch["coords"].to(device, non_blocking=True)
            values = batch["values"].to(device, non_blocking=True)
            cycle_coords = batch["cycle_coords"].to(device, non_blocking=True)
            cycle_values = batch["cycle_values"].to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
                pred = model(volume, coords).clamp(0.0, 1.0)
                cycle_pred = model(volume, cycle_coords).clamp(0.0, 1.0)
                recon_loss = F.l1_loss(pred, values) + 0.25 * F.mse_loss(pred, values)
                cycle_loss = F.l1_loss(cycle_pred, cycle_values)
                loss = recon_loss + profile.cycle_weight * cycle_loss
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
            torch.save(_checkpoint_payload(model, profile, epoch, best_val), best_path)
        else:
            stale += 1
        rows.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "best_val_loss": best_val,
                "lr": optimizer.param_groups[0]["lr"],
                "seconds": time.time() - start,
                "improved": improved,
            }
        )
        print(
            f"fastMRI CycleINR epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "cycleinr_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path


def _checkpoint_payload(model: ArSSRNet, profile: Profile, epoch: int, best_val: float) -> dict:
    return {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "best_val_loss": best_val,
        "dataset": "fastMRI_brain_T2_or_NingXia_T2",
        "stride": profile.stride,
        "sampling": "cycleinr_style_inr",
        "condition": "linear_densified_sparse_volume_coordinate_residual_cycle_consistency",
        "feature_channels": profile.feature_channels,
        "cycle_weight": profile.cycle_weight,
    }
