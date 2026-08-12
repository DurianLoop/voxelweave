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

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json

from .data import CachedFastMRISingleSliceInterpolationDataset, FastMRISingleSliceInterpolationDataset
from .model import ACVTT2p5D
from .settings import DATASET_NAME, Profile, RunPaths


def _autocast_enabled(profile: Profile, device: torch.device) -> bool:
    return device.type == "cuda" and profile.use_amp


def _make_model(profile: Profile, device: torch.device) -> ACVTT2p5D:
    model = ACVTT2p5D(
        num_level=profile.num_level,
        num_ref_enc_level=profile.num_level,
        num_channel=profile.num_channel,
        num_ref_channel=profile.num_channel,
        num_block=profile.num_block,
        num_block_ref=profile.num_block,
        scale=profile.stride,
        transfer_level=profile.transfer_level,
        block_size_per_level=profile.block_size_per_level,
        win_block_size_per_level=tuple([2] * profile.num_level),
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


def _batch_loss(model: nn.Module, batch: dict[str, torch.Tensor], device: torch.device) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
    recon = model(cond)
    l1 = F.l1_loss(recon, target)
    residual_l1 = F.l1_loss(recon - coarse, target - coarse)
    struct = structural_reconstruction_loss(recon, target)
    grad = _gradient_loss(recon, target)
    loss = l1 + 0.20 * residual_l1 + 0.15 * struct + 0.05 * grad
    return loss, {
        "l1": float(l1.detach().item()),
        "residual_l1": float(residual_l1.detach().item()),
        "struct": float(struct.detach().item()),
        "grad": float(grad.detach().item()),
    }


def _validate(model: nn.Module, loader: DataLoader, device: torch.device, epoch: int, profile: Profile) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"ACVTT-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(profile, device)):
                loss, parts = _batch_loss(model, batch, device)
            total += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", l1=f"{parts['l1']:.4f}")
    return total / max(len(loader), 1)


def train_acvtt(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "acvtt_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    dataset_cls = CachedFastMRISingleSliceInterpolationDataset if profile.preload_resized else FastMRISingleSliceInterpolationDataset
    train_ds = dataset_cls("train", profile.stride, profile.train_cases)
    val_ds = dataset_cls("val", profile.stride, profile.val_cases)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.set_float32_matmul_precision("high")
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
    optimizer = torch.optim.AdamW(model.parameters(), lr=profile.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=max(1, profile.patience // 3))
    scaler = torch.amp.GradScaler("cuda", enabled=_autocast_enabled(profile, device))
    rows = []
    best_val = float("inf")
    stale = 0
    print(
        f"{DATASET_NAME} ACVTT 2.5D interpolation: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}, "
        f"grad_accum={profile.grad_accum_steps}, effective_batch={profile.batch_size * profile.grad_accum_steps}, "
        f"num_channel={profile.num_channel}, num_level={profile.num_level}, preload_resized={profile.preload_resized}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        pbar = tqdm(train_loader, desc=f"ACVTT-Epoch {epoch + 1}/{profile.epochs}")
        grad_accum_steps = max(1, profile.grad_accum_steps)
        optimizer.zero_grad(set_to_none=True)
        for step, batch in enumerate(pbar, start=1):
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(profile, device)):
                loss, parts = _batch_loss(model, batch, device)
            scaler.scale(loss / grad_accum_steps).backward()
            if step % grad_accum_steps == 0 or step == len(train_loader):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
            total += float(loss.item())
            pbar.set_postfix(
                loss=f"{loss.item():.4f}",
                l1=f"{parts['l1']:.4f}",
                lr=f"{optimizer.param_groups[0]['lr']:.1e}",
                accum=f"{((step - 1) % grad_accum_steps) + 1}/{grad_accum_steps}",
            )
        train_loss = total / max(len(train_loader), 1)
        val_loss = _validate(model, val_loader, device, epoch + 1, profile)
        scheduler.step(val_loss)
        improved = val_loss < best_val
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
        }
        rows.append(row)
        print(
            f"ACVTT epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "acvtt_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(paths.run_dir / "training_history.json", {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience})
    return best_path


def _checkpoint_payload(model: nn.Module, profile: Profile, epoch: int, best_val: float) -> dict:
    return {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "best_val_loss": best_val,
        "stride": profile.stride,
        "sampling": "acvtt_2p5d",
        "condition": "coarse relative interpolation + left/right sparse reference slices",
        "dataset": DATASET_NAME,
        "batch_size": profile.batch_size,
        "grad_accum_steps": profile.grad_accum_steps,
        "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
        "use_amp": profile.use_amp,
        "preload_resized": profile.preload_resized,
        "model_config": {
            "num_level": profile.num_level,
            "num_ref_enc_level": profile.num_level,
            "num_channel": profile.num_channel,
            "num_ref_channel": profile.num_channel,
            "num_block": profile.num_block,
            "num_block_ref": profile.num_block,
            "scale": profile.stride,
            "transfer_level": profile.transfer_level,
            "block_size_per_level": profile.block_size_per_level,
            "win_block_size_per_level": tuple([2] * profile.num_level),
        },
    }


class FastMRIACVTT2p5DInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload.get("model_config", {})
        self.model = ACVTT2p5D(**config).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = (256, 256)

    def _predict(self, cond_np: np.ndarray) -> np.ndarray:
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda"):
                pred = self.model(cond).float().clamp(0.0, 1.0)
        return pred.squeeze(0).squeeze(0).cpu().numpy()

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
                cond_np = np.stack([left, right, coarse, np.full(self.input_size, rel, dtype=np.float32)], axis=0)
                generated = self._predict(cond_np)
                slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"{DATASET_NAME} ACVTT 2.5D inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count
