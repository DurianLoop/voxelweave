"""P11-E02: IXI five-architecture clean shared/disjoint replication."""
from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from skimage.transform import resize
import torch


HERE = Path(__file__).resolve()
P11 = HERE.parents[1]
PAPER = P11.parent
ROOT = PAPER.parents[1]
OUT = P11 / "outputs"
sys.path[:0] = [str(ROOT / "baseline"), str(ROOT / "pre"), str(ROOT / "design"), str(ROOT)]

TEST_LIST = ROOT / "dataset/IXI/splits/seed3407/test_cases.txt"
METADATA = ROOT / "dataset/IXI/metadata/ixi_cases.csv"
SEED = 20260827
FAMILY = {
    "hat": "transformer_sr",
    "swinir": "transformer_sr",
    "i3net": "inter_intra_cnn",
    "saint": "spatial_attention_cnn",
    "cycleinr": "implicit_coordinate",
}
MODEL_SPECS = {
    "hat": {
        "checkpoint": ROOT / "baseline/ixi_hat_2p5d/runs/full_test115/checkpoints/hat_epoch_best.pth",
        "stored": ROOT / "baseline/ixi_hat_2p5d/runs/full_test115/model_outputs",
    },
    "swinir": {
        "checkpoint": ROOT / "baseline/ixi_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth",
        "stored": ROOT / "baseline/ixi_swinir_2p5d/runs/full_test115/model_outputs",
    },
    "i3net": {
        "checkpoint": ROOT / "baseline/ixi_i3net/runs/full_test115_stable/checkpoints/i3net_epoch_best.pth",
        "stored": ROOT / "baseline/ixi_i3net/runs/full_test115_stable/model_outputs",
    },
    "saint": {
        "checkpoint": ROOT / "pre/ixi_diffusion/runs/saint_full_t2/checkpoints/saint_epoch_best.pth",
        "stored": ROOT / "pre/ixi_diffusion/runs/saint_full_t2_test115/diffusion_outputs",
    },
    "cycleinr": {
        "checkpoint": ROOT / "baseline/ixi_cycleinr/runs/full/checkpoints/cycleinr_epoch_best.pth",
        "stored": ROOT / "baseline/ixi_cycleinr/runs/full_test115/model_outputs",
    },
}


def load_interpolator(name: str, device: str):
    checkpoint = MODEL_SPECS[name]["checkpoint"]
    if not checkpoint.exists():
        raise FileNotFoundError(checkpoint)
    if name == "hat":
        from ixi_hat_2p5d.train import HAT2p5DInterpolator

        return HAT2p5DInterpolator(checkpoint, device=device)
    if name == "swinir":
        from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator

        return SwinIR2p5DInterpolator(checkpoint, device=device)
    if name == "i3net":
        from ixi_i3net.train import I3NetInterpolator

        return I3NetInterpolator(checkpoint, device=device, label="P11-IXI")
    if name == "saint":
        from ixi_diffusion.saint import SAINTInterpolator

        return SAINTInterpolator(checkpoint, device=device)
    if name == "cycleinr":
        from ixi_arssr.inference import ArSSRInterpolator

        return ArSSRInterpolator(checkpoint, device=device)
    raise KeyError(name)


