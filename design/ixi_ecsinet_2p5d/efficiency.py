from __future__ import annotations

import csv
import json
import platform
import sys
import time
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
import torch.nn as nn

from .model import ECSINet


def timing_statistics(seconds: Sequence[float]) -> dict[str, float]:
    values_ms = np.asarray(seconds, dtype=np.float64) * 1000.0
    if values_ms.size == 0:
        raise ValueError("At least one timing sample is required")
    return {
        "forward_ms_mean": float(values_ms.mean()),
        "forward_ms_std": float(values_ms.std(ddof=0)),
        "forward_ms_p50": float(np.quantile(values_ms, 0.50)),
        "forward_ms_p95": float(np.quantile(values_ms, 0.95)),
    }


def benchmark_inference(
    name: str,
    model: nn.Module,
    device: torch.device,
    input_shape: tuple[int, int, int, int],
    warmup: int = 20,
    iterations: int = 100,
) -> dict[str, object]:
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    model = model.to(device).eval()
    x = torch.zeros(input_shape, device=device)
    if device.type == "cuda":
        x = x.contiguous(memory_format=torch.channels_last)
    with torch.no_grad():
        for _ in range(warmup):
            model(x)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
            torch.cuda.reset_peak_memory_stats(device)
        samples: list[float] = []
        for _ in range(iterations):
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            start = time.perf_counter()
            model(x)
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            samples.append(time.perf_counter() - start)
    peak_allocated_mb = float("nan")
    peak_reserved_mb = float("nan")
    if device.type == "cuda":
        peak_allocated_mb = torch.cuda.max_memory_allocated(device) / 1024**2
        peak_reserved_mb = torch.cuda.max_memory_reserved(device) / 1024**2
    return {
        "method": name,
        "input_shape": "x".join(str(value) for value in input_shape),
        "params": int(sum(param.numel() for param in model.parameters())),
        "iterations": iterations,
        **timing_statistics(samples),
        "peak_allocated_mb": peak_allocated_mb,
        "peak_reserved_mb": peak_reserved_mb,
        "device": str(device),
        "definition": "model forward only; excludes IO, resize, and metrics",
    }


