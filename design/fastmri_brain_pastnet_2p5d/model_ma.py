from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from ixi_pastnet_2p5d.model import ChannelAttention, LocalStructureBlock, LongRangeMixer


class MultiScaleContextAdapter(nn.Module):
    """Residual multi-scale context initialized as an exact no-op."""

    def __init__(self, channels: int):
        super().__init__()
        self.norm = nn.GroupNorm(1, channels)
        self.branches = nn.ModuleList(
            [
                nn.Conv2d(channels, channels, 3, padding=dilation, dilation=dilation, groups=channels)
                for dilation in (1, 2, 3)
            ]
        )
        self.project = nn.Sequential(
            nn.Conv2d(channels * 3, channels, 1),
            nn.GELU(),
            ChannelAttention(channels),
            nn.Conv2d(channels, channels, 1),
        )
        nn.init.zeros_(self.project[-1].weight)
        nn.init.zeros_(self.project[-1].bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.norm(x)
        y = torch.cat([branch(y) for branch in self.branches], dim=1)
        return x + self.project(y)


class PASTNetMultiAnchor2p5D(nn.Module):
    """Multi-anchor PAST-Net for deterministic single-slice interpolation.

    Basic input channel order:
    [prev_anchor, left, right, next_anchor, coarse, phase,
     right-left, abs(right-left), prev_valid, next_valid].

    Rich input adds:
    [left-prev_anchor, next_anchor-right, sparse curvature].
    """

    def __init__(
        self,
        input_channels: int = 10,
        base_channels: int = 48,
        num_blocks: int = 8,
        window_size: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 1.0,
        temporal_refine: bool = False,
        refine_scale: float = 0.5,
        anchor_reliability: bool = False,
        context_blocks: int = 0,
    ):
        super().__init__()
        if input_channels not in {10, 13}:
            raise ValueError("PASTNetMultiAnchor2p5D expects 10 basic or 13 rich input channels")
        self.input_channels = input_channels
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        self.window_size = window_size
        self.residual_scale = residual_scale
        self.temporal_refine = temporal_refine
        self.refine_scale = refine_scale
        self.anchor_reliability = anchor_reliability
        self.context_blocks = context_blocks

        self.slice_encoder = nn.Sequential(
            nn.Conv2d(1, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        self.aux_encoder = nn.Sequential(
            nn.Conv2d(input_channels - 5, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
        )
        gate_channels = base_channels * 6
        self.gate = nn.Sequential(
            nn.GroupNorm(1, gate_channels),
            nn.Conv2d(gate_channels, base_channels, 1),
            nn.GELU(),
            nn.Conv2d(base_channels, 5, 1),
        )
        if anchor_reliability:
            reliability_hidden = max(8, base_channels // 4)
            self.reliability_gate = nn.Sequential(
                nn.GroupNorm(1, base_channels * 2),
                nn.Conv2d(base_channels * 2, reliability_hidden, 1),
                nn.GELU(),
                nn.Conv2d(reliability_hidden, 1, 1),
            )
            nn.init.zeros_(self.reliability_gate[-1].weight)
            nn.init.zeros_(self.reliability_gate[-1].bias)
        else:
            self.reliability_gate = None
        self.fuse = nn.Sequential(
            nn.Conv2d(base_channels * 2, base_channels, 3, padding=1),
            nn.GELU(),
        )
        self.body = nn.Sequential(
            *[LocalStructureBlock(base_channels, mlp_ratio=mlp_ratio) for _ in range(num_blocks)]
        )
        self.mixer = LongRangeMixer(base_channels)
        self.context = nn.Sequential(
            *[MultiScaleContextAdapter(base_channels) for _ in range(context_blocks)]
        )
        self.decoder = nn.Sequential(
            nn.GroupNorm(1, base_channels),
            nn.Conv2d(base_channels, base_channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels, base_channels // 2, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(base_channels // 2, 2, 3, padding=1),
        )
        if temporal_refine:
            self.detail_refiner = nn.Sequential(
                nn.GroupNorm(1, base_channels * 2),
                nn.Conv2d(base_channels * 2, base_channels, 3, padding=1),
                nn.GELU(),
                LocalStructureBlock(base_channels, mlp_ratio=mlp_ratio),
                nn.Conv2d(base_channels, 1, 3, padding=1),
            )
        else:
            self.detail_refiner = None

    def _pad(self, x: torch.Tensor) -> tuple[torch.Tensor, int, int]:
        _, _, h, w = x.shape
        pad_h = (self.window_size - h % self.window_size) % self.window_size
        pad_w = (self.window_size - w % self.window_size) % self.window_size
        if pad_h or pad_w:
            x = F.pad(x, (0, pad_w, 0, pad_h), mode="reflect")
        return x, pad_h, pad_w

    def forward_components(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        x, pad_h, pad_w = self._pad(x)
        prev = x[:, 0:1]
        left = x[:, 1:2]
        right = x[:, 2:3]
        next_ = x[:, 3:4]
        coarse = x[:, 4:5]
        phase = x[:, 5:6].clamp(0.0, 1.0)
        diff = x[:, 6:7]
        absdiff = x[:, 7:8]
        prev_valid = x[:, 8:9].clamp(0.0, 1.0)
        next_valid = x[:, 9:10].clamp(0.0, 1.0)
        aux = [phase, diff, absdiff, prev_valid, next_valid]
        if self.input_channels == 13:
            aux.extend([x[:, 10:11], x[:, 11:12], x[:, 12:13]])

        feat_prev = self.slice_encoder(prev)
        feat_left = self.slice_encoder(left)
        feat_right = self.slice_encoder(right)
        feat_next = self.slice_encoder(next_)
        feat_coarse = self.slice_encoder(coarse)
        feat_aux = self.aux_encoder(torch.cat(aux, dim=1))

        anchor_features = [feat_prev, feat_left, feat_right, feat_next, feat_coarse]
        logits = self.gate(torch.cat([*anchor_features, feat_aux], dim=1))
        if self.reliability_gate is not None:
            reliability = []
            for anchor_feature in anchor_features:
                local_score = self.reliability_gate(torch.cat([anchor_feature, feat_aux], dim=1))
                global_score = local_score.mean(dim=(2, 3), keepdim=True)
                reliability.append(local_score + global_score)
            logits = logits + torch.cat(reliability, dim=1)
        outer_prior = 0.35 if self.input_channels == 13 else 0.15
        coarse_prior = 0.4 if self.input_channels == 13 else 0.5
        priors = torch.cat(
            [
                (outer_prior * prev_valid).clamp_min(1e-4),
                (1.0 - phase).clamp_min(1e-4),
                phase.clamp_min(1e-4),
                (outer_prior * next_valid).clamp_min(1e-4),
                torch.full_like(phase, coarse_prior),
            ],
            dim=1,
        )
        weights = torch.softmax(logits + priors.log(), dim=1)
        transferred = (
            weights[:, 0:1] * feat_prev
            + weights[:, 1:2] * feat_left
            + weights[:, 2:3] * feat_right
            + weights[:, 3:4] * feat_next
            + weights[:, 4:5] * feat_coarse
        )
        feat = self.fuse(torch.cat([transferred, feat_aux], dim=1))
        feat = self.context(self.mixer(self.body(feat)))
        decoded = self.decoder(feat)
        residual = torch.tanh(decoded[:, 0:1])
        confidence = torch.sigmoid(decoded[:, 1:2])
        detail_residual = torch.zeros_like(residual)
        if self.detail_refiner is not None:
            local_context = feat_left + feat_right - 2.0 * feat_coarse
            detail_residual = torch.tanh(self.detail_refiner(torch.cat([feat, local_context], dim=1)))
        prediction = coarse + confidence * (self.residual_scale * residual + self.refine_scale * detail_residual)
        if pad_h or pad_w:
            h = prediction.shape[2] - pad_h if pad_h else prediction.shape[2]
            w = prediction.shape[3] - pad_w if pad_w else prediction.shape[3]
            prediction = prediction[:, :, :h, :w]
            residual = residual[:, :, :h, :w]
            detail_residual = detail_residual[:, :, :h, :w]
            confidence = confidence[:, :, :h, :w]
            weights = weights[:, :, :h, :w]
        return {
            "prediction": prediction,
            "residual": residual,
            "detail_residual": detail_residual,
            "confidence": confidence,
            "gate": weights,
        }

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.forward_components(x)["prediction"]