def saint_interpolate_with_physical_origin(wrapper, volume: np.ndarray, stride: int, origin_z: int, full_depth: int) -> np.ndarray:
    """Run SAINT with global physical z coordinates for a shifted phase grid."""
    from ixi_diffusion.common import normalize_volume

    norm, lo, hi = normalize_volume(volume)
    out_depth = (volume.shape[2] - 1) * stride + 1
    out = np.zeros((volume.shape[0], volume.shape[1], out_depth), dtype=np.float32)
    for idx in range(volume.shape[2]):
        out[:, :, idx * stride] = volume[:, :, idx]
    for idx in range(volume.shape[2] - 1):
        left = resize(norm[:, :, idx], wrapper.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
        right = resize(norm[:, :, idx + 1], wrapper.input_size, preserve_range=True, anti_aliasing=True).astype(np.float32)
        for offset in range(1, stride):
            rel = float(offset) / float(stride)
            physical_z = origin_z + idx * stride + offset
            z_abs = float(physical_z) / max(float(full_depth - 1), 1.0)
            cond_np = np.stack(
                [
                    left,
                    right,
                    np.full(wrapper.input_size, rel, dtype=np.float32),
                    np.full(wrapper.input_size, z_abs, dtype=np.float32),
                    wrapper.y_map,
                    wrapper.x_map,
                ],
                axis=0,
            )
            cond = torch.from_numpy(cond_np).float().unsqueeze(0).to(wrapper.device)
            with torch.no_grad():
                pred = wrapper.model(cond).squeeze(0).squeeze(0).cpu().numpy()
            slice_ = resize(pred, volume.shape[:2], preserve_range=True, anti_aliasing=True)
            out[:, :, idx * stride + offset] = np.clip(slice_, 0.0, 1.0) * (hi - lo) + lo
    return out


def nifti_roundtrip(data: np.ndarray, affine: np.ndarray, header: nib.Nifti1Header) -> np.ndarray:
    """Reproduce the benchmark staging/save quantization without a temporary file.

    IXI source headers are int16.  The established evaluation pipeline writes float
    arrays through those headers, so nibabel applies per-volume int16 scaling.  A
    bytes round-trip exactly matches that staging operation and keeps phase-0 and
    phase-2 inputs/outputs on the same numerical footing.
    """
    image = nib.Nifti1Image(data.astype(np.float32), affine, header.copy())
    restored = nib.Nifti1Image.from_bytes(image.to_bytes())
    return restored.get_fdata(dtype=np.float32)


def rho(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    keep = np.isfinite(a) & np.isfinite(b)
    if keep.sum() < 4 or np.std(a[keep]) == 0 or np.std(b[keep]) == 0:
        return float("nan")
    return float(stats.spearmanr(a[keep], b[keep]).statistic)


def paired_metrics(a: np.ndarray, b: np.ndarray, y: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    ea = (a - y)[mask].astype(np.float64)
    eb = (b - y)[mask].astype(np.float64)
    n1, n2 = float(ea @ ea), float(eb @ eb)
    total = 0.5 * (n1 + n2)
    shared = float(np.sum(((ea + eb) / 2.0) ** 2))
    observable = float(np.sum(((ea - eb) / 2.0) ** 2))
    return {
        "paired_error_mae": float(0.5 * (np.abs(ea).mean() + np.abs(eb).mean())),
        "prediction_disagreement_mae": float(np.abs(a - b)[mask].mean()),
        "error_cosine": float(ea @ eb / np.sqrt(n1 * n2)) if n1 > 0 and n2 > 0 else np.nan,
        "shared_error_fraction": shared / total if total > 0 else np.nan,
        "observable_error_fraction": observable / total if total > 0 else np.nan,
    }


def quantile_pick(values: list[int], count: int) -> list[int]:
    values = sorted(values)
    if count <= 0:
        return []
    if len(values) <= count:
        return values
    raw = np.linspace(0, len(values) - 1, count + 2)[1:-1]
    indices = []
    for value in raw:
        idx = int(round(value))
        while idx in indices and idx + 1 < len(values):
            idx += 1
        indices.append(idx)
    return [values[idx] for idx in sorted(set(indices))]


def select_balanced_targets(eligible: list[int], count: int, case_id: str) -> list[int]:
    r1 = [z for z in eligible if z % 4 == 1]
    r3 = [z for z in eligible if z % 4 == 3]
    extra_to_r1 = sum(ord(ch) for ch in case_id) % 2 == 0
    n1 = count // 2 + int(count % 2 and extra_to_r1)
    n3 = count - n1
    chosen = quantile_pick(r1, n1) + quantile_pick(r3, n3)
    if len(chosen) < count:
        remainder = [z for z in eligible if z not in chosen]
        chosen += quantile_pick(remainder, count - len(chosen))
    return sorted(chosen[:count])


def bootstrap_model(case_df: pd.DataFrame, model: str, samples: int, rng: np.random.Generator) -> dict:
    g = case_df[case_df.model.eq(model)]
    pivot_o = g.pivot(index="case", columns="condition", values="observable_error_fraction")
    pivot_e = g.pivot(index="case", columns="condition", values="paired_error_mae")
    pivot_d = g.pivot(index="case", columns="condition", values="prediction_disagreement_mae")
    cases = sorted(set(pivot_o.index) & set(pivot_e.index) & set(pivot_d.index))
    gains = pivot_o.loc[cases, "disjoint"].to_numpy() - pivot_o.loc[cases, "shared"].to_numpy()
    shared_rho = rho(pivot_e.loc[cases, "shared"], pivot_d.loc[cases, "shared"])
    disjoint_rho = rho(pivot_e.loc[cases, "disjoint"], pivot_d.loc[cases, "disjoint"])
    gain_reps, ranking_reps = [], []
    n = len(cases)
    for _ in range(samples):
        idx = rng.integers(0, n, n)
        gain_reps.append(float(np.median(gains[idx])))
        delta = rho(pivot_e.loc[cases, "disjoint"].to_numpy()[idx], pivot_d.loc[cases, "disjoint"].to_numpy()[idx]) - rho(
            pivot_e.loc[cases, "shared"].to_numpy()[idx], pivot_d.loc[cases, "shared"].to_numpy()[idx]
        )
        if np.isfinite(delta):
            ranking_reps.append(delta)
    return {
        "model": model,
        "family": FAMILY[model],
        "cases": n,
        "median_observable_gain": float(np.median(gains)),
        "observable_gain_ci_low": float(np.percentile(gain_reps, 2.5)),
        "observable_gain_ci_high": float(np.percentile(gain_reps, 97.5)),
        "fraction_cases_positive": float(np.mean(gains > 0)),
        "shared_error_ranking_rho": shared_rho,
        "disjoint_error_ranking_rho": disjoint_rho,
        "ranking_delta_rho": disjoint_rho - shared_rho,
        "ranking_delta_ci_low": float(np.percentile(ranking_reps, 2.5)) if ranking_reps else np.nan,
        "ranking_delta_ci_high": float(np.percentile(ranking_reps, 97.5)) if ranking_reps else np.nan,
    }


def analyze(planes: pd.DataFrame, models: list[str], samples: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    case_df = (
        planes.groupby(["dataset", "case", "patient_cluster", "model", "family", "condition"], as_index=False)
        .agg(
            paired_error_mae=("paired_error_mae", "median"),
            prediction_disagreement_mae=("prediction_disagreement_mae", "median"),
            error_cosine=("error_cosine", "median"),
            shared_error_fraction=("shared_error_fraction", "median"),
            observable_error_fraction=("observable_error_fraction", "median"),
        )
    )
    rng = np.random.default_rng(seed)
    summaries = pd.DataFrame([bootstrap_model(case_df, model, samples, rng) for model in models if model in set(case_df.model)])
    model_points = summaries.set_index("model").median_observable_gain.to_dict()
    family_points = {}
    for family in sorted(set(FAMILY[m] for m in model_points)):
        family_points[family] = float(np.mean([model_points[m] for m in model_points if FAMILY[m] == family]))
    loo = {
        family: float(np.mean([value for key, value in family_points.items() if key != family]))
        for family in family_points
        if len(family_points) > 1
    }
    payload = {
        "equal_family_observable_gain": float(np.mean(list(family_points.values()))) if family_points else np.nan,
        "family_points": family_points,
        "leave_one_family_out": loo,
        "all_model_gain_intervals_positive": bool(len(summaries) == len(models) and (summaries.observable_gain_ci_low > 0).all()),
    }
    return case_df, summaries, payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", choices=tuple(MODEL_SPECS), default=list(MODEL_SPECS))
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument("--targets-per-case", type=int, default=5)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--suffix", default="")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--skip-wrapper-validation", action="store_true")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.suffix}" if args.suffix else ""
    plane_path = OUT / f"p11_ixi_clean_per_plane{suffix}.csv"
    validation_path = OUT / f"p11_ixi_wrapper_reproduction{suffix}.csv"
    rows = pd.read_csv(plane_path).to_dict(orient="records") if args.resume and plane_path.exists() else []
    validations = pd.read_csv(validation_path).to_dict(orient="records") if args.resume and validation_path.exists() else []

    metadata = pd.read_csv(METADATA).set_index("case_id")
    cases = [line.strip() for line in TEST_LIST.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.max_cases:
        cases = cases[: args.max_cases]
    started = time.perf_counter()

    for model_name in args.models:
        done = {
            case
            for case, g in pd.DataFrame(rows).query("model == @model_name").groupby("case")
            if set(g.condition) == {"shared", "disjoint"} and g.target_z.nunique() >= args.targets_per_case
        } if rows else set()
        model = load_interpolator(model_name, args.device)
        for case_index, case_id in enumerate(cases, start=1):
            if case_id in done:
                continue
            source = Path(str(metadata.loc[case_id, "T2_path"]))
            source_image = nib.load(str(source))
            full = source_image.get_fdata(dtype=np.float32)
            depth = int(full.shape[2])
            p0_indices = np.arange(0, depth, 4, dtype=int)
            p2_indices = np.arange(2, depth, 4, dtype=int)
            if len(p0_indices) < 2 or len(p2_indices) < 2:
                raise RuntimeError(f"{case_id}: insufficient depth {depth}")
            a0 = np.ascontiguousarray(
                nifti_roundtrip(full[:, :, p0_indices], source_image.affine, source_image.header)
            )
            a2 = np.ascontiguousarray(
                nifti_roundtrip(full[:, :, p2_indices], source_image.affine, source_image.header)
            )
            stored_path = MODEL_SPECS[model_name]["stored"] / f"diff_{source.name}"
            if not stored_path.exists():
                raise FileNotFoundError(stored_path)
            p0 = nib.load(str(stored_path)).get_fdata(dtype=np.float32)
            expected_p0_depth = int(p0_indices[-1] + 1)
            if p0.shape[:2] != full.shape[:2] or p0.shape[2] != expected_p0_depth:
                raise RuntimeError(f"{model_name}/{case_id}: stored shape {p0.shape}, expected depth {expected_p0_depth}")
            if case_index == 1 and not args.skip_wrapper_validation and not any(v.get("model") == model_name for v in validations):
                regenerated = nifti_roundtrip(
                    model.interpolate_volume(a0, stride=4), source_image.affine, source_image.header
                )
                validation = {
                    "model": model_name,
                    "case": case_id,
                    "mae": float(np.mean(np.abs(regenerated - p0))),
                    "max_abs": float(np.max(np.abs(regenerated - p0))),
                    "tolerance": 1e-4,
                }
                validation["pass"] = validation["max_abs"] <= validation["tolerance"]
                validations.append(validation)
                pd.DataFrame(validations).to_csv(validation_path, index=False)
                if not validation["pass"]:
                    raise RuntimeError(f"Wrapper reproduction failed: {validation}")
            pflip = model.interpolate_volume(np.ascontiguousarray(a0[::-1, :, :]), stride=4)[::-1, :, :]
            if model_name == "saint":
                p2 = saint_interpolate_with_physical_origin(model, a2, stride=4, origin_z=2, full_depth=depth)
            else:
                p2 = model.interpolate_volume(a2, stride=4)
            pflip = nifti_roundtrip(pflip, source_image.affine, source_image.header)
            p2 = nifti_roundtrip(p2, source_image.affine, source_image.header)
            gt_depth = int(p0_indices[-1] + 1)
            full_gt = nifti_roundtrip(full[:, :, :gt_depth], source_image.affine, source_image.header)
            eligible = [z for z in range(2, min(int(p0_indices[-1]), int(p2_indices[-1])) + 1) if z % 2 == 1]
            targets = select_balanced_targets(eligible, args.targets_per_case, case_id)
            for z in targets:
                y = full_gt[:, :, z]
                threshold = 0.01 * max(float(np.max(np.abs(y))), 1e-6)
                mask = np.abs(y) > threshold
                if not mask.any():
                    raise RuntimeError(f"{case_id}/z={z}: empty target mask")
                pairs = {
                    "shared": (p0[:, :, z], pflip[:, :, z]),
                    "disjoint": (p0[:, :, z], p2[:, :, z - 2]),
                }
                for condition, (a, b) in pairs.items():
                    rows.append(
                        {
                            "dataset": "ixi",
                            "case": case_id,
                            "patient_cluster": case_id,
                            "model": model_name,
                            "family": FAMILY[model_name],
                            "target_z": z,
                            "target_residue": z % 4,
                            "condition": condition,
                            "anchor_grid_a": "phase0",
                            "anchor_grid_b": "phase0" if condition == "shared" else "phase2",
                            "anchor_overlap": "all" if condition == "shared" else "none",
                            "nearest_distance_multiset": "1;3",
                            "mask_pixels": int(mask.sum()),
                            **paired_metrics(a, b, y, mask),
                        }
                    )
            pd.DataFrame(rows).to_csv(plane_path, index=False)
            print(
                f"P11-E02 {model_name} {case_index}/{len(cases)} {case_id} targets={targets} elapsed={time.perf_counter()-started:.1f}s",
                flush=True,
            )
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    planes = pd.DataFrame(rows)
    completed_models = [name for name in MODEL_SPECS if name in set(planes.model)]
    case_df, summaries, aggregate = analyze(planes, completed_models, args.bootstrap, args.seed)
    case_df.to_csv(OUT / f"p11_ixi_clean_per_case{suffix}.csv", index=False)
    summaries.to_csv(OUT / f"p11_ixi_clean_model_summary{suffix}.csv", index=False)
    payload = {
        "experiment": "P11-E02 IXI five-architecture clean shared/disjoint replication",
        "status": "PILOT" if args.max_cases else "FROZEN PRIMARY",
        "cases_requested": len(cases),
        "models_requested": args.models,
        "models_completed": completed_models,
        "targets_per_case": args.targets_per_case,
        "bootstrap": args.bootstrap,
        "seed": args.seed,
        "saint_global_coordinate_corrected": True,
        "wrapper_validation_required": not args.skip_wrapper_validation,
        "elapsed_seconds": time.perf_counter() - started,
        "aggregate": aggregate,
        "outputs": [plane_path.name, f"p11_ixi_clean_per_case{suffix}.csv", f"p11_ixi_clean_model_summary{suffix}.csv", validation_path.name],
    }
    (OUT / f"p11_ixi_clean_summary{suffix}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(summaries.to_string(index=False))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    os.environ.setdefault("PYTHONHASHSEED", str(SEED))
    main()
