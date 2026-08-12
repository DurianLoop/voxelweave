from __future__ import annotations

import ast
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
import torch


def _to_numpy(value: torch.Tensor | np.ndarray) -> np.ndarray:
    if isinstance(value, torch.Tensor):
        value = value.detach().float().cpu().numpy()
    return np.asarray(value, dtype=np.float64)


def _safe_mean(values: np.ndarray, mask: np.ndarray) -> float:
    selected = values[mask]
    return float(selected.mean()) if selected.size else float("nan")


def _safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    left = left.reshape(-1)
    right = right.reshape(-1)
    finite = np.isfinite(left) & np.isfinite(right)
    left = left[finite]
    right = right[finite]
    if left.size < 2 or float(left.std()) <= 1e-12 or float(right.std()) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(left, right)[0, 1])


def component_statistics(
    parts: Mapping[str, torch.Tensor | np.ndarray],
    target: torch.Tensor | np.ndarray,
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    mask = _to_numpy(parts["mask"])
    residual = _to_numpy(parts["residual"])
    correction = _to_numpy(parts["correction"])
    coarse = _to_numpy(parts["coarse"])
    recon = _to_numpy(parts["recon"])
    change = _to_numpy(parts["change"])
    coarse_grad = _to_numpy(parts["coarse_grad"])
    target_np = _to_numpy(target)

    foreground = np.abs(target_np) > 1e-6
    background = ~foreground
    q25, q75 = np.quantile(change, [0.25, 0.75])
    low_change = change <= q25
    high_change = change >= q75

    mask_row = {
        "mask_mean": float(mask.mean()),
        "mask_std": float(mask.std()),
        "mask_p01": float(np.quantile(mask, 0.01)),
        "mask_p50": float(np.quantile(mask, 0.50)),
        "mask_p99": float(np.quantile(mask, 0.99)),
        "mask_foreground_mean": _safe_mean(mask, foreground),
        "mask_background_mean": _safe_mean(mask, background),
        "mask_high_change_mean": _safe_mean(mask, high_change),
        "mask_low_change_mean": _safe_mean(mask, low_change),
    }
    residual_abs = np.abs(residual)
    correction_abs = np.abs(correction)
    residual_row = {
        "residual_mean": float(residual.mean()),
        "residual_std": float(residual.std()),
        "residual_abs_p95": float(np.quantile(residual_abs, 0.95)),
        "residual_abs_p99": float(np.quantile(residual_abs, 0.99)),
        "residual_abs_max": float(residual_abs.max()),
        "correction_mean": float(correction.mean()),
        "correction_std": float(correction.std()),
        "correction_abs_p95": float(np.quantile(correction_abs, 0.95)),
        "correction_abs_p99": float(np.quantile(correction_abs, 0.99)),
        "correction_abs_max": float(correction_abs.max()),
    }
    target_linear_error = np.abs(target_np - coarse)
    prediction_linear_delta = np.abs(recon - coarse)
    corr_row = {
        "mask_vs_target_linear_error_corr": _safe_corr(mask, target_linear_error),
        "mask_vs_prediction_linear_delta_corr": _safe_corr(mask, prediction_linear_delta),
        "mask_vs_coarse_gradient_corr": _safe_corr(mask, coarse_grad),
    }
    return mask_row, residual_row, corr_row


def evaluate_quality_gate(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    by_method = {str(row["method"]): row for row in rows}
    missing = [name for name in ("ecsinet", "linear", "cubic") if name not in by_method]
    if missing:
        return {"passed": False, "failed_checks": [f"missing method: {name}" for name in missing]}

    higher_is_better = ("psnr_mean", "ssim_mean", "ncc_mean")
    lower_is_better = ("mae_mean", "mse_mean")
    failed: list[str] = []
    ecsinet = by_method["ecsinet"]
    for baseline_name in ("linear", "cubic"):
        baseline = by_method[baseline_name]
        for metric in higher_is_better:
            if float(ecsinet[metric]) <= float(baseline[metric]):
                failed.append(f"ecsinet.{metric} > {baseline_name}.{metric}")
        for metric in lower_is_better:
            if float(ecsinet[metric]) >= float(baseline[metric]):
                failed.append(f"ecsinet.{metric} < {baseline_name}.{metric}")
    return {"passed": not failed, "failed_checks": failed}


def evaluate_mask_gate(
    mask_rows: Iterable[Mapping[str, object]],
    residual_rows: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    masks = list(mask_rows)
    residuals = list(residual_rows)
    failed: list[str] = []
    if not masks:
        failed.append("mask statistics present")
    if not residuals:
        failed.append("residual statistics present")
    if masks:
        mean = float(np.nanmean([float(row["mask_mean"]) for row in masks]))
        std = float(np.nanmean([float(row["mask_std"]) for row in masks]))
        if not 0.01 < mean < 0.99:
            failed.append("0.01 < mask_mean < 0.99")
        if not std >= 0.01:
            failed.append("mask_std >= 0.01")
    else:
        mean = float("nan")
        std = float("nan")
    if residuals:
        correction_max = float(np.nanmax([float(row["correction_abs_max"]) for row in residuals]))
        if not np.isfinite(correction_max):
            failed.append("correction_abs_max finite")
        if correction_max > 1.01:
            failed.append("correction_abs_max <= 1.01")
    else:
        correction_max = float("nan")
    return {
        "passed": not failed,
        "failed_checks": failed,
        "mask_mean": mean,
        "mask_std": std,
        "correction_abs_max": correction_max,
    }


def gpu_preflight(
    snapshot: Mapping[str, object],
    own_pid: int,
    max_utilization_percent: float = 20.0,
    max_memory_fraction: float = 0.25,
) -> dict[str, object]:
    reasons: list[str] = []
    processes = snapshot.get("compute_processes", [])
    foreign = [item for item in processes if int(item["pid"]) != own_pid]
    if foreign:
        reasons.append("foreign_compute_process")
    utilization = float(snapshot["gpu_utilization_percent"])
    if utilization > max_utilization_percent:
        reasons.append("gpu_utilization")
    total = float(snapshot["memory_total_mib"])
    used_fraction = float(snapshot["memory_used_mib"]) / max(total, 1.0)
    if used_fraction > max_memory_fraction:
        reasons.append("gpu_memory")
    return {
        "passed": not reasons,
        "reasons": reasons,
        "foreign_processes": foreign,
        "memory_used_fraction": used_fraction,
        "snapshot": dict(snapshot),
    }


def run_static_validation(output_dir: Path) -> dict[str, object]:
    from .model import ECSINet
    from .settings import PROFILES, build_paths
    from .train import ECSINetInterpolator, _batch_loss

    output_dir.mkdir(parents=True, exist_ok=True)
    package_dir = Path(__file__).resolve().parent
    checks: list[dict[str, object]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    source_files = [
        "model.py",
        "settings.py",
        "train.py",
        "run_all.py",
        "paper_table.py",
        "acceptance.py",
        "efficiency.py",
        "one_click.py",
    ]
    try:
        for name in source_files:
            path = package_dir / name
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        record("ast_parse", True, f"parsed {len(source_files)} Python files")
    except Exception as exc:
        record("ast_parse", False, repr(exc))

    device = torch.device("cpu")
    model = ECSINet(channels=8, num_blocks=1).to(device).eval()
    cond4 = torch.rand(2, 4, 16, 16)
    cond6, _, _, _ = ECSINet.expand_condition(cond4)
    with torch.no_grad():
        parts = model(cond4, return_parts=True)
        out6 = model(cond6)
    record("forward_4ch_shape", tuple(parts["recon"].shape) == (2, 1, 16, 16), str(tuple(parts["recon"].shape)))
    record("forward_6ch_shape", tuple(out6.shape) == (2, 1, 16, 16), str(tuple(out6.shape)))
    expected_keys = {"recon", "residual", "correction", "mask", "coarse", "change", "coarse_grad"}
    record("return_parts", set(parts) == expected_keys, ", ".join(sorted(parts)))
    formula_ok = torch.allclose(parts["recon"], parts["coarse"] + parts["mask"] * parts["residual"], atol=1e-6)
    record("reconstruction_formula", bool(formula_ok), "recon == coarse + mask * residual")
    mask_ok = bool(torch.all(parts["mask"] >= 0.0) and torch.all(parts["mask"] <= 1.0))
    record("mask_range", mask_ok, f"min={parts['mask'].min().item():.6f}, max={parts['mask'].max().item():.6f}")

    profile = PROFILES["smoke"]
    batch = {"cond": cond4, "coarse": cond4[:, 2:3], "target": torch.rand(2, 1, 16, 16)}
    loss, loss_parts = _batch_loss(model, batch, profile, device)
    loss_keys = {"l1", "grad", "residual_l1", "mask_mean", "mask_prior_l1"}
    record("finite_batch_loss", bool(torch.isfinite(loss)), f"loss={loss.item():.6f}")
    record("batch_loss_parts", set(loss_parts) == loss_keys, ", ".join(sorted(loss_parts)))

    checkpoint_path = output_dir / "_static_validation_checkpoint.pth"
    try:
        payload = {
            "model_state_dict": model.state_dict(),
            "stride": 4,
            "model_config": {
                "channels": 8,
                "num_blocks": 1,
                "expansion": 2,
                "kernel_size": 5,
                "residual_scale": 1.0,
                "mask_bias": -2.0,
                "amp": False,
            },
        }
        torch.save(payload, checkpoint_path)
        interpolator = ECSINetInterpolator(checkpoint_path, device="cpu")
        prediction = interpolator._predict_slice(cond4[0].numpy())
        roundtrip_ok = prediction.shape == (16, 16) and bool(np.isfinite(prediction).all())
        record("checkpoint_roundtrip", roundtrip_ok, f"shape={prediction.shape}")
        try:
            interpolator.interpolate_volume(np.zeros((4, 4, 2), dtype=np.float32), stride=2)
        except ValueError as exc:
            record("stride_mismatch_guard", "Checkpoint stride=4" in str(exc), str(exc))
        else:
            record("stride_mismatch_guard", False, "stride mismatch did not raise ValueError")
    except Exception as exc:
        record("checkpoint_roundtrip", False, repr(exc))
        record("stride_mismatch_guard", False, repr(exc))
    finally:
        if checkpoint_path.exists():
            checkpoint_path.unlink()

    run_dirs = {name: str(build_paths(name).run_dir) for name in ("smoke", "mini", "full_test115_x2", "full_test115_x6")}
    unique_dirs = len(set(run_dirs.values())) == len(run_dirs)
    strides_ok = PROFILES["smoke"].stride == 4 and PROFILES["full_test115_x2"].stride == 2 and PROFILES["full_test115_x6"].stride == 6
    record("profile_output_isolation", unique_dirs, json.dumps(run_dirs, ensure_ascii=False))
    record("profile_strides", strides_ok, "smoke=x4, full_test115_x2=x2, full_test115_x6=x6")

    result = {"passed": all(bool(item["passed"]) for item in checks), "checks": checks}
    (output_dir / "static_validation.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# ECSI-Net Static Validation", "", f"Overall: `{'PASS' if result['passed'] else 'FAIL'}`", ""]
    for item in checks:
        lines.append(f"- [{'x' if item['passed'] else ' '}] `{item['name']}`: {item['detail']}")
    (output_dir / "static_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def analyze_checkpoint(
    checkpoint: Path,
    profile_name: str,
    metrics_dir: Path,
    report_dir: Path,
    max_samples: int = 256,
    visual_count: int = 3,
    device_name: str | None = None,
) -> dict[str, object]:
    from ixi_diffusion.data import IXISingleSliceInterpolationDataset

    from .model import ECSINet
    from .settings import PROFILES

    if max_samples <= 0:
        raise ValueError("max_samples must be positive")
    profile = PROFILES[profile_name]
    device = torch.device(device_name or ("cuda" if torch.cuda.is_available() else "cpu"))
    payload = torch.load(checkpoint, map_location=device)
    config = dict(payload.get("model_config", {}))
    amp = bool(config.pop("amp", True))
    model = ECSINet(**config).to(device).eval()
    model.load_state_dict(payload["model_state_dict"])
    if device.type == "cuda":
        model = model.to(memory_format=torch.channels_last)

    dataset = IXISingleSliceInterpolationDataset(
        "test",
        profile.modality,
        profile.stride,
        profile.test_cases,
        target_shape=profile.target_shape,
    )
    sample_count = min(max_samples, len(dataset))
    indices = np.linspace(0, len(dataset) - 1, num=sample_count, dtype=np.int64)
    mask_rows: list[dict[str, object]] = []
    residual_rows: list[dict[str, object]] = []
    correlation_rows: list[dict[str, object]] = []
    visual_payloads: list[tuple[dict[str, np.ndarray], dict[str, object]]] = []

    for sample_index in indices.tolist():
        batch = dataset[sample_index]
        cond = batch["cond"].unsqueeze(0).to(device)
        target = batch["target"].unsqueeze(0).to(device)
        if device.type == "cuda":
            cond = cond.contiguous(memory_format=torch.channels_last)
            target = target.contiguous(memory_format=torch.channels_last)
        with torch.no_grad():
            with torch.amp.autocast(device_type=device.type, enabled=device.type == "cuda" and amp):
                parts = model(cond, return_parts=True)
        mask_row, residual_row, correlation_row = component_statistics(parts, target)
        _path, case_id, z, offset, depth = dataset.items[sample_index]
        metadata: dict[str, object] = {
            "sample_index": sample_index,
            "case": case_id,
            "z": z,
            "offset": offset,
            "depth": depth,
            "phase": float(offset) / float(profile.stride),
        }
        mask_rows.append({**metadata, **mask_row})
        residual_rows.append({**metadata, **residual_row})
        correlation_rows.append({**metadata, **correlation_row})
        if len(visual_payloads) < visual_count:
            visual_payloads.append(
                (
                    {
                        "target": _to_numpy(target[0, 0]),
                        "linear": _to_numpy(parts["coarse"][0, 0]),
                        "prediction": _to_numpy(parts["recon"][0, 0]),
                        "absolute_error": np.abs(_to_numpy(parts["recon"][0, 0]) - _to_numpy(target[0, 0])),
                        "mask": _to_numpy(parts["mask"][0, 0]),
                        "residual": _to_numpy(parts["residual"][0, 0]),
                    },
                    metadata,
                )
            )

    metrics_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(metrics_dir / "mask_statistics.csv", mask_rows)
    _write_csv(metrics_dir / "residual_statistics.csv", residual_rows)
    _write_csv(metrics_dir / "mask_correlation.csv", correlation_rows)

    if visual_payloads:
        import matplotlib.pyplot as plt

        visual_dir = report_dir / "visual_qc"
        visual_dir.mkdir(parents=True, exist_ok=True)
        for values, metadata in visual_payloads:
            fig, axes = plt.subplots(2, 3, figsize=(12, 8), constrained_layout=True)
            for axis, (title, image) in zip(axes.flat, values.items()):
                cmap = "magma" if title in {"absolute_error", "mask", "residual"} else "gray"
                shown = axis.imshow(image, cmap=cmap)
                axis.set_title(title)
                axis.axis("off")
                fig.colorbar(shown, ax=axis, fraction=0.046, pad=0.04)
            fig.suptitle(f"{metadata['case']} z={metadata['z']} offset={metadata['offset']}")
            fig.savefig(
                visual_dir / f"{metadata['case']}_z{metadata['z']}_o{metadata['offset']}.png",
                dpi=160,
            )
            plt.close(fig)

    gate = evaluate_mask_gate(mask_rows, residual_rows)
    result = {
        "passed": gate["passed"],
        "samples": sample_count,
        "profile": profile_name,
        "checkpoint": str(checkpoint),
        "device": str(device),
        "gate": gate,
        "mean_correlations": {
            key: float(np.nanmean([float(row[key]) for row in correlation_rows]))
            for key in (
                "mask_vs_target_linear_error_corr",
                "mask_vs_prediction_linear_delta_corr",
                "mask_vs_coarse_gradient_corr",
            )
        },
    }
    (report_dir / "component_acceptance.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        f"# ECSI-Net {profile_name} Component Acceptance",
        "",
        f"Overall: `{'PASS' if result['passed'] else 'FAIL'}`",
        "",
        f"Samples: `{sample_count}`",
        f"Mask mean: `{float(gate['mask_mean']):.6f}`",
        f"Mask std: `{float(gate['mask_std']):.6f}`",
        f"Correction abs max: `{float(gate['correction_abs_max']):.6f}`",
        "",
        "Failed checks:",
    ]
    failed_checks = list(gate["failed_checks"])
    lines.extend([f"- {item}" for item in failed_checks] or ["- None"])
    (report_dir / "component_acceptance.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result
