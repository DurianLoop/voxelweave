from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
from skimage.transform import resize
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json
from ixi_diffusion.data import IXISingleSliceInterpolationDataset, case_paths

from .model import ResSRDiff2p5D
from .settings import Profile, RunPaths


class CachedIXISingleSliceInterpolationDataset(Dataset):
    def __init__(
        self,
        split: str,
        modality: str,
        stride: int = 4,
        case_limit: int | None = None,
        target_shape: tuple[int, int] = (256, 256),
    ):
        self.split = split
        self.modality = modality
        self.stride = stride
        self.target_shape = target_shape
        self.volumes: list[np.ndarray] = []
        self.items: list[tuple[int, int, int]] = []
        paths = case_paths(split, modality, case_limit)
        print(f"IXI {split} cached single-slice: loading/resizing {len(paths)} cases...")
        for case_index, path in enumerate(tqdm(paths, desc=f"ResSRDiff-cache-{split}")):
            volume, _, _ = load_nifti(path)
            norm, _, _ = normalize_volume(volume)
            depth = int(norm.shape[2])
            resized = np.empty((depth, *target_shape), dtype=np.float16)
            for z in range(depth):
                resized[z] = resize(
                    norm[:, :, z],
                    target_shape,
                    preserve_range=True,
                    anti_aliasing=True,
                ).astype(np.float16)
            self.volumes.append(resized)
            for z in range(0, depth - stride):
                for offset in range(1, stride):
                    self.items.append((case_index, z, offset))
        print(
            f"IXI {split} cached single-slice: modality={modality}, cases={len(paths)}, "
            f"samples={len(self.items)}, stride={stride}, cache_gb={self.cache_gb:.2f}"
        )

    @property
    def cache_gb(self) -> float:
        return sum(volume.nbytes for volume in self.volumes) / 1024**3

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        case_index, z, offset = self.items[index]
        volume = self.volumes[case_index]
        left = volume[z].astype(np.float32, copy=False)
        right = volume[z + self.stride].astype(np.float32, copy=False)
        target = volume[z + offset].astype(np.float32, copy=False)
        rel = float(offset) / float(self.stride)
        coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
        return {
            "coarse": torch.from_numpy(coarse[None, :, :]),
            "target": torch.from_numpy(target[None, :, :]),
        }


def _autocast_enabled(profile: Profile, device: torch.device) -> bool:
    return device.type == "cuda" and profile.use_amp


def _make_model(profile: Profile, device: torch.device) -> ResSRDiff2p5D:
    return ResSRDiff2p5D(
        model_channels=profile.model_channels,
        num_res_blocks=profile.num_res_blocks,
        attention_resolutions=profile.attention_resolutions,
        steps=profile.steps,
    ).to(device)


def _batch_loss(model: ResSRDiff2p5D, batch: dict[str, torch.Tensor], device: torch.device) -> tuple[torch.Tensor, dict[str, float]]:
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    return model.training_loss(target, coarse)


def _validate(model: ResSRDiff2p5D, loader: DataLoader, device: torch.device, epoch: int, profile: Profile) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"ResSRDiff-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(profile, device)):
                loss, parts = _batch_loss(model, batch, device)
            total += float(loss.item())
            pbar.set_postfix(loss=f"{loss.item():.4f}", mse=f"{parts['mse']:.4f}")
    return total / max(len(loader), 1)


def train_ressrdiff(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "ressrdiff_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    dataset_cls = CachedIXISingleSliceInterpolationDataset if profile.preload_resized else IXISingleSliceInterpolationDataset
    train_ds = dataset_cls("train", profile.modality, profile.stride, profile.train_cases)
    val_ds = dataset_cls("val", profile.modality, profile.stride, profile.val_cases)
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
    optimizer = torch.optim.RAdam(model.parameters(), lr=profile.lr, betas=(0.9, 0.999), weight_decay=1e-5)
    scaler = torch.amp.GradScaler("cuda", enabled=_autocast_enabled(profile, device))
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=max(1, profile.patience // 3),
    )
    rows = []
    best_val = float("inf")
    stale = 0
    print(
        f"IXI Res-SRDiff 2.5D refinement: device={device}, profile={profile.name}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}, "
        f"grad_accum={profile.grad_accum_steps}, effective_batch={profile.batch_size * profile.grad_accum_steps}, "
        f"model_channels={profile.model_channels}, steps={profile.steps}, amp={profile.use_amp}, "
        f"preload_resized={profile.preload_resized}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        model.train()
        total = 0.0
        pbar = tqdm(train_loader, desc=f"ResSRDiff-Epoch {epoch + 1}/{profile.epochs}")
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
                mse=f"{parts['mse']:.4f}",
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
            f"Res-SRDiff epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    torch.save(_checkpoint_payload(model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "ressrdiff_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {"best_val_loss": best_val, "epochs_completed": len(rows), "early_stopped": stale >= profile.patience},
    )
    return best_path


def _checkpoint_payload(model: ResSRDiff2p5D, profile: Profile, epoch: int, best_val: float) -> dict:
    return {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "best_val_loss": best_val,
        "modality": profile.modality,
        "stride": profile.stride,
        "sampling": "ressrdiff_2p5d_refinement",
        "condition": "linear coarse slice as low-quality conditioning image",
        "batch_size": profile.batch_size,
        "grad_accum_steps": profile.grad_accum_steps,
        "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
        "use_amp": profile.use_amp,
        "preload_resized": profile.preload_resized,
        "model_config": {
            "model_channels": profile.model_channels,
            "num_res_blocks": profile.num_res_blocks,
            "attention_resolutions": profile.attention_resolutions,
            "steps": profile.steps,
        },
    }


class ResSRDiff2p5DInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload.get("model_config", {})
        self.model = ResSRDiff2p5D(**config).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = (256, 256)

    def _predict(self, coarse_np: np.ndarray) -> np.ndarray:
        coarse = torch.from_numpy(coarse_np).float().unsqueeze(0).unsqueeze(0).to(self.device)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda"):
                pred = self.model.sample(coarse).float().clamp(0.0, 1.0)
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
                generated = self._predict(coarse)
                slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI Res-SRDiff 2.5D inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count
