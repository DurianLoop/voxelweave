from __future__ import annotations

import torch
import torch.nn.functional as F


def charbonnier(pred: torch.Tensor, target: torch.Tensor, eps: float = 1e-3) -> torch.Tensor:
    return torch.sqrt((pred - target).pow(2) + eps * eps).mean()


def gradient_xy(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    dx = x[..., :, 1:] - x[..., :, :-1]
    dy = x[..., 1:, :] - x[..., :-1, :]
    return dx, dy


def gradient_xy_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pred_dx, pred_dy = gradient_xy(pred)
    target_dx, target_dy = gradient_xy(target)
    return F.l1_loss(pred_dx, target_dx) + F.l1_loss(pred_dy, target_dy)


def _normalize_per_sample(x: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    reduce_dims = tuple(range(1, x.ndim))
    lo = x.amin(dim=reduce_dims, keepdim=True)
    hi = x.amax(dim=reduce_dims, keepdim=True)
    return (x - lo) / (hi - lo).clamp_min(eps)


def heteroscedastic_l1(
    pred: torch.Tensor,
    target: torch.Tensor,
    log_variance: torch.Tensor,
    lambda_logvar: float,
) -> torch.Tensor:
    error = (pred - target).abs()
    log_variance = log_variance.clamp(-6.0, 4.0)
    return (torch.exp(-log_variance) * error + lambda_logvar * log_variance).mean()


def calibration_loss(pred: torch.Tensor, target: torch.Tensor, uncertainty: torch.Tensor) -> torch.Tensor:
    error = (pred.detach() - target.detach()).abs()
    error_norm = _normalize_per_sample(error)
    uncertainty_norm = _normalize_per_sample(uncertainty)
    return F.l1_loss(uncertainty_norm, error_norm)


def rasinet_group_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    coarse: torch.Tensor,
    residual: torch.Tensor,
    log_variance: torch.Tensor,
    uncertainty: torch.Tensor,
    weights: dict[str, float],
) -> tuple[torch.Tensor, dict[str, float]]:
    rec = charbonnier(pred, target)
    unc = heteroscedastic_l1(pred, target, log_variance, weights["lambda_logvar"])
    grad_xy = gradient_xy_loss(pred, target)
    res = F.l1_loss(pred, coarse)
    cal = calibration_loss(pred, target, uncertainty)
    residual_mag = residual.abs().mean()
    total = (
        rec
        + weights["lambda_unc"] * unc
        + weights["lambda_grad_xy"] * grad_xy
        + weights["lambda_res"] * res
        + weights["lambda_cal"] * cal
    )
    return total, {
        "rec": float(rec.detach().item()),
        "unc": float(unc.detach().item()),
        "grad_xy": float(grad_xy.detach().item()),
        "res": float(res.detach().item()),
        "cal": float(cal.detach().item()),
        "residual_mag": float(residual_mag.detach().item()),
    }
