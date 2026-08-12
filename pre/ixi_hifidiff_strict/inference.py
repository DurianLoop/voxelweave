from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from skimage.transform import resize

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv
from topcow_diffusion.diffusion import DiffusionSchedule

from .data import from_model_space, to_model_space
from .model import StrictHiFiDiffUNet


class StrictHiFiDiffInterpolator:
    def __init__(self, checkpoint: Path, sample_steps: int, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        self.input_size = (int(payload["target_size"]), int(payload["target_size"]))
        self.model = StrictHiFiDiffUNet(base_channels=int(payload["base_channels"])).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.schedule = DiffusionSchedule(int(payload["diffusion_steps"]), self.device)
        self.sample_steps = sample_steps

    def _sample_slice(self, cond: torch.Tensor, offset: torch.Tensor) -> np.ndarray:
        x = torch.randn((1, 1, *self.input_size), device=self.device)
        timesteps = self.schedule.sample_timesteps(self.sample_steps)
        with torch.no_grad():
            for idx, step in enumerate(timesteps):
                t = torch.full((1,), step, device=self.device, dtype=torch.long)
                pred_noise = self.model(x, cond, offset, t, self.schedule.steps)
                pred_x0 = self.schedule.predict_x0(x, t, pred_noise).clamp(-1.0, 1.0)
                if idx == len(timesteps) - 1:
                    x = pred_x0
                else:
                    next_step = timesteps[idx + 1]
                    alpha_next = self.schedule.alpha_bars[next_step]
                    x = alpha_next.sqrt() * pred_x0 + (1.0 - alpha_next).sqrt() * pred_noise
        generated = x.squeeze(0).squeeze(0).cpu().numpy()
        return from_model_space(generated)

    def interpolate_volume(self, volume: np.ndarray, stride: int) -> np.ndarray:
        norm, lo, hi = normalize_volume(volume)
        out_depth = (volume.shape[2] - 1) * stride + 1
        out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        for idx in range(volume.shape[2]):
            out[:, :, idx * stride] = volume[:, :, idx]
        for idx in range(volume.shape[2] - 1):
            left = resize(norm[:, :, idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            right = resize(norm[:, :, idx + 1], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            cond_np = np.stack([to_model_space(left), to_model_space(right)], axis=0)
            cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
            for offset_idx in range(1, stride):
                offset_value = torch.tensor([[float(offset_idx) / float(stride)]], device=self.device)
                generated = self._sample_slice(cond, offset_value)
                slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset_idx] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"Strict HiFi-Diff inference: {src.name}")
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
        if not pred_path.exists() or not linear_path.exists():
            continue
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
