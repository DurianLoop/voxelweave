from __future__ import annotations

import copy
import math
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from skimage.transform import resize
from torch.utils.data import DataLoader
from tqdm import tqdm

from ixi_diffusion.common import ensure_dir, load_nifti, normalize_volume, save_nifti, write_csv, write_json
from ixi_pastnet_2p5d.model import PASTNet2p5D
from ixi_pastnet_2p5d.train import _autocast_enabled, _batch_loss, _charbonnier, _gradient_loss, _make_model as _make_v1_model

from .data import (
    MA4_MISSING_OFFSETS,
    FastMRIMA3CIntervalDataset,
    FastMRIMA4WindowInterpolationDataset,
    FastMRISingleSliceInterpolationDataset,
    build_ma4_window_sample,
)
from .model_ma import PASTNetMultiAnchor2p5D
from .model_ma3j import PASTNetMA3Joint2p5D
from .model_ma4 import PASTNetMA4Window2p5D
from .settings import DATASET_NAME, Profile, RunPaths


MA3_SINGLE_VARIANTS = {"ma3", "ma3af", "ma3ms", "ma3afms"}
MA3_JOINT_VARIANTS = {"ma3j", "ma3ir"}
RICH_MULTI_ANCHOR_VARIANTS = {"ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg", *MA3_JOINT_VARIANTS}


class ModelEMA:
    def __init__(self, model: nn.Module, decay: float):
        self.module = copy.deepcopy(model).eval()
        self.decay = float(decay)
        self.updates = 0
        for param in self.module.parameters():
            param.requires_grad = False

    @torch.no_grad()
    def update(self, model: nn.Module) -> None:
        self.updates += 1
        decay = min(self.decay, (1.0 + self.updates) / (10.0 + self.updates))
        source = model.state_dict()
        for name, value in self.module.state_dict().items():
            current = source[name].detach()
            if value.is_floating_point():
                value.mul_(decay).add_(current, alpha=1.0 - decay)
            else:
                value.copy_(current)


def _is_window_profile(profile: Profile) -> bool:
    return profile.model_variant == "ma4w"


def _is_ma3c_profile(profile: Profile) -> bool:
    return profile.model_variant in {"ma3c", "ma3cg", *MA3_JOINT_VARIANTS}


def _is_multi_anchor(profile: Profile) -> bool:
    return profile.model_variant in {"ma", *RICH_MULTI_ANCHOR_VARIANTS}


def _multi_anchor_input_channels(profile: Profile) -> int:
    return 13 if profile.model_variant in RICH_MULTI_ANCHOR_VARIANTS else 10


def _multi_anchor_feature_mode(profile: Profile) -> str:
    return "rich" if profile.model_variant in RICH_MULTI_ANCHOR_VARIANTS else "basic"


def _make_model_for_profile(profile: Profile, device: torch.device) -> nn.Module:
    if _is_window_profile(profile):
        model = PASTNetMA4Window2p5D(
            input_channels=22,
            output_channels=len(MA4_MISSING_OFFSETS),
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
        ).to(device)
    elif profile.model_variant in MA3_JOINT_VARIANTS:
        model = PASTNetMA3Joint2p5D(
            input_channels=13,
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
            temporal_refine=True,
            refine_scale=profile.refine_scale,
            joint_scale=profile.joint_scale,
            anchor_reliability=profile.anchor_reliability,
            context_blocks=profile.context_blocks,
            interval_refine=profile.model_variant == "ma3ir",
        ).to(device)
    elif _is_multi_anchor(profile):
        model = PASTNetMultiAnchor2p5D(
            input_channels=_multi_anchor_input_channels(profile),
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
            temporal_refine=profile.model_variant in {*MA3_SINGLE_VARIANTS, "ma3c", "ma3cg"},
            refine_scale=profile.refine_scale,
            anchor_reliability=profile.anchor_reliability,
            context_blocks=profile.context_blocks,
        ).to(device)
    else:
        model = _make_v1_model(profile, device)
    if device.type == "cuda" and profile.model_variant not in MA3_JOINT_VARIANTS:
        model = model.to(memory_format=torch.channels_last)
    return model


def _trainable_parameters_for_profile(model: nn.Module, profile: Profile) -> list[nn.Parameter]:
    if not profile.freeze_backbone:
        return [p for p in model.parameters() if p.requires_grad]
    allowed = ("joint_head.", "interval_refiner.") if profile.model_variant in MA3_JOINT_VARIANTS else ("gate.", "decoder.", "detail_refiner.")
    trainable: list[nn.Parameter] = []
    frozen = 0
    for name, param in model.named_parameters():
        param.requires_grad = name.startswith(allowed)
        if param.requires_grad:
            trainable.append(param)
        else:
            frozen += param.numel()
    if not trainable:
        raise RuntimeError(f"profile {profile.name} freeze_backbone=True left no trainable parameters")
    trainable_count = sum(p.numel() for p in trainable)
    print(
        f"MA3 guarded calibration: trainable_params={trainable_count:,}, "
        f"frozen_params={frozen:,}, trainable_scope={','.join(allowed)}"
    )
    return trainable


def _parameter_role(name: str) -> str:
    adapter_tokens = (
        "reliability_gate.",
        "context.",
        "interval_refiner.",
        "joint_head.",
    )
    if any(token in name for token in adapter_tokens):
        return "adapter"
    head_tokens = ("gate.", "decoder.", "detail_refiner.")
    if any(token in name for token in head_tokens):
        return "head"
    return "backbone"


