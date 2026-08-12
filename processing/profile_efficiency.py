from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from ixi_diffusion.common import ensure_dir
from ixi_diffusion.saint import SAINTInterpolationNet
from ixi_swinir_2p5d.model import SwinIR2p5D


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docx" / "experiment_notes" / "efficiency"
SIZE = 256


def _count_params(model: nn.Module) -> int:
    return int(sum(param.numel() for param in model.parameters()))


def _estimate_forward_macs(model: nn.Module, device: torch.device, channels: int) -> int:
    macs = 0
    hooks = []

    def hook(module: nn.Module, _inputs: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        if isinstance(module, nn.Conv2d):
            batch, out_channels, out_h, out_w = [int(v) for v in output.shape]
            kh, kw = module.kernel_size
            macs += batch * out_channels * out_h * out_w * module.in_channels * kh * kw // module.groups
        elif isinstance(module, nn.ConvTranspose2d):
            batch, out_channels, out_h, out_w = [int(v) for v in output.shape]
            kh, kw = module.kernel_size
            macs += batch * module.in_channels * out_h * out_w * out_channels * kh * kw // module.groups
        elif isinstance(module, nn.Linear):
            batch = int(np.prod(output.shape[:-1])) if output.ndim > 1 else 1
            macs += batch * module.in_features * module.out_features

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.ConvTranspose2d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model.eval()
    with torch.no_grad():
        x = torch.zeros((1, channels, SIZE, SIZE), device=device)
        model(x)
    for item in hooks:
        item.remove()
    return int(macs)


def _load_saint(device: torch.device) -> nn.Module:
    checkpoint = ROOT / "fastmri_brain_t2_saint_expanded" / "runs" / "full" / "checkpoints" / "saint_epoch_best.pth"
    model = SAINTInterpolationNet().to(device)
    if checkpoint.exists():
        payload = torch.load(checkpoint, map_location=device)
        model.load_state_dict(payload["model_state_dict"])
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
    return model.eval()


def _load_swinir(device: torch.device) -> nn.Module:
    checkpoint = ROOT / "fastmri_brain_swinir_2p5d" / "runs" / "full" / "checkpoints" / "swinir_epoch_best.pth"
    if checkpoint.exists():
        payload = torch.load(checkpoint, map_location=device)
        config = payload.get("model_config", {})
    else:
        config = {"embed_dim": 48, "depths": (2, 2, 2), "num_heads": (3, 3, 3), "window_size": 8}
    model = SwinIR2p5D(**config).to(device)
    if checkpoint.exists():
        model.load_state_dict(payload["model_state_dict"])
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
    return model.eval()


def _benchmark(model: nn.Module, device: torch.device, channels: int, warmup: int, iters: int) -> dict[str, float]:
    x = torch.zeros((1, channels, SIZE, SIZE), device=device)
    if device.type == "cuda":
        x = x.contiguous(memory_format=torch.channels_last)
    with torch.no_grad():
        for _ in range(warmup):
            model(x)
        if device.type == "cuda":
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats(device)
        start = time.perf_counter()
        for _ in range(iters):
            model(x)
        if device.type == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
    peak_mb = float("nan")
    allocated_mb = float("nan")
    if device.type == "cuda":
        peak_mb = torch.cuda.max_memory_allocated(device) / 1024**2
        allocated_mb = torch.cuda.memory_allocated(device) / 1024**2
    return {
        "forward_ms_mean": elapsed * 1000.0 / iters,
        "cuda_peak_allocated_mb": peak_mb,
        "cuda_allocated_after_benchmark_mb": allocated_mb,
    }


def _row(name: str, model: nn.Module, device: torch.device, channels: int, warmup: int, iters: int) -> dict[str, object]:
    params = _count_params(model)
    macs = _estimate_forward_macs(model, device, channels)
    bench = _benchmark(model, device, channels, warmup, iters)
    return {
        "method": name,
        "input": f"1x{channels}x{SIZE}x{SIZE}",
        "params": params,
        "params_m": params / 1e6,
        "param_memory_mb_fp32": params * 4 / 1024**2,
        "single_forward_macs_g": macs / 1e9,
        "single_forward_flops_g": 2 * macs / 1e9,
        "forward_ms_mean": bench["forward_ms_mean"],
        "cuda_peak_allocated_mb": bench["cuda_peak_allocated_mb"],
        "cuda_allocated_after_benchmark_mb": bench["cuda_allocated_after_benchmark_mb"],
        "device": str(device),
        "definition": "one generated 256x256 slice, model forward only, no NIfTI IO or resize",
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# T2/x4 Efficiency Profile",
        "",
        "口径：单个 256x256 generated slice 的模型 forward-only；不包含 NIfTI IO、resize、metric 计算或整例循环开销。",
        "",
        "| Method | Input | Params(M) | FLOPs(G) | Forward ms | CUDA peak MB | Note |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["method"]),
                    str(row["input"]),
                    f"{float(row['params_m']):.4f}",
                    f"{float(row['single_forward_flops_g']):.4f}",
                    f"{float(row['forward_ms_mean']):.4f}",
                    "nan" if np.isnan(float(row["cuda_peak_allocated_mb"])) else f"{float(row['cuda_peak_allocated_mb']):.2f}",
                    str(row["definition"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "说明：FLOPs 使用 Conv2d / ConvTranspose2d / Linear hook 估算，attention 中 softmax、matmul 和 normalization 未完全计入，因此 Transformer 的 FLOPs 偏保守；该表主要用于本项目内同脚本横向比较。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    warmup = 20
    iters = 100
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rows = [
        _row("SAINT-style", _load_saint(device), device, channels=6, warmup=warmup, iters=iters),
        _row("SwinIR-style 2.5D", _load_swinir(device), device, channels=4, warmup=warmup, iters=iters),
    ]
    ensure_dir(OUT_DIR)
    _write_csv(OUT_DIR / "t2_efficiency_saint_swinir.csv", rows)
    _write_markdown(OUT_DIR / "t2_efficiency_saint_swinir.md", rows)
    (OUT_DIR / "t2_efficiency_saint_swinir.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Efficiency profile written: {OUT_DIR}")


if __name__ == "__main__":
    main()
