from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from skimage.transform import resize

from .data import normalize_volume
from .model import GeneratorUNet


def expected_upsampled_depth(sparse_depth: int, stride: int = 4) -> int:
    if sparse_depth <= 0:
        raise ValueError("sparse_depth must be positive")
    return (sparse_depth - 1) * stride + 1


class GAN2p5DInterpolator:
    def __init__(
        self,
        checkpoint: Path,
        device: str | None = None,
        target_shape: tuple[int, int] = (256, 256),
        stride: int | None = None,
    ):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        checkpoint_stride = payload.get("stride") if isinstance(payload, dict) else None
        self.stride = int(stride if stride is not None else checkpoint_stride if checkpoint_stride is not None else 4)
        if self.stride < 2:
            raise ValueError(f"stride must be at least 2, got {self.stride}")
        if checkpoint_stride is not None and int(checkpoint_stride) != self.stride:
            raise ValueError(f"Checkpoint stride={checkpoint_stride} does not match requested stride={self.stride}")
        target_slices = self.stride - 1
        self.generator = GeneratorUNet(in_channels=target_slices + 3, out_channels=target_slices).to(self.device)
        state = payload.get("generator_state_dict", payload)
        self.generator.load_state_dict(state)
        self.generator.eval()
        self.target_shape = target_shape

    def interpolate_sparse_volume(self, sparse_volume: np.ndarray, stride: int = 4) -> np.ndarray:
        if stride != self.stride:
            raise ValueError(f"Interpolator was initialized for x{self.stride}, received x{stride}")
        norm, lo, hi = normalize_volume(sparse_volume)
        height, width, sparse_depth = sparse_volume.shape
        out = np.zeros((height, width, expected_upsampled_depth(sparse_depth, stride)), dtype=np.float32)
        for idx in range(sparse_depth):
            out[:, :, idx * stride] = sparse_volume[:, :, idx]
        with torch.no_grad():
            for idx in range(sparse_depth - 1):
                left = resize(norm[:, :, idx], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
                right = resize(norm[:, :, idx + 1], self.target_shape, preserve_range=True, anti_aliasing=True).astype(np.float32)
                z_pos = (idx + 0.5) / max(sparse_depth - 1, 1)
                relative_positions = [offset / float(stride) for offset in range(1, stride)]
                cond = np.stack(
                    [
                        left,
                        right,
                        np.full(self.target_shape, z_pos, dtype=np.float32),
                        *[np.full(self.target_shape, pos, dtype=np.float32) for pos in relative_positions],
                    ],
                    axis=0,
                )
                inp = torch.from_numpy(cond).float().unsqueeze(0).to(self.device)
                pred, _flows, _coarse = self.generator(inp)
                pred_np = pred.squeeze(0).float().cpu().numpy()
                for offset in range(1, stride):
                    generated = resize(
                        pred_np[offset - 1],
                        (height, width),
                        preserve_range=True,
                        anti_aliasing=True,
                    )
                    out[:, :, idx * stride + offset] = np.clip(generated, 0.0, 1.0) * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, load_nifti, save_nifti, stride: int = 4) -> int:
        output_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for path in sorted(input_dir.glob("*.nii.gz")):
            volume, affine, header = load_nifti(path)
            out = self.interpolate_sparse_volume(volume.astype(np.float32), stride=stride)
            save_nifti(out, affine, header, output_dir / f"diff_{path.name}")
            count += 1
        return count
