from __future__ import annotations

import time
from pathlib import Path

import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from .data import GANMultiSliceDataset
from .losses import gradient_loss, smoothness_loss
from .model import Discriminator, GeneratorUNet


def _autocast_enabled(device: torch.device) -> bool:
    return device.type == "cuda"


def _checkpoint(generator: nn.Module, discriminator: nn.Module, epoch: int, best_val: float, meta: dict) -> dict:
    return {
        "epoch": epoch,
        "generator_state_dict": generator.state_dict(),
        "discriminator_state_dict": discriminator.state_dict(),
        "best_val_loss": best_val,
        **meta,
    }


def _validate(generator: nn.Module, loader: DataLoader, device: torch.device) -> float:
    generator.eval()
    total = 0.0
    with torch.no_grad():
        for cond, target in loader:
            cond = cond.to(device, non_blocking=True)
            target = target.to(device, non_blocking=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                pred, _flows, _coarse = generator(cond)
                loss = F.l1_loss(pred, target) + 0.2 * gradient_loss(pred, target)
            total += float(loss.item())
    return total / max(len(loader), 1)


def train_gan(
    train_paths: list[Path],
    val_paths: list[Path],
    loader,
    checkpoints_dir: Path,
    history_writer,
    epochs: int,
    batch_size: int,
    patience: int,
    lr: float,
    stride: int,
    target_shape: tuple[int, int],
    num_workers: int,
    skip_if_checkpoint_exists: bool,
    meta: dict,
) -> Path:
    if stride < 2:
        raise ValueError(f"stride must be at least 2, got {stride}")
    meta = {**meta, "stride": stride}
    best_path = checkpoints_dir / "gan_epoch_best.pth"
    final_path = checkpoints_dir / "gan_epoch_final.pth"
    if skip_if_checkpoint_exists and best_path.exists() and final_path.exists():
        return best_path
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_ds = GANMultiSliceDataset(train_paths, loader, stride=stride, target_shape=target_shape)
    val_ds = GANMultiSliceDataset(val_paths, loader, stride=stride, target_shape=target_shape)
    if len(train_ds) == 0 or len(val_ds) == 0:
        raise RuntimeError(f"Empty GAN dataset: train_samples={len(train_ds)}, val_samples={len(val_ds)}")
    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=num_workers > 0,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=num_workers > 0,
    )
    target_slices = stride - 1
    condition_channels = target_slices + 3
    generator = GeneratorUNet(in_channels=condition_channels, out_channels=target_slices).to(device)
    discriminator = Discriminator(in_channels=condition_channels + target_slices).to(device)
    g_opt = torch.optim.Adam(generator.parameters(), lr=lr, betas=(0.5, 0.999))
    d_opt = torch.optim.Adam(discriminator.parameters(), lr=lr, betas=(0.5, 0.999))
    adv = nn.MSELoss()
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_val = float("inf")
    stale = 0
    rows: list[dict] = []
    print(
        f"GAN 2.5D: device={device}, train_cases={len(train_paths)}, val_cases={len(val_paths)}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={batch_size}, "
        f"steps_per_epoch={len(train_loader)}, epochs={epochs}"
    )
    for epoch in range(epochs):
        start = time.time()
        generator.train()
        discriminator.train()
        g_total = 0.0
        d_total = 0.0
        pbar = tqdm(train_loader, desc=f"GAN-Epoch {epoch + 1}/{epochs}")
        for cond, target in pbar:
            cond = cond.to(device, non_blocking=True)
            target = target.to(device, non_blocking=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                fake, flows, coarse = generator(cond)
                pred_fake = discriminator(fake, cond)
                valid = torch.full_like(pred_fake, 0.9)
                loss_gan = adv(pred_fake, valid)
                loss_l1 = F.l1_loss(fake, target) * 10.0
                loss_coarse = F.l1_loss(coarse, target) * max(0.0, 5.0 * (1.0 - epoch / max(epochs, 1)))
                loss_grad = gradient_loss(fake, target) * 1.0
                loss_smooth = smoothness_loss(flows) * 0.05
                g_loss = loss_gan + loss_l1 + loss_coarse + loss_grad + loss_smooth
            g_opt.zero_grad(set_to_none=True)
            scaler.scale(g_loss).backward()
            scaler.step(g_opt)
            scaler.update()

            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device)):
                pred_real = discriminator(target, cond)
                real_loss = adv(pred_real, torch.full_like(pred_real, 0.9))
                pred_fake_d = discriminator(fake.detach(), cond)
                fake_loss = adv(pred_fake_d, torch.full_like(pred_fake_d, 0.1))
                d_loss = 0.5 * (real_loss + fake_loss)
            d_opt.zero_grad(set_to_none=True)
            scaler.scale(d_loss).backward()
            scaler.step(d_opt)
            scaler.update()

            g_total += float(g_loss.item())
            d_total += float(d_loss.item())
            pbar.set_postfix(g=f"{g_loss.item():.3f}", d=f"{d_loss.item():.3f}", l1=f"{loss_l1.item():.3f}")
        train_g = g_total / max(len(train_loader), 1)
        train_d = d_total / max(len(train_loader), 1)
        val_loss = _validate(generator, val_loader, device)
        improved = val_loss < best_val
        if improved:
            best_val = val_loss
            stale = 0
            torch.save(_checkpoint(generator, discriminator, epoch, best_val, meta), best_path)
        else:
            stale += 1
        rows.append(
            {
                "epoch": epoch,
                "g_loss": train_g,
                "d_loss": train_d,
                "val_loss": val_loss,
                "best_val_loss": best_val,
                "seconds": time.time() - start,
                "improved": improved,
            }
        )
        print(
            f"GAN epoch {epoch + 1}/{epochs}: G={train_g:.4f}, D={train_d:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, stale={stale}/{patience}"
        )
        if stale >= patience:
            print(f"Early stopping: stale={stale}")
            break
    torch.save(_checkpoint(generator, discriminator, rows[-1]["epoch"], best_val, meta), final_path)
    history_writer(rows)
    return best_path
