from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from skimage.transform import resize
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json

from .data import CachedRASIGroupInterpolationDataset, RASIGroupInterpolationDataset, build_rasinet_condition
from .losses import rasinet_group_loss
from .model import RASINet2p5D
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device, profile: Profile | None = None) -> bool:
    return device.type == "cuda" and (profile is None or profile.amp)


def _make_model(profile: Profile, device: torch.device) -> RASINet2p5D:
    model = RASINet2p5D(
        stride=profile.stride,
        base_channels=profile.base_channels,
        num_blocks=profile.num_blocks,
        mlp_ratio=profile.mlp_ratio,
        residual_scale=profile.residual_scale,
    ).to(device)
    return model


def _loss_weights(profile: Profile) -> dict[str, float]:
    return {
        "lambda_unc": profile.lambda_unc,
        "lambda_logvar": profile.lambda_logvar,
        "lambda_grad_xy": profile.lambda_grad_xy,
        "lambda_res": profile.lambda_res,
        "lambda_cal": profile.lambda_cal,
    }


def _batch_loss(model: nn.Module, batch: dict[str, torch.Tensor], profile: Profile, device: torch.device) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
    out = model.forward_components(cond)
    pred = out["prediction"].clamp(0.0, 1.0)
    loss, parts = rasinet_group_loss(
        pred=pred,
        target=target,
        coarse=coarse,
        residual=out["residual"],
        log_variance=out["log_variance"],
        uncertainty=out["uncertainty"],
        weights=_loss_weights(profile),
    )
    parts["confidence_mean"] = float(out["confidence"].detach().mean().item())
    parts["uncertainty_mean"] = float(out["uncertainty"].detach().mean().item())
    parts["uncertainty_std"] = float(out["uncertainty"].detach().std().item())
    parts["logvar_mean"] = float(out["log_variance"].detach().mean().item())
    return loss, parts