def _build_optimizer(model: nn.Module, profile: Profile) -> torch.optim.Optimizer:
    role_scales = {
        "backbone": profile.backbone_lr_scale,
        "head": profile.head_lr_scale,
        "adapter": profile.adapter_lr_scale,
    }
    grouped: dict[tuple[str, bool], list[nn.Parameter]] = {}
    counts = {"backbone": 0, "head": 0, "adapter": 0}
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        role = _parameter_role(name)
        use_decay = param.ndim >= 2 and not name.endswith("bias") and "norm" not in name.lower()
        grouped.setdefault((role, use_decay), []).append(param)
        counts[role] += param.numel()
    if not grouped:
        raise RuntimeError(f"profile {profile.name} left no trainable optimizer parameters")

    param_groups = []
    for (role, use_decay), params in grouped.items():
        role_lr = profile.lr * role_scales[role]
        param_groups.append(
            {
                "params": params,
                "lr": role_lr,
                "base_lr": role_lr,
                "weight_decay": profile.weight_decay if use_decay else 0.0,
                "role": role,
            }
        )
    kwargs = {
        "betas": profile.optimizer_betas,
        "eps": profile.optimizer_eps,
        "weight_decay": 0.0,
    }
    optimizer_name = profile.optimizer_name.lower()
    if optimizer_name == "adamw":
        optimizer = torch.optim.AdamW(param_groups, **kwargs)
    elif optimizer_name == "radam":
        optimizer = torch.optim.RAdam(param_groups, decoupled_weight_decay=True, **kwargs)
    else:
        raise ValueError(f"Unsupported optimizer_name={profile.optimizer_name!r}")
    print(
        f"Optimizer={optimizer.__class__.__name__}, betas={profile.optimizer_betas}, "
        f"weight_decay={profile.weight_decay:g}, params(backbone/head/adapter)="
        f"{counts['backbone']:,}/{counts['head']:,}/{counts['adapter']:,}"
    )
    return optimizer


def _set_epoch_learning_rates(optimizer: torch.optim.Optimizer, profile: Profile, epoch: int) -> None:
    if profile.scheduler_name != "warmup_cosine":
        return
    if profile.warmup_epochs > 0 and epoch < profile.warmup_epochs:
        factor = float(epoch + 1) / float(profile.warmup_epochs)
    else:
        decay_epochs = max(1, profile.epochs - profile.warmup_epochs - 1)
        progress = min(1.0, max(0.0, (epoch - profile.warmup_epochs) / decay_epochs))
        cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
        factor = profile.min_lr_ratio + (1.0 - profile.min_lr_ratio) * cosine
    for group in optimizer.param_groups:
        role = str(group.get("role", "backbone"))
        active = not (epoch < profile.adapter_only_epochs and role != "adapter")
        group["lr"] = float(group["base_lr"]) * factor if active else 0.0


def _role_learning_rate(optimizer: torch.optim.Optimizer, role: str) -> float:
    values = [float(group["lr"]) for group in optimizer.param_groups if group.get("role") == role]
    return max(values, default=0.0)


def _make_teacher_model(profile: Profile, device: torch.device) -> nn.Module | None:
    if profile.lambda_teacher <= 0:
        return None
    if profile.init_checkpoint is None:
        raise ValueError(f"profile {profile.name} uses lambda_teacher but has no init_checkpoint")
    payload = torch.load(profile.init_checkpoint, map_location=device)
    payload_variant = str(payload.get("model_variant", "v1"))
    if profile.model_variant in MA3_JOINT_VARIANTS and payload_variant == "ma3":
        teacher = PASTNetMultiAnchor2p5D(
            input_channels=13,
            base_channels=profile.base_channels,
            num_blocks=profile.num_blocks,
            window_size=profile.window_size,
            mlp_ratio=profile.mlp_ratio,
            residual_scale=profile.residual_scale,
            temporal_refine=True,
            refine_scale=profile.refine_scale,
        ).to(device)
    else:
        teacher = _make_model_for_profile(profile, device)
    teacher.load_state_dict(payload["model_state_dict"])
    teacher.eval()
    for param in teacher.parameters():
        param.requires_grad = False
    print(
        f"Teacher trust-region enabled: checkpoint={profile.init_checkpoint}, "
        f"lambda_teacher={profile.lambda_teacher:g}"
    )
    return teacher


def _reverse_multi_anchor_input(cond: torch.Tensor) -> torch.Tensor:
    prev = cond[:, 0:1]
    left = cond[:, 1:2]
    right = cond[:, 2:3]
    next_ = cond[:, 3:4]
    coarse = cond[:, 4:5]
    phase = cond[:, 5:6]
    diff = cond[:, 6:7]
    absdiff = cond[:, 7:8]
    prev_valid = cond[:, 8:9]
    next_valid = cond[:, 9:10]
    channels = [
        next_,
        right,
        left,
        prev,
        coarse,
        1.0 - phase,
        -diff,
        absdiff,
        next_valid,
        prev_valid,
    ]
    if cond.shape[1] == 13:
        prev_delta = cond[:, 10:11]
        next_delta = cond[:, 11:12]
        curvature = cond[:, 12:13]
        channels.extend([-next_delta, -prev_delta, curvature])
    return torch.cat(
        channels,
        dim=1,
    )


def _load_compatible_state_dict(model: nn.Module, source_state: dict[str, torch.Tensor]) -> dict[str, object]:
    target_state = model.state_dict()
    compatible = {
        key: value
        for key, value in source_state.items()
        if key in target_state and tuple(value.shape) == tuple(target_state[key].shape)
    }
    missing_keys = [key for key in target_state if key not in compatible]
    unexpected_keys = [key for key in source_state if key not in target_state]
    model.load_state_dict(compatible, strict=False)
    return {
        "loaded": len(compatible),
        "missing": len(missing_keys),
        "unexpected": len(unexpected_keys),
        "missing_keys": missing_keys,
        "unexpected_keys": unexpected_keys,
    }


def _assemble_ma4_window(anchor_window: torch.Tensor, missing: torch.Tensor) -> torch.Tensor:
    batch, _, h, w = missing.shape
    out = missing.new_zeros((batch, 13, h, w))
    for anchor_idx, offset in enumerate((0, 4, 8, 12)):
        out[:, offset] = anchor_window[:, anchor_idx]
    for missing_idx, offset in enumerate(MA4_MISSING_OFFSETS):
        out[:, offset] = missing[:, missing_idx]
    return out


def _z_curvature_loss(recon_window: torch.Tensor, target_window: torch.Tensor) -> torch.Tensor:
    recon_curv = recon_window[:, 2:] - 2.0 * recon_window[:, 1:-1] + recon_window[:, :-2]
    target_curv = target_window[:, 2:] - 2.0 * target_window[:, 1:-1] + target_window[:, :-2]
    return F.l1_loss(recon_curv, target_curv)


