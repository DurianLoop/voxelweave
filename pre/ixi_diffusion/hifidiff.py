from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from skimage.transform import resize
from torch.utils.data import DataLoader
from tqdm import tqdm

from topcow_diffusion.diffusion import DiffusionSchedule
from topcow_diffusion.losses import structural_reconstruction_loss
from topcow_diffusion.model import NoisePredictorUNet

from .common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json
from .data import IXISingleSliceInterpolationDataset
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device) -> bool:
    return device.type == "cuda"


def _build_model() -> NoisePredictorUNet:
    return NoisePredictorUNet(in_channels=6, out_channels=1, base_channels=32)


def _reconstruct_from_residual(coarse: torch.Tensor, residual01: torch.Tensor) -> torch.Tensor:
    residual = residual01 * 2.0 - 1.0
    return (coarse + residual).clamp(0.0, 1.0)


def _batch_loss(model, schedule, batch, device, diffusion_steps: int) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond"].to(device, non_blocking=True)
    target_residual = batch["residual01"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        target_residual = target_residual.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)
    t = torch.randint(0, diffusion_steps, (target_residual.shape[0],), device=device)
    noise = torch.randn_like(target_residual)
    noisy = schedule.q_sample(target_residual, t, noise)
    pred_noise = model(noisy, cond, t, diffusion_steps)
    pred_residual01 = schedule.predict_x0(noisy, t, pred_noise).clamp(0.0, 1.0)
    recon = _reconstruct_from_residual(coarse, pred_residual01)
    noise_loss = torch.mean((pred_noise - noise) ** 2)
    recon_l1 = F.l1_loss(recon, target)
    struct = structural_reconstruction_loss(recon, target)
    loss = noise_loss + 0.5 * recon_l1 + 0.2 * struct
    return loss, {
        "noise": float(noise_loss.detach().item()),
        "l1": float(recon_l1.detach().item()),
        "struct": float(struct.detach().item()),
    }


def _validate(model, loader, schedule, device, profile: Profile, epoch: int) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"HiFi-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                loss, parts = _batch_loss(model, schedule, batch, device, profile.diffusion_steps)
            total += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", l1=f"{parts['l1']:.4f}")
    return total / max(len(loader), 1)


def train_hifidiff(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "hifidiff_epoch_best.pth"
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

    model = _build_model().to(device)
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
        f"IXI HiFiDiff-like residual diffusion: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}, "
        f"diffusion_steps={profile.diffusion_steps}, sample_steps={profile.sample_steps}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        accum = 0.0
        pbar = tqdm(train_loader, desc=f"HiFi-Epoch {epoch + 1}/{profile.epochs}")
        for batch in pbar:
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                loss, parts = _batch_loss(model, schedule, batch, device, profile.diffusion_steps)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            accum += float(loss.item())
            pbar.set_postfix(
                loss=f"{loss.item():.4f}",
                noise=f"{parts['noise']:.4f}",
                l1=f"{parts['l1']:.4f}",
                lr=f"{optimizer.param_groups[0]['lr']:.1e}",
            )
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
                    "sampling": "hifidiff_residual",
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
            f"HiFi epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, val={val_loss:.4f}, "
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
            "diffusion_steps": profile.diffusion_steps,
            "modality": profile.modality,
            "stride": profile.stride,
            "sampling": "hifidiff_residual",
            "condition": "left_right_linear_coarse_relative_position",
        },
        paths.checkpoints / "hifidiff_epoch_final.pth",
    )
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path


class HiFiDiffResidualInterpolator:
    def __init__(
        self,
        checkpoint: Path,
        sample_steps: int,
        device: str | None = None,
        partial_start_fraction: float = 0.20,
    ):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        self.model = _build_model().to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.schedule = DiffusionSchedule(int(payload["diffusion_steps"]), self.device)
        self.sample_steps = sample_steps
        self.input_size = (256, 256)
        self.partial_start_fraction = float(partial_start_fraction)

    def _sample_residual(self, cond: torch.Tensor) -> np.ndarray:
        start_step = max(1, int(round((self.schedule.steps - 1) * self.partial_start_fraction)))
        timesteps_tensor = torch.linspace(start_step, 0, self.sample_steps, device=self.device).round().long()
        timesteps = [int(v.item()) for v in timesteps_tensor]
        zero_residual = torch.full((1, 1, *self.input_size), 0.5, device=self.device)
        noise = torch.randn_like(zero_residual)
        t0 = torch.full((1,), timesteps[0], device=self.device, dtype=torch.long)
        x = self.schedule.q_sample(zero_residual, t0, noise)
        with torch.no_grad():
            for idx, step in enumerate(timesteps):
                t = torch.full((1,), step, device=self.device, dtype=torch.long)
                pred_noise = self.model(x, cond, t, self.schedule.steps)
                pred_x0 = self.schedule.predict_x0(x, t, pred_noise).clamp(0.0, 1.0)
                if idx == len(timesteps) - 1:
                    x = pred_x0
                else:
                    next_step = timesteps[idx + 1]
                    alpha_next = self.schedule.alpha_bars[next_step]
                    x = alpha_next.sqrt() * pred_x0 + (1 - alpha_next).sqrt() * pred_noise
        return x.squeeze(0).squeeze(0).cpu().numpy()

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
                residual01 = self._sample_residual(cond)
                generated = np.clip(coarse + (residual01 * 2.0 - 1.0), 0.0, 1.0)
                slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI HiFiDiff-like inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count
