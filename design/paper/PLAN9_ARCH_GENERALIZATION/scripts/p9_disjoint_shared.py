"""Plan-9 preregistered same-target shared-vs-disjoint architecture test.

The protocol is frozen in HYPOTHESIS_REGISTRATION.md. Dense source volumes are
used only to synthesize the counterfactual phase-2 acquisition and to evaluate
the five physical targets missing from both x4 lattices.
"""
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
import torch


HERE = Path(__file__).resolve()
P9 = HERE.parents[1]
PAPER = P9.parent
ROOT = PAPER.parents[1]
OUT = P9 / "outputs"
sys.path[:0] = [str(ROOT / "baseline"), str(ROOT / "pre"), str(ROOT / "design"), str(ROOT)]

TEST_LIST = ROOT / "dataset" / "fastMRI_brain_T2" / "processed" / "splits" / "nifti_seed3407" / "test_cases.txt"
SOURCE_DIR = ROOT / "dataset" / "fastMRI_brain_T2" / "processed" / "nifti"
TARGETS = (3, 5, 7, 9, 11)
SEED = 20260814

MODEL_SPECS = {
    "hat": {
        "checkpoint": ROOT / "baseline" / "fastmri_brain_hat_2p5d" / "runs" / "full" / "checkpoints" / "hat_epoch_best.pth",
        "stored": ROOT / "baseline" / "fastmri_brain_hat_2p5d" / "runs" / "full" / "model_outputs",
        "family": "transformer_sr",
    },
    "swinir": {
        "checkpoint": ROOT / "baseline" / "fastmri_brain_swinir_2p5d" / "runs" / "full" / "checkpoints" / "swinir_epoch_best.pth",
        "stored": ROOT / "baseline" / "fastmri_brain_swinir_2p5d" / "runs" / "full" / "model_outputs",
        "family": "transformer_sr",
    },
    "i3net": {
        "checkpoint": ROOT / "baseline" / "fastmri_brain_i3net" / "runs" / "full" / "checkpoints" / "i3net_epoch_best.pth",
        "stored": ROOT / "baseline" / "fastmri_brain_i3net" / "runs" / "full" / "model_outputs",
        "family": "dedicated_inter_intra_cnn",
    },
    "saint": {
        "checkpoint": ROOT / "baseline" / "fastmri_brain_t2_saint_expanded" / "runs" / "full" / "checkpoints" / "saint_epoch_best.pth",
        "stored": ROOT / "baseline" / "fastmri_brain_t2_saint_expanded" / "runs" / "full" / "saint_outputs",
        "family": "spatial_attention_cnn",
    },
    "cycleinr": {
        "checkpoint": ROOT / "baseline" / "fastmri_brain_cycleinr" / "runs" / "full" / "checkpoints" / "cycleinr_epoch_best.pth",
        "stored": ROOT / "baseline" / "fastmri_brain_cycleinr" / "runs" / "full" / "model_outputs",
        "family": "implicit_coordinate_cycle",
    },
}


def load_interpolator(name: str, device: str):
    checkpoint = MODEL_SPECS[name]["checkpoint"]
    if name == "hat":
        from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator

        return FastMRIHAT2p5DInterpolator(checkpoint, device=device)
    if name == "swinir":
        from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator

        return FastMRISwinIR2p5DInterpolator(checkpoint, device=device)
    if name == "i3net":
        from ixi_i3net.train import I3NetInterpolator

        return I3NetInterpolator(checkpoint, device=device, label="Plan9-fastMRI")
    if name == "saint":
        from ixi_diffusion.saint import SAINTInterpolator

        return SAINTInterpolator(checkpoint, device=device)
    if name == "cycleinr":
        from ixi_arssr.inference import ArSSRInterpolator

        return ArSSRInterpolator(checkpoint, device=device)
    raise KeyError(name)


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
    n1 = float(ea @ ea)
    n2 = float(eb @ eb)
    total = 0.5 * (n1 + n2)
    shared = float(np.sum(((ea + eb) / 2.0) ** 2))
    observable = float(np.sum(((ea - eb) / 2.0) ** 2))
    cosine = float(ea @ eb / np.sqrt(n1 * n2)) if n1 > 0 and n2 > 0 else float("nan")
    return {
        "paired_error_mae": float(0.5 * (np.abs(ea).mean() + np.abs(eb).mean())),
        "prediction_disagreement_mae": float(np.abs(a - b)[mask].mean()),
        "error_cosine": cosine,
        "shared_error_fraction": shared / total if total > 0 else float("nan"),
        "observable_error_fraction": observable / total if total > 0 else float("nan"),
    }