def _assemble_ma3c_interval_window(anchor_pair: torch.Tensor, missing: torch.Tensor) -> torch.Tensor:
    left = anchor_pair[:, 0]
    right = anchor_pair[:, 1]
    return torch.cat([left, missing[:, 0], missing[:, 1], missing[:, 2], right], dim=1)


def _batch_loss_ma3c(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    profile: Profile,
    device: torch.device,
    teacher_model: nn.Module | None = None,
) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond_ma_stack"].to(device, non_blocking=True)
    coarse = batch["coarse_stack"].to(device, non_blocking=True)
    target = batch["target_stack"].to(device, non_blocking=True)
    anchor_pair = batch["anchor_pair"].to(device, non_blocking=True)
    batch_size, offsets, channels, height, width = cond.shape
    flat_cond = cond.reshape(batch_size * offsets, channels, height, width)
    flat_coarse = coarse.reshape(batch_size * offsets, 1, height, width)
    flat_target = target.reshape(batch_size * offsets, 1, height, width)
    if device.type == "cuda":
        flat_cond = flat_cond.contiguous(memory_format=torch.channels_last)
        flat_coarse = flat_coarse.contiguous(memory_format=torch.channels_last)
        flat_target = flat_target.contiguous(memory_format=torch.channels_last)

    out = model.forward_components(flat_cond)
    flat_recon = out["prediction"].clamp(0.0, 1.0)
    recon = flat_recon.reshape(batch_size, offsets, 1, height, width)
    charb = _charbonnier(flat_recon, flat_target)
    mse = F.mse_loss(flat_recon, flat_target)
    grad = _gradient_loss(flat_recon, flat_target)
    edge = _laplacian_loss(flat_recon, flat_target)
    res = F.l1_loss(flat_recon, flat_coarse)
    teacher = flat_recon.new_tensor(0.0)
    if teacher_model is not None and profile.lambda_teacher > 0:
        with torch.no_grad():
            teacher_pred = teacher_model(flat_cond).clamp(0.0, 1.0)
        teacher = F.l1_loss(flat_recon, teacher_pred)
    sym = flat_recon.new_tensor(0.0)
    if profile.lambda_sym > 0:
        reverse = model(_reverse_multi_anchor_input(flat_cond)).clamp(0.0, 1.0)
        sym = F.l1_loss(flat_recon, reverse)
    recon_window = _assemble_ma3c_interval_window(anchor_pair, recon)
    target_window = _assemble_ma3c_interval_window(anchor_pair, target)
    z_smooth = _z_curvature_loss(recon_window, target_window)
    loss = (
        charb
        + profile.lambda_mse * mse
        + profile.lambda_grad * grad
        + profile.lambda_res * res
        + profile.lambda_sym * sym
        + profile.lambda_edge * edge
        + profile.lambda_z * z_smooth
        + profile.lambda_teacher * teacher
    )
    gate = out["gate"].detach()
    return loss, {
        "charbonnier": float(charb.detach().item()),
        "mse": float(mse.detach().item()),
        "gradient": float(grad.detach().item()),
        "edge": float(edge.detach().item()),
        "residual_reg": float(res.detach().item()),
        "symmetry": float(sym.detach().item()),
        "z_smooth": float(z_smooth.detach().item()),
        "teacher": float(teacher.detach().item()),
        "confidence_mean": float(out["confidence"].detach().mean().item()),
        "gate_prev": float(gate[:, 0].mean().item()),
        "gate_left": float(gate[:, 1].mean().item()),
        "gate_right": float(gate[:, 2].mean().item()),
        "gate_next": float(gate[:, 3].mean().item()),
        "gate_coarse": float(gate[:, 4].mean().item()),
    }


