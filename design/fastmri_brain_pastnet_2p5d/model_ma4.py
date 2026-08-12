from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from ixi_pastnet_2p5d.model import LocalStructureBlock, LongRangeMixer


class PASTNetMA4Window2p5D(nn.Module):
    """Window-level MA4 PAST-Net for x4 fastMRI through-plane interpolation.

    Input channel order:
    [4 sparse anchors, 9 linear coarse missing slices, 9 phase maps].
    The model predicts the 9 missing slices in the 13-slice window as residuals
    over the linear coarse stack.
    """

    def __init__(
        self,
        input_channels: int = 22,
        output_channels: int = 9,
        base_channels: int = 96,
        num_blocks: int = 12,
        window_size: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 0.75,
    ):
        super().__init__()
        if input_channels < 13:
            raise ValueError("PASTNetMA4Window2p5D expects anchors plus a coarse missing stack")
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        self.window_size = window_size
        self.mlp_ratio = mlp_ratio
        self.residual_scale = residual_scale

        self.stem = nn.Sequential(
            nn.Conv2d(input_channels, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.anchor_encoder = nn.Sequential(
            nn.Conv2d(4, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.coarse_encoder = nn.Sequential(
            nn.Conv2d(output_channels, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.fuse = nn.Sequential(
            nn.GroupNorm(1, base_channels * 3),
            nn.Conv2d(base_channels * 3, base_channels, 1),
            nn.GELU(),
        )
        self.body = nn.Sequential(
            *[LocalStructureBlock(base_channels, mlp_ratio=mlp_ratio) for _ in range(num_blocks)]
        )
        self.mixer = LongRangeMixer(base_channels)
        self.decoder = nn.Sequential(
            nn.GroupNorm(1, base_channels),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels // 2, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels // 2, output_channels * 2, 3, padding=1),
        )
        self._init_identity_residual()

    def _init_identity_residual(self) -> None:
        final = self.decoder[-1]
        if isinstance(final, nn.Conv2d):
            nn.init.zeros_(final.weight)
            nn.init.zeros_(final.bias)

    def _pad(self, x: torch.Tensor) -> tuple[torch.Tensor, int, int]:
        _, _, h, w = x.shape
        pad_h = (self.window_size - h % self.window_size) % self.window_size
        pad_w = (self.window_size - w % self.window_size) % self.window_size
        if pad_h or pad_w:
            x = F.pad(x, (0, pad_w, 0, pad_h), mode="reflect")
        return x, pad_h, pad_w

    def forward_components(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        x, pad_h, pad_w = self._pad(x)
        anchors = x[:, 0:4]
        coarse = x[:, 4 : 4 + self.output_channels]
        feat = self.stem(x)
        anchor_feat = self.anchor_encoder(anchors)
        coarse_feat = self.coarse_encoder(coarse)
        feat = self.fuse(torch.cat([feat, anchor_feat, coarse_feat], dim=1))
        feat = self.mixer(self.body(feat))
        decoded = self.decoder(feat)
        residual = torch.tanh(decoded[:, : self.output_channels])
        confidence = torch.sigmoid(decoded[:, self.output_channels :])
        prediction = coarse + confidence * self.residual_scale * residual
        if pad_h or pad_w:
            h = prediction.shape[2] - pad_h if pad_h else prediction.shape[2]
            w = prediction.shape[3] - pad_w if pad_w else prediction.shape[3]
            prediction = prediction[:, :, :h, :w]
            residual = residual[:, :, :h, :w]
            confidence = confidence[:, :, :h, :w]
        return {
            "prediction": prediction,
            "residual": residual,
            "confidence": confidence,
        }

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.forward_components(x)["prediction"]
