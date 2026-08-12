from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from skimage.transform import resize
from torch.utils.data import DataLoader, RandomSampler, Subset
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json
from ixi_diffusion.data import IXISingleSliceInterpolationDataset

from fastmri_brain_pastnet_2p5d.model_ma import PASTNetMultiAnchor2p5D

from .data import IXIMultiAnchorSingleSliceDataset
from .model import PASTNet2p5D
from .settings import Profile, RunPaths


def _autocast_enabled(device: torch.device, profile: Profile | None = None) -> bool:
    return device.type == "cuda" and (profile is None or profile.amp)


def _make_model(profile: Profile, device: torch.device) -> nn.Module:
    if profile.model_variant == "ma3":
        model = PASTNetMultiAnchor2p5D(
            input_channels=13,
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
            temporal_refine=True,
            refine_scale=profile.refine_scale,
        ).to(device)
    else:
        model = PASTNet2p5D(
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
        ).to(device)
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
    return model


def _pastnet_input(cond: torch.Tensor) -> torch.Tensor:
    left = cond[:, 0:1]
    right = cond[:, 1:2]
    coarse = cond[:, 2:3]
    phase = cond[:, 3:4]
    diff = right - left
    return torch.cat([left, right, coarse, phase, diff, diff.abs()], dim=1)


def _reverse_pastnet_input(cond: torch.Tensor) -> torch.Tensor:
    left = cond[:, 0:1]
    right = cond[:, 1:2]
    coarse = cond[:, 2:3]
    phase = cond[:, 3:4]
    diff = left - right
    return torch.cat([right, left, coarse, 1.0 - phase, diff, diff.abs()], dim=1)


def _reverse_multi_anchor_input(cond: torch.Tensor) -> torch.Tensor:
    channels = [
        cond[:, 3:4],
        cond[:, 2:3],
        cond[:, 1:2],
        cond[:, 0:1],
        cond[:, 4:5],
        1.0 - cond[:, 5:6],
        -cond[:, 6:7],
        cond[:, 7:8],
        cond[:, 9:10],
        cond[:, 8:9],
        -cond[:, 11:12],
        -cond[:, 10:11],
        cond[:, 12:13],
    ]
    return torch.cat(channels, dim=1)


def _charbonnier(pred: torch.Tensor, target: torch.Tensor, eps: float = 1e-3) -> torch.Tensor:
    return torch.sqrt((pred - target).pow(2) + eps * eps).mean()


def _gradient_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pred_dx = pred[:, :, :, 1:] - pred[:, :, :, :-1]
    pred_dy = pred[:, :, 1:, :] - pred[:, :, :-1, :]
    target_dx = target[:, :, :, 1:] - target[:, :, :, :-1]
    target_dy = target[:, :, 1:, :] - target[:, :, :-1, :]
    return F.l1_loss(pred_dx, target_dx) + F.l1_loss(pred_dy, target_dy)


def _laplacian_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    kernel = pred.new_tensor(
        [[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]]
    ).view(1, 1, 3, 3)
    return F.l1_loss(F.conv2d(pred, kernel, padding=1), F.conv2d(target, kernel, padding=1))


def _batch_loss(model: nn.Module, batch: dict[str, torch.Tensor], profile: Profile, device: torch.device) -> tuple[torch.Tensor, dict[str, float]]:
    if profile.model_variant == "ma3":
        return _batch_loss_ma3(model, batch, profile, device)
    cond = batch["cond"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)

    x = _pastnet_input(cond)
    out = model.forward_components(x)
    recon = out["prediction"].clamp(0.0, 1.0)
    charb = _charbonnier(recon, target)
    grad = _gradient_loss(recon, target)
    res = F.l1_loss(recon, coarse)
    sym = recon.new_tensor(0.0)
    if profile.lambda_sym > 0:
        reverse = model(_reverse_pastnet_input(cond)).clamp(0.0, 1.0)
        sym = F.l1_loss(recon, reverse)
    loss = charb + profile.lambda_grad * grad + profile.lambda_res * res + profile.lambda_sym * sym
    return loss, {
        "charbonnier": float(charb.detach().item()),
        "gradient": float(grad.detach().item()),
        "residual_reg": float(res.detach().item()),
        "symmetry": float(sym.detach().item()),
        "confidence_mean": float(out["confidence"].detach().mean().item()),
        "gate_left": float(out["gate"][:, 0].detach().mean().item()),
        "gate_right": float(out["gate"][:, 1].detach().mean().item()),
        "gate_coarse": float(out["gate"][:, 2].detach().mean().item()),
    }