def _batch_loss_ma3j(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    profile: Profile,
    device: torch.device,
    teacher_model: nn.Module | None = None,
) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond_ma_stack"].to(device, non_blocking=True)
    coarse = batch["coarse_stack"].to(device, non_blocking=True)
    target = batch["target_stack"].to(device, non_blocking=True)
    anchor_pair = batch["anchor_pair"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous()
        coarse = coarse.contiguous()
        target = target.contiguous()

    out = model.forward_components(cond)
    recon = out["prediction"].clamp(0.0, 1.0)
    base = out["base_prediction"].detach().clamp(0.0, 1.0)
    flat_recon = recon.reshape(-1, 1, recon.shape[-2], recon.shape[-1])
    flat_target = target.reshape(-1, 1, target.shape[-2], target.shape[-1])
    flat_coarse = coarse.reshape(-1, 1, coarse.shape[-2], coarse.shape[-1])
    charb = _charbonnier(flat_recon, flat_target)
    mse = F.mse_loss(flat_recon, flat_target)
    grad = _gradient_loss(flat_recon, flat_target)
    edge = _laplacian_loss(flat_recon, flat_target)
    res = F.l1_loss(flat_recon, flat_coarse)
    teacher = flat_recon.new_tensor(0.0)
    if teacher_model is not None and profile.lambda_teacher > 0:
        batch_size, offsets, channels, height, width = cond.shape
        with torch.no_grad():
            if isinstance(teacher_model, PASTNetMA3Joint2p5D):
                teacher_pred = teacher_model(cond).clamp(0.0, 1.0)
            else:
                flat_cond = cond.reshape(batch_size * offsets, channels, height, width)
                teacher_pred = teacher_model(flat_cond).reshape(batch_size, offsets, 1, height, width).clamp(0.0, 1.0)
        teacher = F.l1_loss(recon, teacher_pred)
    sym = flat_recon.new_tensor(0.0)
    if profile.lambda_sym > 0:
        flipped_cond = _reverse_multi_anchor_input(cond.reshape(-1, cond.shape[2], cond.shape[3], cond.shape[4]))
        flipped_cond = flipped_cond.reshape(cond.shape)
        reverse = torch.flip(model(flipped_cond).clamp(0.0, 1.0), dims=(1,))
        sym = F.l1_loss(recon, reverse)
    recon_window = _assemble_ma3c_interval_window(anchor_pair, recon)
    target_window = _assemble_ma3c_interval_window(anchor_pair, target)
    z_smooth = _z_curvature_loss(recon_window, target_window)
    base_guard = F.l1_loss(recon, base)
    loss = (
        charb
        + profile.lambda_mse * mse
        + profile.lambda_grad * grad
        + profile.lambda_res * res
        + profile.lambda_sym * sym
        + profile.lambda_edge * edge
        + profile.lambda_z * z_smooth
        + profile.lambda_teacher * teacher
        + 0.02 * base_guard
    )
    return loss, {
        "charbonnier": float(charb.detach().item()),
        "mse": float(mse.detach().item()),
        "gradient": float(grad.detach().item()),
        "edge": float(edge.detach().item()),
        "residual_reg": float(res.detach().item()),
        "symmetry": float(sym.detach().item()),
        "z_smooth": float(z_smooth.detach().item()),
        "teacher": float(teacher.detach().item()),
        "confidence_mean": float(out["joint_confidence"].detach().mean().item()),
        "gate_prev": float(out["gate"][:, :, 0].detach().mean().item()),
        "gate_left": float(out["gate"][:, :, 1].detach().mean().item()),
        "gate_right": float(out["gate"][:, :, 2].detach().mean().item()),
        "gate_next": float(out["gate"][:, :, 3].detach().mean().item()),
        "gate_coarse": float(out["gate"][:, :, 4].detach().mean().item()),
    }


def _batch_loss_window(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    profile: Profile,
    device: torch.device,
) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond_window"].to(device, non_blocking=True)
    coarse = batch["coarse_missing"].to(device, non_blocking=True)
    target = batch["target_missing"].to(device, non_blocking=True)
    anchors = batch["anchor_window"].to(device, non_blocking=True)
    target_window = batch["target_window"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)

    out = model.forward_components(cond)
    recon = out["prediction"].clamp(0.0, 1.0)
    charb = _charbonnier(recon, target)
    mse = F.mse_loss(recon, target)
    grad = _gradient_loss(recon, target)
    edge = _laplacian_loss(recon, target)
    res = F.l1_loss(recon, coarse)
    z_smooth = _z_curvature_loss(_assemble_ma4_window(anchors, recon), target_window)
    loss = (
        charb
        + profile.lambda_mse * mse
        + profile.lambda_grad * grad
        + profile.lambda_res * res
        + profile.lambda_edge * edge
        + profile.lambda_z * z_smooth
    )
    return loss, {
        "charbonnier": float(charb.detach().item()),
        "mse": float(mse.detach().item()),
        "gradient": float(grad.detach().item()),
        "edge": float(edge.detach().item()),
        "residual_reg": float(res.detach().item()),
        "symmetry": 0.0,
        "z_smooth": float(z_smooth.detach().item()),
        "confidence_mean": float(out["confidence"].detach().mean().item()),
    }


def _batch_loss_ma(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    profile: Profile,
    device: torch.device,
) -> tuple[torch.Tensor, dict[str, float]]:
    cond = batch["cond_ma"].to(device, non_blocking=True)
    coarse = batch["coarse"].to(device, non_blocking=True)
    target = batch["target"].to(device, non_blocking=True)
    if device.type == "cuda":
        cond = cond.contiguous(memory_format=torch.channels_last)
        coarse = coarse.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)

    out = model.forward_components(cond)
    recon = out["prediction"].clamp(0.0, 1.0)
    charb = _charbonnier(recon, target)
    mse = F.mse_loss(recon, target)
    grad = _gradient_loss(recon, target)
    edge = _laplacian_loss(recon, target)
    res = F.l1_loss(recon, coarse)
    sym = recon.new_tensor(0.0)
    if profile.lambda_sym > 0:
        reverse = model(_reverse_multi_anchor_input(cond)).clamp(0.0, 1.0)
        sym = F.l1_loss(recon, reverse)
    loss = (
        charb
        + profile.lambda_mse * mse
        + profile.lambda_grad * grad
        + profile.lambda_res * res
        + profile.lambda_sym * sym
        + profile.lambda_edge * edge
    )
    gate = out["gate"].detach()
    return loss, {
        "charbonnier": float(charb.detach().item()),
        "mse": float(mse.detach().item()),
        "gradient": float(grad.detach().item()),
        "edge": float(edge.detach().item()),
        "residual_reg": float(res.detach().item()),
        "symmetry": float(sym.detach().item()),
        "confidence_mean": float(out["confidence"].detach().mean().item()),
        "gate_prev": float(gate[:, 0].mean().item()),
        "gate_left": float(gate[:, 1].mean().item()),
        "gate_right": float(gate[:, 2].mean().item()),
        "gate_next": float(gate[:, 3].mean().item()),
        "gate_coarse": float(gate[:, 4].mean().item()),
    }


def _batch_loss_for_profile(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    profile: Profile,
    device: torch.device,
    teacher_model: nn.Module | None = None,
) -> tuple[torch.Tensor, dict[str, float]]:
    if profile.model_variant in MA3_JOINT_VARIANTS:
        return _batch_loss_ma3j(model, batch, profile, device, teacher_model)
    if _is_ma3c_profile(profile):
        return _batch_loss_ma3c(model, batch, profile, device, teacher_model)
    if _is_window_profile(profile):
        return _batch_loss_window(model, batch, profile, device)
    if _is_multi_anchor(profile):
        return _batch_loss_ma(model, batch, profile, device)
    return _batch_loss(model, batch, profile, device)


