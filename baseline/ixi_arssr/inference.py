from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from skimage.transform import resize

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti
from ixi_diffusion.inference import write_intensity_sanity

from .data import _resize_volume
from .model import ArSSRNet


class ArSSRInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None, query_chunk: int = 65536):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        self.feature_channels = int(payload.get("feature_channels", 24))
        self.model = ArSSRNet(feature_channels=self.feature_channels).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.query_chunk = query_chunk
        self.input_size = (256, 256)

    def _predict_hr128(self, sparse_norm: np.ndarray, out_depth: int) -> np.ndarray:
        sparse_zyx = _resize_volume(sparse_norm, self.input_size)
        stride = max((out_depth - 1) // max(sparse_zyx.shape[0] - 1, 1), 1)
        dense = _densify_sparse(sparse_zyx, stride=stride)
        if dense.shape[0] != out_depth:
            # Fallback for unusual depths: resize along z with linear interpolation.
            resized = np.zeros((out_depth, *self.input_size), dtype=np.float32)
            z_old = np.linspace(0, 1, dense.shape[0])
            z_new = np.linspace(0, 1, out_depth)
            for y in range(self.input_size[0]):
                for x in range(self.input_size[1]):
                    resized[:, y, x] = np.interp(z_new, z_old, dense[:, y, x])
            dense = resized
        volume_t = torch.from_numpy(dense[None, None].astype(np.float32)).to(self.device)

        zz, yy, xx = np.meshgrid(
            np.arange(out_depth, dtype=np.float32),
            np.arange(self.input_size[0], dtype=np.float32),
            np.arange(self.input_size[1], dtype=np.float32),
            indexing="ij",
        )
        coords = np.stack(
            [
                xx.reshape(-1) / max(self.input_size[1] - 1, 1) * 2.0 - 1.0,
                yy.reshape(-1) / max(self.input_size[0] - 1, 1) * 2.0 - 1.0,
                zz.reshape(-1) / max(out_depth - 1, 1) * 2.0 - 1.0,
            ],
            axis=1,
        ).astype(np.float32)
        preds = np.zeros((coords.shape[0],), dtype=np.float32)
        with torch.no_grad():
            for start in range(0, coords.shape[0], self.query_chunk):
                chunk = torch.from_numpy(coords[start : start + self.query_chunk]).to(self.device).unsqueeze(0)
                pred = self.model(volume_t, chunk).clamp(0.0, 1.0)
                preds[start : start + self.query_chunk] = pred.squeeze(0).squeeze(-1).cpu().numpy()
        return preds.reshape(out_depth, self.input_size[0], self.input_size[1])

    def interpolate_volume(self, volume: np.ndarray, stride: int = 4) -> np.ndarray:
        norm, lo, hi = normalize_volume(volume)
        out_depth = (volume.shape[2] - 1) * stride + 1
        generated = self._predict_hr128(norm, out_depth)
        out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        for z in range(out_depth):
            out[:, :, z] = resize(generated[z], volume.shape[:2], preserve_range=True, anti_aliasing=True)
        for idx in range(volume.shape[2]):
            out[:, :, idx * stride] = norm[:, :, idx]
        return out * (hi - lo) + lo

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"IXI ArSSR-style inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count


def _densify_sparse(sparse: np.ndarray, stride: int) -> np.ndarray:
    out_depth = (sparse.shape[0] - 1) * stride + 1
    dense = np.zeros((out_depth, sparse.shape[1], sparse.shape[2]), dtype=np.float32)
    for idx in range(sparse.shape[0]):
        dense[idx * stride] = sparse[idx]
    for idx in range(sparse.shape[0] - 1):
        left = sparse[idx]
        right = sparse[idx + 1]
        for offset in range(1, stride):
            rel = offset / stride
            dense[idx * stride + offset] = (1.0 - rel) * left + rel * right
    return dense
