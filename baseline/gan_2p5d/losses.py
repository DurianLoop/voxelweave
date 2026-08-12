from __future__ import annotations

import torch
import torch.nn.functional as F


def gradient_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pred_dx = pred[:, :, :, 1:] - pred[:, :, :, :-1]
    tgt_dx = target[:, :, :, 1:] - target[:, :, :, :-1]
    pred_dy = pred[:, :, 1:, :] - pred[:, :, :-1, :]
    tgt_dy = target[:, :, 1:, :] - target[:, :, :-1, :]
    return F.l1_loss(pred_dx, tgt_dx) + F.l1_loss(pred_dy, tgt_dy)


def smoothness_loss(flow: torch.Tensor) -> torch.Tensor:
    dy = torch.abs(flow[:, :, 1:, :] - flow[:, :, :-1, :]).mean()
    dx = torch.abs(flow[:, :, :, 1:] - flow[:, :, :, :-1]).mean()
    return dx + dy