def _estimate_forward_macs(model: nn.Module, device: torch.device, input_shape: tuple[int, int, int, int]) -> int:
    macs = 0
    hooks = []

    def hook(module: nn.Module, _inputs: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal macs
        if isinstance(module, nn.Conv2d):
            batch, out_channels, out_h, out_w = [int(value) for value in output.shape]
            kh, kw = module.kernel_size
            macs += batch * out_channels * out_h * out_w * module.in_channels * kh * kw // module.groups
        elif isinstance(module, nn.Linear):
            batch = int(np.prod(output.shape[:-1])) if output.ndim > 1 else 1
            macs += batch * module.in_features * module.out_features

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            hooks.append(module.register_forward_hook(hook))
    model = model.to(device).eval()
    x = torch.zeros(input_shape, device=device)
    with torch.no_grad():
        model(x)
    for item in hooks:
        item.remove()
    return int(macs)


def _benchmark_training(
    name: str,
    model: nn.Module,
    device: torch.device,
    input_shape: tuple[int, int, int, int],
    warmup: int,
    iterations: int,
) -> dict[str, object]:
    model = model.to(device).train()
    x = torch.rand(input_shape, device=device)
    target = torch.rand((input_shape[0], 1, input_shape[2], input_shape[3]), device=device)
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)
        x = x.contiguous(memory_format=torch.channels_last)
        target = target.contiguous(memory_format=torch.channels_last)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")

    def step() -> None:
        optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda"):
            prediction = model(x)
            loss = torch.nn.functional.l1_loss(prediction, target)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

    for _ in range(warmup):
        step()
    if device.type == "cuda":
        torch.cuda.synchronize(device)
        torch.cuda.reset_peak_memory_stats(device)
    samples: list[float] = []
    for _ in range(iterations):
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        start = time.perf_counter()
        step()
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        samples.append(time.perf_counter() - start)
    timing = timing_statistics(samples)
    peak_allocated_mb = float("nan")
    peak_reserved_mb = float("nan")
    if device.type == "cuda":
        peak_allocated_mb = torch.cuda.max_memory_allocated(device) / 1024**2
        peak_reserved_mb = torch.cuda.max_memory_reserved(device) / 1024**2
    return {
        "method": name,
        "batch_size": input_shape[0],
        "iterations": iterations,
        "seconds_per_iteration": timing["forward_ms_mean"] / 1000.0,
        "samples_per_second": input_shape[0] / max(timing["forward_ms_mean"] / 1000.0, 1e-12),
        "peak_allocated_mb": peak_allocated_mb,
        "peak_reserved_mb": peak_reserved_mb,
        "status": "ok",
        "device": str(device),
        "definition": "synthetic forward + L1 backward + AdamW step with AMP on CUDA",
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _environment(device: torch.device, image_size: int, warmup: int, inference_iterations: int, training_iterations: int) -> dict[str, object]:
    environment: dict[str, object] = {
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "device": str(device),
        "image_size": image_size,
        "warmup": warmup,
        "inference_iterations": inference_iterations,
        "training_iterations": training_iterations,
        "amp_on_cuda": True,
        "tf32_matmul": bool(torch.backends.cuda.matmul.allow_tf32),
        "tf32_cudnn": bool(torch.backends.cudnn.allow_tf32),
    }
    if device.type == "cuda":
        props = torch.cuda.get_device_properties(device)
        environment.update(
            {
                "gpu_name": props.name,
                "gpu_total_memory_mib": props.total_memory / 1024**2,
                "gpu_compute_capability": f"{props.major}.{props.minor}",
            }
        )
    return environment


def run_ecsinet_profile(
    output_dir: Path,
    device: torch.device,
    configurations: Sequence[dict[str, object]],
    image_size: int = 256,
    warmup: int = 20,
    inference_iterations: int = 100,
    training_iterations: int = 20,
) -> dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    complexity_rows: list[dict[str, object]] = []
    inference_rows: list[dict[str, object]] = []
    memory_rows: list[dict[str, object]] = []
    for config in configurations:
        name = str(config["name"])
        channels = int(config["channels"])
        num_blocks = int(config["num_blocks"])
        model = ECSINet(channels=channels, num_blocks=num_blocks)
        input_shape = (1, 4, image_size, image_size)
        macs = _estimate_forward_macs(model, device, input_shape)
        inference = benchmark_inference(
            name=name,
            model=model,
            device=device,
            input_shape=input_shape,
            warmup=warmup,
            iterations=inference_iterations,
        )
        inference_rows.append(inference)
        complexity_rows.append(
            {
                "method": name,
                "channels": channels,
                "num_blocks": num_blocks,
                "params": inference["params"],
                "params_m": int(inference["params"]) / 1e6,
                "macs_g": macs / 1e9,
                "flops_g": 2.0 * macs / 1e9,
                "input_shape": inference["input_shape"],
                "definition": "one generated slice; Conv2d and Linear hooks",
            }
        )
        del model
        for batch_size in [int(value) for value in config["batch_sizes"]]:
            try:
                row = _benchmark_training(
                    name=name,
                    model=ECSINet(channels=channels, num_blocks=num_blocks),
                    device=device,
                    input_shape=(batch_size, 4, image_size, image_size),
                    warmup=min(warmup, 3),
                    iterations=training_iterations,
                )
            except torch.cuda.OutOfMemoryError:
                if device.type == "cuda":
                    torch.cuda.empty_cache()
                row = {
                    "method": name,
                    "batch_size": batch_size,
                    "iterations": training_iterations,
                    "seconds_per_iteration": float("nan"),
                    "samples_per_second": float("nan"),
                    "peak_allocated_mb": float("nan"),
                    "peak_reserved_mb": float("nan"),
                    "status": "oom",
                    "device": str(device),
                    "definition": "synthetic forward + L1 backward + AdamW step with AMP on CUDA",
                }
            memory_rows.append(row)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    _write_csv(output_dir / "efficiency_profile.csv", complexity_rows)
    _write_csv(output_dir / "memory_profile.csv", memory_rows)
    _write_csv(output_dir / "inference_profile.csv", inference_rows)
    environment = _environment(device, image_size, warmup, inference_iterations, training_iterations)
    (output_dir / "profile_environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    lines = [
        "# ECSI-Net Efficiency Profile",
        "",
        "Inference is forward-only. Training throughput uses synthetic inputs and includes forward, L1 backward, and AdamW step.",
        "",
        "| Method | Params(M) | FLOPs(G) | Forward mean ms | Forward P95 ms |",
        "|---|---:|---:|---:|---:|",
    ]
    for complexity, inference in zip(complexity_rows, inference_rows):
        lines.append(
            f"| {complexity['method']} | {float(complexity['params_m']):.4f} | "
            f"{float(complexity['flops_g']):.4f} | {float(inference['forward_ms_mean']):.4f} | "
            f"{float(inference['forward_ms_p95']):.4f} |"
        )
    lines.extend(["", f"Device: `{device}`. Image size: `{image_size}x{image_size}`."])
    (output_dir / "profile_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"configurations": len(complexity_rows), "training_rows": len(memory_rows)}