def _validate(model: nn.Module, loader: DataLoader, profile: Profile, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"RASI-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss(model, batch, profile, device)
            if not torch.isfinite(loss):
                continue
            total += float(loss.item())
            count += 1
            pbar.set_postfix(
                loss=f"{loss.item():.4f}",
                rec=f"{parts['rec']:.4f}",
                unc=f"{parts['unc']:.4f}",
                cal=f"{parts['cal']:.4f}",
            )
    return total / max(count, 1) if count else float("nan")


def train_rasinet(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "rasinet_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    dataset_cls = CachedRASIGroupInterpolationDataset if profile.preload_resized else RASIGroupInterpolationDataset
    train_ds = dataset_cls(
        "train",
        profile.modality,
        profile.stride,
        profile.train_cases,
        profile.target_shape,
        profile.window_step,
    )
    val_ds = dataset_cls(
        "val",
        profile.modality,
        profile.stride,
        profile.val_cases,
        profile.target_shape,
        profile.window_step,
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
        f"IXI RASI-Net 2.5D: device={device}, profile={profile.name}, "
        f"train_windows={len(train_ds)}, val_windows={len(val_ds)}, batch={profile.batch_size}, "
        f"grad_accum={profile.grad_accum_steps}, effective_batch={profile.batch_size * profile.grad_accum_steps}, "
        f"channels={profile.base_channels}, blocks={profile.num_blocks}, stride=x{profile.stride}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        count = 0
        skipped_nonfinite = 0
        grad_accum_steps = max(1, profile.grad_accum_steps)
        optimizer.zero_grad(set_to_none=True)
        pbar = tqdm(train_loader, desc=f"RASI-Epoch {epoch + 1}/{profile.epochs}")
        for step, batch in enumerate(pbar, start=1):
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss(model, batch, profile, device)
            if not torch.isfinite(loss):
                skipped_nonfinite += 1
                optimizer.zero_grad(set_to_none=True)
                pbar.set_postfix(loss="nonfinite", skipped=skipped_nonfinite)
                continue
            scaler.scale(loss / grad_accum_steps).backward()
            if step % grad_accum_steps == 0 or step == len(train_loader):
                scaler.unscale_(optimizer)
                grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                if torch.isfinite(grad_norm):
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    skipped_nonfinite += 1
                    scaler.update()
                optimizer.zero_grad(set_to_none=True)
            total += float(loss.item())
            count += 1
            pbar.set_postfix(
                loss=f"{loss.item():.4f}",
                rec=f"{parts['rec']:.4f}",
                unc=f"{parts['unc']:.4f}",
                cal=f"{parts['cal']:.4f}",
                u=f"{parts['uncertainty_mean']:.3f}",
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
        }
        rows.append(row)
        print(
            f"RASI-Net epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "rasinet_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path


def _checkpoint_payload(model: nn.Module, profile: Profile, epoch: int, best_val: float) -> dict:
    return {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "best_val_loss": best_val,
        "modality": profile.modality,
        "stride": profile.stride,
        "target_shape": profile.target_shape,
        "window_step": profile.window_step,
        "amp": profile.amp,
        "sampling": "rasinet_reliability_aware_group",
        "condition": "left/right anchors + all linear coarse phases + phase maps + directional difference + abs difference",
        "batch_size": profile.batch_size,
        "grad_accum_steps": profile.grad_accum_steps,
        "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
        "loss": _loss_weights(profile),
        "model_config": {
            "stride": profile.stride,
            "base_channels": profile.base_channels,
            "num_blocks": profile.num_blocks,
            "mlp_ratio": profile.mlp_ratio,
            "residual_scale": profile.residual_scale,
        },
    }


class RASINet2p5DInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload.get("model_config", {})
        self.model = RASINet2p5D(**config).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = tuple(payload.get("target_shape", (256, 256)))
        self.amp = bool(payload.get("amp", True))

    def _predict_group_components(self, cond_np: np.ndarray) -> dict[str, np.ndarray]:
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
                out = self.model.forward_components(cond)
        return {
            "prediction": out["prediction"].float().clamp(0.0, 1.0).squeeze(0).cpu().numpy(),
            "uncertainty": out["uncertainty"].float().squeeze(0).cpu().numpy(),
            "confidence": out["confidence"].float().squeeze(0).cpu().numpy(),
            "residual": out["residual"].float().squeeze(0).cpu().numpy(),
        }

    def interpolate_volume(self, volume: np.ndarray, stride: int = 4) -> dict[str, np.ndarray]:
        norm, lo, hi = normalize_volume(volume)
        out_depth = (volume.shape[2] - 1) * stride + 1
        out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        uncertainty = np.zeros_like(out, dtype=np.float32)
        confidence = np.ones_like(out, dtype=np.float32)
        residual = np.zeros_like(out, dtype=np.float32)
        for idx in range(volume.shape[2]):
            out[:, :, idx * stride] = volume[:, :, idx]
        for idx in range(volume.shape[2] - 1):
            left = resize(norm[:, :, idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            right = resize(norm[:, :, idx + 1], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            cond_np, _coarse = build_rasinet_condition(left, right, stride, self.input_size)
            generated = self._predict_group_components(cond_np)
            for offset in range(1, stride):
                out[:, :, idx * stride + offset] = (
                    resize(generated["prediction"][offset - 1], volume.shape[:2], preserve_range=True, anti_aliasing=True)
                    * (hi - lo)
                    + lo
                )
                uncertainty[:, :, idx * stride + offset] = resize(
                    generated["uncertainty"][offset - 1],
                    volume.shape[:2],
                    preserve_range=True,
                    anti_aliasing=True,
                )
                confidence[:, :, idx * stride + offset] = resize(
                    generated["confidence"][offset - 1],
                    volume.shape[:2],
                    preserve_range=True,
                    anti_aliasing=True,
                )
                residual[:, :, idx * stride + offset] = (
                    resize(generated["residual"][offset - 1], volume.shape[:2], preserve_range=True, anti_aliasing=True)
                    * (hi - lo)
                )
        return {
            "prediction": out,
            "uncertainty": uncertainty,
            "confidence": confidence,
            "residual": residual,
        }

    def process_folder(
        self,
        input_dir: Path,
        output_dir: Path,
        stride: int,
        uncertainty_dir: Path | None = None,
        confidence_dir: Path | None = None,
        residual_dir: Path | None = None,
    ) -> int:
        ensure_dir(output_dir)
        if uncertainty_dir is not None:
            ensure_dir(uncertainty_dir)
        if confidence_dir is not None:
            ensure_dir(confidence_dir)
        if residual_dir is not None:
            ensure_dir(residual_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI RASI-Net 2.5D inference: {src.name}")
            volume, affine, header = load_nifti(src)
            maps = self.interpolate_volume(volume, stride=stride)
            save_nifti(maps["prediction"], affine, header, output_dir / f"diff_{src.name}")
            if uncertainty_dir is not None:
                save_nifti(maps["uncertainty"], affine, header, uncertainty_dir / f"uncertainty_{src.name}")
            if confidence_dir is not None:
                save_nifti(maps["confidence"], affine, header, confidence_dir / f"confidence_{src.name}")
            if residual_dir is not None:
                save_nifti(maps["residual"], affine, header, residual_dir / f"residual_{src.name}")
            count += 1
        return count
