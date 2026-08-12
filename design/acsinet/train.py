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

from .data import ACSIGroupInterpolationDataset, CachedACSIGroupInterpolationDataset, build_acsinet_condition
from .losses import acsi_group_loss
from .model import ACSINet2p5D
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device, profile: Profile | None = None) -> bool:
    return device.type == "cuda" and (profile is None or profile.amp)


def _make_model(profile: Profile, device: torch.device) -> ACSINet2p5D:
    model = ACSINet2p5D(
        stride=profile.stride,
        base_channels=profile.base_channels,
        num_blocks=profile.num_blocks,
        z_refine_channels=profile.z_refine_channels,
        mlp_ratio=profile.mlp_ratio,
        residual_scale=profile.residual_scale,
    ).to(device)
    return model


def _loss_weights(profile: Profile) -> dict[str, float]:
    return {
        "lambda_grad_xy": profile.lambda_grad_xy,
        "lambda_zgrad": profile.lambda_zgrad,
        "lambda_zlap": profile.lambda_zlap,
        "lambda_edge_z": profile.lambda_edge_z,
        "lambda_anat": profile.lambda_anat,
        "lambda_res": profile.lambda_res,
    }


def _batch_loss(model: nn.Module, batch: dict[str, torch.Tensor], profile: Profile, device: torch.device) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
    out = model.forward_components(cond)
    pred = out["prediction"].clamp(0.0, 1.0)
    anchors = cond[:, 0:2]
    loss, parts = acsi_group_loss(
        pred=pred,
        target=target,
        coarse=coarse,
        anchors=anchors,
        residual=out["residual"],
        weights=_loss_weights(profile),
    )
    parts["confidence_mean"] = float(out["confidence"].detach().mean().item())
    return loss, parts


def _validate(model: nn.Module, loader: DataLoader, profile: Profile, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"ACSI-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss(model, batch, profile, device)
            if not torch.isfinite(loss):
                continue
            total += float(loss.item())
            count += 1
            pbar.set_postfix(loss=f"{loss.item():.4f}", rec=f"{parts['rec']:.4f}", zg=f"{parts['zgrad']:.4f}")
    return total / max(count, 1) if count else float("nan")


def train_acsinet(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "acsinet_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    dataset_cls = CachedACSIGroupInterpolationDataset if profile.preload_resized else ACSIGroupInterpolationDataset
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
        f"IXI ACSI-Net 2.5D: device={device}, profile={profile.name}, "
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
        pbar = tqdm(train_loader, desc=f"ACSI-Epoch {epoch + 1}/{profile.epochs}")
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
                zg=f"{parts['zgrad']:.4f}",
                ez=f"{parts['edge_z']:.4f}",
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
            f"ACSI-Net epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "acsinet_epoch_final.pth")
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
        "sampling": "acsinet_group_anatomy_consistent",
        "condition": "left/right anchors + all linear coarse phases + phase maps + directional difference + abs difference",
        "batch_size": profile.batch_size,
        "grad_accum_steps": profile.grad_accum_steps,
        "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
        "loss": _loss_weights(profile),
        "model_config": {
            "stride": profile.stride,
            "base_channels": profile.base_channels,
            "num_blocks": profile.num_blocks,
            "z_refine_channels": profile.z_refine_channels,
            "mlp_ratio": profile.mlp_ratio,
            "residual_scale": profile.residual_scale,
        },
    }


class ACSINet2p5DInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload.get("model_config", {})
        self.model = ACSINet2p5D(**config).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = tuple(payload.get("target_shape", (256, 256)))
        self.amp = bool(payload.get("amp", True))

    def _predict_group(self, cond_np: np.ndarray) -> np.ndarray:
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
                pred = self.model(cond).float().clamp(0.0, 1.0)
        return pred.squeeze(0).cpu().numpy()

    def interpolate_volume(self, volume: np.ndarray, stride: int = 4) -> np.ndarray:
        norm, lo, hi = normalize_volume(volume)
        out_depth = (volume.shape[2] - 1) * stride + 1
        out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        for idx in range(volume.shape[2]):
            out[:, :, idx * stride] = volume[:, :, idx]
        for idx in range(volume.shape[2] - 1):
            left = resize(norm[:, :, idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            right = resize(norm[:, :, idx + 1], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            cond_np, _coarse = build_acsinet_condition(left, right, stride, self.input_size)
            generated_group = self._predict_group(cond_np)
            for offset in range(1, stride):
                generated = resize(generated_group[offset - 1], volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = generated * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI ACSI-Net 2.5D inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count
