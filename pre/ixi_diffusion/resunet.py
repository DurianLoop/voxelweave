from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from skimage.transform import resize
from torch.utils.data import DataLoader
from tqdm import tqdm

from topcow_diffusion.losses import structural_reconstruction_loss

from .common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json
from .data import IXISingleSliceInterpolationDataset
from .settings import Profile, RunPaths


class ResBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.GroupNorm(8, out_channels),
            nn.SiLU(),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.GroupNorm(8, out_channels),
        )
        self.skip = nn.Conv2d(in_channels, out_channels, 1) if in_channels != out_channels else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.silu(self.block(x) + self.skip(x))


class ResidualInterpolationUNet(nn.Module):
    def __init__(self, in_channels: int = 4, base_channels: int = 32):
        super().__init__()
        self.down0 = ResBlock(in_channels, base_channels)
        self.pool0 = nn.MaxPool2d(2)
        self.down1 = ResBlock(base_channels, base_channels * 2)
        self.pool1 = nn.MaxPool2d(2)
        self.mid = ResBlock(base_channels * 2, base_channels * 4)
        self.up1 = nn.ConvTranspose2d(base_channels * 4, base_channels * 2, 2, stride=2)
        self.dec1 = ResBlock(base_channels * 4, base_channels * 2)
        self.up0 = nn.ConvTranspose2d(base_channels * 2, base_channels, 2, stride=2)
        self.dec0 = ResBlock(base_channels * 2, base_channels)
        self.out = nn.Conv2d(base_channels, 1, 1)

    def forward(self, cond: torch.Tensor) -> torch.Tensor:
        d0 = self.down0(cond)
        d1 = self.down1(self.pool0(d0))
        mid = self.mid(self.pool1(d1))
        u1 = self.up1(mid)
        u1 = self.dec1(torch.cat([u1, d1], dim=1))
        u0 = self.up0(u1)
        u0 = self.dec0(torch.cat([u0, d0], dim=1))
        return torch.tanh(self.out(u0))


def _autocast_enabled(device: torch.device) -> bool:
    return device.type == "cuda"


def _make_model(device: torch.device) -> ResidualInterpolationUNet:
    model = ResidualInterpolationUNet().to(device)
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
    return model


def _batch_loss(model, batch, device) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)
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


def _validate(model, loader, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"ResUNet-Val {epoch}", leave=False)
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
    train_ds = IXISingleSliceInterpolationDataset("train", profile.modality, profile.stride, profile.train_cases)
    val_ds = IXISingleSliceInterpolationDataset("val", profile.modality, profile.stride, profile.val_cases)
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

    model = _make_model(device)
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
        f"IXI ResUNet residual interpolation: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        accum = 0.0
        pbar = tqdm(train_loader, desc=f"ResUNet-Epoch {epoch + 1}/{profile.epochs}")
        for batch in pbar:
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                loss, parts = _batch_loss(model, batch, device)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            accum += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", l1=f"{parts['l1']:.4f}", lr=f"{optimizer.param_groups[0]['lr']:.1e}")
        train_loss = accum / max(len(train_loader), 1)
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
                    "modality": profile.modality,
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
            f"ResUNet epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
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
            "modality": profile.modality,
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


class ResUNetResidualInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        self.model = ResidualInterpolationUNet().to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = (256, 256)

    def _predict_residual(self, cond: torch.Tensor) -> np.ndarray:
        with torch.no_grad():
            residual = self.model(cond).clamp(-1.0, 1.0)
        return residual.squeeze(0).squeeze(0).cpu().numpy()

    def interpolate_volume(self, volume: np.ndarray, stride: int = 4) -> np.ndarray:
        norm, lo, hi = normalize_volume(volume)
        out_depth = (volume.shape[2] - 1) * stride + 1
        out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        for idx in range(volume.shape[2]):
            out[:, :, idx * stride] = volume[:, :, idx]
        for idx in range(volume.shape[2] - 1):
            left = resize(norm[:, :, idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            right = resize(norm[:, :, idx + 1], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            for offset in range(1, stride):
                rel = float(offset) / float(stride)
                coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
                cond_np = np.stack(
                    [
                        left,
                        right,
                        coarse,
                        np.full(self.input_size, rel, dtype=np.float32),
                    ],
                    axis=0,
                )
                cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
                residual = self._predict_residual(cond)
                generated = np.clip(coarse + residual, 0.0, 1.0)
                slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI ResUNet inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count
