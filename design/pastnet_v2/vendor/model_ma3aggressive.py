from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from .model_ma3latent import PASTNetMA3LatentInterval2p5D


def _groups(channels: int) -> int:
    for groups in (8, 4, 2):
        if channels % groups == 0:
            return groups
    return 1


class Residual2DBlock(nn.Module):
    def __init__(self, channels: int, dilation: int = 1):
        super().__init__()
        self.body = nn.Sequential(
            nn.GroupNorm(_groups(channels), channels),
            nn.Conv2d(channels, channels, 3, padding=dilation, dilation=dilation),
            nn.GELU(),
            nn.Conv2d(channels, channels, 3, padding=dilation, dilation=dilation),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.body(x)


class PhaseFlowRefiner(nn.Module):
    """Warp both interval anchors toward every queried phase before correction."""

    def __init__(self, channels: int, max_flow: float = 8.0):
        super().__init__()
        self.max_flow = float(max_flow)
        self.flow = nn.Sequential(
            nn.Conv2d(6, channels, 3, padding=1),
            nn.GELU(),
            Residual2DBlock(channels, dilation=1),
            Residual2DBlock(channels, dilation=2),
            nn.Conv2d(channels, 4, 3, padding=1),
        )
        self.correct = nn.Sequential(
            nn.Conv2d(7, channels, 3, padding=1),
            nn.GELU(),
            Residual2DBlock(channels, dilation=1),
            Residual2DBlock(channels, dilation=3),
            nn.Conv2d(channels, 2, 3, padding=1),
        )
        nn.init.zeros_(self.flow[-1].weight)
        nn.init.zeros_(self.flow[-1].bias)
        nn.init.zeros_(self.correct[-1].weight)
        nn.init.zeros_(self.correct[-1].bias)

    @staticmethod
    def _warp(image: torch.Tensor, flow: torch.Tensor) -> torch.Tensor:
        batch, _, height, width = image.shape
        yy, xx = torch.meshgrid(
            torch.linspace(-1.0, 1.0, height, device=image.device, dtype=image.dtype),
            torch.linspace(-1.0, 1.0, width, device=image.device, dtype=image.dtype),
            indexing="ij",
        )
        grid = torch.stack([xx, yy], dim=-1).unsqueeze(0).expand(batch, -1, -1, -1)
        flow_x = 2.0 * flow[:, 0] / max(1, width - 1)
        flow_y = 2.0 * flow[:, 1] / max(1, height - 1)
        grid = grid + torch.stack([flow_x, flow_y], dim=-1)
        return F.grid_sample(image, grid, mode="bilinear", padding_mode="border", align_corners=True)

    def forward(self, cond: torch.Tensor, base: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch, offsets, _, height, width = cond.shape
        flat = cond.reshape(batch * offsets, cond.shape[2], height, width)
        flat_base = base.reshape(batch * offsets, 1, height, width)
        left, right = flat[:, 1:2], flat[:, 2:3]
        coarse, phase = flat[:, 4:5], flat[:, 5:6]
        flow_input = torch.cat([left, right, (right - left).abs(), coarse, phase, flat_base], dim=1)
        low = F.avg_pool2d(flow_input, 2, 2)
        flow = F.interpolate(self.flow(low), size=(height, width), mode="bilinear", align_corners=False)
        flow = self.max_flow * torch.tanh(flow)
        left_warp = self._warp(left, flow[:, 0:2])
        right_warp = self._warp(right, flow[:, 2:4])
        aligned = (1.0 - phase) * left_warp + phase * right_warp
        output = self.correct(
            torch.cat([flat_base, coarse, aligned, left_warp, right_warp, phase, right_warp - left_warp], dim=1)
        )
        correction = output[:, 0:1].reshape(batch, offsets, 1, height, width)
        confidence = torch.sigmoid(output[:, 1:2]).reshape(batch, offsets, 1, height, width)
        return correction, confidence


class ImplicitCoordinateRefiner(nn.Module):
    """Continuous Fourier-coordinate decoder shared by all through-plane offsets."""

    def __init__(self, channels: int):
        super().__init__()
        self.anchor_encoder = nn.Sequential(
            nn.Conv2d(4, channels, 5, padding=2),
            nn.GELU(),
            Residual2DBlock(channels, dilation=1),
            Residual2DBlock(channels, dilation=2),
            Residual2DBlock(channels, dilation=4),
        )
        self.coordinate_encoder = nn.Sequential(nn.Conv2d(7, channels, 1), nn.GELU())
        self.decoder = nn.Sequential(
            nn.Conv2d(channels * 2 + 2, channels, 3, padding=1),
            nn.GELU(),
            Residual2DBlock(channels, dilation=1),
            Residual2DBlock(channels, dilation=3),
            nn.Conv2d(channels, 2, 3, padding=1),
        )
        nn.init.zeros_(self.decoder[-1].weight)
        nn.init.zeros_(self.decoder[-1].bias)

    @staticmethod
    def _fourier_phase(phase: torch.Tensor) -> torch.Tensor:
        features = [phase]
        for frequency in (1.0, 2.0, 4.0):
            features.extend(
                [torch.sin(math.pi * frequency * phase), torch.cos(math.pi * frequency * phase)]
            )
        return torch.cat(features, dim=1)

    def forward(self, cond: torch.Tensor, base: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch, offsets, _, height, width = cond.shape
        anchors = cond[:, 0, (0, 1, 2, 3)]
        anchor_feature = self.anchor_encoder(anchors)
        anchor_feature = anchor_feature[:, None].expand(-1, offsets, -1, -1, -1)
        flat_anchor = anchor_feature.reshape(batch * offsets, anchor_feature.shape[2], height, width)
        phase = cond[:, :, 5:6].reshape(batch * offsets, 1, height, width)
        coordinate = self.coordinate_encoder(self._fourier_phase(phase))
        flat_base = base.reshape(batch * offsets, 1, height, width)
        coarse = cond[:, :, 4:5].reshape(batch * offsets, 1, height, width)
        output = self.decoder(torch.cat([flat_anchor, coordinate, flat_base, coarse], dim=1))
        correction = output[:, 0:1].reshape(batch, offsets, 1, height, width)
        confidence = torch.sigmoid(output[:, 1:2]).reshape(batch, offsets, 1, height, width)
        return correction, confidence


class ConvGRU3DCell(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.gates = nn.Conv3d(channels * 2, channels * 2, 3, padding=1)
        self.candidate = nn.Conv3d(channels * 2, channels, 3, padding=1)

    def forward(self, x: torch.Tensor, hidden: torch.Tensor) -> torch.Tensor:
        reset, update = torch.sigmoid(self.gates(torch.cat([x, hidden], dim=1))).chunk(2, dim=1)
        candidate = torch.tanh(self.candidate(torch.cat([x, reset * hidden], dim=1)))
        return (1.0 - update) * hidden + update * candidate


class RecurrentErrorFeedbackRefiner(nn.Module):
    """Unrolled interval correction driven by anchor-clamped z-curvature feedback."""

    def __init__(self, channels: int, steps: int):
        super().__init__()
        self.steps = int(steps)
        self.condition = nn.Sequential(
            nn.Conv3d(6, channels, (1, 3, 3), padding=(0, 1, 1)),
            nn.GELU(),
            nn.Conv3d(channels, channels, 3, padding=1),
            nn.GELU(),
        )
        self.feedback = nn.Conv3d(1, channels, 3, padding=1)
        self.cell = ConvGRU3DCell(channels)
        self.output = nn.Conv3d(channels, 2, 3, padding=1)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)

    @staticmethod
    def _curvature(cond: torch.Tensor, current: torch.Tensor) -> torch.Tensor:
        left = cond[:, 0, 1:2].unsqueeze(2)
        right = cond[:, 0, 2:3].unsqueeze(2)
        middle = current.permute(0, 2, 1, 3, 4)
        volume = torch.cat([left, middle, right], dim=2)
        return volume[:, :, :-2] - 2.0 * volume[:, :, 1:-1] + volume[:, :, 2:]

    def forward(self, cond: torch.Tensor, base: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        features = torch.stack(
            [base[:, :, 0], cond[:, :, 4], cond[:, :, 1], cond[:, :, 2], cond[:, :, 5], cond[:, :, 6]],
            dim=1,
        )
        condition = self.condition(features)
        hidden = torch.zeros_like(condition)
        accumulated = base.new_zeros(base.shape)
        confidence = base.new_zeros(base.shape)
        for _ in range(self.steps):
            current = base + 0.15 * torch.tanh(accumulated)
            feedback = self.feedback(self._curvature(cond, current))
            hidden = self.cell(condition + feedback, hidden)
            output = self.output(hidden).permute(0, 2, 1, 3, 4)
            accumulated = accumulated + output[:, :, 0:1] / float(self.steps)
            confidence = confidence + torch.sigmoid(output[:, :, 1:2]) / float(self.steps)
        return accumulated, confidence


class DualDomainRefiner(nn.Module):
    """Fuse spatial residual experts with explicit low/mid/high FFT bands."""

    def __init__(self, channels: int, offsets: int = 3):
        super().__init__()
        source_channels = offsets * 2
        self.offsets = offsets
        self.spatial = nn.Sequential(
            nn.Conv2d(source_channels, channels, 5, padding=2),
            nn.GELU(),
            Residual2DBlock(channels, dilation=1),
            Residual2DBlock(channels, dilation=3),
            nn.Conv2d(channels, offsets, 3, padding=1),
        )
        self.spectral = nn.Sequential(
            nn.Conv2d(source_channels * 4, channels, 3, padding=1),
            nn.GELU(),
            Residual2DBlock(channels, dilation=1),
            Residual2DBlock(channels, dilation=2),
            nn.Conv2d(channels, offsets, 3, padding=1),
        )
        self.gate = nn.Sequential(
            nn.Conv2d(source_channels, channels // 2, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(channels // 2, offsets, 1),
        )
        for module in (self.spatial[-1], self.spectral[-1]):
            nn.init.zeros_(module.weight)
            nn.init.zeros_(module.bias)

    @staticmethod
    def _bands(source: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        dtype = source.dtype
        height, width = source.shape[-2:]
        spectrum = torch.fft.rfft2(source.float(), norm="ortho")
        fy = torch.fft.fftfreq(height, device=source.device).view(height, 1)
        fx = torch.fft.rfftfreq(width, device=source.device).view(1, -1)
        radius = torch.sqrt(fx.square() + fy.square())
        low_mask = torch.exp(-((radius / 0.10).clamp_min(1e-6) ** 4))
        high_mask = 1.0 - torch.exp(-((radius / 0.28).clamp_min(1e-6) ** 4))
        mid_mask = (1.0 - low_mask - high_mask).clamp_min(0.0)
        inverse = lambda mask: torch.fft.irfft2(spectrum * mask, s=(height, width), norm="ortho").to(dtype)
        return inverse(low_mask), inverse(mid_mask), inverse(high_mask)

    def forward(self, cond: torch.Tensor, base: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        base_stack = base[:, :, 0]
        coarse_stack = cond[:, :, 4]
        source = torch.cat([base_stack, coarse_stack], dim=1)
        low, mid, high = self._bands(source)
        spatial = self.spatial(source)
        spectral = self.spectral(torch.cat([source, low, mid, high], dim=1))
        gate = torch.sigmoid(self.gate(source))
        correction = gate * spatial + (1.0 - gate) * spectral
        return correction[:, :, None], gate[:, :, None]


class VolumetricUNetRefiner(nn.Module):
    """Anchor-clamped 3-D U-Net over [left, q1, q2, q3, right]."""

    def __init__(self, channels: int):
        super().__init__()
        self.enc1 = nn.Sequential(
            nn.Conv3d(3, channels, 3, padding=1),
            nn.GELU(),
            nn.Conv3d(channels, channels, 3, padding=1),
            nn.GELU(),
        )
        self.down1 = nn.Conv3d(channels, channels * 2, (3, 4, 4), stride=(1, 2, 2), padding=(1, 1, 1))
        self.enc2 = nn.Sequential(nn.GELU(), nn.Conv3d(channels * 2, channels * 2, 3, padding=1), nn.GELU())
        self.down2 = nn.Conv3d(channels * 2, channels * 4, (3, 4, 4), stride=(1, 2, 2), padding=(1, 1, 1))
        self.bottleneck = nn.Sequential(
            nn.GELU(),
            nn.Conv3d(channels * 4, channels * 4, 3, padding=1),
            nn.GELU(),
            nn.Conv3d(channels * 4, channels * 4, 3, padding=1),
            nn.GELU(),
        )
        self.up2 = nn.Conv3d(channels * 4 + channels * 2, channels * 2, 3, padding=1)
        self.up1 = nn.Conv3d(channels * 2 + channels, channels, 3, padding=1)
        self.output = nn.Conv3d(channels, 2, 3, padding=1)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)

    @staticmethod
    def _window(cond: torch.Tensor, middle: torch.Tensor) -> torch.Tensor:
        left = cond[:, 0, 1:2].unsqueeze(2)
        right = cond[:, 0, 2:3].unsqueeze(2)
        return torch.cat([left, middle.permute(0, 2, 1, 3, 4), right], dim=2)

    def forward(self, cond: torch.Tensor, base: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        base_window = self._window(cond, base)
        coarse_window = self._window(cond, cond[:, :, 4:5])
        phase = cond[:, :, 5:6].permute(0, 2, 1, 3, 4)
        phase_window = torch.cat([torch.zeros_like(phase[:, :, :1]), phase, torch.ones_like(phase[:, :, :1])], dim=2)
        x1 = self.enc1(torch.cat([base_window, coarse_window, phase_window], dim=1))
        x2 = self.enc2(self.down1(x1))
        latent = self.bottleneck(self.down2(x2))
        latent = F.interpolate(latent, size=x2.shape[-3:], mode="trilinear", align_corners=False)
        x = F.gelu(self.up2(torch.cat([latent, x2], dim=1)))
        x = F.interpolate(x, size=x1.shape[-3:], mode="trilinear", align_corners=False)
        x = F.gelu(self.up1(torch.cat([x, x1], dim=1)))
        output = self.output(x)[:, :, 1:4].permute(0, 2, 1, 3, 4)
        return output[:, :, 0:1], torch.sigmoid(output[:, :, 1:2])


class PASTNetMA3Aggressive2p5D(nn.Module):
    """G079 backbone plus one independently testable high-capacity mechanism."""

    MODES = {"phase_flow", "implicit_coord", "recurrent", "dual_domain", "volumetric_unet"}

    def __init__(
        self,
        input_channels: int = 13,
        base_channels: int = 64,
        num_blocks: int = 10,
        window_size: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 1.0,
        temporal_refine: bool = True,
        refine_scale: float = 0.35,
        context_blocks: int = 2,
        latent_mixer: str = "multiscale",
        latent_scales: tuple[int, ...] = (2, 4),
        latent_scale: float = 0.35,
        aggressive_mode: str = "phase_flow",
        aggressive_channels: int = 32,
        aggressive_steps: int = 3,
        aggressive_scale: float = 0.20,
    ):
        super().__init__()
        if aggressive_mode not in self.MODES:
            raise ValueError(f"Unsupported aggressive_mode={aggressive_mode!r}")
        self.aggressive_mode = aggressive_mode
        self.aggressive_channels = int(aggressive_channels)
        self.aggressive_steps = int(aggressive_steps)
        self.aggressive_scale = float(aggressive_scale)
        self.base = PASTNetMA3LatentInterval2p5D(
            input_channels=input_channels,
            base_channels=base_channels,
            num_blocks=num_blocks,
            window_size=window_size,
            mlp_ratio=mlp_ratio,
            residual_scale=residual_scale,
            temporal_refine=temporal_refine,
            refine_scale=refine_scale,
            context_blocks=context_blocks,
            latent_mixer=latent_mixer,
            latent_scales=latent_scales,
            latent_scale=latent_scale,
        )
        if aggressive_mode == "phase_flow":
            refiner: nn.Module = PhaseFlowRefiner(aggressive_channels)
        elif aggressive_mode == "implicit_coord":
            refiner = ImplicitCoordinateRefiner(aggressive_channels)
        elif aggressive_mode == "recurrent":
            refiner = RecurrentErrorFeedbackRefiner(aggressive_channels, aggressive_steps)
        elif aggressive_mode == "dual_domain":
            refiner = DualDomainRefiner(aggressive_channels)
        else:
            refiner = VolumetricUNetRefiner(aggressive_channels)
        self.aggressive_refiner = refiner

    def forward_components(self, cond_stack: torch.Tensor) -> dict[str, torch.Tensor]:
        base_out = self.base.forward_components(cond_stack)
        base_prediction = base_out["prediction"]
        correction, confidence = self.aggressive_refiner(cond_stack, base_prediction)
        prediction = base_prediction + self.aggressive_scale * confidence * torch.tanh(correction)
        return {
            "prediction": prediction,
            "base_prediction": base_prediction,
            "joint_correction": prediction - base_prediction,
            "joint_confidence": confidence,
            "confidence": base_out["confidence"],
            "gate": base_out["gate"],
        }

    def forward(self, cond_stack: torch.Tensor) -> torch.Tensor:
        return self.forward_components(cond_stack)["prediction"]