def _laplacian_loss(recon: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    kernel = recon.new_tensor(
        [[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]]
    ).view(1, 1, 3, 3).repeat(recon.shape[1], 1, 1, 1)
    recon_lap = F.conv2d(recon, kernel, padding=1, groups=recon.shape[1])
    target_lap = F.conv2d(target, kernel, padding=1, groups=target.shape[1])
    return F.l1_loss(recon_lap, target_lap)


def train_pastnet(paths: RunPaths, profile: Profile) -> Path:
    best_path = paths.checkpoints / "pastnet_epoch_best.pth"
    if profile.skip_training_if_checkpoint_exists and best_path.exists():
        return best_path

    ensure_dir(paths.checkpoints)
    if _is_ma3c_profile(profile):
        train_ds = FastMRIMA3CIntervalDataset(
            "train",
            profile.stride,
            profile.train_cases,
            profile.target_shape,
            window_step=profile.window_step,
        )
        val_ds = FastMRIMA3CIntervalDataset(
            "val",
            profile.stride,
            profile.val_cases,
            profile.target_shape,
            window_step=profile.window_step,
        )
    elif _is_window_profile(profile):
        train_ds = FastMRIMA4WindowInterpolationDataset(
            "train",
            profile.stride,
            profile.train_cases,
            profile.target_shape,
            window_step=profile.window_step,
        )
        val_ds = FastMRIMA4WindowInterpolationDataset(
            "val",
            profile.stride,
            profile.val_cases,
            profile.target_shape,
            window_step=profile.window_step,
        )
    else:
        train_ds = FastMRISingleSliceInterpolationDataset(
            "train",
            profile.stride,
            profile.train_cases,
            profile.target_shape,
            multi_anchor=_is_multi_anchor(profile),
            anchor_features=_multi_anchor_feature_mode(profile),
        )
        val_ds = FastMRISingleSliceInterpolationDataset(
            "val",
            profile.stride,
            profile.val_cases,
            profile.target_shape,
            multi_anchor=_is_multi_anchor(profile),
            anchor_features=_multi_anchor_feature_mode(profile),
        )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    train_loader = DataLoader(
        train_ds,
        batch_size=profile.batch_size,
        shuffle=True,
        num_workers=profile.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=profile.num_workers > 0,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=profile.batch_size,
        shuffle=False,
        num_workers=profile.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=profile.num_workers > 0,
    )

    model = _make_model_for_profile(profile, device)
    warm_start_best = float("inf")
    if profile.init_checkpoint is not None:
        if not profile.init_checkpoint.exists():
            raise FileNotFoundError(f"Warm-start checkpoint not found: {profile.init_checkpoint}")
        payload = torch.load(profile.init_checkpoint, map_location=device)
        payload_variant = str(payload.get("model_variant", "v1"))
        if payload_variant == profile.model_variant:
            model.load_state_dict(payload["model_state_dict"])
            warm_start_best = float(payload.get("best_val_loss", float("inf")))
            torch.save(_checkpoint_payload(model, profile, -1, warm_start_best), best_path)
            print(
                f"Warm-start PAST-Net from {profile.init_checkpoint} "
                f"(pretrained_epochs={profile.pretrained_epochs}, best_val={warm_start_best:.6g})"
            )
        elif profile.model_variant in {"ma3c", "ma3cg"} and payload_variant == "ma3":
            model.load_state_dict(payload["model_state_dict"])
            print(
                f"Warm-start {profile.model_variant.upper()} from MA3 checkpoint {profile.init_checkpoint}; "
                f"{profile.model_variant.upper()} validation loss will be re-measured under interval consistency."
            )
        elif profile.model_variant in MA3_JOINT_VARIANTS and payload_variant == "ma3":
            report = _load_compatible_state_dict(
                model,
                {f"single.{key}": value for key, value in payload["model_state_dict"].items()},
            )
            print(
                f"Warm-start {profile.model_variant.upper()} single-slice branch from MA3 checkpoint {profile.init_checkpoint} "
                f"(loaded={report['loaded']}, missing={report['missing']}, unexpected={report['unexpected']}); "
                f"{'3D interval refiner' if profile.model_variant == 'ma3ir' else 'joint head'} starts as zero residual."
            )
        elif profile.model_variant in {"ma3af", "ma3ms", "ma3afms"} and payload_variant == "ma3":
            report = _load_compatible_state_dict(model, payload["model_state_dict"])
            print(
                f"Warm-start {profile.model_variant.upper()} adapters from MA3 checkpoint {profile.init_checkpoint} "
                f"(loaded={report['loaded']}, missing={report['missing']}, unexpected={report['unexpected']}); "
                "new residual adapters start as no-ops."
            )
        elif profile.model_variant in MA3_SINGLE_VARIANTS and payload_variant == "ma2":
            report = _load_compatible_state_dict(model, payload["model_state_dict"])
            print(
                f"Partial warm-start MA3 from MA2 checkpoint {profile.init_checkpoint} "
                f"(loaded={report['loaded']}, missing={report['missing']}, unexpected={report['unexpected']})"
            )
        else:
            raise ValueError(
                f"Warm-start checkpoint model_variant={payload_variant!r} does not match "
                f"profile model_variant={profile.model_variant!r}"
            )
    teacher_model = _make_teacher_model(profile, device)
    trainable_params = _trainable_parameters_for_profile(model, profile)
    optimizer = _build_optimizer(model, profile)
    if profile.scheduler_name == "plateau":
        scheduler: torch.optim.lr_scheduler.ReduceLROnPlateau | None = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=0.5,
            patience=max(1, profile.patience // 3),
        )
    elif profile.scheduler_name == "warmup_cosine":
        scheduler = None
    else:
        raise ValueError(f"Unsupported scheduler_name={profile.scheduler_name!r}")
    ema = ModelEMA(model, profile.ema_decay) if profile.ema_decay > 0 else None
    scaler = torch.amp.GradScaler("cuda", enabled=_autocast_enabled(device, profile))
    rows = []
    best_val = warm_start_best
    stale = 0
    print(
        f"fastMRI-brain-T2 PAST-Net 2.5D: device={device}, profile={profile.name}, "
        f"model_variant={profile.model_variant}, "
        f"train_samples={len(train_ds)}, val_samples={len(val_ds)}, batch={profile.batch_size}, "
        f"grad_accum={profile.grad_accum_steps}, effective_batch={profile.batch_size * profile.grad_accum_steps}, "
        f"channels={profile.base_channels}, blocks={profile.num_blocks}, stride=x{profile.stride}, "
        f"scheduler={profile.scheduler_name}, warmup={profile.warmup_epochs}, "
        f"adapter_only={profile.adapter_only_epochs}, ema={profile.ema_decay:g}"
    )
    for epoch in range(profile.epochs):
        start = time.time()
        _set_epoch_learning_rates(optimizer, profile, epoch)
        model.train()
        total = 0.0
        count = 0
        skipped_nonfinite = 0
        grad_accum_steps = max(1, profile.grad_accum_steps)
        optimizer.zero_grad(set_to_none=True)
        pbar = tqdm(train_loader, desc=f"FastMRI-PASTNet-Epoch {epoch + 1}/{profile.epochs}")
        for step, batch in enumerate(pbar, start=1):
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss_for_profile(model, batch, profile, device, teacher_model)
            if not torch.isfinite(loss):
                skipped_nonfinite += 1
                optimizer.zero_grad(set_to_none=True)
                pbar.set_postfix(loss="nonfinite", skipped=skipped_nonfinite)
                continue
            scaler.scale(loss / grad_accum_steps).backward()
            if step % grad_accum_steps == 0 or step == len(train_loader):
                scaler.unscale_(optimizer)
                grad_norm = torch.nn.utils.clip_grad_norm_(trainable_params, profile.grad_clip_norm)
                if torch.isfinite(grad_norm):
                    scaler.step(optimizer)
                    if ema is not None:
                        ema.update(model)
                else:
                    skipped_nonfinite += 1
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
            total += float(loss.item())
            count += 1
            pbar.set_postfix(
                loss=f"{loss.item():.4f}",
                ch=f"{parts['charbonnier']:.4f}",
                sym=f"{parts['symmetry']:.4f}",
                conf=f"{parts['confidence_mean']:.2f}",
                lr=f"{max(float(group['lr']) for group in optimizer.param_groups):.1e}",
            )
        train_loss = total / max(count, 1) if count else float("nan")
        eval_model = ema.module if ema is not None else model
        val_loss = _validate(eval_model, val_loader, profile, device, epoch + 1, teacher_model)
        if np.isfinite(val_loss) and scheduler is not None:
            scheduler.step(val_loss)
        improved = np.isfinite(val_loss) and val_loss < best_val
        if improved:
            best_val = val_loss
            stale = 0
            torch.save(_checkpoint_payload(eval_model, profile, epoch, best_val), best_path)
        else:
            stale += 1
        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "best_val_loss": best_val,
            "lr": max(float(group["lr"]) for group in optimizer.param_groups),
            "lr_backbone": _role_learning_rate(optimizer, "backbone"),
            "lr_head": _role_learning_rate(optimizer, "head"),
            "lr_adapter": _role_learning_rate(optimizer, "adapter"),
            "seconds": time.time() - start,
            "improved": improved,
            "finite_train_batches": count,
            "skipped_nonfinite": skipped_nonfinite,
        }
        rows.append(row)
        print(
            f"fastMRI PAST-Net epoch {epoch + 1}/{profile.epochs}: train={train_loss:.4f}, "
            f"val={val_loss:.4f}, best={best_val:.4f}, lr={row['lr']:.2e}, "
            f"seconds={row['seconds']:.1f}, stale={stale}/{profile.patience}"
        )
        if stale >= profile.patience:
            print(f"Early stopping: stale={stale}")
            break

    final_model = ema.module if ema is not None else model
    torch.save(_checkpoint_payload(final_model, profile, rows[-1]["epoch"], best_val), paths.checkpoints / "pastnet_epoch_final.pth")
    write_csv(paths.run_dir / "training_history.csv", rows)
    write_json(
        paths.run_dir / "training_history.json",
        {
            "best_val_loss": best_val,
            "epochs_completed": len(rows),
            "early_stopped": stale >= profile.patience,
            "optimizer": profile.optimizer_name,
            "scheduler": profile.scheduler_name,
            "ema_decay": profile.ema_decay,
        },
    )
    return best_path


