from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def window_partition(x: torch.Tensor, window_size: int) -> torch.Tensor:
    b, h, w, c = x.shape
    x = x.view(b, h // window_size, window_size, w // window_size, window_size, c)
    return x.permute(0, 1, 3, 2, 4, 5).contiguous().view(-1, window_size * window_size, c)


def window_reverse(windows: torch.Tensor, window_size: int, h: int, w: int) -> torch.Tensor:
    b = int(windows.shape[0] / (h * w / window_size / window_size))
    x = windows.view(b, h // window_size, w // window_size, window_size, window_size, -1)
    return x.permute(0, 1, 3, 2, 4, 5).contiguous().view(b, h, w, -1)


class ChannelAttention(nn.Module):
    """RCAN-style channel attention used by HAT's hybrid attention blocks."""

    def __init__(self, dim: int, squeeze_factor: int = 16):
        super().__init__()
        hidden = max(4, dim // squeeze_factor)
        self.attn = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(dim, hidden, 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(hidden, dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.attn(x)


class WindowAttention(nn.Module):
    def __init__(self, dim: int, window_size: int, num_heads: int):
        super().__init__()
        self.dim = dim
        self.window_size = window_size
        self.num_heads = num_heads
        head_dim = dim // num_heads
        self.scale = head_dim**-0.5
        self.relative_position_bias_table = nn.Parameter(
            torch.zeros((2 * window_size - 1) * (2 * window_size - 1), num_heads)
        )
        coords = torch.stack(torch.meshgrid(torch.arange(window_size), torch.arange(window_size), indexing="ij"))
        coords_flatten = torch.flatten(coords, 1)
        relative = coords_flatten[:, :, None] - coords_flatten[:, None, :]
        relative = relative.permute(1, 2, 0).contiguous()
        relative[:, :, 0] += window_size - 1
        relative[:, :, 1] += window_size - 1
        relative[:, :, 0] *= 2 * window_size - 1
        self.register_buffer("relative_position_index", relative.sum(-1), persistent=False)
        self.qkv = nn.Linear(dim, dim * 3)
        self.proj = nn.Linear(dim, dim)
        nn.init.trunc_normal_(self.relative_position_bias_table, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b_windows, n, c = x.shape
        qkv = self.qkv(x).reshape(b_windows, n, 3, self.num_heads, c // self.num_heads)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        attn = (q * self.scale) @ k.transpose(-2, -1)
        bias = self.relative_position_bias_table[self.relative_position_index.view(-1)]
        bias = bias.view(n, n, -1).permute(2, 0, 1).contiguous()
        attn = (attn + bias.unsqueeze(0)).softmax(dim=-1)
        x = (attn @ v).transpose(1, 2).reshape(b_windows, n, c)
        return self.proj(x)


class OverlapCrossAttention(nn.Module):
    """HAT-style overlap attention: query from a window, key/value from a larger neighborhood."""

    def __init__(self, dim: int, window_size: int, num_heads: int, overlap_ratio: float = 0.5):
        super().__init__()
        self.dim = dim
        self.window_size = window_size
        self.num_heads = num_heads
        self.overlap_size = int(window_size * (1.0 + overlap_ratio))
        if self.overlap_size <= window_size:
            self.overlap_size = window_size + 2
        if self.overlap_size % 2 != window_size % 2:
            self.overlap_size += 1
        head_dim = dim // num_heads
        self.scale = head_dim**-0.5
        self.norm = nn.LayerNorm(dim)
        self.q = nn.Linear(dim, dim)
        self.kv = nn.Linear(dim, dim * 2)
        self.proj = nn.Linear(dim, dim)
        self.unfold = nn.Unfold(
            kernel_size=(self.overlap_size, self.overlap_size),
            stride=window_size,
            padding=(self.overlap_size - window_size) // 2,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c, h, w = x.shape
        x_hw = x.permute(0, 2, 3, 1).contiguous()
        q_windows = window_partition(self.norm(x_hw), self.window_size)
        q = self.q(q_windows).reshape(-1, self.window_size * self.window_size, self.num_heads, c // self.num_heads)
        q = q.permute(0, 2, 1, 3)

        kv_windows = self.unfold(x).transpose(1, 2).contiguous()
        kv_windows = kv_windows.view(-1, self.overlap_size * self.overlap_size, c)
        kv = self.kv(self.norm(kv_windows)).reshape(
            -1, self.overlap_size * self.overlap_size, 2, self.num_heads, c // self.num_heads
        )
        kv = kv.permute(2, 0, 3, 1, 4)
        k, v = kv[0], kv[1]
        attn = ((q * self.scale) @ k.transpose(-2, -1)).softmax(dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(-1, self.window_size * self.window_size, c)
        out = self.proj(out)
        return window_reverse(out, self.window_size, h, w).permute(0, 3, 1, 2).contiguous()


class Mlp(nn.Module):
    def __init__(self, dim: int, hidden_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class HybridAttentionBlock(nn.Module):
    def __init__(
        self,
        dim: int,
        num_heads: int,
        window_size: int = 8,
        shift_size: int = 0,
        mlp_ratio: float = 2.0,
        channel_scale: float = 0.01,
    ):
        super().__init__()
        self.window_size = window_size
        self.shift_size = shift_size
        self.norm1 = nn.LayerNorm(dim)
        self.attn = WindowAttention(dim, window_size, num_heads)
        self.channel_attn = ChannelAttention(dim)
        self.channel_scale = channel_scale
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = Mlp(dim, int(dim * mlp_ratio))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c, h, w = x.shape
        shortcut = x
        y = x.permute(0, 2, 3, 1).contiguous()
        y = self.norm1(y)
        if self.shift_size > 0:
            y = torch.roll(y, shifts=(-self.shift_size, -self.shift_size), dims=(1, 2))
        windows = self.attn(window_partition(y, self.window_size))
        y = window_reverse(windows, self.window_size, h, w)
        if self.shift_size > 0:
            y = torch.roll(y, shifts=(self.shift_size, self.shift_size), dims=(1, 2))
        y = y.permute(0, 3, 1, 2).contiguous()
        x = shortcut + y + self.channel_scale * self.channel_attn(shortcut)
        z = x.permute(0, 2, 3, 1).contiguous()
        z = self.mlp(self.norm2(z))
        return x + z.permute(0, 3, 1, 2).contiguous()


class ResidualHybridAttentionGroup(nn.Module):
    def __init__(
        self,
        dim: int,
        depth: int,
        num_heads: int,
        window_size: int,
        mlp_ratio: float,
        overlap_ratio: float,
    ):
        super().__init__()
        blocks = []
        for idx in range(depth):
            shift = 0 if idx % 2 == 0 else window_size // 2
            blocks.append(HybridAttentionBlock(dim, num_heads, window_size, shift, mlp_ratio))
        self.blocks = nn.Sequential(*blocks)
        self.overlap_attn = OverlapCrossAttention(dim, window_size, num_heads, overlap_ratio)
        self.conv = nn.Conv2d(dim, dim, 3, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        body = self.blocks(x)
        body = body + self.overlap_attn(body)
        return x + self.conv(body)


class HAT2p5D(nn.Module):
    """HAT-style residual restoration net adapted to 2.5D slice interpolation."""

    def __init__(
        self,
        in_channels: int = 4,
        embed_dim: int = 48,
        depths: tuple[int, ...] = (2, 2, 2),
        num_heads: tuple[int, ...] = (3, 3, 3),
        window_size: int = 8,
        mlp_ratio: float = 2.0,
        overlap_ratio: float = 0.5,
        residual_scale: float = 1.0,
    ):
        super().__init__()
        if len(depths) != len(num_heads):
            raise ValueError("depths and num_heads must have the same length")
        self.window_size = window_size
        self.residual_scale = residual_scale
        self.head = nn.Conv2d(in_channels, embed_dim, 3, padding=1)
        self.body = nn.Sequential(
            *[
                ResidualHybridAttentionGroup(embed_dim, depth, heads, window_size, mlp_ratio, overlap_ratio)
                for depth, heads in zip(depths, num_heads)
            ]
        )
        self.body_conv = nn.Conv2d(embed_dim, embed_dim, 3, padding=1)
        self.tail = nn.Sequential(
            nn.Conv2d(embed_dim, embed_dim, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(embed_dim, 1, 3, padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, _, h, w = x.shape
        pad_h = (self.window_size - h % self.window_size) % self.window_size
        pad_w = (self.window_size - w % self.window_size) % self.window_size
        if pad_h or pad_w:
            x = F.pad(x, (0, pad_w, 0, pad_h), mode="reflect")
        feat = self.head(x)
        body = self.body_conv(self.body(feat)) + feat
        residual = torch.tanh(self.tail(body)) * self.residual_scale
        if pad_h or pad_w:
            residual = residual[:, :, :h, :w]
        return residual
