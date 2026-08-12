from __future__ import annotations

import torch
from pytorch_msssim import ssim


def gradient_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pred_dx = pred[:, :, :, 1:] - pred[:, :, :, :-1]
    target_dx = target[:, :, :, 1:] - target[:, :, :, :-1]
    pred_dy = pred[:, :, 1:, :] - pred[:, :, :-1, :]
    target_dy = target[:, :, 1:, :] - target[:, :, :-1, :]
    return torch.mean(torch.abs(pred_dx - target_dx)) + torch.mean(torch.abs(pred_dy - target_dy))


def foreground_weight_map(target: torch.Tensor) -> torch.Tensor:
    flat = target.flatten(start_dim=2)
    threshold = torch.quantile(flat, 0.75, dim=2, keepdim=True).unsqueeze(-1)
    foreground = (target >= threshold).float()
    brightness = 1.0 + target * 2.0
    return brightness * (1.0 + foreground * 2.0)


def structural_reconstruction_loss(pred_x0: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    weighted_l1 = torch.mean(torch.abs(pred_x0 - target) * foreground_weight_map(target))
    ssim_loss = 1 - ssim(pred_x0, target, data_range=1.0, size_average=True)
    grad = gradient_loss(pred_x0, target)
    return 5.0 * weighted_l1 + 2.0 * ssim_loss + grad
