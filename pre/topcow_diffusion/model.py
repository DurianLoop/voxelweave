from __future__ import annotations

import torch
import torch.nn as nn


class ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.GroupNorm(8, out_channels),
            nn.SiLU(),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.GroupNorm(8, out_channels),
            nn.SiLU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class NoisePredictorUNet(nn.Module):
    def __init__(self, in_channels: int = 10, out_channels: int = 3, base_channels: int = 32):
        super().__init__()
        self.down1 = ConvBlock(in_channels, base_channels)
        self.pool1 = nn.MaxPool2d(2)
        self.down2 = ConvBlock(base_channels, base_channels * 2)
        self.pool2 = nn.MaxPool2d(2)
        self.mid = ConvBlock(base_channels * 2, base_channels * 4)
        self.up2 = nn.ConvTranspose2d(base_channels * 4, base_channels * 2, 2, stride=2)
        self.dec2 = ConvBlock(base_channels * 4, base_channels * 2)
        self.up1 = nn.ConvTranspose2d(base_channels * 2, base_channels, 2, stride=2)
        self.dec1 = ConvBlock(base_channels * 2, base_channels)
        self.out = nn.Conv2d(base_channels, out_channels, 1)

    def forward(self, noisy: torch.Tensor, cond: torch.Tensor, t: torch.Tensor, total_steps: int) -> torch.Tensor:
        t_map = (t.float() / max(total_steps - 1, 1)).view(-1, 1, 1, 1)
        t_map = t_map.expand(-1, 1, noisy.shape[2], noisy.shape[3])
        x = torch.cat([noisy, cond, t_map], dim=1)
        d1 = self.down1(x)
        d2 = self.down2(self.pool1(d1))
        mid = self.mid(self.pool2(d2))
        u2 = self.up2(mid)
        u2 = self.dec2(torch.cat([u2, d2], dim=1))
        u1 = self.up1(u2)
        u1 = self.dec1(torch.cat([u1, d1], dim=1))
        return self.out(u1)
