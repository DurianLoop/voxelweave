from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class Residual3DBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv3d(channels, channels, 3, padding=1),
            nn.GroupNorm(4, channels),
            nn.SiLU(),
            nn.Conv3d(channels, channels, 3, padding=1),
            nn.GroupNorm(4, channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.silu(x + self.block(x))


class ArSSRNet(nn.Module):
    """ArSSR-style 3D feature encoder plus coordinate MLP.

    The forward interface follows the official idea: encode a low-resolution
    volume, sample local features at arbitrary normalized coordinates, then
    predict the intensity at each coordinate.
    """

    def __init__(self, feature_channels: int = 24, hidden_dim: int = 128):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv3d(1, feature_channels, 3, padding=1),
            nn.SiLU(),
            Residual3DBlock(feature_channels),
            Residual3DBlock(feature_channels),
            nn.Conv3d(feature_channels, feature_channels, 3, padding=1),
            nn.SiLU(),
        )
        self.mlp = nn.Sequential(
            nn.Linear(feature_channels + 4, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, 1),
        )
        nn.init.zeros_(self.mlp[-1].weight)
        nn.init.zeros_(self.mlp[-1].bias)

    def forward(self, volume: torch.Tensor, coords: torch.Tensor) -> torch.Tensor:
        features = self.encoder(volume)
        # coords are normalized as x,y,z in [-1,1]; grid_sample expects x,y,z.
        grid = coords.view(coords.shape[0], coords.shape[1], 1, 1, 3)
        sampled = F.grid_sample(features, grid, mode="bilinear", padding_mode="border", align_corners=True)
        sampled = sampled.squeeze(-1).squeeze(-1).permute(0, 2, 1)
        base = F.grid_sample(volume, grid, mode="bilinear", padding_mode="border", align_corners=True)
        base = base.squeeze(-1).squeeze(-1).permute(0, 2, 1)
        residual = 0.05 * torch.tanh(self.mlp(torch.cat([sampled, base, coords], dim=-1)))
        return base + residual
