from __future__ import annotations

import torch


class DiffusionSchedule:
    def __init__(self, steps: int, device: torch.device | str):
        self.steps = steps
        self.device = torch.device(device)
        self.betas = torch.linspace(1e-4, 0.02, steps, device=self.device)
        self.alphas = 1.0 - self.betas
        self.alpha_bars = torch.cumprod(self.alphas, dim=0)

    def q_sample(self, x0: torch.Tensor, t: torch.Tensor, noise: torch.Tensor) -> torch.Tensor:
        alpha_bar = self.alpha_bars[t].view(-1, 1, 1, 1)
        return alpha_bar.sqrt() * x0 + (1 - alpha_bar).sqrt() * noise

    def predict_x0(self, noisy: torch.Tensor, t: torch.Tensor, pred_noise: torch.Tensor) -> torch.Tensor:
        alpha_bar = self.alpha_bars[t].view(-1, 1, 1, 1)
        return (noisy - (1 - alpha_bar).sqrt() * pred_noise) / alpha_bar.sqrt()

    def sample_timesteps(self, sample_steps: int) -> list[int]:
        raw = torch.linspace(self.steps - 1, 0, sample_steps, device=self.device)
        return [int(v.item()) for v in raw.round()]
