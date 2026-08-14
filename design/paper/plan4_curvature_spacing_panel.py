"""Build a plane panel for a target-free curvature-spacing difficulty law.

All proxy features use acquired anchors only.  The target is used only for
retrospective reconstruction-error and oracle interpolation-residual labels.
"""
from __future__ import annotations
import sys
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan4_outputs"
sys.path[:0] = [str(ROOT / "baseline"), str(ROOT / "design"), str(ROOT / "pre")]
from rasinet.optimization_protocol import profile_sources, case_names, prediction_path, gt_path


def masked_mean(a, mask):
    return float(np.asarray(a)[mask].mean())


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for dataset in ("fastmri", "ningxia"):
        folds = [None] if dataset == "fastmri" else [f"fold_{i:02d}" for i in range(8)]
        for factor in (2, 4, 6):
            ref = profile_sources(dataset, factor)["i3net"]
            for fold in folds:
                cases = case_names(ref, fold)
                for case in cases:
                    gt_img = nib.load(str(gt_path(ref, fold, case)))
                    gt = gt_img.get_fdata(dtype=np.float32)
                    dz = float(gt_img.header.get_zooms()[2])
                    acquired = gt[:, :, ::factor]
                    # Robust volume scale computed from acquired data only.
                    nz = np.abs(acquired[np.abs(acquired) > 0])
                    scale = float(np.quantile(nz, .99)) if nz.size else 1.0
                    preds = {m: nib.load(str(prediction_path(profile_sources(dataset, factor)[m], fold, case))).get_fdata(dtype=np.float32)
                             for m in ("i3net", "hat", "swinir")}
                    for z in range(1, gt.shape[2]-1):
                        if z % factor == 0:
                            continue
                        left = (z // factor) * factor; right = left + factor
                        if right >= gt.shape[2] or any(z >= p.shape[2] for p in preds.values()):
                            continue
                        t = (z-left)/factor
                        a, b, y = gt[:, :, left], gt[:, :, right], gt[:, :, z]
                        mask = (np.abs(a) > .01*scale) | (np.abs(b) > .01*scale)
                        if not mask.any():
                            continue
                        linear = (1-t)*a + t*b
                        change = masked_mean(np.abs(b-a), mask) / scale
                        # Second differences at acquired anchor locations; no missing target enters.
                        seconds = []
                        if left-factor >= 0:
                            seconds.append(np.abs(gt[:, :, left-factor] - 2*a + b))
                        if right+factor < gt.shape[2]:
                            seconds.append(np.abs(a - 2*b + gt[:, :, right+factor]))
                        if not seconds:
                            continue
                        curvature = masked_mean(np.mean(seconds, axis=0), mask) / (scale * (factor*dz)**2)
                        theory = curvature * (factor*dz)**2 * t*(1-t) / 2
                        oracle = masked_mean(np.abs(y-linear), mask) / scale
                        common = {"dataset":dataset,"fold":fold,"case":case,"factor":factor,"z":z,"t":t,
                                  "spacing_mm":factor*dz,"anchor_change":change,"input_curvature":curvature,
                                  "curvature_spacing_term":theory,"oracle_linear_residual":oracle,"scale":scale}
                        for model, pred in preds.items():
                            rows.append({**common,"target_model":model,
                                         "normalized_error":masked_mean(np.abs(pred[:, :, z]-y), mask)/scale})
                    print("curvature",dataset,factor,fold,case,flush=True)
    x = pd.DataFrame(rows)
    x.to_csv(OUT / "curvature_spacing_per_plane.csv", index=False)
    print(x.groupby(["dataset","factor","target_model"]).size().to_string())


if __name__ == "__main__":
    main()
