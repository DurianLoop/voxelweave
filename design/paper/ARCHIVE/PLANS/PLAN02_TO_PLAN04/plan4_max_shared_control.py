"""Maximum-anchor-overlap negative control via through-plane reversal equivariance.

The original and reversed runs contain exactly the same acquired x4 anchors.
After reversing the prediction back to physical z, their disagreement is a
target-preserving witness under maximal shared measurement context.  It is
contrasted with the phase-shift intervention, which shares zero anchors.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan4_outputs"
sys.path.insert(0, str(ROOT / "baseline"))
sys.path.insert(0, str(ROOT / "design"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "pre"))
from rasinet.optimization_protocol import profile_sources, case_names, prediction_path, gt_path
from rasinet.icassp_statistics import ranking_metrics

TARGETS = ("hat", "swinir")


def corr(a, b):
    return float(stats.spearmanr(a, b).statistic) if len(a) > 2 and np.std(a) > 0 and np.std(b) > 0 else float("nan")


def make_model(dataset, target, checkpoint):
    if dataset == "fastmri":
        if target == "hat":
            from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator
            return FastMRIHAT2p5DInterpolator(checkpoint)
        from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator
        return FastMRISwinIR2p5DInterpolator(checkpoint)
    if target == "hat":
        from ixi_hat_2p5d.train import HAT2p5DInterpolator
        return HAT2p5DInterpolator(checkpoint)
    from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator
    return SwinIR2p5DInterpolator(checkpoint)


def add_case(rows, dataset, fold, case, target, gt, p0, model):
    sparse = np.ascontiguousarray(gt[:, :, ::4])
    reversed_prediction = model.interpolate_volume(np.ascontiguousarray(sparse[:, :, ::-1]), stride=4)[:, :, ::-1]
    usable = min(gt.shape[2], p0.shape[2], reversed_prediction.shape[2])
    # Match the phase-shift experiment's common unobserved targets.
    for z in range(usable):
        if z % 4 not in (1, 3):
            continue
        a, b, y = p0[:, :, z], reversed_prediction[:, :, z], gt[:, :, z]
        threshold = .01 * max(float(np.max(np.abs(a))), 1e-6)
        mask = np.abs(a) > threshold
        disagreement = np.abs(a - b)
        error = .5 * (np.abs(a - y) + np.abs(b - y))
        rows.append({"dataset": dataset, "fold": fold, "case": case, "target_model": target, "z": z,
                     "shared_anchor_count": 2, "max_shared_inconsistency": float(disagreement[mask].mean()),
                     "phase0_error": float(np.abs(a-y)[mask].mean()), "mean_error": float(error[mask].mean()),
                     "pixel_rho": corr(disagreement[mask], error[mask])})


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for dataset in ("fastmri", "ningxia"):
        ref = profile_sources(dataset, 4)["i3net"]
        folds = [None] if dataset == "fastmri" else [f"fold_{i:02d}" for i in range(8)]
        for target in TARGETS:
            src = profile_sources(dataset, 4)[target]
            for fold in folds:
                checkpoint = src.run_dir(fold) / "checkpoints" / f"{target}_epoch_best.pth"
                model = make_model(dataset, target, checkpoint)
                for case in case_names(src, fold):
                    gt = nib.load(str(gt_path(ref, fold, case))).get_fdata(dtype=np.float32)
                    p0 = nib.load(str(prediction_path(src, fold, case))).get_fdata(dtype=np.float32)
                    add_case(rows, dataset, fold, case, target, gt, p0, model)
                    print("max-shared", dataset, target, fold, case, flush=True)
    x = pd.DataFrame(rows)
    x.to_csv(OUT / "max_shared_per_plane.csv", index=False)
    cases = x.groupby(["dataset", "case", "target_model"], as_index=False).agg(
        score=("max_shared_inconsistency", "median"), error=("mean_error", "median"), pixel_rho=("pixel_rho", "median"))
    cases.to_csv(OUT / "max_shared_per_case.csv", index=False)
    profiles = []
    for (dataset, model), g in cases.groupby(["dataset", "target_model"]):
        profiles.append({"dataset": dataset, "target_model": model, **ranking_metrics(g.error, g.score),
                         "median_pixel_rho": float(g.pixel_rho.median()), "median_score": float(g.score.median())})
    result = {"label": "MECHANISTIC / MAXIMUM SHARED-ANCHOR NEGATIVE CONTROL", "anchor_overlap": 2,
              "cases": {d: int(g.case.nunique()) for d, g in cases.groupby("dataset")}, "planes": len(x),
              "profiles": profiles}
    (OUT / "max_shared_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
