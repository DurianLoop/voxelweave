from __future__ import annotations

import torch
import torch.nn.functional as F


def charbonnier_masked(pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor, eps: float = 1e-3) -> torch.Tensor:
    values = torch.sqrt((pred - target).pow(2) + eps * eps) * mask
    pixels = pred.shape[-1] * pred.shape[-2]
    return values.sum() / (mask.sum() * pixels).clamp_min(1.0)


def gradient_xy(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    dx = x[..., :, 1:] - x[..., :, :-1]
    dy = x[..., 1:, :] - x[..., :-1, :]
    return dx, dy


def gradient_xy_loss(pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    pred_dx, pred_dy = gradient_xy(pred)
    target_dx, target_dy = gradient_xy(target)
    return F.l1_loss(pred_dx * mask, target_dx * mask) + F.l1_loss(pred_dy * mask, target_dy * mask)


def z_gradient_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return F.l1_loss(pred[:, 1:] - pred[:, :-1], target[:, 1:] - target[:, :-1])


def z_laplacian_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pred_lap = pred[:, :-2] - 2.0 * pred[:, 1:-1] + pred[:, 2:]
    target_lap = target[:, :-2] - 2.0 * target[:, 1:-1] + target[:, 2:]
    return F.l1_loss(pred_lap, target_lap)


def _edge_magnitude(stack: torch.Tensor) -> torch.Tensor:
    dx, dy = gradient_xy(stack)
    dx = F.pad(dx, (0, 1, 0, 0))
    dy = F.pad(dy, (0, 0, 0, 1))
    return torch.sqrt(dx.pow(2) + dy.pow(2) + 1e-6)


def edge_z_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return z_gradient_loss(_edge_magnitude(pred), _edge_magnitude(target))


def _adjacent_ncc_profile(stack: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """Adjacent-slice Pearson NCC for every sample and z transition."""
    left = stack[:, :-1].flatten(start_dim=2)
    right = stack[:, 1:].flatten(start_dim=2)
    left = left - left.mean(dim=-1, keepdim=True)
    right = right - right.mean(dim=-1, keepdim=True)
    denominator = torch.sqrt(left.square().sum(dim=-1) * right.square().sum(dim=-1)).clamp_min(eps)
    return (left * right).sum(dim=-1) / denominator


def z_ncc_profile_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Match each reconstructed adjacent-slice NCC to its ground-truth counterpart."""
    return F.l1_loss(_adjacent_ncc_profile(pred), _adjacent_ncc_profile(target))


def anatomy_weighted_l1(pred: torch.Tensor, target: torch.Tensor, coarse: torch.Tensor, gen_mask: torch.Tensor) -> torch.Tensor:
    coarse_edge = _edge_magnitude(coarse).mean(dim=1, keepdim=True)
    target_change = (target - coarse).abs().mean(dim=1, keepdim=True)
    weight = coarse_edge + target_change
    reduce_dims = tuple(range(1, weight.ndim))
    weight = 1.0 + weight / weight.amax(dim=reduce_dims, keepdim=True).clamp_min(1e-6)
    pixels = pred.shape[-1] * pred.shape[-2]
    return (weight * (pred - target).abs() * gen_mask).sum() / (gen_mask.sum() * pixels).clamp_min(1.0)


def acsi_v2_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    coarse: torch.Tensor,
    residual: torch.Tensor,
    gen_mask_1d: torch.Tensor,
    weights: dict[str, float],
) -> tuple[torch.Tensor, dict[str, float]]:
    gen_mask = gen_mask_1d[:, :, None, None].to(pred.device)
    rec = charbonnier_masked(pred, target, gen_mask)
    grad_xy = gradient_xy_loss(pred, target, gen_mask)
    zgrad = z_gradient_loss(pred, target)
    zlap = z_laplacian_loss(pred, target)
    edge_z = edge_z_loss(pred, target)
    z_ncc = z_ncc_profile_loss(pred, target)
    anat = anatomy_weighted_l1(pred, target, coarse, gen_mask)
    res = (residual.abs() * gen_mask).sum() / gen_mask.sum().clamp_min(1.0)
    total = (
        rec
        + weights["lambda_grad_xy"] * grad_xy
        + weights["lambda_zgrad"] * zgrad
        + weights["lambda_zlap"] * zlap
        + weights["lambda_edge_z"] * edge_z
        + weights["lambda_z_ncc"] * z_ncc
        + weights["lambda_anat"] * anat
        + weights["lambda_res"] * res
    )
    return total, {
        "rec": float(rec.detach().item()),
        "grad_xy": float(grad_xy.detach().item()),
        "zgrad": float(zgrad.detach().item()),
        "zlap": float(zlap.detach().item()),
        "edge_z": float(edge_z.detach().item()),
        "z_ncc": float(z_ncc.detach().item()),
        "anat": float(anat.detach().item()),
        "res": float(res.detach().item()),
    }
