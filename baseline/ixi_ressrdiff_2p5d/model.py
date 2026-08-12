from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import torch
import torch.nn as nn


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESSRDIFF_SCRIPT_ROOT = PROJECT_ROOT / "external" / "Res-SRDiff" / "script"
if str(RESSRDIFF_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(RESSRDIFF_SCRIPT_ROOT))

from diffusion.Gaussian_model import create_gaussian_diffusion  # noqa: E402
from networks.unet import UNetModelSwin  # noqa: E402


@dataclass(frozen=True)
class ResSRDiffConfig:
    image_size: int = 256
    in_channels: int = 1
    out_channels: int = 1
    model_channels: int = 32
    num_res_blocks: tuple[int, ...] = (1, 1, 1, 1)
    attention_resolutions: tuple[int, ...] = (32, 16)
    steps: int = 4
    schedule_name: str = "exponential"
    etas_end: float = 0.99
    min_noise_level: float = 0.2
    kappa: float = 2.0
    predict_type: str = "xstart"
    scale_factor: float = 1.0
    normalize_input: bool = False


class ResSRDiff2p5D(nn.Module):
    """Official Res-SRDiff core adapted as a deterministic slice-refinement baseline."""

    def __init__(self, **kwargs):
        super().__init__()
        cfg = ResSRDiffConfig(**kwargs)
        self.config = cfg
        self.model = UNetModelSwin(
            image_size=cfg.image_size,
            in_channels=cfg.in_channels,
            model_channels=cfg.model_channels,
            out_channels=cfg.out_channels,
            num_res_blocks=cfg.num_res_blocks,
            attention_resolutions=cfg.attention_resolutions,
            cond_lq=True,
            lq_size=cfg.image_size,
        )
        self.diffusion = create_gaussian_diffusion(
            sf=1.0,
            schedule_name=cfg.schedule_name,
            schedule_kwargs={"power": 0.3},
            etas_end=cfg.etas_end,
            steps=cfg.steps,
            min_noise_level=cfg.min_noise_level,
            kappa=cfg.kappa,
            weighted_mse=False,
            predict_type=cfg.predict_type,
            timestep_respacing=None,
            scale_factor=cfg.scale_factor,
            normalize_input=cfg.normalize_input,
            latent_flag=False,
        )

    @property
    def steps(self) -> int:
        return self.config.steps

    def training_loss(self, target01: torch.Tensor, coarse01: torch.Tensor) -> tuple[torch.Tensor, dict[str, float]]:
        target = target01 * 2.0 - 1.0
        coarse = coarse01 * 2.0 - 1.0
        t = torch.randint(0, self.steps, size=(target.shape[0],), device=target.device)
        noise = torch.randn_like(target)
        losses, _z_t, pred = self.diffusion.training_losses(
            model=self.model,
            x_start=target,
            y=coarse,
            t=t,
            model_kwargs={"lq": coarse},
            noise=noise,
        )
        mse = losses["mse"].mean()
        pred01 = pred.clamp(-1.0, 1.0) * 0.5 + 0.5
        l1 = torch.nn.functional.l1_loss(pred01, target01)
        loss = mse + 0.25 * l1
        return loss, {"mse": float(mse.detach().item()), "pred_l1": float(l1.detach().item())}

    @torch.no_grad()
    def sample(self, coarse01: torch.Tensor) -> torch.Tensor:
        coarse = coarse01 * 2.0 - 1.0
        out = self.diffusion.p_sample_loop(
            y=coarse,
            model=self.model,
            first_stage_model=None,
            noise=None,
            noise_repeat=False,
            clip_denoised=True,
            denoised_fn=None,
            model_kwargs={"lq": coarse},
            progress=False,
        )
        return (out.clamp(-1.0, 1.0) * 0.5 + 0.5).clamp(0.0, 1.0)