def bootstrap_effect(case_df: pd.DataFrame, model: str, samples: int) -> dict[str, float | int]:
    g = case_df[case_df.model == model]
    pivot_e = g.pivot(index="case", columns="condition", values="paired_error_mae")
    pivot_d = g.pivot(index="case", columns="condition", values="prediction_disagreement_mae")
    cases = sorted(set(pivot_e.index) & set(pivot_d.index))
    observed_shared = rho(pivot_e.loc[cases, "shared"], pivot_d.loc[cases, "shared"])
    observed_disjoint = rho(pivot_e.loc[cases, "disjoint"], pivot_d.loc[cases, "disjoint"])
    observed = observed_disjoint - observed_shared
    rng = np.random.default_rng(SEED)
    reps = []
    n = len(cases)
    for _ in range(samples):
        idx = rng.integers(0, n, n)
        es = pivot_e.loc[cases, "shared"].to_numpy()[idx]
        ds = pivot_d.loc[cases, "shared"].to_numpy()[idx]
        ed = pivot_e.loc[cases, "disjoint"].to_numpy()[idx]
        dd = pivot_d.loc[cases, "disjoint"].to_numpy()[idx]
        value = rho(ed, dd) - rho(es, ds)
        if np.isfinite(value):
            reps.append(value)
    lo, hi = np.percentile(reps, [2.5, 97.5]) if reps else (np.nan, np.nan)
    return {
        "cases": n,
        "shared_error_ranking_rho": observed_shared,
        "disjoint_error_ranking_rho": observed_disjoint,
        "disjoint_minus_shared_rho": observed,
        "ci_low": float(lo),
        "ci_high": float(hi),
        "bootstrap_valid": len(reps),
    }