def _validate(
    model: nn.Module,
    loader: DataLoader,
    profile: Profile,
    device: torch.device,
    epoch: int,
    teacher_model: nn.Module | None = None,
) -> float:
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        pbar = tqdm(loader, desc=f"FastMRI-PASTNet-Val {epoch}", leave=False)
        for batch in pbar:
            with torch.amp.autocast(device_type=device.type, enabled=_autocast_enabled(device, profile)):
                loss, parts = _batch_loss_for_profile(model, batch, profile, device, teacher_model)
            if not torch.isfinite(loss):
                continue
            total += float(loss.item())
            count += 1
            pbar.set_postfix(loss=f"{loss.item():.4f}", ch=f"{parts['charbonnier']:.4f}", conf=f"{parts['confidence_mean']:.2f}")
    return total / max(count, 1) if count else float("nan")


def _checkpoint_payload(model: nn.Module, profile: Profile, epoch: int, best_val: float) -> dict:
    if _is_window_profile(profile):
        sampling = "pastnet_ma4_window_residual_psnr_aligned"
        condition = "4 sparse anchors + 9 linear coarse missing slices + 9 phase maps"
        input_channels = 22
    elif _is_multi_anchor(profile):
        rich = profile.model_variant in RICH_MULTI_ANCHOR_VARIANTS
        sampling = (
            "pastnet_ma3ir_lowres_3d_interval_refined_rich_phase_aware_residual"
            if profile.model_variant == "ma3ir"
            else
            "pastnet_ma3j_joint_interval_refined_rich_phase_aware_residual"
            if profile.model_variant == "ma3j"
            else
            "pastnet_ma3cg_guarded_interval_consistency_refined_rich_phase_aware_single_slice_residual"
            if profile.model_variant == "ma3cg"
            else
            "pastnet_ma3c_interval_consistency_refined_rich_phase_aware_single_slice_residual"
            if profile.model_variant == "ma3c"
            else
            "pastnet_multi_anchor_reliability_multiscale_residual"
            if profile.model_variant == "ma3afms"
            else
            "pastnet_multi_anchor_multiscale_residual"
            if profile.model_variant == "ma3ms"
            else
            "pastnet_multi_anchor_reliability_residual"
            if profile.model_variant == "ma3af"
            else
            "pastnet_multi_anchor_refined_rich_phase_aware_single_slice_residual"
            if profile.model_variant == "ma3"
            else
            "pastnet_multi_anchor_rich_phase_aware_single_slice_residual"
            if rich
            else "pastnet_multi_anchor_phase_aware_single_slice_residual"
        )
        condition = (
            "prev/left/right/next anchors + linear coarse + phase + directional difference "
            "+ abs difference + outer-anchor validity masks"
            + (" + outer-anchor deltas + sparse curvature" if rich else "")
            + (" + interval z-curvature consistency" if profile.model_variant in {"ma3c", "ma3cg", *MA3_JOINT_VARIANTS} else "")
            + (" + low-resolution 3D interval residual refiner" if profile.model_variant == "ma3ir" else "")
            + (" + joint three-offset residual head" if profile.model_variant == "ma3j" else "")
            + (" + frozen-backbone teacher trust region" if profile.model_variant == "ma3cg" else "")
            + (" + MSE PSNR tuning" if profile.lambda_mse > 0 else "")
        )
        input_channels = _multi_anchor_input_channels(profile)
    else:
        sampling = "pastnet_phase_aware_single_slice_residual"
        condition = "left/right anchors + linear coarse + phase + directional difference + abs difference"
        input_channels = 6
    return {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "best_val_loss": best_val,
        "model_variant": profile.model_variant,
        "dataset": DATASET_NAME,
        "modality": "T2",
        "stride": profile.stride,
        "target_shape": profile.target_shape,
        "amp": profile.amp,
        "sampling": sampling,
        "condition": condition,
        "batch_size": profile.batch_size,
        "grad_accum_steps": profile.grad_accum_steps,
        "effective_batch_size": profile.batch_size * profile.grad_accum_steps,
        "optimization": {
            "optimizer": profile.optimizer_name,
            "betas": profile.optimizer_betas,
            "eps": profile.optimizer_eps,
            "scheduler": profile.scheduler_name,
            "warmup_epochs": profile.warmup_epochs,
            "min_lr_ratio": profile.min_lr_ratio,
            "base_lr": profile.lr,
            "backbone_lr_scale": profile.backbone_lr_scale,
            "head_lr_scale": profile.head_lr_scale,
            "adapter_lr_scale": profile.adapter_lr_scale,
            "adapter_only_epochs": profile.adapter_only_epochs,
            "weight_decay": profile.weight_decay,
            "ema_decay": profile.ema_decay,
            "grad_clip_norm": profile.grad_clip_norm,
        },
        "init_checkpoint": str(profile.init_checkpoint) if profile.init_checkpoint is not None else None,
        "pretrained_epochs": profile.pretrained_epochs,
        "total_epoch_budget": profile.pretrained_epochs + profile.epochs,
        "loss": {
            "charbonnier": 1.0,
            "mse": profile.lambda_mse,
            "gradient": profile.lambda_grad,
            "residual_regularization": profile.lambda_res,
            "symmetry": profile.lambda_sym,
            "edge": profile.lambda_edge,
            "z_smooth": profile.lambda_z,
            "teacher": profile.lambda_teacher,
            "joint_base_guard": 0.02 if profile.model_variant in MA3_JOINT_VARIANTS else 0.0,
        },
        "freeze_backbone": profile.freeze_backbone,
        "model_config": {
            "input_channels": input_channels,
            **({"output_channels": len(MA4_MISSING_OFFSETS)} if _is_window_profile(profile) else {}),
            "base_channels": profile.base_channels,
            "num_blocks": profile.num_blocks,
            "window_size": profile.window_size,
            "mlp_ratio": profile.mlp_ratio,
            "residual_scale": profile.residual_scale,
            **(
                {}
                if _is_window_profile(profile) or not _is_multi_anchor(profile)
                else {
                    "temporal_refine": profile.model_variant in {*MA3_SINGLE_VARIANTS, "ma3c", "ma3cg", *MA3_JOINT_VARIANTS},
                    "refine_scale": profile.refine_scale,
                    **(
                        {
                            "anchor_reliability": profile.anchor_reliability,
                            "context_blocks": profile.context_blocks,
                        }
                        if profile.model_variant not in MA3_JOINT_VARIANTS
                        else {}
                    ),
                    **(
                        {
                            "joint_scale": profile.joint_scale,
                            "anchor_reliability": profile.anchor_reliability,
                            "context_blocks": profile.context_blocks,
                            "interval_refine": profile.model_variant == "ma3ir",
                        }
                        if profile.model_variant in MA3_JOINT_VARIANTS
                        else {}
                    ),
                }
            ),
        },
    }


