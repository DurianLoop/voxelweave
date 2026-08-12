from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .model_ma import PASTNetMultiAnchor2p5D


class PASTNetMA3Joint2p5D(nn.Module):
    """MA3 backbone with a joint interval head for offsets 1/2/3.

    The single-slice MA3 branch is kept load-compatible with existing MA3
    checkpoints. The joint head is zero-initialized, so the model starts as
    exactly the MA3 teacher and learns only cross-offset residual corrections.
    """

    def __init__(
        self,
        input_channels: int = 13,
        base_channels: int = 48,
        num_blocks: int = 8,
        window_size: int = 8,
        mlp_ratio: float = 2.0,
        residual_scale: float = 1.0,
        temporal_refine: bool = True,
        refine_scale: float = 0.3,
        joint_scale: float = 0.2,
        anchor_reliability: bool = False,
        context_blocks: int = 0,
        interval_refine: bool = False,
    ):
        super().__init__()
        if input_channels != 13:
            raise ValueError("PASTNetMA3Joint2p5D expects rich 13-channel interval inputs")
        self.input_channels = input_channels
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        self.window_size = window_size
        self.residual_scale = residual_scale
        self.temporal_refine = temporal_refine
        self.refine_scale = refine_scale
        self.joint_scale = joint_scale
        self.anchor_reliability = anchor_reliability
        self.context_blocks = context_blocks
        self.interval_refine = interval_refine
        self.single = PASTNetMultiAnchor2p5D(
            input_channels=input_channels,
            base_channels=base_channels,
            num_blocks=num_blocks,
            window_size=window_size,
            mlp_ratio=mlp_ratio,
            residual_scale=residual_scale,
            temporal_refine=temporal_refine,
            refine_scale=refine_scale,
            anchor_reliability=anchor_reliability,
            context_blocks=context_blocks,
        )
        if interval_refine:
            interval_channels = max(24, base_channels // 2)
            self.interval_refiner = nn.ModuleDict(
                {
                    "encoder": nn.Sequential(
                        nn.Conv2d(10, interval_channels, 3, stride=2, padding=1),
                        nn.GroupNorm(4, interval_channels),
                        nn.GELU(),
                        nn.Conv2d(interval_channels, interval_channels, 3, stride=2, padding=1),
                        nn.GroupNorm(4, interval_channels),
                        nn.GELU(),
                    ),
                    "mixer": nn.Sequential(
                        nn.Conv3d(
                            interval_channels,
                            interval_channels,
                            3,
                            padding=1,
                            groups=interval_channels,
                        ),
                        nn.GroupNorm(4, interval_channels),
                        nn.GELU(),
                        nn.Conv3d(interval_channels, interval_channels, 1),
                        nn.GELU(),
                        nn.Conv3d(interval_channels, 2, 1),
                    ),
                }
            )
            nn.init.zeros_(self.interval_refiner["mixer"][-1].weight)
            nn.init.zeros_(self.interval_refiner["mixer"][-1].bias)
        else:
            joint_channels = 16
            self.joint_head = nn.Sequential(
                nn.GroupNorm(1, joint_channels),
                nn.Conv2d(joint_channels, base_channels, 3, padding=1),
                nn.GELU(),
                nn.Conv2d(base_channels, base_channels, 3, padding=1),
                nn.GELU(),
                nn.Conv2d(base_channels, 6, 3, padding=1),
            )
            nn.init.zeros_(self.joint_head[-1].weight)
            nn.init.zeros_(self.joint_head[-1].bias)

    def forward_components(self, cond_stack: torch.Tensor) -> dict[str, torch.Tensor]:
        batch, offsets, channels, height, width = cond_stack.shape
        if offsets != 3 or channels != self.input_channels:
            raise ValueError("MA3J expects cond_stack shape (B, 3, 13, H, W)")
        flat = cond_stack.reshape(batch * offsets, channels, height, width)
        single_parts = self.single.forward_components(flat)
        base = single_parts["prediction"].reshape(batch, offsets, 1, height, width)
        coarse = cond_stack[:, :, 4]
        phase = cond_stack[:, :, 5]
        if self.interval_refine:
            selected = flat[:, [1, 2, 4, 5, 6, 7, 10, 11, 12]]
            encoded = self.interval_refiner["encoder"](torch.cat([single_parts["prediction"], selected], dim=1))
            low_h, low_w = encoded.shape[-2:]
            encoded = encoded.reshape(batch, offsets, encoded.shape[1], low_h, low_w).permute(0, 2, 1, 3, 4)
            joint = self.interval_refiner["mixer"](encoded)
            joint = joint.permute(0, 2, 1, 3, 4).reshape(batch * offsets, 2, low_h, low_w)
            joint = F.interpolate(joint, size=(height, width), mode="bilinear", align_corners=False)
            joint = joint.reshape(batch, offsets, 2, height, width)
            correction = torch.tanh(joint[:, :, 0:1])
            joint_confidence = torch.sigmoid(joint[:, :, 1:2])
            prediction = base + joint_confidence * self.joint_scale * correction
            return {
                "prediction": prediction,
                "base_prediction": base,
                "joint_correction": correction,
                "joint_confidence": joint_confidence,
                "confidence": single_parts["confidence"].reshape(batch, offsets, 1, height, width),
                "gate": single_parts["gate"].reshape(batch, offsets, 5, height, width),
            }
        left = cond_stack[:, 0, 1:2]
        right = cond_stack[:, 0, 2:3]
        prev_anchor = cond_stack[:, 0, 0:1]
        next_anchor = cond_stack[:, 0, 3:4]
        diff = cond_stack[:, 0, 6:7]
        absdiff = cond_stack[:, 0, 7:8]
        curvature = cond_stack[:, 0, 12:13]
        joint_input = torch.cat(
            [
                base.squeeze(2),
                coarse,
                phase,
                left,
                right,
                prev_anchor,
                next_anchor,
                diff,
                absdiff,
                curvature,
            ],
            dim=1,
        )
        joint = self.joint_head(joint_input)
        correction = torch.tanh(joint[:, 0:3]).unsqueeze(2)
        joint_confidence = torch.sigmoid(joint[:, 3:6]).unsqueeze(2)
        prediction = base + joint_confidence * self.joint_scale * correction
        return {
            "prediction": prediction,
            "base_prediction": base,
            "joint_correction": correction,
            "joint_confidence": joint_confidence,
            "confidence": single_parts["confidence"].reshape(batch, offsets, 1, height, width),
            "gate": single_parts["gate"].reshape(batch, offsets, 5, height, width),
        }

    def forward(self, cond_stack: torch.Tensor) -> torch.Tensor:
        return self.forward_components(cond_stack)["prediction"]
