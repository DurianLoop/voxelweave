from __future__ import annotations

import torch
import torch.nn as nn


class ChannelAttention(nn.Module):
    def __init__(self, channels: int, squeeze: int = 8):
        super().__init__()
        hidden = max(4, channels // squeeze)
        self.net = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(channels, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, channels, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.net(x)


class AnatomyBlock(nn.Module):
    def __init__(self, channels: int, mlp_ratio: float = 2.0):
        super().__init__()
        hidden = int(channels * mlp_ratio)
        self.local = nn.Sequential(
            nn.GroupNorm(1, channels),
            nn.Conv2d(channels, channels, 3, padding=1, groups=channels),
            nn.Conv2d(channels, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, channels, 1),
            ChannelAttention(channels),
        )
        self.ffn = nn.Sequential(
            nn.GroupNorm(1, channels),
            nn.Conv2d(channels, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, channels, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.local(x)
        return x + self.ffn(x)


class ACSINetV2(nn.Module):
    """Lightweight I3Net-aligned ACSI model.

    For x4 it consumes a 13-slice window condition built from 4 sparse anchors,
    13 linear coarse slices, 13 phase maps, and adjacent-anchor differences.
    It predicts the full 13-slice HR window while preserving anchor positions.
    """

    def __init__(
        self,
        stride: int = 4,
        lr_slice_patch: int = 4,
        base_channels: int = 32,
        num_blocks: int = 6,
        z_refine_channels: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 0.5,
    ):
        super().__init__()
        self.stride = stride
        self.lr_slice_patch = lr_slice_patch
        self.hr_slice_patch = stride * (lr_slice_patch - 1) + 1
        self.anchor_count = lr_slice_patch
        self.input_channels = self.anchor_count + self.hr_slice_patch * 2 + (self.anchor_count - 1) * 2
        self.residual_scale = residual_scale

        self.anchor_encoder = nn.Sequential(nn.Conv2d(self.anchor_count, base_channels, 3, padding=1), nn.GELU())
        self.coarse_encoder = nn.Sequential(nn.Conv2d(self.hr_slice_patch, base_channels, 3, padding=1), nn.GELU())
        self.phase_encoder = nn.Sequential(nn.Conv2d(self.hr_slice_patch, base_channels, 1), nn.GELU())
        self.diff_encoder = nn.Sequential(nn.Conv2d((self.anchor_count - 1) * 2, base_channels, 3, padding=1), nn.GELU())
        self.fuse = nn.Sequential(nn.Conv2d(base_channels * 4, base_channels, 3, padding=1), nn.GELU())
        self.body = nn.Sequential(*[AnatomyBlock(base_channels, mlp_ratio=mlp_ratio) for _ in range(num_blocks)])
        self.decoder = nn.Sequential(
            nn.GroupNorm(1, base_channels),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels // 2, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels // 2, self.hr_slice_patch * 2, 3, padding=1),
        )
        nn.init.zeros_(self.decoder[-1].weight)
        nn.init.zeros_(self.decoder[-1].bias)
        self.z_refine = nn.Sequential(
            nn.Conv3d(1, z_refine_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv3d(z_refine_channels, 1, 3, padding=1),
        )
        nn.init.zeros_(self.z_refine[-1].weight)
        nn.init.zeros_(self.z_refine[-1].bias)

        anchor_mask = torch.zeros(1, self.hr_slice_patch, 1, 1)
        anchor_mask[:, :: self.stride] = 1.0
        self.register_buffer("anchor_mask", anchor_mask, persistent=False)

    def _split(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if x.shape[1] != self.input_channels:
            raise ValueError(f"ACSI-v2 expected {self.input_channels} channels, got {x.shape[1]}")
        anchors = x[:, : self.anchor_count]
        coarse_start = self.anchor_count
        phase_start = coarse_start + self.hr_slice_patch
        diff_start = phase_start + self.hr_slice_patch
        coarse = x[:, coarse_start:phase_start]
        phases = x[:, phase_start:diff_start]
        diffs = x[:, diff_start:]
        return anchors, coarse, phases, diffs

    def forward_components(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        anchors, coarse, phases, diffs = self._split(x)
        feat = self.fuse(
            torch.cat(
                [
                    self.anchor_encoder(anchors),
                    self.coarse_encoder(coarse),
                    self.phase_encoder(phases),
                    self.diff_encoder(diffs),
                ],
                dim=1,
            )
        )
        feat = self.body(feat)
        decoded = self.decoder(feat)
        residual = torch.tanh(decoded[:, : self.hr_slice_patch])
        confidence = torch.sigmoid(decoded[:, self.hr_slice_patch :])
        coarse_prediction = coarse + confidence * self.residual_scale * residual
        refined = coarse_prediction + 0.1 * torch.tanh(self.z_refine(coarse_prediction.unsqueeze(1)).squeeze(1))
        prediction = refined * (1.0 - self.anchor_mask) + coarse * self.anchor_mask
        return {
            "prediction": prediction,
            "coarse_prediction": coarse_prediction,
            "residual": residual,
            "confidence": confidence,
        }

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.forward_components(x)["prediction"]