def _batch_loss_ma3(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    profile: Profile,
    device: torch.device,
) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond_ma"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)

    out = model.forward_components(cond)
    recon = out["prediction"].clamp(0.0, 1.0)
    charb = _charbonnier(recon, target)
    mse = F.mse_loss(recon, target)
    grad = _gradient_loss(recon, target)
    edge = _laplacian_loss(recon, target)
    res = F.l1_loss(recon, coarse)
    sym = recon.new_tensor(0.0)
    if profile.lambda_sym > 0:
        reverse = model(_reverse_multi_anchor_input(cond)).clamp(0.0, 1.0)
        sym = F.l1_loss(recon, reverse)
    loss = (
        charb
        + profile.lambda_mse * mse
        + profile.lambda_grad * grad
        + profile.lambda_res * res
        + profile.lambda_sym * sym
        + profile.lambda_edge * edge
    )
    gate = out["gate"].detach()
    return loss, {
        "charbonnier": float(charb.detach().item()),
        "mse": float(mse.detach().item()),
        "gradient": float(grad.detach().item()),
        "edge": float(edge.detach().item()),
        "residual_reg": float(res.detach().item()),
        "symmetry": float(sym.detach().item()),
        "confidence_mean": float(out["confidence"].detach().mean().item()),
        "gate_prev": float(gate[:, 0].mean().item()),
        "gate_left": float(gate[:, 1].mean().item()),
        "gate_right": float(gate[:, 2].mean().item()),
        "gate_next": float(gate[:, 3].mean().item()),
        "gate_coarse": float(gate[:, 4].mean().item()),
    }


