from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


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


class LocalStructureBlock(nn.Module):
    """Lightweight local restoration block: depthwise conv + MLP + channel attention."""

    def __init__(self, channels: int, mlp_ratio: float = 2.0):
        super().__init__()
        hidden = int(channels * mlp_ratio)
        self.norm1 = nn.GroupNorm(1, channels)
        self.depthwise = nn.Conv2d(channels, channels, 3, padding=1, groups=channels)
        self.pointwise = nn.Sequential(
            nn.Conv2d(channels, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, channels, 1),
        )
        self.attn = ChannelAttention(channels)
        self.norm2 = nn.GroupNorm(1, channels)
        self.ffn = nn.Sequential(
            nn.Conv2d(channels, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, channels, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.depthwise(self.norm1(x))
        y = self.pointwise(y)
        x = x + self.attn(y)
        return x + self.ffn(self.norm2(x))


class LongRangeMixer(nn.Module):
    """Stable large-kernel context mixer for anatomical consistency."""

    def __init__(self, channels: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.GroupNorm(1, channels),
            nn.Conv2d(channels, channels, 9, padding=4, groups=channels),
            nn.Conv2d(channels, channels, 1),
            nn.GELU(),
            ChannelAttention(channels),
            nn.Conv2d(channels, channels, 3, padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.net(x)


class PASTNet2p5D(nn.Module):
    """Phase-Aware Structure-Transfer Network for single-slice interpolation.

    Input channel order is [left, right, coarse, phase, right-left, abs(right-left)].
    The model predicts a confidence-gated bounded residual around the linear coarse slice.
    """

    def __init__(
        self,
        input_channels: int = 6,
        base_channels: int = 48,
        num_blocks: int = 8,
        window_size: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 1.0,
    ):
        super().__init__()
        if input_channels != 6:
            raise ValueError("PASTNet2p5D v1 expects exactly 6 input channels")
        self.input_channels = input_channels
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        self.window_size = window_size
        self.residual_scale = residual_scale

        self.slice_encoder = nn.Sequential(
            nn.Conv2d(1, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.aux_encoder = nn.Sequential(
            nn.Conv2d(3, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        gate_channels = base_channels * 4
        self.gate = nn.Sequential(
            nn.GroupNorm(1, gate_channels),
            nn.Conv2d(gate_channels, base_channels, 1),
            nn.GELU(),
            nn.Conv2d(base_channels, 3, 1),
        )
        self.fuse = nn.Sequential(
            nn.Conv2d(base_channels * 2, base_channels, 3, padding=1),
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
            nn.Conv2d(base_channels // 2, 2, 3, padding=1),
        )

    def _pad(self, x: torch.Tensor) -> tuple[torch.Tensor, int, int]:
        _, _, h, w = x.shape
        pad_h = (self.window_size - h % self.window_size) % self.window_size
        pad_w = (self.window_size - w % self.window_size) % self.window_size
        if pad_h or pad_w:
            x = F.pad(x, (0, pad_w, 0, pad_h), mode="reflect")
        return x, pad_h, pad_w

    def forward_components(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        x, pad_h, pad_w = self._pad(x)
        left = x[:, 0:1]
        right = x[:, 1:2]
        coarse = x[:, 2:3]
        phase = x[:, 3:4].clamp(0.0, 1.0)
        diff = x[:, 4:5]
        absdiff = x[:, 5:6]

        feat_left = self.slice_encoder(left)
        feat_right = self.slice_encoder(right)
        feat_coarse = self.slice_encoder(coarse)
        feat_aux = self.aux_encoder(torch.cat([phase, diff, absdiff], dim=1))

        logits = self.gate(torch.cat([feat_left, feat_right, feat_coarse, feat_aux], dim=1))
        priors = torch.cat(
            [
                (1.0 - phase).clamp_min(1e-4),
                phase.clamp_min(1e-4),
                torch.full_like(phase, 0.5),
            ],
            dim=1,
        )
        weights = torch.softmax(logits + priors.log(), dim=1)
        transferred = (
            weights[:, 0:1] * feat_left
            + weights[:, 1:2] * feat_right
            + weights[:, 2:3] * feat_coarse
        )
        feat = self.fuse(torch.cat([transferred, feat_aux], dim=1))
        feat = self.mixer(self.body(feat))
        decoded = self.decoder(feat)
        residual = torch.tanh(decoded[:, 0:1])
        confidence = torch.sigmoid(decoded[:, 1:2])
        prediction = coarse + confidence * self.residual_scale * residual
        if pad_h or pad_w:
            h = prediction.shape[2] - pad_h if pad_h else prediction.shape[2]
            w = prediction.shape[3] - pad_w if pad_w else prediction.shape[3]
            prediction = prediction[:, :, :h, :w]
            residual = residual[:, :, :h, :w]
            confidence = confidence[:, :, :h, :w]
            weights = weights[:, :, :h, :w]
        return {
            "prediction": prediction,
            "residual": residual,
            "confidence": confidence,
            "gate": weights,
        }

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.forward_components(x)["prediction"]

