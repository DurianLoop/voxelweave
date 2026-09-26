from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def _groups(channels: int) -> int:
    for groups in (8, 4, 2):
        if channels % groups == 0:
            return groups
    return 1


class WindowResidualBlock(nn.Module):
    def __init__(self, channels: int, dilation: int = 1):
        super().__init__()
        hidden = channels * 2
        self.spatial = nn.Sequential(
            nn.GroupNorm(_groups(channels), channels),
            nn.Conv2d(channels, channels, 3, padding=dilation, dilation=dilation, groups=channels),
            nn.Conv2d(channels, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, channels, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.spatial(x)


class WindowPhaseFlow(nn.Module):
    """Generate phase-specific bidirectional anchor warps for a whole interval."""

    def __init__(self, channels: int, max_flow: float = 8.0):
        super().__init__()
        self.max_flow = float(max_flow)
        self.net = nn.Sequential(
            nn.Conv2d(8, channels, 3, padding=1),
            nn.GELU(),
            WindowResidualBlock(channels, dilation=1),
            WindowResidualBlock(channels, dilation=2),
            nn.Conv2d(channels, 4, 3, padding=1),
        )
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    @staticmethod
    def _warp(image: torch.Tensor, flow: torch.Tensor) -> torch.Tensor:
        batch, _, height, width = image.shape
        yy, xx = torch.meshgrid(
            torch.linspace(-1.0, 1.0, height, device=image.device, dtype=image.dtype),
            torch.linspace(-1.0, 1.0, width, device=image.device, dtype=image.dtype),
            indexing="ij",
        )
        grid = torch.stack([xx, yy], dim=-1).unsqueeze(0).expand(batch, -1, -1, -1)
        normalized = torch.stack(
            [2.0 * flow[:, 0] / max(1, width - 1), 2.0 * flow[:, 1] / max(1, height - 1)],
            dim=-1,
        )
        return F.grid_sample(image, grid + normalized, mode="bilinear", padding_mode="border", align_corners=True)

    def forward(self, cond: torch.Tensor) -> torch.Tensor:
        batch, offsets, _, height, width = cond.shape
        flat = cond.reshape(batch * offsets, cond.shape[2], height, width)
        flow_input = torch.cat(
            [
                flat[:, 0:4],
                flat[:, 4:5],
                flat[:, 5:6],
                flat[:, 7:8],
                flat[:, 12:13],
            ],
            dim=1,
        )
        low = F.avg_pool2d(flow_input, 2, 2)
        flow = F.interpolate(self.net(low), size=(height, width), mode="bilinear", align_corners=False)
        flow = self.max_flow * torch.tanh(flow)
        left = flat[:, 1:2]
        right = flat[:, 2:3]
        phase = flat[:, 5:6]
        aligned = (1.0 - phase) * self._warp(left, flow[:, :2]) + phase * self._warp(right, flow[:, 2:])
        return aligned.reshape(batch, offsets, height, width)


class OffsetVolumeMixer(nn.Module):
    """Create three query tokens at the U-Net bottleneck and mix them in 3-D."""

    def __init__(self, channels: int):
        super().__init__()
        self.offset_embedding = nn.Parameter(torch.zeros(1, channels, 3, 1, 1))
        nn.init.trunc_normal_(self.offset_embedding, std=0.02)
        self.volume = nn.Sequential(
            nn.Conv3d(channels, channels, 3, padding=1, groups=channels),
            nn.GroupNorm(_groups(channels), channels),
            nn.GELU(),
            nn.Conv3d(channels, channels, 1),
            nn.GELU(),
            nn.Conv3d(channels, channels, 3, padding=1, groups=channels),
        )
        self.merge = nn.Conv2d(channels * 3, channels, 1)

    def forward(self, feature: torch.Tensor) -> torch.Tensor:
        volume = feature.unsqueeze(2).expand(-1, -1, 3, -1, -1) + self.offset_embedding
        volume = volume + self.volume(volume)
        return self.merge(volume.permute(0, 2, 1, 3, 4).flatten(1, 2))


class PASTNetSparseWindow2p5D(nn.Module):
    """Independent four-anchor sparse-window synthesis backbone.

    It predicts all three missing x4 offsets jointly from one interval and does
    not consume predictions from an earlier PAST-Net checkpoint.
    """

    MODES = {"pyramid", "phase_flow", "dual_domain", "hybrid"}

    def __init__(
        self,
        input_channels: int = 13,
        base_channels: int = 40,
        num_blocks: int = 2,
        window_size: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 0.75,
        temporal_refine: bool = True,
        refine_scale: float = 0.35,
        sparse_mode: str = "pyramid",
        flow_channels: int = 24,
    ):
        super().__init__()
        del window_size, mlp_ratio, temporal_refine, refine_scale
        if input_channels != 13:
            raise ValueError("PASTNetSparseWindow2p5D expects rich 13-channel interval inputs")
        if sparse_mode not in self.MODES:
            raise ValueError(f"Unsupported sparse_mode={sparse_mode!r}")
        self.input_channels = input_channels
        self.base_channels = int(base_channels)
        self.num_blocks = int(num_blocks)
        self.residual_scale = float(residual_scale)
        self.sparse_mode = sparse_mode
        self.use_flow = sparse_mode in {"phase_flow", "hybrid"}
        self.use_frequency = sparse_mode in {"dual_domain", "hybrid"}
        self.use_volume = sparse_mode == "hybrid"
        if self.use_flow:
            self.phase_flow = WindowPhaseFlow(flow_channels)
        else:
            self.phase_flow = None

        feature_channels = 17 + (3 if self.use_flow else 0) + (9 if self.use_frequency else 0)
        c = self.base_channels
        repeats = max(1, self.num_blocks)
        self.stem = nn.Sequential(
            nn.Conv2d(feature_channels, c, 5, padding=2),
            nn.GELU(),
            *[WindowResidualBlock(c, dilation=1 + i % 2) for i in range(repeats)],
        )
        self.down1 = nn.Conv2d(c, c * 2, 4, stride=2, padding=1)
        self.enc1 = nn.Sequential(
            nn.GELU(),
            *[WindowResidualBlock(c * 2, dilation=1 + i % 2) for i in range(repeats)],
        )
        self.down2 = nn.Conv2d(c * 2, c * 4, 4, stride=2, padding=1)
        self.enc2 = nn.Sequential(
            nn.GELU(),
            *[WindowResidualBlock(c * 4, dilation=1 + i % 3) for i in range(repeats + 1)],
        )
        self.down3 = nn.Conv2d(c * 4, c * 6, 4, stride=2, padding=1)
        self.bottleneck = nn.Sequential(
            nn.GELU(),
            *[WindowResidualBlock(c * 6, dilation=1 + i % 3) for i in range(repeats + 2)],
        )
        self.offset_volume = OffsetVolumeMixer(c * 6) if self.use_volume else None
        self.up2 = nn.Sequential(
            nn.Conv2d(c * 10, c * 4, 3, padding=1),
            nn.GELU(),
            WindowResidualBlock(c * 4),
        )
        self.up1 = nn.Sequential(
            nn.Conv2d(c * 6, c * 2, 3, padding=1),
            nn.GELU(),
            WindowResidualBlock(c * 2),
        )
        self.up0 = nn.Sequential(
            nn.Conv2d(c * 3, c, 3, padding=1),
            nn.GELU(),
            WindowResidualBlock(c),
        )
        self.output = nn.Conv2d(c, 6, 3, padding=1)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)

    @staticmethod
    def _base_features(cond: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        anchors = cond[:, 0, 0:4]
        coarse = cond[:, :, 4]
        phases = cond[:, :, 5]
        shared = torch.cat(
            [
                cond[:, 0, 6:8],
                cond[:, 0, 8:10],
                cond[:, 0, 10:13],
            ],
            dim=1,
        )
        return torch.cat([anchors, coarse, phases, shared], dim=1), coarse, phases

    @staticmethod
    def _frequency_bands(source: torch.Tensor) -> torch.Tensor:
        dtype = source.dtype
        height, width = source.shape[-2:]
        spectrum = torch.fft.rfft2(source.float(), norm="ortho")
        fy = torch.fft.fftfreq(height, device=source.device).view(height, 1)
        fx = torch.fft.rfftfreq(width, device=source.device).view(1, -1)
        radius = torch.sqrt(fx.square() + fy.square())
        low = torch.exp(-((radius / 0.10).clamp_min(1e-6) ** 4))
        high = 1.0 - torch.exp(-((radius / 0.28).clamp_min(1e-6) ** 4))
        mid = (1.0 - low - high).clamp_min(0.0)
        bands = [torch.fft.irfft2(spectrum * mask, s=(height, width), norm="ortho") for mask in (low, mid, high)]
        return torch.cat(bands, dim=1).to(dtype)

    @staticmethod
    def _gate(phases: torch.Tensor) -> torch.Tensor:
        prev = torch.full_like(phases, 0.10)
        next_ = torch.full_like(phases, 0.10)
        coarse = torch.full_like(phases, 0.50)
        logits = torch.stack([prev, 1.0 - phases, phases, next_, coarse], dim=2)
        return torch.softmax(logits, dim=2)

    def forward_components(self, cond: torch.Tensor) -> dict[str, torch.Tensor]:
        if cond.ndim != 5 or cond.shape[1:3] != (3, 13):
            raise ValueError("sparse-window PAST-Net expects shape (B, 3, 13, H, W)")
        features, coarse, phases = self._base_features(cond)
        extras = []
        if self.phase_flow is not None:
            extras.append(self.phase_flow(cond))
        if self.use_frequency:
            extras.append(self._frequency_bands(coarse))
        if extras:
            features = torch.cat([features, *extras], dim=1)

        x0 = self.stem(features)
        x1 = self.enc1(self.down1(x0))
        x2 = self.enc2(self.down2(x1))
        x3 = self.bottleneck(self.down3(x2))
        if self.offset_volume is not None:
            x3 = self.offset_volume(x3)
        x = F.interpolate(x3, size=x2.shape[-2:], mode="bilinear", align_corners=False)
        x = self.up2(torch.cat([x, x2], dim=1))
        x = F.interpolate(x, size=x1.shape[-2:], mode="bilinear", align_corners=False)
        x = self.up1(torch.cat([x, x1], dim=1))
        x = F.interpolate(x, size=x0.shape[-2:], mode="bilinear", align_corners=False)
        x = self.up0(torch.cat([x, x0], dim=1))
        output = self.output(x)
        residual = torch.tanh(output[:, :3])
        confidence = torch.sigmoid(output[:, 3:])
        prediction = coarse + self.residual_scale * confidence * residual
        prediction = prediction[:, :, None]
        confidence = confidence[:, :, None]
        coarse_prediction = coarse[:, :, None]
        return {
            "prediction": prediction,
            "base_prediction": coarse_prediction,
            "joint_correction": prediction - coarse_prediction,
            "joint_confidence": confidence,
            "confidence": confidence,
            "gate": self._gate(phases),
        }

    def forward(self, cond: torch.Tensor) -> torch.Tensor:
        return self.forward_components(cond)["prediction"]
