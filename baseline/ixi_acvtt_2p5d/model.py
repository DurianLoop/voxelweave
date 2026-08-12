from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import torch
import torch.nn as nn


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACVTT_ROOT = PROJECT_ROOT / "external" / "ACVTT"
if str(ACVTT_ROOT) not in sys.path:
    sys.path.insert(0, str(ACVTT_ROOT))

from models.ACVTT import ACVTT  # noqa: E402


@dataclass
class ACVTTConfig:
    num_level: int = 3
    num_channel: int = 32
    num_block: int = 1
    kernel_size: int = 3
    scale: int = 4
    patch_size: int = 256
    slide_overlap: int = 0
    long_skip: bool = True
    long_skip_feat: bool = False
    do_fusion: bool = True
    output_lr_up: bool = False
    act_first: bool = False
    cat_feat: bool = False
    use_resenc: bool = False
    use_resdec: bool = False
    act_after_res: bool = False
    num_ref_slices: int = 2
    num_ref_enc_level: int = 3
    num_ref_channel: int = 32
    num_block_ref: int = 1
    use_resenc_ref: bool = False
    act_after_res_ref: bool = False
    transfer_level: tuple[int, ...] = (0, 1, 2)
    block_size_per_level: tuple[int, ...] = (8, 4, 2)
    win_block_size_per_level: tuple[int, ...] = (2, 2, 2)
    down_op: str | None = None
    up_op: str | None = None
    down_op_ref: str | None = None
    do_norm: bool = True
    norm_type_for_attn: str = "sep_layernorm"
    layernorm_affine: bool = True
    layernorm_bias: bool = True
    norm_order: int = 1
    norm_dim: int = -2
    do_proj_qkv: bool = True
    num_block_proj_in: int = 0
    kernel_size_proj_in: int = 1
    do_proj_after_unfold: bool = False
    reduce_proj_qk_dim: bool = False
    reduce_proj_qk_by_block: bool = False
    reduce_proj_v_by_block: bool = False
    do_proj_after_norm: bool = False
    proj_after_norm_qk_only: bool = False
    do_proj_out_unfold: bool = False
    do_proj_after_attn: bool = True
    num_block_proj_out: int = 0
    kernel_size_proj_out: int = 1
    output_attention: bool = False
    attn_softmax: bool = True
    show_normalize: bool = False
    output_residual: bool = False
    get_random_test_ref: bool = False
    get_uniform_test_ref: bool = False
    shared_ref_enc: bool = True
    init_ref_enc: bool = False
    input_gt: bool = False
    use_hr_ref: bool = False
    pre_transfer: bool = False
    roll_hr_ref: bool = False
    roll_xy: tuple[int, int] = (0, 0)
    roll_xy_start: tuple[int, int] = (0, 0)
    roll_xy_step: tuple[int, int] = (1, 1)
    identical_shift: bool = False
    random_roll: bool = False
    append_orig_hr_ref: bool = False
    alpha_trainable: bool = False
    alpha_transf: float = 1.0
    apply_attention: bool = True
    zero_conv: bool = False
    NL_in_NL: bool = False
    win_do_proj_qkv: bool = False
    win_do_norm: bool = False
    win_do_proj_out: bool = False


class ACVTT2p5D(nn.Module):
    """ACVTT core adapted to the project two-anchor through-plane protocol."""

    def __init__(self, **kwargs):
        super().__init__()
        cfg = ACVTTConfig(**kwargs)
        self.config = cfg
        self.net = ACVTT(cfg)

    def forward(self, cond: torch.Tensor) -> torch.Tensor:
        left = cond[:, 0:1]
        right = cond[:, 1:2]
        coarse = cond[:, 2:3]
        lr_pair = torch.cat([coarse, coarse], dim=1)
        ref_pair = torch.cat([left, right], dim=1)
        out = self.net(
            {
                "slice_lr": lr_pair,
                "slice_hr": coarse,
                "slice_ref": ref_pair,
            }
        )["out"]
        return out.clamp(0.0, 1.0)
