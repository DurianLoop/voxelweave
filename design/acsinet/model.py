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


class ACSINet2p5D(nn.Module):
    """Anatomy-Consistent Slice Interpolation Network.

    For x4 the input channel order is [S0, S4, C1, C2, C3, P1, P2, P3, D, A].
    The model predicts all intermediate slices as one group and lightly refines
    [S0, Y1, ..., Yk, S_end] with a shallow Conv3D z-context head.
    """

    def __init__(
        self,
        stride: int = 4,
        base_channels: int = 40,
        num_blocks: int = 6,
        z_refine_channels: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 0.75,
    ):
        super().__init__()
        if stride < 2:
            raise ValueError("ACSI-Net requires stride >= 2")
        self.stride = stride
        self.group_size = stride - 1
        self.input_channels = 2 * stride + 2
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        self.z_refine_channels = z_refine_channels
        self.residual_scale = residual_scale

        self.anchor_encoder = nn.Sequential(
            nn.Conv2d(2, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.coarse_encoder = nn.Sequential(
            nn.Conv2d(self.group_size, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.phase_encoder = nn.Sequential(
            nn.Conv2d(self.group_size, base_channels, 1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 1),
        )
        self.diff_encoder = nn.Sequential(
            nn.Conv2d(2, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.fuse = nn.Sequential(
            nn.Conv2d(base_channels * 4, base_channels, 3, padding=1),
            nn.GELU(),
        )
        self.body = nn.Sequential(*[AnatomyBlock(base_channels, mlp_ratio=mlp_ratio) for _ in range(num_blocks)])
        self.decoder = nn.Sequential(
            nn.GroupNorm(1, base_channels),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels // 2, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels // 2, self.group_size * 2, 3, padding=1),
        )
        self.z_refine = nn.Sequential(
            nn.Conv3d(1, z_refine_channels, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv3d(z_refine_channels, 1, kernel_size=3, padding=1),
        )
        nn.init.zeros_(self.z_refine[-1].weight)
        nn.init.zeros_(self.z_refine[-1].bias)

    def _split(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if x.shape[1] != self.input_channels:
            raise ValueError(f"ACSI-Net expected {self.input_channels} channels, got {x.shape[1]}")
        anchors = x[:, 0:2]
        coarse = x[:, 2 : 2 + self.group_size]
        phases = x[:, 2 + self.group_size : 2 + 2 * self.group_size]
        diff = x[:, -2:]
        return anchors, coarse, phases, diff

    def forward_components(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        anchors, coarse, phases, diff = self._split(x)
        feat = self.fuse(
            torch.cat(
                [
                    self.anchor_encoder(anchors),
                    self.coarse_encoder(coarse),
                    self.phase_encoder(phases),
                    self.diff_encoder(diff),
                ],
                dim=1,
            )
        )
        feat = self.body(feat)
        decoded = self.decoder(feat)
        residual = torch.tanh(decoded[:, : self.group_size])
        confidence = torch.sigmoid(decoded[:, self.group_size :])
        coarse_prediction = coarse + confidence * self.residual_scale * residual

        stack = torch.cat([anchors[:, 0:1], coarse_prediction, anchors[:, 1:2]], dim=1)
        refined_stack = stack + 0.1 * torch.tanh(self.z_refine(stack.unsqueeze(1)).squeeze(1))
        prediction = refined_stack[:, 1:-1]
        return {
            "prediction": prediction,
            "coarse_prediction": coarse_prediction,
            "residual": residual,
            "confidence": confidence,
            "stack": refined_stack,
        }

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.forward_components(x)["prediction"]
