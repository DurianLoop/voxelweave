from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def spatial_gradient(x: torch.Tensor) -> torch.Tensor:
    grad = torch.zeros_like(x)
    grad[:, :, :, 1:] += (x[:, :, :, 1:] - x[:, :, :, :-1]).abs()
    grad[:, :, 1:, :] += (x[:, :, 1:, :] - x[:, :, :-1, :]).abs()
    return grad


class ECALayer(nn.Module):
    def __init__(self, channels: int, kernel_size: int = 3):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(1, 1, kernel_size, padding=(kernel_size - 1) // 2, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        weights = self.pool(x).squeeze(-1).transpose(1, 2)
        weights = self.conv(weights).transpose(1, 2).unsqueeze(-1)
        return x * torch.sigmoid(weights)


class EBlock(nn.Module):
    """Depthwise residual block used by ECSI-Net instead of full attention."""

    def __init__(self, channels: int, expansion: int = 2, kernel_size: int = 5, eca_kernel: int = 3):
        super().__init__()
        hidden = channels * expansion
        padding = kernel_size // 2
        self.net = nn.Sequential(
            nn.Conv2d(channels, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, hidden, kernel_size, padding=padding, groups=hidden),
            nn.GELU(),
            ECALayer(hidden, kernel_size=eca_kernel),
            nn.Conv2d(hidden, channels, 1),
        )
        self.scale = nn.Parameter(torch.tensor(0.1, dtype=torch.float32))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.net(x) * self.scale


class ECSIStem(nn.Module):
    def __init__(self, in_channels: int, channels: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(channels, channels, 3, padding=1, groups=channels),
            nn.GELU(),
            nn.Conv2d(channels, channels, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class ECSIOutputHead(nn.Module):
    def __init__(self, channels: int, residual_scale: float):
        super().__init__()
        self.residual_scale = residual_scale
        self.net = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(channels, 1, 3, padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.tanh(self.net(x)) * self.residual_scale


class ECSINet(nn.Module):
    """Efficient Clinical Slice Interpolation Network.

    The public input can be either four channels `[L, R, C, P]` or the explicit
    six-channel design input `[L, R, C, P, D, A]`.
    """

    def __init__(
        self,
        in_channels: int = 6,
        channels: int = 48,
        num_blocks: int = 8,
        expansion: int = 2,
        kernel_size: int = 5,
        residual_scale: float = 1.0,
        mask_bias: float = -2.0,
    ):
        super().__init__()
        if in_channels != 6:
            raise ValueError("ECSINet expects the explicit six-channel internal representation")
        self.channels = channels
        self.num_blocks = num_blocks
        self.expansion = expansion
        self.kernel_size = kernel_size
        self.residual_scale = residual_scale
        self.mask_bias = mask_bias
        self.stem = ECSIStem(in_channels, channels)
        self.blocks = nn.Sequential(
            *[EBlock(channels, expansion=expansion, kernel_size=kernel_size) for _ in range(num_blocks)]
        )
        self.body_conv = nn.Conv2d(channels, channels, 3, padding=1)
        mask_hidden = max(8, channels // 2)
        self.mask_branch = nn.Sequential(
            nn.Conv2d(channels + 2, mask_hidden, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(mask_hidden, mask_hidden, 3, padding=1, groups=mask_hidden),
            nn.GELU(),
            nn.Conv2d(mask_hidden, 1, 1),
        )
        self.residual_head = ECSIOutputHead(channels, residual_scale=residual_scale)
        self._init_mask_bias(mask_bias)

    @staticmethod
    def expand_condition(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if x.ndim != 4:
            raise ValueError(f"Expected BCHW input, got shape={tuple(x.shape)}")
        if x.shape[1] == 4:
            left = x[:, 0:1]
            right = x[:, 1:2]
            coarse = x[:, 2:3]
            phase = x[:, 3:4]
            diff = right - left
            change = diff.abs()
            x = torch.cat([left, right, coarse, phase, diff, change], dim=1)
        elif x.shape[1] == 6:
            left = x[:, 0:1]
            right = x[:, 1:2]
            coarse = x[:, 2:3]
            phase = x[:, 3:4]
            diff = x[:, 4:5]
            change = x[:, 5:6]
            _ = left, right, phase, diff
        else:
            raise ValueError(f"Expected 4 or 6 channels, got {x.shape[1]}")
        return x, coarse, change, spatial_gradient(coarse)

    def _init_mask_bias(self, value: float) -> None:
        final = self.mask_branch[-1]
        if isinstance(final, nn.Conv2d) and final.bias is not None:
            nn.init.constant_(final.bias, value)

    def forward(self, x: torch.Tensor, return_parts: bool = False) -> torch.Tensor | dict[str, torch.Tensor]:
        x6, coarse, change, coarse_grad = self.expand_condition(x)
        stem = self.stem(x6)
        feat = self.body_conv(self.blocks(stem)) + stem
        mask = torch.sigmoid(self.mask_branch(torch.cat([feat, change, coarse_grad], dim=1)))
        residual = self.residual_head(feat)
        correction = mask * residual
        recon = coarse + correction
        if return_parts:
            return {
                "recon": recon,
                "residual": residual,
                "correction": correction,
                "mask": mask,
                "coarse": coarse,
                "change": change,
                "coarse_grad": coarse_grad,
            }
        return recon

