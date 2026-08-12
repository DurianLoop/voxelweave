from __future__ import annotations

import sys
import time
from argparse import Namespace
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from skimage.transform import resize
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json

from .data import IXII3NetWindowDataset
from .settings import Profile, RunPaths


PROJECT_ROOT = Path(__file__).resolve().parents[2]
I3NET_ROOT = PROJECT_ROOT / "external" / "I3Net"
if str(I3NET_ROOT) not in sys.path:
    sys.path.insert(0, str(I3NET_ROOT))

from model_zoo.i3net.basic_model import I3Net  # noqa: E402


def _autocast_enabled(device: torch.device, profile: Profile | None = None) -> bool:
    return device.type == "cuda" and (profile is None or profile.amp)


def _model_args(profile: Profile) -> Namespace:
    return Namespace(
        upscale=profile.stride,
        lr_slice_patch=profile.lr_slice_patch,
        hr_slice_patch=profile.hr_slice_patch,
        kernel_size=profile.kernel_size,
        n_feats=profile.n_feats,
        num_blocks=profile.num_blocks,
        res_scale=profile.res_scale,
        head_num=profile.head_num,
        window_size=profile.window_size,
        win_num_sqrt=profile.win_num_sqrt,
    )


def _make_model(profile: Profile, device: torch.device) -> I3Net:
    return I3Net(_model_args(profile)).to(device)


def _batch_loss(model: torch.nn.Module, hr: torch.Tensor, profile: Profile, device: torch.device) -> torch.Tensor:
    gt = hr.to(device, non_blocking=True)
    lr = gt[..., :: profile.stride]
    sr = model(lr).clamp(0.0, 1.0)
    return F.l1_loss(sr, gt)


def _validate(model: torch.nn.Module, loader: DataLoader, profile: Profile, device: torch.device, epoch: int) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"I3Net-Val {epoch}", leave=False)
        for hr in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss = _batch_loss(model, hr, profile, device)
            if not torch.isfinite(loss):
                continue
            total += float(loss.item())
            count += 1
            pbar.set_postfix(loss=f"{loss.item():.4f}")
    return total / max(count, 1) if count else float("nan")


def _checkpoint_payload(model: torch.nn.Module, profile: Profile, epoch: int, best_val: float) -> dict:
    condition = f"{profile.lr_slice_patch} sparse through-plane slices -> {profile.hr_slice_patch} HR slices for x{profile.stride}"
    return {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "best_val_loss": best_val,
        "modality": profile.modality,
        "stride": profile.stride,
        "sampling": "i3net_inter_intra_slice_window",
        "condition": condition,
        "model_config": {
            "lr_slice_patch": profile.lr_slice_patch,
            "hr_slice_patch": profile.hr_slice_patch,
            "kernel_size": profile.kernel_size,
            "n_feats": profile.n_feats,
            "num_blocks": profile.num_blocks,
            "res_scale": profile.res_scale,
            "head_num": profile.head_num,
            "window_size": profile.window_size,
            "win_num_sqrt": profile.win_num_sqrt,
            "amp": profile.amp,
        },
    }


def train_i3net(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "i3net_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    train_ds = IXII3NetWindowDataset("train", profile)
    val_ds = IXII3NetWindowDataset("val", profile)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    train_loader = DataLoader(
        train_ds,
        batch_size=profile.batch_size,
        shuffle=profile.shuffle_windows,
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
        f"IXI I3Net interpolation: device={device}, profile={profile.name}, "
        f"train_windows={len(train_ds)}, val_windows={len(val_ds)}, batch={profile.batch_size}, "
        f"n_feats={profile.n_feats}, blocks={profile.num_blocks}, "
        f"shuffle={profile.shuffle_windows}, cache_resized={profile.cache_resized_volumes}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        count = 0
        skipped_nonfinite = 0
        pbar = tqdm(train_loader, desc=f"I3Net-Epoch {epoch + 1}/{profile.epochs}")
        for hr in pbar:
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss = _batch_loss(model, hr, profile, device)
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
            pbar.set_postfix(loss=f"{loss.item():.4f}", lr=f"{optimizer.param_groups[0]['lr']:.1e}", skipped=skipped_nonfinite)
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
            f"I3Net epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "i3net_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path


class I3NetInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None, label: str = "IXI"):
        self.label = label
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload["model_config"]
        checkpoint_stride = int(payload.get("stride", config.get("stride", 4)))
        profile = Profile(
            name="loaded",
            stride=checkpoint_stride,
            **{k: v for k, v in config.items() if k not in {"hr_slice_patch", "stride"}},
        )
        self.amp = bool(config.get("amp", True))
        self.stride = checkpoint_stride
        self.lr_slice_patch = profile.lr_slice_patch
        self.input_size = profile.target_shape
        self.model = _make_model(profile, self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()

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
        with torch.no_grad():
            for start in range(resized.shape[2] - self.lr_slice_patch + 1):
                lr_window = resized[:, :, start : start + self.lr_slice_patch]
                tensor = torch.from_numpy(lr_window).float().unsqueeze(0).to(self.device)
                with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
                    pred = self.model(tensor).float().clamp(0.0, 1.0)
                pred_np = pred.squeeze(0).cpu().numpy()
                out_start = start * stride
                out_end = out_start + pred_np.shape[2]
                sr[:, :, out_start:out_end] += pred_np
                sr_count[:, :, out_start:out_end] += 1.0
        if np.any(sr_count == 0):
            raise RuntimeError("I3Net sliding-window inference left uncovered slices")
        sr /= sr_count
        restored = np.empty((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        for idx in range(out_depth):
            restored[:, :, idx] = resize(sr[:, :, idx], volume.shape[:2], preserve_range=True, anti_aliasing=True)
        return restored * (hi - lo) + lo

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"{self.label} I3Net inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count
