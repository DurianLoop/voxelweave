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


class PhaseFiLM(nn.Module):
    def __init__(self, phase_channels: int, feature_channels: int):
        super().__init__()
        hidden = max(16, feature_channels // 2)
        self.mlp = nn.Sequential(
            nn.Linear(phase_channels, hidden),
            nn.GELU(),
            nn.Linear(hidden, feature_channels * 2),
        )

    def forward(self, feat: torch.Tensor, phase_maps: torch.Tensor) -> torch.Tensor:
        phase = phase_maps.mean(dim=(2, 3))
        gamma_beta = self.mlp(phase)
        gamma, beta = gamma_beta.chunk(2, dim=1)
        gamma = 1.0 + gamma[:, :, None, None]
        beta = beta[:, :, None, None]
        return gamma * feat + beta


class ReliabilityBlock(nn.Module):
    def __init__(self, channels: int, mlp_ratio: float = 2.0):
        super().__init__()
        hidden = int(channels * mlp_ratio)
        self.local = nn.Sequential(
            nn.GroupNorm(1, channels),
            nn.Conv2d(channels, channels, 5, padding=2, groups=channels),
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


def _head(in_channels: int, out_channels: int) -> nn.Sequential:
    return nn.Sequential(
        nn.GroupNorm(1, in_channels),
        nn.Conv2d(in_channels, in_channels, 3, padding=1),
        nn.GELU(),
        nn.Conv2d(in_channels, out_channels, 1),
    )


class RASINet2p5D(nn.Module):
    """Reliability-Aware Slice Interpolation Network.

    For x4 the input channel order is [S0, S4, C1, C2, C3, P1, P2, P3, D, A].
    The network predicts the whole intermediate slice group and returns
    confidence, residual, and uncertainty maps for the generated slices.
    """

    def __init__(
        self,
        stride: int = 4,
        base_channels: int = 48,
        num_blocks: int = 6,
        mlp_ratio: float = 2.0,
        residual_scale: float = 0.75,
        min_log_variance: float = -6.0,
        max_log_variance: float = 4.0,
    ):
        super().__init__()
        if stride < 2:
            raise ValueError("RASI-Net requires stride >= 2")
        self.stride = stride
        self.group_size = stride - 1
        self.input_channels = 2 * stride + 2
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        self.residual_scale = residual_scale
        self.min_log_variance = min_log_variance
        self.max_log_variance = max_log_variance

        self.encoder = nn.Sequential(
            nn.Conv2d(self.input_channels, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.phase_film = PhaseFiLM(self.group_size, base_channels)
        self.body = nn.Sequential(
            *[ReliabilityBlock(base_channels, mlp_ratio=mlp_ratio) for _ in range(num_blocks)]
        )
        self.residual_head = _head(base_channels, self.group_size)
        self.confidence_head = _head(base_channels, self.group_size)
        self.logvar_head = _head(base_channels, self.group_size)

        nn.init.zeros_(self.residual_head[-1].weight)
        nn.init.zeros_(self.residual_head[-1].bias)
        nn.init.zeros_(self.confidence_head[-1].bias)
        nn.init.constant_(self.logvar_head[-1].bias, -2.0)

    def _split(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if x.shape[1] != self.input_channels:
            raise ValueError(f"RASI-Net expected {self.input_channels} channels, got {x.shape[1]}")
        anchors = x[:, 0:2]
        coarse = x[:, 2 : 2 + self.group_size]
        phases = x[:, 2 + self.group_size : 2 + 2 * self.group_size]
        diff = x[:, -2:]
        return anchors, coarse, phases, diff

    def forward_components(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        anchors, coarse, phases, _diff = self._split(x)
        feat = self.encoder(x)
        feat = self.phase_film(feat, phases)
        feat = self.body(feat)

        residual_raw = self.residual_head(feat)
        residual = self.residual_scale * torch.tanh(residual_raw)
        confidence = torch.sigmoid(self.confidence_head(feat))
        log_variance = self.logvar_head(feat).clamp(self.min_log_variance, self.max_log_variance)
        uncertainty = torch.nn.functional.softplus(log_variance) + 1e-6
        prediction = coarse + confidence * residual
        stack = torch.cat([anchors[:, 0:1], prediction, anchors[:, 1:2]], dim=1)
        return {
            "prediction": prediction,
            "coarse_prediction": prediction,
            "residual": residual,
            "residual_raw": residual_raw,
            "confidence": confidence,
            "log_variance": log_variance,
            "uncertainty": uncertainty,
            "stack": stack,
        }

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.forward_components(x)["prediction"]
