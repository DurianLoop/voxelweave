from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from skimage.transform import resize

from topcow_diffusion.diffusion import DiffusionSchedule
from topcow_diffusion.model import NoisePredictorUNet

from .common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv


class PureNoiseDiffusionInterpolator:
    def __init__(self, checkpoint: Path, sample_steps: int, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        self.model = NoisePredictorUNet().to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.schedule = DiffusionSchedule(int(payload["diffusion_steps"]), self.device)
        self.sample_steps = sample_steps
        self.input_size = (256, 256)

    def _sample_triplet(self, cond: torch.Tensor) -> np.ndarray:
        x = torch.randn((1, 3, *self.input_size), device=self.device)
        timesteps = self.schedule.sample_timesteps(self.sample_steps)
        with torch.no_grad():
            for idx, step in enumerate(timesteps):
                t = torch.full((1,), step, device=self.device, dtype=torch.long)
                pred_noise = self.model(x, cond, t, self.schedule.steps)
                pred_x0 = self.schedule.predict_x0(x, t, pred_noise).clamp(0, 1)
                if idx == len(timesteps) - 1:
                    x = pred_x0
                else:
                    next_step = timesteps[idx + 1]
                    alpha_next = self.schedule.alpha_bars[next_step]
                    x = alpha_next.sqrt() * pred_x0 + (1 - alpha_next).sqrt() * pred_noise
        return x.squeeze(0).cpu().numpy()

    def interpolate_volume(self, volume: np.ndarray, stride: int = 4) -> np.ndarray:
        norm, lo, hi = normalize_volume(volume)
        out_depth = (volume.shape[2] - 1) * stride + 1
        out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        for idx in range(volume.shape[2]):
            out[:, :, idx * stride] = volume[:, :, idx]
        for idx in range(volume.shape[2] - 1):
            prev = resize(norm[:, :, idx], self.input_size, preserve_range=True, anti_aliasing=True)
            nxt = resize(norm[:, :, idx + 1], self.input_size, preserve_range=True, anti_aliasing=True)
            z_pos = (idx + 0.5) / max(volume.shape[2] - 1, 1)
            cond_np = np.stack(
                [
                    prev,
                    nxt,
                    np.full(self.input_size, z_pos, dtype=np.float32),
                    np.full(self.input_size, 0.25, dtype=np.float32),
                    np.full(self.input_size, 0.50, dtype=np.float32),
                    np.full(self.input_size, 0.75, dtype=np.float32),
                ],
                axis=0,
            )
            cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
            generated = self._sample_triplet(cond)
            for offset in range(1, stride):
                slice_ = resize(generated[offset - 1], volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI pure-noise diffusion inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count


def write_intensity_sanity(gt_dir: Path, pred_dir: Path, baseline_dir: Path, metrics_dir: Path) -> None:
    rows = []
    for gt_path in sorted(gt_dir.glob("*.nii.gz")):
        pred_path = pred_dir / f"diff_{gt_path.name}"
        linear_path = baseline_dir / f"linear_{gt_path.name}"
        gt, _, _ = load_nifti(gt_path)
        pred, _, _ = load_nifti(pred_path)
        linear, _, _ = load_nifti(linear_path)
        for name, data in [("gt", gt), ("diffusion", pred), ("linear", linear)]:
            values = data[np.isfinite(data)]
            rows.append(
                {
                    "case": gt_path.name,
                    "source": name,
                    "min": float(np.min(values)),
                    "p1": float(np.percentile(values, 1)),
                    "median": float(np.percentile(values, 50)),
                    "p99": float(np.percentile(values, 99)),
                    "max": float(np.max(values)),
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                }
            )
    write_csv(metrics_dir / "intensity_sanity.csv", rows)
