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


def z_gradient_loss(pred_stack: torch.Tensor, target_stack: torch.Tensor) -> torch.Tensor:
    return F.l1_loss(pred_stack[:, 1:] - pred_stack[:, :-1], target_stack[:, 1:] - target_stack[:, :-1])


def z_laplacian_loss(pred_stack: torch.Tensor, target_stack: torch.Tensor) -> torch.Tensor:
    pred_lap = pred_stack[:, :-2] - 2.0 * pred_stack[:, 1:-1] + pred_stack[:, 2:]
    target_lap = target_stack[:, :-2] - 2.0 * target_stack[:, 1:-1] + target_stack[:, 2:]
    return F.l1_loss(pred_lap, target_lap)


def _edge_magnitude(stack: torch.Tensor) -> torch.Tensor:
    dx, dy = gradient_xy(stack)
    dx = F.pad(dx, (0, 1, 0, 0))
    dy = F.pad(dy, (0, 0, 0, 1))
    return torch.sqrt(dx.pow(2) + dy.pow(2) + 1e-6)


def edge_z_loss(pred_stack: torch.Tensor, target_stack: torch.Tensor) -> torch.Tensor:
    pred_edge = _edge_magnitude(pred_stack)
    target_edge = _edge_magnitude(target_stack)
    return z_gradient_loss(pred_edge, target_edge)


def anatomy_weighted_l1(pred: torch.Tensor, target: torch.Tensor, coarse: torch.Tensor, absdiff: torch.Tensor) -> torch.Tensor:
    coarse_edge = _edge_magnitude(coarse).mean(dim=1, keepdim=True)
    weight = coarse_edge + absdiff
    reduce_dims = tuple(range(1, weight.ndim))
    weight = weight / weight.amax(dim=reduce_dims, keepdim=True).clamp_min(1e-6)
    weight = 1.0 + weight
    return (weight * (pred - target).abs()).mean()


def acsi_group_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    coarse: torch.Tensor,
    anchors: torch.Tensor,
    residual: torch.Tensor,
    weights: dict[str, float],
) -> tuple[torch.Tensor, dict[str, float]]:
    pred_stack = torch.cat([anchors[:, 0:1], pred, anchors[:, 1:2]], dim=1)
    target_stack = torch.cat([anchors[:, 0:1], target, anchors[:, 1:2]], dim=1)
    absdiff = (anchors[:, 1:2] - anchors[:, 0:1]).abs()

    rec = charbonnier(pred, target)
    grad_xy = gradient_xy_loss(pred, target)
    zgrad = z_gradient_loss(pred_stack, target_stack)
    zlap = z_laplacian_loss(pred_stack, target_stack)
    edge_z = edge_z_loss(pred_stack, target_stack)
    anat = anatomy_weighted_l1(pred, target, coarse, absdiff)
    res = residual.abs().mean()
    total = (
        rec
        + weights["lambda_grad_xy"] * grad_xy
        + weights["lambda_zgrad"] * zgrad
        + weights["lambda_zlap"] * zlap
        + weights["lambda_edge_z"] * edge_z
        + weights["lambda_anat"] * anat
        + weights["lambda_res"] * res
    )
    return total, {
        "rec": float(rec.detach().item()),
        "grad_xy": float(grad_xy.detach().item()),
        "zgrad": float(zgrad.detach().item()),
        "zlap": float(zlap.detach().item()),
        "edge_z": float(edge_z.detach().item()),
        "anat": float(anat.detach().item()),
        "res": float(res.detach().item()),
    }