def _validate(model: nn.Module, loader: DataLoader, profile: Profile, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"PASTNet-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss(model, batch, profile, device)
            if not torch.isfinite(loss):
                continue
            total += float(loss.item())
            count += 1
            pbar.set_postfix(loss=f"{loss.item():.4f}", ch=f"{parts['charbonnier']:.4f}", conf=f"{parts['confidence_mean']:.2f}")
    return total / max(count, 1) if count else float("nan")


def train_pastnet(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "pastnet_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    dataset_class = IXIMultiAnchorSingleSliceDataset if profile.model_variant == "ma3" else IXISingleSliceInterpolationDataset
    train_ds = dataset_class(
        "train", profile.modality, profile.stride, profile.train_cases, target_shape=profile.target_shape
    )
    val_ds = dataset_class(
        "val", profile.modality, profile.stride, profile.val_cases, target_shape=profile.target_shape
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    train_sampler = None
    train_shuffle = True
    if profile.train_samples_per_epoch is not None and profile.train_samples_per_epoch < len(train_ds):
        sampler_generator = torch.Generator().manual_seed(3407)
        train_sampler = RandomSampler(
            train_ds,
            replacement=False,
            num_samples=profile.train_samples_per_epoch,
            generator=sampler_generator,
        )
        train_shuffle = False
    val_data = val_ds
    if profile.val_samples_per_epoch is not None and profile.val_samples_per_epoch < len(val_ds):
        val_indices = np.linspace(
            0, len(val_ds) - 1, num=profile.val_samples_per_epoch, dtype=np.int64
        ).tolist()
        val_data = Subset(val_ds, val_indices)
    train_loader = DataLoader(
        train_ds,
        batch_size=profile.batch_size,
        shuffle=train_shuffle,
        sampler=train_sampler,
        num_workers=profile.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=profile.num_workers > 0,
    )
    val_loader = DataLoader(
        val_data,
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
        f"IXI PAST-Net 2.5D: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}, "
        f"epoch_train_samples={len(train_loader.sampler)}, epoch_val_samples={len(val_data)}, "
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
        pbar = tqdm(train_loader, desc=f"PASTNet-Epoch {epoch + 1}/{profile.epochs}")
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
                else:
                    skipped_nonfinite += 1
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
            total += float(loss.item())
            count += 1
            pbar.set_postfix(
                loss=f"{loss.item():.4f}",
                ch=f"{parts['charbonnier']:.4f}",
                sym=f"{parts['symmetry']:.4f}",
                conf=f"{parts['confidence_mean']:.2f}",
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
            f"PAST-Net epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "pastnet_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path


def _checkpoint_payload(model: nn.Module, profile: Profile, epoch: int, best_val: float) -> dict:
    is_ma3 = profile.model_variant == "ma3"
    return {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "best_val_loss": best_val,
        "modality": profile.modality,
        "stride": profile.stride,
        "target_shape": profile.target_shape,
        "amp": profile.amp,
        "model_variant": profile.model_variant,
        "sampling": (
            "pastnet_multi_anchor_refined_rich_phase_aware_single_slice_residual"
            if is_ma3
            else "pastnet_phase_aware_single_slice_residual"
        ),
        "condition": (
            "prev/left/right/next anchors + linear coarse + phase + directional and absolute differences "
            "+ validity masks + outer-anchor deltas + sparse curvature"
            if is_ma3
            else "left/right anchors + linear coarse + phase + directional difference + abs difference"
        ),
        "batch_size": profile.batch_size,
        "grad_accum_steps": profile.grad_accum_steps,
        "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
        "train_samples_per_epoch": profile.train_samples_per_epoch,
        "val_samples_per_epoch": profile.val_samples_per_epoch,
        "loss": {
            "charbonnier": 1.0,
            "mse": profile.lambda_mse,
            "gradient": profile.lambda_grad,
            "residual_regularization": profile.lambda_res,
            "symmetry": profile.lambda_sym,
            "edge": profile.lambda_edge,
        },
        "model_config": {
            "input_channels": 13 if is_ma3 else 6,
            "base_channels": profile.base_channels,
            "num_blocks": profile.num_blocks,
            "window_size": profile.window_size,
            "mlp_ratio": profile.mlp_ratio,
            "residual_scale": profile.residual_scale,
            **({"temporal_refine": True, "refine_scale": profile.refine_scale} if is_ma3 else {}),
        },
    }


class PASTNet2p5DInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload.get("model_config", {})
        self.model_variant = str(payload.get("model_variant", "v1"))
        if self.model_variant == "ma3":
            self.model = PASTNetMultiAnchor2p5D(**config).to(self.device)
        else:
            self.model = PASTNet2p5D(**config).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = tuple(payload.get("target_shape", (256, 256)))
        self.amp = bool(payload.get("amp", True))

    def _predict_slice(self, cond_np: np.ndarray) -> np.ndarray:
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
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
            diff = (right - left).astype(np.float32)
            absdiff = np.abs(diff).astype(np.float32)
            if self.model_variant == "ma3":
                prev_idx = idx - 1
                next_idx = idx + 2
                prev_valid_value = 1.0 if prev_idx >= 0 else 0.0
                next_valid_value = 1.0 if next_idx < volume.shape[2] else 0.0
                if prev_idx < 0:
                    prev_idx = idx
                if next_idx >= volume.shape[2]:
                    next_idx = idx + 1
                prev_anchor = resize(
                    norm[:, :, prev_idx], self.input_size, preserve_range=True, anti_aliasing=True
                ).astype(np.float32)
                next_anchor = resize(
                    norm[:, :, next_idx], self.input_size, preserve_range=True, anti_aliasing=True
                ).astype(np.float32)
                prev_valid = np.full(self.input_size, prev_valid_value, dtype=np.float32)
                next_valid = np.full(self.input_size, next_valid_value, dtype=np.float32)
                prev_delta = ((left - prev_anchor) * prev_valid_value).astype(np.float32)
                next_delta = ((next_anchor - right) * next_valid_value).astype(np.float32)
                curvature = (next_delta - prev_delta).astype(np.float32)
            for offset in range(1, stride):
                rel = float(offset) / float(stride)
                coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
                phase = np.full(self.input_size, rel, dtype=np.float32)
                if self.model_variant == "ma3":
                    cond_np = np.stack(
                        [
                            prev_anchor,
                            left,
                            right,
                            next_anchor,
                            coarse,
                            phase,
                            diff,
                            absdiff,
                            prev_valid,
                            next_valid,
                            prev_delta,
                            next_delta,
                            curvature,
                        ],
                        axis=0,
                    )
                else:
                    cond_np = np.stack([left, right, coarse, phase, diff, absdiff], axis=0)
                generated = self._predict_slice(cond_np)
                slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI PAST-Net 2.5D inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count
