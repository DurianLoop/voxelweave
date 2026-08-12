from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class LayerNorm2d(nn.Module):
    def __init__(self, dim: int):
        super().__init__()
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.norm(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2).contiguous()


class DirectionalSelectiveScan2D(nn.Module):
    """A dependency-light 2D selective scan surrogate inspired by SMamba/MambaIR."""

    def __init__(self, dim: int):
        super().__init__()
        self.direction_logits = nn.Parameter(torch.zeros(4, dim, 1, 1))
        self.channel_gate = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(dim, max(4, dim // 4), 1),
            nn.SiLU(inplace=True),
            nn.Conv2d(max(4, dim // 4), dim, 1),
            nn.Sigmoid(),
        )

    @staticmethod
    def _running_mean(x: torch.Tensor, dim: int) -> torch.Tensor:
        length = x.shape[dim]
        denom_shape = [1] * x.ndim
        denom_shape[dim] = length
        denom = torch.arange(1, length + 1, device=x.device, dtype=x.dtype).view(*denom_shape)
        return torch.cumsum(x, dim=dim) / denom

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lr = self._running_mean(x, dim=3)
        rl = torch.flip(self._running_mean(torch.flip(x, dims=(3,)), dim=3), dims=(3,))
        tb = self._running_mean(x, dim=2)
        bt = torch.flip(self._running_mean(torch.flip(x, dims=(2,)), dim=2), dims=(2,))
        weights = torch.softmax(self.direction_logits, dim=0)
        scanned = weights[0] * lr + weights[1] * rl + weights[2] * tb + weights[3] * bt
        return scanned * self.channel_gate(x)


class MambaStyleBlock(nn.Module):
    def __init__(self, dim: int, expansion: int = 2):
        super().__init__()
        hidden = dim * expansion
        self.norm = LayerNorm2d(dim)
        self.in_proj = nn.Conv2d(dim, hidden * 2, 1)
        self.dwconv = nn.Conv2d(hidden, hidden, 3, padding=1, groups=hidden)
        self.scan = DirectionalSelectiveScan2D(hidden)
        self.out_proj = nn.Conv2d(hidden, dim, 1)
        self.ffn = nn.Sequential(
            LayerNorm2d(dim),
            nn.Conv2d(dim, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        shortcut = x
        feat, gate = self.in_proj(self.norm(x)).chunk(2, dim=1)
        feat = self.scan(self.dwconv(feat))
        x = shortcut + self.out_proj(feat * torch.sigmoid(gate))
        return x + self.ffn(x)


class ConvStem(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SMambaUNet2p5D(nn.Module):
    """SMamba-UNet/MambaIR-style residual net for 2.5D MRI slice interpolation."""

    def __init__(
        self,
        in_channels: int = 4,
        embed_dim: int = 48,
        depths: tuple[int, ...] = (2, 2, 2),
        num_heads: tuple[int, ...] = (3, 3, 3),
        window_size: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 1.0,
    ):
        super().__init__()
        del num_heads, window_size
        expansion = max(1, int(round(mlp_ratio)))
        shallow_depth = depths[0] if depths else 2
        deep_depth = depths[1] if len(depths) > 1 else shallow_depth
        self.residual_scale = residual_scale
        self.head = ConvStem(in_channels, embed_dim)
        self.enc = nn.Sequential(*[MambaStyleBlock(embed_dim, expansion) for _ in range(shallow_depth)])
        self.down = nn.Sequential(
            nn.Conv2d(embed_dim, embed_dim * 2, 3, stride=2, padding=1),
            nn.GELU(),
        )
        self.bottleneck = nn.Sequential(*[MambaStyleBlock(embed_dim * 2, expansion) for _ in range(deep_depth)])
        self.up = nn.Sequential(
            nn.Conv2d(embed_dim * 2, embed_dim * 4, 3, padding=1),
            nn.PixelShuffle(2),
            nn.GELU(),
        )
        self.fuse = nn.Conv2d(embed_dim * 2, embed_dim, 1)
        self.dec = nn.Sequential(*[MambaStyleBlock(embed_dim, expansion) for _ in range(shallow_depth)])
        self.tail = nn.Sequential(
            nn.Conv2d(embed_dim, embed_dim, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(embed_dim, 1, 3, padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, _, h, w = x.shape
        pad_h = h % 2
        pad_w = w % 2
        if pad_h or pad_w:
            x = F.pad(x, (0, pad_w, 0, pad_h), mode="reflect")
        skip = self.enc(self.head(x))
        deep = self.bottleneck(self.down(skip))
        up = self.up(deep)
        if up.shape[-2:] != skip.shape[-2:]:
            up = F.interpolate(up, size=skip.shape[-2:], mode="bilinear", align_corners=False)
        feat = self.dec(self.fuse(torch.cat([skip, up], dim=1)))
        residual = torch.tanh(self.tail(feat)) * self.residual_scale
        if pad_h or pad_w:
            residual = residual[:, :, :h, :w]
        return residual
