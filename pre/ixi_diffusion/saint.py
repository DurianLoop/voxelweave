from __future__ import annotations

import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from skimage.transform import resize
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from topcow_diffusion.losses import structural_reconstruction_loss

from .common import ensure_dir, load_nifti, normalize_volume, read_case_ids, save_nifti, write_csv, write_json
from .data import VolumeCache
from .settings import IXI_ROOT, Profile, RunPaths


class SpatialAwareInterpolationDataset(Dataset):
    """SAINT-style dataset: neighboring slices plus relative spatial position."""

    def __init__(
        self,
        split: str,
        modality: str,
        stride: int = 4,
        case_limit: int | None = None,
        seed: int = 3407,
        target_shape: tuple[int, int] = (256, 256),
    ):
        import pandas as pd

        self.split = split
        self.modality = modality
        self.stride = stride
        self.target_shape = target_shape
        self.cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
        split_path = IXI_ROOT / "splits" / f"seed{seed}" / f"{split}_cases.txt"
        self.case_ids = read_case_ids(split_path, case_limit)
        self.items: list[tuple[object, str, int, int, int]] = []
        for case_id in self.case_ids:
            row = self.cases[self.cases["case_id"] == case_id].iloc[0]
            path = row[f"{modality}_path"]
            shape = str(row[f"{modality}_shape"])
            depth = int(shape.split("x")[2])
            for z in range(0, depth - stride):
                for offset in range(1, stride):
                    self.items.append((path, case_id, z, offset, depth))
        yy = np.linspace(-1.0, 1.0, target_shape[0], dtype=np.float32)[:, None]
        xx = np.linspace(-1.0, 1.0, target_shape[1], dtype=np.float32)[None, :]
        self.y_map = np.repeat(yy, target_shape[1], axis=1)
        self.x_map = np.repeat(xx, target_shape[0], axis=0)
        self.cache = VolumeCache(max_items=4)
        print(
            f"IXI SAINT-style {split}: modality={modality}, cases={len(self.case_ids)}, "
            f"samples={len(self.items)}, stride={stride}"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, _case_id, z, offset, depth = self.items[index]
        volume = self.cache.get(path)
        left = resize(volume[:, :, z], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
        right = resize(volume[:, :, z + self.stride], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
        target = resize(
            volume[:, :, z + offset],
            self.target_shape,
            preserve_range=True,
            anti_aliasing=True,
        ).astype(np.float32)
        rel = float(offset) / float(self.stride)
        z_abs = float(z + offset) / max(float(depth - 1), 1.0)
        cond = np.stack(
            [
                left,
                right,
                np.full(self.target_shape, rel, dtype=np.float32),
                np.full(self.target_shape, z_abs, dtype=np.float32),
                self.y_map,
                self.x_map,
            ],
            axis=0,
        ).astype(np.float32)
        return {
            "cond": torch.from_numpy(cond),
            "target": torch.from_numpy(target[None, :, :]),
            "coarse": torch.from_numpy(((1.0 - rel) * left + rel * right)[None, :, :].astype(np.float32)),
        }


class SpatialGate(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.gate = nn.Sequential(
            nn.Conv2d(channels + 4, channels, 1),
            nn.SiLU(),
            nn.Conv2d(channels, channels, 1),
            nn.Sigmoid(),
        )

    def forward(self, feat: torch.Tensor, spatial: torch.Tensor) -> torch.Tensor:
        spatial_resized = F.interpolate(spatial, size=feat.shape[-2:], mode="bilinear", align_corners=False)
        return feat * (1.0 + self.gate(torch.cat([feat, spatial_resized], dim=1)))


class SAINTBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.norm1 = nn.GroupNorm(8, out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)
        self.norm2 = nn.GroupNorm(8, out_channels)
        self.skip = nn.Conv2d(in_channels, out_channels, 1) if in_channels != out_channels else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = F.silu(self.norm1(self.conv1(x)))
        y = self.norm2(self.conv2(y))
        return F.silu(y + self.skip(x))


class SAINTInterpolationNet(nn.Module):
    """Spatially-aware interpolation baseline aligned with SAINT's conditioning idea."""

    def __init__(self, in_channels: int = 6, base_channels: int = 48):
        super().__init__()
        self.enc0 = SAINTBlock(in_channels, base_channels)
        self.gate0 = SpatialGate(base_channels)
        self.pool0 = nn.MaxPool2d(2)
        self.enc1 = SAINTBlock(base_channels, base_channels * 2)
        self.gate1 = SpatialGate(base_channels * 2)
        self.pool1 = nn.MaxPool2d(2)
        self.mid = SAINTBlock(base_channels * 2, base_channels * 4)
        self.gate_mid = SpatialGate(base_channels * 4)
        self.up1 = nn.ConvTranspose2d(base_channels * 4, base_channels * 2, 2, stride=2)
        self.dec1 = SAINTBlock(base_channels * 4, base_channels * 2)
        self.up0 = nn.ConvTranspose2d(base_channels * 2, base_channels, 2, stride=2)
        self.dec0 = SAINTBlock(base_channels * 2, base_channels)
        self.out = nn.Conv2d(base_channels, 1, 1)

    def forward(self, cond: torch.Tensor) -> torch.Tensor:
        spatial = cond[:, 2:6]
        e0 = self.gate0(self.enc0(cond), spatial)
        e1 = self.gate1(self.enc1(self.pool0(e0)), spatial)
        mid = self.gate_mid(self.mid(self.pool1(e1)), spatial)
        d1 = self.dec1(torch.cat([self.up1(mid), e1], dim=1))
        d0 = self.dec0(torch.cat([self.up0(d1), e0], dim=1))
        return torch.sigmoid(self.out(d0))


def _autocast_enabled(device: torch.device) -> bool:
    return device.type == "cuda"


def _gradient_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pred_dx = pred[:, :, :, 1:] - pred[:, :, :, :-1]
    pred_dy = pred[:, :, 1:, :] - pred[:, :, :-1, :]
    tgt_dx = target[:, :, :, 1:] - target[:, :, :, :-1]
    tgt_dy = target[:, :, 1:, :] - target[:, :, :-1, :]
    return F.l1_loss(pred_dx, tgt_dx) + F.l1_loss(pred_dy, tgt_dy)


def _batch_loss(model: nn.Module, batch: dict[str, torch.Tensor], device: torch.device) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)
    pred = model(cond)
    l1 = F.l1_loss(pred, target)
    coarse_residual = F.l1_loss(pred - coarse, target - coarse)
    struct = structural_reconstruction_loss(pred, target)
    grad = _gradient_loss(pred, target)
    loss = l1 + 0.15 * coarse_residual + 0.2 * struct + 0.05 * grad
    return loss, {"l1": float(l1.item()), "struct": float(struct.item()), "grad": float(grad.item())}


def _validate(model: nn.Module, loader: DataLoader, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"SAINT-Val {epoch}", leave=False)
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
    train_ds = SpatialAwareInterpolationDataset("train", profile.modality, profile.stride, profile.train_cases)
    val_ds = SpatialAwareInterpolationDataset("val", profile.modality, profile.stride, profile.val_cases)
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
        f"IXI SAINT-style interpolation: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        pbar = tqdm(train_loader, desc=f"SAINT-Epoch {epoch + 1}/{profile.epochs}")
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
                    "modality": profile.modality,
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
            f"SAINT epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, val={val_loss:.4f}, "
            f"best={best_val:.4f}, lr={row['lr']:.2e}, seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
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


class SAINTInterpolator:
    def __init__(self, checkpoint, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        self.model = SAINTInterpolationNet().to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = (256, 256)
        yy = np.linspace(-1.0, 1.0, self.input_size[0], dtype=np.float32)[:, None]
        xx = np.linspace(-1.0, 1.0, self.input_size[1], dtype=np.float32)[None, :]
        self.y_map = np.repeat(yy, self.input_size[1], axis=1)
        self.x_map = np.repeat(xx, self.input_size[0], axis=0)

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
                z_abs = float(idx * stride + offset) / max(float(out_depth - 1), 1.0)
                cond_np = np.stack(
                    [
                        left,
                        right,
                        np.full(self.input_size, rel, dtype=np.float32),
                        np.full(self.input_size, z_abs, dtype=np.float32),
                        self.y_map,
                        self.x_map,
                    ],
                    axis=0,
                )
                cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
                with torch.no_grad():
                    pred = self.model(cond).squeeze(0).squeeze(0).cpu().numpy()
                slice_ = resize(pred, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = np.clip(slice_, 0.0, 1.0) * (hi - lo) + lo
        return out

    def process_folder(self, input_dir, output_dir, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI SAINT inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count

