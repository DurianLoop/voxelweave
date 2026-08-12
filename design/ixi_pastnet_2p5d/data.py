from __future__ import annotations

import numpy as np
import torch
from skimage.transform import resize

from ixi_diffusion.data import IXISingleSliceInterpolationDataset


class IXIMultiAnchorSingleSliceDataset(IXISingleSliceInterpolationDataset):
    """IXI single-slice dataset with the same 13-channel condition used by fastMRI G07."""

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        item = super().__getitem__(index)
        path, _case_id, z, _offset, depth = self.items[index]
        volume = self.cache.get(path)

        left = item["cond"][0].numpy()
        right = item["cond"][1].numpy()
        coarse = item["cond"][2].numpy()
        phase = item["cond"][3].numpy()

        prev_idx = z - self.stride
        next_idx = z + 2 * self.stride
        prev_valid_value = 1.0 if prev_idx >= 0 else 0.0
        next_valid_value = 1.0 if next_idx < depth else 0.0
        if prev_idx < 0:
            prev_idx = z
        if next_idx >= depth:
            next_idx = z + self.stride

        prev_anchor = resize(
            volume[:, :, prev_idx], self.target_shape, preserve_range=True, anti_aliasing=True
        ).astype(np.float32)
        next_anchor = resize(
            volume[:, :, next_idx], self.target_shape, preserve_range=True, anti_aliasing=True
        ).astype(np.float32)
        diff = (right - left).astype(np.float32)
        absdiff = np.abs(diff).astype(np.float32)
        prev_valid = np.full(self.target_shape, prev_valid_value, dtype=np.float32)
        next_valid = np.full(self.target_shape, next_valid_value, dtype=np.float32)
        prev_delta = ((left - prev_anchor) * prev_valid_value).astype(np.float32)
        next_delta = ((next_anchor - right) * next_valid_value).astype(np.float32)
        curvature = (next_delta - prev_delta).astype(np.float32)

        cond_ma = np.stack(
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
        ).astype(np.float32)
        item["cond_ma"] = torch.from_numpy(cond_ma)
        return item
