from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .model_ma import PASTNetMultiAnchor2p5D


class LatentConvMixer(nn.Module):
    """Local 3D offset/spatial mixer with a zero-initialized residual output."""

    def __init__(self, channels: int):
        super().__init__()
        self.offset_embedding = nn.Parameter(torch.zeros(1, channels, 3, 1, 1))
        self.body = nn.Sequential(
            nn.Conv3d(channels, channels, 3, padding=1, groups=channels),
            nn.GroupNorm(1, channels),
            nn.GELU(),
            nn.Conv3d(channels, channels, 1),
            nn.GELU(),
        )
        self.output = nn.Conv3d(channels, channels + 1, 1)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)

    def forward(self, feature: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        output = self.output(self.body(feature + self.offset_embedding))
        return output[:, :-1], output[:, -1:]


class LatentOffsetAttention(nn.Module):
    """Self-attention over the three missing offsets at each latent location."""

    def __init__(self, channels: int, num_heads: int = 4):
        super().__init__()
        self.offset_embedding = nn.Parameter(torch.zeros(1, 3, channels))
        nn.init.trunc_normal_(self.offset_embedding, std=0.02)
        self.norm = nn.LayerNorm(channels)
        self.attention = nn.MultiheadAttention(channels, num_heads, batch_first=True)
        self.spatial = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1, groups=channels),
            nn.GELU(),
            nn.Conv2d(channels, channels, 1),
        )
        self.output = nn.Conv3d(channels, channels + 1, 1)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)

    def forward(self, feature: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch, channels, offsets, height, width = feature.shape
        tokens = feature.permute(0, 3, 4, 2, 1).reshape(batch * height * width, offsets, channels)
        query = self.norm(tokens + self.offset_embedding)
        attended, _ = self.attention(query, query, query, need_weights=False)
        tokens = tokens + attended
        spatial = tokens.reshape(batch, height, width, offsets, channels).permute(0, 3, 4, 1, 2)
        spatial = self.spatial(spatial.reshape(batch * offsets, channels, height, width))
        spatial = spatial.reshape(batch, offsets, channels, height, width).permute(0, 2, 1, 3, 4)
        output = self.output(spatial)
        return output[:, :-1], output[:, -1:]


class PASTNetMA3LatentInterval2p5D(nn.Module):
    """G073 backbone with pre-decoder interaction among offsets 1/2/3."""

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
        latent_mixer: str = "conv",
        latent_scales: tuple[int, ...] = (4,),
        latent_scale: float = 0.25,
    ):
        super().__init__()
        if input_channels != 13:
            raise ValueError("PASTNetMA3LatentInterval2p5D expects 13-channel rich inputs")
        if latent_mixer not in {"conv", "attention", "multiscale", "hybrid"}:
            raise ValueError(f"Unsupported latent_mixer={latent_mixer!r}")
        if not latent_scales or any(scale < 1 for scale in latent_scales):
            raise ValueError("latent_scales must contain positive integers")
        self.input_channels = input_channels
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        self.window_size = window_size
        self.residual_scale = residual_scale
        self.temporal_refine = temporal_refine
        self.refine_scale = refine_scale
        self.context_blocks = context_blocks
        self.latent_mixer = latent_mixer
        self.latent_scales = tuple(int(scale) for scale in latent_scales)
        self.latent_scale = float(latent_scale)
        self.single = PASTNetMultiAnchor2p5D(
            input_channels=input_channels,
            base_channels=base_channels,
            num_blocks=num_blocks,
            window_size=window_size,
            mlp_ratio=mlp_ratio,
            residual_scale=residual_scale,
            temporal_refine=temporal_refine,
            refine_scale=refine_scale,
            context_blocks=context_blocks,
        )
        modules = []
        largest_scale = max(self.latent_scales)
        for scale in self.latent_scales:
            use_attention = latent_mixer == "attention" or (
                latent_mixer == "hybrid" and scale == largest_scale
            )
            modules.append(
                LatentOffsetAttention(base_channels)
                if use_attention
                else LatentConvMixer(base_channels)
            )
        self.latent_mixers = nn.ModuleList(modules)

    def forward_components(self, cond_stack: torch.Tensor) -> dict[str, torch.Tensor]:
        batch, offsets, channels, height, width = cond_stack.shape
        if offsets != 3 or channels != self.input_channels:
            raise ValueError("latent interval PAST-Net expects shape (B, 3, 13, H, W)")
        flat = cond_stack.reshape(batch * offsets, channels, height, width)
        encoded = self.single.encode_components(flat)
        feature = encoded["feature"]
        if not isinstance(feature, torch.Tensor):
            raise TypeError("PAST-Net encoded feature must be a tensor")
        feat_h, feat_w = feature.shape[-2:]
        feature_stack = feature.reshape(batch, offsets, self.base_channels, feat_h, feat_w).permute(0, 2, 1, 3, 4)
        delta_sum = torch.zeros_like(feature_stack)
        confidence_sum = feature_stack.new_zeros((batch, 1, offsets, feat_h, feat_w))
        for scale, mixer in zip(self.latent_scales, self.latent_mixers):
            low = F.avg_pool2d(feature, kernel_size=scale, stride=scale) if scale > 1 else feature
            low_h, low_w = low.shape[-2:]
            low_stack = low.reshape(batch, offsets, self.base_channels, low_h, low_w).permute(0, 2, 1, 3, 4)
            delta, confidence_logit = mixer(low_stack)
            flat_delta = delta.permute(0, 2, 1, 3, 4).reshape(batch * offsets, self.base_channels, low_h, low_w)
            flat_conf = confidence_logit.permute(0, 2, 1, 3, 4).reshape(batch * offsets, 1, low_h, low_w)
            if (low_h, low_w) != (feat_h, feat_w):
                flat_delta = F.interpolate(flat_delta, size=(feat_h, feat_w), mode="bilinear", align_corners=False)
                flat_conf = F.interpolate(flat_conf, size=(feat_h, feat_w), mode="bilinear", align_corners=False)
            delta_sum += flat_delta.reshape(batch, offsets, self.base_channels, feat_h, feat_w).permute(0, 2, 1, 3, 4)
            confidence_sum += torch.sigmoid(
                flat_conf.reshape(batch, offsets, 1, feat_h, feat_w).permute(0, 2, 1, 3, 4)
            )
        divisor = float(len(self.latent_mixers))
        delta_mean = delta_sum / divisor
        confidence = confidence_sum / divisor
        mixed_stack = feature_stack + self.latent_scale * confidence * delta_mean
        mixed = mixed_stack.permute(0, 2, 1, 3, 4).reshape(batch * offsets, self.base_channels, feat_h, feat_w)
        base_parts = self.single.decode_components(encoded)
        mixed_parts = self.single.decode_components(encoded, feature_override=mixed)
        base_prediction = base_parts["prediction"].reshape(batch, offsets, 1, height, width)
        prediction = mixed_parts["prediction"].reshape(batch, offsets, 1, height, width)
        confidence_image = confidence.permute(0, 2, 1, 3, 4).reshape(batch * offsets, 1, feat_h, feat_w)
        confidence_image = F.interpolate(confidence_image, size=(height, width), mode="bilinear", align_corners=False)
        confidence_image = confidence_image.reshape(batch, offsets, 1, height, width)
        return {
            "prediction": prediction,
            "base_prediction": base_prediction,
            "joint_correction": prediction - base_prediction,
            "joint_confidence": confidence_image,
            "confidence": mixed_parts["confidence"].reshape(batch, offsets, 1, height, width),
            "gate": mixed_parts["gate"].reshape(batch, offsets, 5, height, width),
        }

    def forward(self, cond_stack: torch.Tensor) -> torch.Tensor:
        return self.forward_components(cond_stack)["prediction"]