def add_stable_wrong(planes: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    planes = planes.copy()
    summaries = []
    planes["stable_wrong"] = False
    for model, g in planes.groupby("model"):
        shared = g[g.condition == "shared"]
        error_threshold = float(shared.paired_error_mae.quantile(0.75))
        disagreement_threshold = float(shared.prediction_disagreement_mae.quantile(0.25))
        idx = g.index
        planes.loc[idx, "stable_wrong"] = (
            (planes.loc[idx, "paired_error_mae"] >= error_threshold)
            & (planes.loc[idx, "prediction_disagreement_mae"] <= disagreement_threshold)
        )
        rates = planes.loc[idx].groupby("condition").stable_wrong.mean()
        summaries.append(
            {
                "model": model,
                "error_threshold": error_threshold,
                "disagreement_threshold": disagreement_threshold,
                "shared_stable_wrong_rate": float(rates.get("shared", np.nan)),
                "disjoint_stable_wrong_rate": float(rates.get("disjoint", np.nan)),
                "shared_minus_disjoint_rate": float(rates.get("shared", np.nan) - rates.get("disjoint", np.nan)),
            }
        )
    return planes, summaries


def run_model(name: str, cases: list[str], device: str) -> tuple[list[dict], list[dict]]:
    model = load_interpolator(name, device)
    rows: list[dict] = []
    validations: list[dict] = []
    started = time.perf_counter()
    for index, case in enumerate(cases, start=1):
        case_file = case if case.endswith(".nii.gz") else f"{case}.nii.gz"
        source = SOURCE_DIR / case_file
        full = nib.load(str(source)).get_fdata(dtype=np.float32)
        if full.shape[2] < 15:
            raise ValueError(f"{case}: depth {full.shape[2]} is insufficient for frozen A2")
        a0 = np.ascontiguousarray(full[:, :, [0, 4, 8, 12]])
        a2 = np.ascontiguousarray(full[:, :, [2, 6, 10, 14]])
        p0 = model.interpolate_volume(a0, stride=4)
        p2 = model.interpolate_volume(a2, stride=4)
        pflip = model.interpolate_volume(np.ascontiguousarray(a0[::-1, :, :]), stride=4)[::-1, :, :]
        if p0.shape[2] != 13 or p2.shape[2] != 13 or pflip.shape[2] != 13:
            raise RuntimeError(f"{name}/{case}: unexpected output depths {p0.shape}, {p2.shape}, {pflip.shape}")

        stored_path = MODEL_SPECS[name]["stored"] / f"diff_{case_file}"
        stored = nib.load(str(stored_path)).get_fdata(dtype=np.float32)
        if stored.shape != p0.shape:
            raise RuntimeError(f"{name}/{case}: stored {stored.shape} != regenerated {p0.shape}")
        validations.append(
            {
                "model": name,
                "case": case,
                "regenerated_vs_stored_mae": float(np.mean(np.abs(p0 - stored))),
                "regenerated_vs_stored_max_abs": float(np.max(np.abs(p0 - stored))),
            }
        )

        for z in TARGETS:
            y = full[:, :, z]
            threshold = 0.01 * max(float(np.max(np.abs(y))), 1e-6)
            mask = np.abs(y) > threshold
            if mask.sum() == 0:
                raise RuntimeError(f"{case}/z={z}: empty target mask")
            q0 = p0[:, :, z]
            pairs = {"shared": pflip[:, :, z], "disjoint": p2[:, :, z - 2]}
            for condition, q1 in pairs.items():
                rows.append(
                    {
                        "dataset": "fastmri",
                        "factor": 4,
                        "case": case,
                        "patient_cluster": case,
                        "model": name,
                        "family": MODEL_SPECS[name]["family"],
                        "target_z": z,
                        "condition": condition,
                        "anchor_set_a": "0;4;8;12",
                        "anchor_set_b": "0;4;8;12" if condition == "shared" else "2;6;10;14",
                        "anchor_overlap_count": 4 if condition == "shared" else 0,
                        "mask_pixels": int(mask.sum()),
                        **paired_metrics(q0, q1, y, mask),
                    }
                )
        elapsed = time.perf_counter() - started
        print(f"P9 disjoint/shared {name} {index}/{len(cases)} {case} elapsed={elapsed:.1f}s", flush=True)
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return rows, validations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", choices=tuple(MODEL_SPECS), default=list(MODEL_SPECS))
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--suffix", default="")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    cases = [line.strip() for line in TEST_LIST.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.max_cases:
        cases = cases[: args.max_cases]
    all_rows: list[dict] = []
    all_validations: list[dict] = []
    started = time.perf_counter()
    for name in args.models:
        rows, validations = run_model(name, cases, args.device)
        all_rows.extend(rows)
        all_validations.extend(validations)

    planes = pd.DataFrame(all_rows)
    planes, stable = add_stable_wrong(planes)
    case_df = (
        planes.groupby(["dataset", "factor", "case", "patient_cluster", "model", "family", "condition"], as_index=False)
        .agg(
            paired_error_mae=("paired_error_mae", "median"),
            prediction_disagreement_mae=("prediction_disagreement_mae", "median"),
            error_cosine=("error_cosine", "median"),
            shared_error_fraction=("shared_error_fraction", "median"),
            observable_error_fraction=("observable_error_fraction", "median"),
            stable_wrong_rate=("stable_wrong", "mean"),
        )
    )
    summaries = []
    for name in args.models:
        effect = bootstrap_effect(case_df, name, args.bootstrap)
        metrics = {}
        g = case_df[case_df.model == name]
        for condition, h in g.groupby("condition"):
            metrics[condition] = {
                "median_error_cosine": float(h.error_cosine.median()),
                "median_shared_error_fraction": float(h.shared_error_fraction.median()),
                "median_observable_error_fraction": float(h.observable_error_fraction.median()),
                "median_prediction_disagreement_mae": float(h.prediction_disagreement_mae.median()),
            }
        summaries.append({"model": name, "family": MODEL_SPECS[name]["family"], **effect, "conditions": metrics})

    suffix = f"_{args.suffix}" if args.suffix else ""
    planes.to_csv(OUT / f"p9_disjoint_shared_per_plane{suffix}.csv", index=False)
    case_df.to_csv(OUT / f"p9_disjoint_shared_per_case{suffix}.csv", index=False)
    pd.DataFrame(all_validations).to_csv(OUT / f"p9_wrapper_reproduction{suffix}.csv", index=False)
    payload = {
        "experiment": "H-ARCH-01 primary same-target shared-vs-disjoint",
        "status": "PILOT" if args.max_cases else "FROZEN PRIMARY",
        "models": args.models,
        "cases": len(cases),
        "targets_per_case": len(TARGETS),
        "device": args.device,
        "bootstrap_samples": args.bootstrap,
        "seed": SEED,
        "elapsed_seconds": time.perf_counter() - started,
        "summaries": summaries,
        "stable_wrong": stable,
    }
    (OUT / f"p9_disjoint_shared_summary{suffix}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONHASHSEED", str(SEED))
    main()
