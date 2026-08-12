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

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json
from ixi_diffusion.data import IXISingleSliceInterpolationDataset

from .model import ECSINet, spatial_gradient
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device, profile: Profile | None = None) -> bool:
    return device.type == "cuda" and (profile is None or profile.amp)


def _make_model(profile: Profile, device: torch.device) -> ECSINet:
    model = ECSINet(
        channels=profile.channels,
        num_blocks=profile.num_blocks,
        expansion=profile.expansion,
        kernel_size=profile.kernel_size,
        residual_scale=profile.residual_scale,
        mask_bias=profile.mask_bias,
    ).to(device)
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
    return model


def _gradient_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pred_dx = pred[:, :, :, 1:] - pred[:, :, :, :-1]
    pred_dy = pred[:, :, 1:, :] - pred[:, :, :-1, :]
    tgt_dx = target[:, :, :, 1:] - target[:, :, :, :-1]
    tgt_dy = target[:, :, 1:, :] - target[:, :, :-1, :]
    return F.l1_loss(pred_dx, tgt_dx) + F.l1_loss(pred_dy, tgt_dy)


def _normalize_per_sample(x: torch.Tensor) -> torch.Tensor:
    flat = x.flatten(1)
    lo = flat.min(dim=1).values.view(-1, 1, 1, 1)
    hi = flat.max(dim=1).values.view(-1, 1, 1, 1)
    return (x - lo) / (hi - lo + 1e-6)


def _mask_prior(cond: torch.Tensor, coarse: torch.Tensor) -> torch.Tensor:
    left = cond[:, 0:1]
    right = cond[:, 1:2]
    change = (right - left).abs()
    return _normalize_per_sample(change + spatial_gradient(coarse))


def _batch_loss(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    profile: Profile,
    device: torch.device,
) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)
    parts = model(cond, return_parts=True)
    recon = parts["recon"].clamp(0.0, 1.0)
    target_residual = (target - coarse).clamp(-1.0, 1.0)
    l1 = F.l1_loss(recon, target)
    grad = _gradient_loss(recon, target)
    residual_l1 = F.l1_loss(parts["correction"], target_residual)
    mask_mean = parts["mask"].mean()
    prior = _mask_prior(cond, coarse)
    prior_l1 = F.l1_loss(parts["mask"], prior)
    loss = (
        l1
        + profile.lambda_grad * grad
        + profile.lambda_residual * residual_l1
        + profile.lambda_mask * mask_mean
        + profile.lambda_prior * prior_l1
    )
    return loss, {
        "l1": float(l1.detach().item()),
        "grad": float(grad.detach().item()),
        "residual_l1": float(residual_l1.detach().item()),
        "mask_mean": float(mask_mean.detach().item()),
        "mask_prior_l1": float(prior_l1.detach().item()),
    }


def _validate(model: nn.Module, loader: DataLoader, profile: Profile, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"ECSI-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss(model, batch, profile, device)
            if not torch.isfinite(loss):
                continue
            total += float(loss.item())
            count += 1
            pbar.set_postfix(loss=f"{loss.item():.4f}", mask=f"{parts['mask_mean']:.3f}")
    return total / max(count, 1) if count else float("nan")


def _checkpoint_payload(model: nn.Module, profile: Profile, epoch: int, best_val: float) -> dict:
    return {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "best_val_loss": best_val,
        "modality": profile.modality,
        "stride": profile.stride,
        "sampling": "ecsinet_change_aware_residual",
        "condition": "left/right adjacent sparse slices + linear coarse + relative position, with internal D/A channels",
        "model_config": {
            "channels": profile.channels,
            "num_blocks": profile.num_blocks,
            "expansion": profile.expansion,
            "kernel_size": profile.kernel_size,
            "residual_scale": profile.residual_scale,
            "mask_bias": profile.mask_bias,
            "amp": profile.amp,
        },
    }


def train_ecsinet(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "ecsinet_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    train_ds = IXISingleSliceInterpolationDataset(
        "train",
        profile.modality,
        profile.stride,
        profile.train_cases,
        target_shape=profile.target_shape,
    )
    val_ds = IXISingleSliceInterpolationDataset(
        "val",
        profile.modality,
        profile.stride,
        profile.val_cases,
        target_shape=profile.target_shape,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
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
        f"IXI ECSI-Net interpolation: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}, "
        f"channels={profile.channels}, blocks={profile.num_blocks}, kernel={profile.kernel_size}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        count = 0
        skipped_nonfinite = 0
        pbar = tqdm(train_loader, desc=f"ECSI-Epoch {epoch + 1}/{profile.epochs}")
        last_parts = {}
        for batch in pbar:
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss(model, batch, profile, device)
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
            last_parts = parts
            pbar.set_postfix(
                loss=f"{loss.item():.4f}",
                l1=f"{parts['l1']:.4f}",
                mask=f"{parts['mask_mean']:.3f}",
                lr=f"{optimizer.param_groups[0]['lr']:.1e}",
            )
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
            **{f"last_{key}": value for key, value in last_parts.items()},
        }
        rows.append(row)
        print(
            f"ECSI epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "ecsinet_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path


class ECSINetInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None, label: str = "IXI"):
        self.label = label
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload.get("model_config", {})
        self.amp = bool(config.pop("amp", True))
        self.stride = int(payload.get("stride", 4))
        self.input_size = (256, 256)
        self.model = ECSINet(**config).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()

    def _predict_slice(self, cond_np: np.ndarray) -> np.ndarray:
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
                pred = self.model(cond).float().clamp(0.0, 1.0)
        return pred.squeeze(0).squeeze(0).cpu().numpy()

    def interpolate_volume(self, volume: np.ndarray, stride: int = 4) -> np.ndarray:
        if stride != self.stride:
            raise ValueError(f"Checkpoint stride={self.stride}, requested stride={stride}")
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
                    [left, right, coarse, np.full(self.input_size, rel, dtype=np.float32)],
                    axis=0,
                )
                generated = self._predict_slice(cond_np)
                slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"{self.label} ECSI-Net inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count

