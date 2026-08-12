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

from .data import ACSIV2WindowDataset, build_acsi_v2_condition
from .losses import acsi_v2_loss
from .model import ACSINetV2
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device, profile: Profile | None = None) -> bool:
    return device.type == "cuda" and (profile is None or profile.amp)


def _make_model(profile: Profile, device: torch.device) -> ACSINetV2:
    return ACSINetV2(
        stride=profile.stride,
        lr_slice_patch=profile.lr_slice_patch,
        base_channels=profile.base_channels,
        num_blocks=profile.num_blocks,
        z_refine_channels=profile.z_refine_channels,
        mlp_ratio=profile.mlp_ratio,
        residual_scale=profile.residual_scale,
    ).to(device)


def _loss_weights(profile: Profile) -> dict[str, float]:
    return {
        "lambda_grad_xy": profile.lambda_grad_xy,
        "lambda_zgrad": profile.lambda_zgrad,
        "lambda_zlap": profile.lambda_zlap,
        "lambda_edge_z": profile.lambda_edge_z,
        "lambda_z_ncc": profile.lambda_z_ncc,
        "lambda_anat": profile.lambda_anat,
        "lambda_res": profile.lambda_res,
    }


def _batch_loss(model: nn.Module, batch: dict[str, torch.Tensor], profile: Profile, device: torch.device) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    gen_mask = batch["gen_mask"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
    out = model.forward_components(cond)
    pred = out["prediction"].clamp(0.0, 1.0)
    loss, parts = acsi_v2_loss(
        pred=pred,
        target=target,
        coarse=coarse,
        residual=out["residual"],
        gen_mask_1d=gen_mask,
        weights=_loss_weights(profile),
    )
    parts["confidence_mean"] = float(out["confidence"].detach().mean().item())
    return loss, parts


def _validate(model: nn.Module, loader: DataLoader, profile: Profile, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"ACSI-v2-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss(model, batch, profile, device)
            if not torch.isfinite(loss):
                continue
            total += float(loss.item())
            count += 1
            pbar.set_postfix(loss=f"{loss.item():.4f}", rec=f"{parts['rec']:.4f}", zg=f"{parts['zgrad']:.4f}")
    return total / max(count, 1) if count else float("nan")


def train_acsinet_v2(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "acsinet_v2_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    train_ds = ACSIV2WindowDataset("train", profile)
    val_ds = ACSIV2WindowDataset("val", profile)
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
        f"IXI ACSI-Net v2: device={device}, profile={profile.name}, "
        f"train_windows={len(train_ds)}, val_windows={len(val_ds)}, batch={profile.batch_size}, "
        f"anchors={profile.lr_slice_patch}, hr_patch={profile.hr_slice_patch}, channels={profile.base_channels}, "
        f"blocks={profile.num_blocks}, stride=x{profile.stride}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        count = 0
        skipped_nonfinite = 0
        grad_accum_steps = max(1, profile.grad_accum_steps)
        optimizer.zero_grad(set_to_none=True)
        pbar = tqdm(train_loader, desc=f"ACSI-v2-Epoch {epoch + 1}/{profile.epochs}")
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
            f"ACSI-Net v2 epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "acsinet_v2_epoch_final.pth")
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
        "lr_slice_patch": profile.lr_slice_patch,
        "hr_slice_patch": profile.hr_slice_patch,
        "target_shape": profile.target_shape,
        "window_step": profile.window_step,
        "amp": profile.amp,
        "sampling": "acsinet_v2_multi_anchor_anatomy_consistent",
        "condition": "4 sparse anchors + 13 linear coarse slices + 13 phase maps + adjacent-anchor differences",
        "batch_size": profile.batch_size,
        "grad_accum_steps": profile.grad_accum_steps,
        "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
        "loss": _loss_weights(profile),
        "model_config": {
            "stride": profile.stride,
            "lr_slice_patch": profile.lr_slice_patch,
            "base_channels": profile.base_channels,
            "num_blocks": profile.num_blocks,
            "z_refine_channels": profile.z_refine_channels,
            "mlp_ratio": profile.mlp_ratio,
            "residual_scale": profile.residual_scale,
        },
    }


class ACSINetV2Interpolator:
    def __init__(self, checkpoint: Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload["model_config"]
        self.model = ACSINetV2(**config).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = tuple(payload.get("target_shape", (256, 256)))
        self.amp = bool(payload.get("amp", True))
        self.stride = int(payload.get("stride", 4))
        self.lr_slice_patch = int(payload.get("lr_slice_patch", 4))
        self.profile = Profile(
            name="loaded",
            stride=self.stride,
            lr_slice_patch=self.lr_slice_patch,
            target_shape=self.input_size,
            amp=self.amp,
            **{k: v for k, v in config.items() if k not in {"stride", "lr_slice_patch"}},
        )

    def _predict_window(self, window: np.ndarray) -> np.ndarray:
        cond_np, _coarse, _gen_mask = build_acsi_v2_condition(window, self.profile)
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
                pred = self.model(cond).float().clamp(0.0, 1.0)
        return pred.squeeze(0).cpu().numpy()

    def interpolate_volume(self, volume: np.ndarray, stride: int = 4) -> np.ndarray:
        if stride != self.stride:
            raise ValueError(f"Checkpoint stride={self.stride}, requested stride={stride}")
        norm, lo, hi = normalize_volume(volume)
        resized = np.stack(
            [
                resize(norm[:, :, idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
                for idx in range(norm.shape[2])
            ],
            axis=-1,
        )
        out_depth = (resized.shape[2] - 1) * stride + 1
        sr = np.zeros((*self.input_size, out_depth), dtype=np.float32)
        sr_count = np.zeros((*self.input_size, out_depth), dtype=np.float32)
        for start in range(resized.shape[2] - self.lr_slice_patch + 1):
            sparse_window = resized[:, :, start : start + self.lr_slice_patch]
            hr_window = np.empty((*self.input_size, self.profile.hr_slice_patch), dtype=np.float32)
            for idx in range(self.profile.hr_slice_patch):
                left_anchor = idx // stride
                right_anchor = min(left_anchor + 1, self.lr_slice_patch - 1)
                if idx % stride == 0:
                    hr_window[:, :, idx] = sparse_window[:, :, left_anchor]
                else:
                    rel = float(idx - left_anchor * stride) / float(stride)
                    hr_window[:, :, idx] = (1.0 - rel) * sparse_window[:, :, left_anchor] + rel * sparse_window[:, :, right_anchor]
            pred_np = self._predict_window(hr_window)
            out_start = start * stride
            out_end = out_start + pred_np.shape[0]
            sr[:, :, out_start:out_end] += np.moveaxis(pred_np, 0, -1)
            sr_count[:, :, out_start:out_end] += 1.0
        if np.any(sr_count == 0):
            raise RuntimeError("ACSI-v2 sliding-window inference left uncovered slices")
        sr /= sr_count
        restored = np.empty((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        for idx in range(out_depth):
            restored[:, :, idx] = resize(sr[:, :, idx], volume.shape[:2], preserve_range=True, anti_aliasing=True)
        return restored * (hi - lo) + lo

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI ACSI-Net v2 inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count


def write_complexity(paths: RunPaths, profile: Profile) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = _make_model(profile, device)
    params = sum(p.numel() for p in model.parameters())
    macs = 0

    def hook(module, _inputs, output):
        nonlocal macs
        kernel_ops = 1
        for value in module.kernel_size:
            kernel_ops *= value
        kernel_ops *= module.in_channels // module.groups
        macs += int(output.numel() * kernel_ops)

    handles = []
    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.Conv3d)):
            handles.append(module.register_forward_hook(hook))
    with torch.no_grad():
        dummy = torch.zeros(1, model.input_channels, *profile.target_shape, device=device)
        model(dummy)
    for handle in handles:
        handle.remove()
    macs_g = macs / 1e9
    write_json(
        paths.metrics / "complexity.json",
        {
            "model": "acsinet_v2_multi_anchor_anatomy_consistent",
            "params": int(params),
            "params_m": params / 1e6,
            "window_forward_macs_g": macs_g,
            "window_forward_flops_g": 2.0 * macs_g,
            "generated_slices_per_window": profile.hr_slice_patch - profile.lr_slice_patch,
            "per_generated_slice_flops_g": (2.0 * macs_g) / max(1, profile.hr_slice_patch - profile.lr_slice_patch),
            "flops_definition": f"one {profile.target_shape[0]}x{profile.target_shape[1]} ACSI-v2 window forward, "
            f"{profile.lr_slice_patch} sparse anchors -> {profile.hr_slice_patch} HR slices",
        },
    )