class FastMRIPASTNet2p5DInterpolator:
    def __init__(self, checkpoint: Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        payload = torch.load(checkpoint, map_location=self.device)
        config = payload.get("model_config", {})
        self.model_variant = str(payload.get("model_variant", "v1"))
        if self.model_variant == "ma4w":
            self.model = PASTNetMA4Window2p5D(**config).to(self.device)
        elif self.model_variant in MA3_JOINT_VARIANTS:
            self.model = PASTNetMA3Joint2p5D(**config).to(self.device)
        elif self.model_variant in {"ma", "ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg"}:
            self.model = PASTNetMultiAnchor2p5D(**config).to(self.device)
        else:
            self.model = PASTNet2p5D(**config).to(self.device)
        self.model.load_state_dict(payload["model_state_dict"])
        self.model.eval()
        self.input_size = tuple(payload.get("target_shape", (256, 256)))
        self.amp = bool(payload.get("amp", True))

    def _predict_slice(self, cond_np: np.ndarray) -> np.ndarray:
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
                pred = self.model(cond).float().clamp(0.0, 1.0)
        return pred.squeeze(0).squeeze(0).cpu().numpy()

    def _predict_window(self, cond_np: np.ndarray) -> np.ndarray:
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
                pred = self.model(cond).float().clamp(0.0, 1.0)
        return pred.squeeze(0).cpu().numpy()

    def _predict_joint_interval(self, cond_np: np.ndarray) -> np.ndarray:
        cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(self.device)
        with torch.no_grad():
            with torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda" and self.amp):
                pred = self.model(cond).float().clamp(0.0, 1.0)
        return pred.squeeze(0).squeeze(1).cpu().numpy()

    def _ma4_condition_from_anchors(self, anchors: list[np.ndarray], stride: int) -> np.ndarray:
        coarse_missing: list[np.ndarray] = []
        phase_maps: list[np.ndarray] = []
        for offset in MA4_MISSING_OFFSETS:
            segment = offset // stride
            rel = float(offset - segment * stride) / float(stride)
            coarse_missing.append(((1.0 - rel) * anchors[segment] + rel * anchors[segment + 1]).astype(np.float32))
            phase_maps.append(np.full(self.input_size, rel, dtype=np.float32))
        return np.concatenate(
            [
                np.stack(anchors, axis=0).astype(np.float32),
                np.stack(coarse_missing, axis=0).astype(np.float32),
                np.stack(phase_maps, axis=0).astype(np.float32),
            ],
            axis=0,
        )

    def _interpolate_volume_ma4w(self, volume: np.ndarray, stride: int) -> np.ndarray:
        norm, lo, hi = normalize_volume(volume)
        out_depth = (volume.shape[2] - 1) * stride + 1
        out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        pred_acc = np.zeros_like(out)
        pred_count = np.zeros_like(out)
        for idx in range(volume.shape[2]):
            out[:, :, idx * stride] = norm[:, :, idx]
        if volume.shape[2] >= 4:
            for start in range(volume.shape[2] - 3):
                anchors = [
                    resize(norm[:, :, start + anchor_idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
                    for anchor_idx in range(4)
                ]
                pred_missing = self._predict_window(self._ma4_condition_from_anchors(anchors, stride))
                for missing_idx, offset in enumerate(MA4_MISSING_OFFSETS):
                    out_idx = start * stride + offset
                    if out_idx >= out_depth:
                        continue
                    slice_ = resize(
                        pred_missing[missing_idx],
                        volume.shape[:2],
                        preserve_range=True,
                        anti_aliasing=True,
                    ).astype(np.float32)
                    pred_acc[:, :, out_idx] += slice_
                    pred_count[:, :, out_idx] += 1.0

        for idx in range(volume.shape[2] - 1):
            left = norm[:, :, idx]
            right = norm[:, :, idx + 1]
            for offset in range(1, stride):
                out_idx = idx * stride + offset
                covered = pred_count[:, :, out_idx] > 0
                if np.any(covered):
                    out[:, :, out_idx] = pred_acc[:, :, out_idx] / np.maximum(pred_count[:, :, out_idx], 1.0)
                else:
                    rel = float(offset) / float(stride)
                    out[:, :, out_idx] = ((1.0 - rel) * left + rel * right).astype(np.float32)
        return out * (hi - lo) + lo

    def interpolate_volume(self, volume: np.ndarray, stride: int = 4) -> np.ndarray:
        if self.model_variant == "ma4w":
            return self._interpolate_volume_ma4w(volume, stride)
        norm, lo, hi = normalize_volume(volume)
        out_depth = (volume.shape[2] - 1) * stride + 1
        out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
        for idx in range(volume.shape[2]):
            out[:, :, idx * stride] = volume[:, :, idx]
        for idx in range(volume.shape[2] - 1):
            left = resize(norm[:, :, idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            right = resize(norm[:, :, idx + 1], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
            diff = (right - left).astype(np.float32)
            absdiff = np.abs(diff).astype(np.float32)
            if self.model_variant in {"ma", "ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg", *MA3_JOINT_VARIANTS}:
                prev_idx = idx - 1
                next_idx = idx + 2
                prev_valid_value = 1.0 if prev_idx >= 0 else 0.0
                next_valid_value = 1.0 if next_idx < volume.shape[2] else 0.0
                if prev_idx < 0:
                    prev_idx = idx
                if next_idx >= volume.shape[2]:
                    next_idx = idx + 1
                prev_anchor = resize(norm[:, :, prev_idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
                next_anchor = resize(norm[:, :, next_idx], self.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
                prev_valid = np.full(self.input_size, prev_valid_value, dtype=np.float32)
                next_valid = np.full(self.input_size, next_valid_value, dtype=np.float32)
            if self.model_variant in MA3_JOINT_VARIANTS:
                joint_conds = []
                for offset in range(1, stride):
                    rel = float(offset) / float(stride)
                    coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
                    phase = np.full(self.input_size, rel, dtype=np.float32)
                    prev_delta = ((left - prev_anchor) * prev_valid_value).astype(np.float32)
                    next_delta = ((next_anchor - right) * next_valid_value).astype(np.float32)
                    curvature = (next_delta - prev_delta).astype(np.float32)
                    joint_conds.append(
                        np.stack(
                            [
                                prev_anchor,
                                left,
                                right,
                                next_anchor,
                                coarse,
                                phase,
                                diff,
                                absdiff,
                                prev_valid,
                                next_valid,
                                prev_delta,
                                next_delta,
                                curvature,
                            ],
                            axis=0,
                        )
                    )
                generated_stack = self._predict_joint_interval(np.stack(joint_conds, axis=0).astype(np.float32))
                for offset, generated in enumerate(generated_stack, start=1):
                    slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                    out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
                continue
            for offset in range(1, stride):
                rel = float(offset) / float(stride)
                coarse = ((1.0 - rel) * left + rel * right).astype(np.float32)
                phase = np.full(self.input_size, rel, dtype=np.float32)
                if self.model_variant in {"ma", "ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg"}:
                    channels = [prev_anchor, left, right, next_anchor, coarse, phase, diff, absdiff, prev_valid, next_valid]
                    if self.model_variant in {"ma2", *MA3_SINGLE_VARIANTS, "ma3c", "ma3cg"}:
                        prev_delta = ((left - prev_anchor) * prev_valid_value).astype(np.float32)
                        next_delta = ((next_anchor - right) * next_valid_value).astype(np.float32)
                        curvature = (next_delta - prev_delta).astype(np.float32)
                        channels.extend([prev_delta, next_delta, curvature])
                    cond_np = np.stack(channels, axis=0)
                else:
                    cond_np = np.stack([left, right, coarse, phase, diff, absdiff], axis=0)
                generated = self._predict_slice(cond_np)
                slice_ = resize(generated, volume.shape[:2], preserve_range=True, anti_aliasing=True)
                out[:, :, idx * stride + offset] = slice_ * (hi - lo) + lo
        return out

    def process_folder(self, input_dir: Path, output_dir: Path, stride: int) -> int:
        ensure_dir(output_dir)
        count = 0
        for src in sorted(input_dir.glob("*.nii.gz")):
            print(f"fastMRI PAST-Net 2.5D inference: {src.name}")
            volume, affine, header = load_nifti(src)
            pred = self.interpolate_volume(volume, stride=stride)
            save_nifti(pred, affine, header, output_dir / f"diff_{src.name}")
            count += 1
        return count
