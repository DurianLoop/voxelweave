from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


def sinusoidal_embedding(values: torch.Tensor, dim: int) -> torch.Tensor:
    half = dim // 2
    freqs = torch.exp(
        torch.arange(half, device=values.device, dtype=torch.float32)
        * -(math.log(10000.0) / max(half - 1, 1))
    )
    args = values.float().view(-1, 1) * freqs.view(1, -1)
    emb = torch.cat([torch.sin(args), torch.cos(args)], dim=1)
    if dim % 2 == 1:
        emb = F.pad(emb, (0, 1))
    return emb


class HiFiConditionEncoder(nn.Module):
    """Hierarchical feature extractor for adjacent slices and relative offset."""

    def __init__(self, base_channels: int, embed_dim: int):
        super().__init__()
        self.offset_mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.SiLU(),
            nn.Linear(embed_dim, embed_dim),
        )
        self.stem = nn.Sequential(
            nn.Conv2d(2, base_channels, 3, padding=1),
            nn.GroupNorm(8, base_channels),
            nn.SiLU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
            nn.GroupNorm(8, base_channels),
            nn.SiLU(),
        )
        self.down1 = nn.Sequential(
            nn.Conv2d(base_channels, base_channels * 2, 3, stride=2, padding=1),
            nn.GroupNorm(8, base_channels * 2),
            nn.SiLU(),
            nn.Conv2d(base_channels * 2, base_channels * 2, 3, padding=1),
            nn.GroupNorm(8, base_channels * 2),
            nn.SiLU(),
        )
        self.down2 = nn.Sequential(
            nn.Conv2d(base_channels * 2, base_channels * 4, 3, stride=2, padding=1),
            nn.GroupNorm(8, base_channels * 4),
            nn.SiLU(),
            nn.Conv2d(base_channels * 4, base_channels * 4, 3, padding=1),
            nn.GroupNorm(8, base_channels * 4),
            nn.SiLU(),
        )
        self.film = nn.ModuleList(
            [
                nn.Linear(embed_dim, base_channels * 2),
                nn.Linear(embed_dim, base_channels * 4),
                nn.Linear(embed_dim, base_channels * 8),
            ]
        )

    def _modulate(self, x: torch.Tensor, emb: torch.Tensor, layer: nn.Linear) -> torch.Tensor:
        scale_shift = layer(emb)
        scale, shift = scale_shift.chunk(2, dim=1)
        scale = scale.view(scale.shape[0], -1, 1, 1)
        shift = shift.view(shift.shape[0], -1, 1, 1)
        return x * (1.0 + scale) + shift

    def forward(self, cond: torch.Tensor, offset: torch.Tensor) -> list[torch.Tensor]:
        emb = self.offset_mlp(sinusoidal_embedding(offset.squeeze(1), self.offset_mlp[0].in_features))
        f0 = self._modulate(self.stem(cond), emb, self.film[0])
        f1 = self._modulate(self.down1(f0), emb, self.film[1])
        f2 = self._modulate(self.down2(f1), emb, self.film[2])
        return [f0, f1, f2]


class ModulatedResBlock(nn.Module):
    def __init__(self, channels: int, embed_dim: int):
        super().__init__()
        self.norm1 = nn.GroupNorm(8, channels)
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
        self.norm2 = nn.GroupNorm(8, channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
        self.mod = nn.Linear(embed_dim, channels * 4)

    def forward(self, x: torch.Tensor, emb: torch.Tensor, cond_feat: torch.Tensor | None = None) -> torch.Tensor:
        if cond_feat is not None:
            if cond_feat.shape[-2:] != x.shape[-2:]:
                cond_feat = F.interpolate(cond_feat, size=x.shape[-2:], mode="bilinear", align_corners=False)
            x = x + cond_feat
        s1, b1, s2, b2 = self.mod(emb).chunk(4, dim=1)
        s1 = s1.view(s1.shape[0], -1, 1, 1)
        b1 = b1.view(b1.shape[0], -1, 1, 1)
        s2 = s2.view(s2.shape[0], -1, 1, 1)
        b2 = b2.view(b2.shape[0], -1, 1, 1)
        h = self.norm1(x)
        h = h * (1.0 + s1) + b1
        h = self.conv1(F.silu(h))
        h = self.norm2(h)
        h = h * (1.0 + s2) + b2
        h = self.conv2(F.silu(h))
        return x + h


class StrictHiFiDiffUNet(nn.Module):
    def __init__(self, base_channels: int = 48, embed_dim: int = 128):
        super().__init__()
        self.embed_dim = embed_dim
        self.time_mlp = nn.Sequential(nn.Linear(embed_dim, embed_dim), nn.SiLU(), nn.Linear(embed_dim, embed_dim))
        self.offset_mlp = nn.Sequential(nn.Linear(embed_dim, embed_dim), nn.SiLU(), nn.Linear(embed_dim, embed_dim))
        self.cond_encoder = HiFiConditionEncoder(base_channels, embed_dim)
        self.cond_proj = nn.ModuleList(
            [
                nn.Conv2d(base_channels, base_channels, 1),
                nn.Conv2d(base_channels * 2, base_channels * 2, 1),
                nn.Conv2d(base_channels * 4, base_channels * 4, 1),
            ]
        )
        self.in_conv = nn.Conv2d(1, base_channels, 3, padding=1)
        self.down0 = ModulatedResBlock(base_channels, embed_dim)
        self.downsample0 = nn.Conv2d(base_channels, base_channels * 2, 3, stride=2, padding=1)
        self.down1 = ModulatedResBlock(base_channels * 2, embed_dim)
        self.downsample1 = nn.Conv2d(base_channels * 2, base_channels * 4, 3, stride=2, padding=1)
        self.mid = ModulatedResBlock(base_channels * 4, embed_dim)
        self.up1 = nn.ConvTranspose2d(base_channels * 4, base_channels * 2, 2, stride=2)
        self.dec1 = ModulatedResBlock(base_channels * 2, embed_dim)
        self.up0 = nn.ConvTranspose2d(base_channels * 2, base_channels, 2, stride=2)
        self.dec0 = ModulatedResBlock(base_channels, embed_dim)
        self.out_norm = nn.GroupNorm(8, base_channels)
        self.out_conv = nn.Conv2d(base_channels, 1, 1)

    def forward(
        self,
        noisy: torch.Tensor,
        cond: torch.Tensor,
        offset: torch.Tensor,
        t: torch.Tensor,
        total_steps: int,
    ) -> torch.Tensor:
        t_emb = sinusoidal_embedding(t.float() / max(total_steps - 1, 1), self.embed_dim)
        o_emb = sinusoidal_embedding(offset.squeeze(1), self.embed_dim)
        emb = self.time_mlp(t_emb) + self.offset_mlp(o_emb)
        feats = self.cond_encoder(cond, offset)
        feats = [proj(feat) for proj, feat in zip(self.cond_proj, feats)]
        x0 = self.in_conv(noisy)
        d0 = self.down0(x0, emb, feats[0])
        d1 = self.down1(self.downsample0(d0), emb, feats[1])
        mid = self.mid(self.downsample1(d1), emb, feats[2])
        u1 = self.up1(mid) + d1
        u1 = self.dec1(u1, emb, feats[1])
        u0 = self.up0(u1) + d0
        u0 = self.dec0(u0, emb, feats[0])
        return self.out_conv(F.silu(self.out_norm(u0)))
