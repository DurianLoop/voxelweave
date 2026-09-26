"""P6-E06: frozen Anchor-CV V1 explanation and strong input baselines.

Registered in PLAN6_HYPOTHESES_AND_EXPERIMENTS.md before computation.
All three cohorts are evaluated; NingXia inference clusters eight patients.
"""
from __future__ import annotations

import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import ndimage, stats
from skimage.metrics import structural_similarity

HERE = Path(__file__).resolve()
UP = HERE.parents[1]
OUT = UP / "outputs"
RNG = np.random.default_rng(20260813)
BOOT_REPS = 5000
METHODS = [
    "anchor_cv",
    "anchor_cv_scale_normalized",
    "adjacent_mae",
    "adjacent_rmse",
    "adjacent_ssim_error",
    "adjacent_gradient_mae",
    "adjacent_lowfreq_mae",
    "adjacent_highfreq_mae",
    "first_difference_variability",
]


def finite_rho(a, b, kind="spearman"):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return float("nan")
    if kind == "kendall":
        return float(stats.kendalltau(a[ok], b[ok]).statistic)
    return float(stats.spearmanr(a[ok], b[ok]).statistic)


def rank_array(x):
    return stats.rankdata(np.asarray(x, float), method="average")


def partial_rank_corr(x, y, controls):
    x = np.asarray(x, float); y = np.asarray(y, float); c = np.asarray(controls, float)
    ok = np.isfinite(x) & np.isfinite(y) & np.all(np.isfinite(c), axis=1)
    if ok.sum() < c.shape[1] + 5:
        return float("nan")
    xr = rank_array(x[ok]); yr = rank_array(y[ok]); cr = np.column_stack([rank_array(c[ok, j]) for j in range(c.shape[1])])
    design = np.column_stack([np.ones(ok.sum()), cr])
    rx = xr - design @ np.linalg.lstsq(design, xr, rcond=None)[0]
    ry = yr - design @ np.linalg.lstsq(design, yr, rcond=None)[0]
    return float(stats.pearsonr(rx, ry).statistic)


def risk_curve(score, error):
    score = np.asarray(score, float); error = np.asarray(error, float)
    order = np.argsort(score)  # retain lowest predicted risk
    n = len(error); coverages = np.arange(1, n + 1) / n
    risks = np.array([error[order[:k]].mean() for k in range(1, n + 1)])
    aurc = float(np.trapezoid(risks, coverages))
    oracle = np.argsort(error)
    reverse = oracle[::-1]
    oa = float(np.trapezoid([error[oracle[:k]].mean() for k in range(1, n + 1)], coverages))
    ra = float(np.trapezoid([error[reverse[:k]].mean() for k in range(1, n + 1)], coverages))
    naurc = (aurc - oa) / (ra - oa) if ra > oa else float("nan")
    fixed = {}
    for c in (.1, .2, .3, .5, .7, .9):
        k = max(1, int(np.ceil(c * n))); fixed[str(c)] = float(error[order[:k]].mean())
    return aurc, float(naurc), fixed


def robust_range(v):
    nz = v[np.isfinite(v) & (np.abs(v) > 0)]
    if nz.size < 100:
        nz = v[np.isfinite(v)]
    lo, hi = np.percentile(nz, [1, 99])
    return float(max(hi - lo, 1e-6))


def case_features(gt):
    anchors = list(range(0, gt.shape[2], 4)); scale = robust_range(gt); rows = []
    first_scalar = []
    for left, right in zip(anchors[:-1], anchors[1:]):
        a = gt[:, :, left].astype(np.float64); b = gt[:, :, right].astype(np.float64)
        mask = (np.abs(a) > .01 * max(float(np.max(np.abs(a))), 1e-6)) | (np.abs(b) > .01 * max(float(np.max(np.abs(b))), 1e-6))
        if not np.any(mask):
            continue
        d = a - b; dr = float(max(np.max([a.max(), b.max()]) - np.min([a.min(), b.min()]), 1e-6))
        ga = np.hypot(ndimage.sobel(a, 0), ndimage.sobel(a, 1)); gb = np.hypot(ndimage.sobel(b, 0), ndimage.sobel(b, 1))
        la = ndimage.gaussian_filter(a, 2.0); lb = ndimage.gaussian_filter(b, 2.0)
        ha = a - la; hb = b - lb
        ssim = structural_similarity(a, b, data_range=dr)
        rows.append((np.abs(d)[mask].mean(), np.sqrt(np.mean(d[mask] ** 2)), 1.0 - ssim,
                     np.abs(ga - gb)[mask].mean(), np.abs(la - lb)[mask].mean(), np.abs(ha - hb)[mask].mean()))
        first_scalar.append(float(np.abs(d)[mask].mean()))
    second = []
    for j in range(1, len(anchors) - 1):
        # Preserve the frozen implementation's float32 arithmetic and mask.
        z = anchors[j]; target = gt[:, :, z].astype(np.float32)
        pred = .5 * (gt[:, :, anchors[j-1]].astype(np.float32) + gt[:, :, anchors[j+1]].astype(np.float32))
        mask = np.abs(target) > .01 * max(float(np.max(np.abs(target))), 1e-6)
        if np.any(mask):
            second.append(float(np.abs(pred - target)[mask].mean()))
    q = np.asarray(rows, float)
    return {
        "anchor_cv_recomputed": float(np.median(second)),
        "robust_intensity_range": scale,
        "adjacent_mae": float(np.median(q[:, 0])),
        "adjacent_rmse": float(np.median(q[:, 1])),
        "adjacent_ssim_error": float(np.median(q[:, 2])),
        "adjacent_gradient_mae": float(np.median(q[:, 3])),
        "adjacent_lowfreq_mae": float(np.median(q[:, 4])),
        "adjacent_highfreq_mae": float(np.median(q[:, 5])),
        "first_difference_variability": float(np.median(np.abs(np.diff(first_scalar)))) if len(first_scalar) > 1 else 0.0,
        "acquired_anchor_pairs": len(rows),
        "withheld_anchors": len(second),
    }


def main():
    manifest = pd.read_csv(UP / "DATA_MANIFEST.csv")
    m = manifest[(manifest.factor == 4) & (manifest.architecture == "hat")].drop_duplicates(["dataset", "case_id"])
    feature_rows = []
    for i, r in enumerate(m.itertuples(), 1):
        gt = nib.load(r.ground_truth_file).get_fdata(dtype=np.float32)
        f = case_features(gt)
        feature_rows.append({"dataset": r.dataset, "case": r.case_id, "patient_cluster": r.patient_cluster,
                             "spacing_mm": r.physical_spacing_mm, **f})
        print(f"P6-E06 features {i}/{len(m)} {r.dataset} {r.case_id}", flush=True)
    f = pd.DataFrame(feature_rows)
    locked = pd.read_csv(OUT / "anchor_cross_validation_per_case.csv")
    x = locked.merge(f, on=["dataset", "case", "patient_cluster"], validate="many_to_one")
    x["anchor_cv"] = x["score"]
    x["anchor_cv_scale_normalized"] = x.anchor_cv / x.robust_intensity_range
    x["x4_error_scale_normalized"] = x.x4_error / x.robust_intensity_range
    x.to_csv(OUT / "plan6_anchor_cv_explanation_per_case.csv", index=False)

    summaries = []; deltas = []; influence = []
    for ds, g0 in x.groupby("dataset"):
        # Average model-specific endpoints before examination-level confirmation.
        aggs = {k: "median" for k in METHODS + ["x4_error", "x4_error_scale_normalized", "robust_intensity_range", "spacing_mm"]}
        if g0.benefit_x4_to_x2.notna().all(): aggs["benefit_x4_to_x2"] = "mean"
        g = g0.groupby(["case", "patient_cluster"], as_index=False).agg(aggs)
        endpoints = ["x4_error", "x4_error_scale_normalized"] + (["benefit_x4_to_x2"] if "benefit_x4_to_x2" in g else [])
        for endpoint in endpoints:
            for method in METHODS:
                sr = finite_rho(g[method], g[endpoint]); kt = finite_rho(g[method], g[endpoint], "kendall")
                aurc, naurc, fixed = risk_curve(g[method], g[endpoint])
                summaries.append({"dataset": ds, "cases": int(g.case.nunique()), "patient_clusters": int(g.patient_cluster.nunique()),
                                  "endpoint": endpoint, "method": method, "spearman": sr, "kendall": kt,
                                  "aurc": aurc, "naurc": naurc, "risk_at_coverage": fixed})
            controls = g[["adjacent_mae", "robust_intensity_range", "spacing_mm"]].to_numpy(float)
            summaries.append({"dataset": ds, "cases": int(g.case.nunique()), "patient_clusters": int(g.patient_cluster.nunique()),
                              "endpoint": endpoint, "method": "anchor_cv_partial_rank_given_adjacent_scale_spacing",
                              "spearman": partial_rank_corr(g.anchor_cv, g[endpoint], controls), "kendall": None,
                              "aurc": None, "naurc": None, "risk_at_coverage": None})
        # Cluster bootstrap deltas against all trivial baselines on primary error endpoint.
        clusters = g.patient_cluster.unique(); by = {c: g[g.patient_cluster == c] for c in clusters}
        for method in METHODS[2:]:
            vals = []
            for _ in range(BOOT_REPS):
                b = pd.concat([by[c] for c in RNG.choice(clusters, len(clusters), replace=True)], ignore_index=True)
                vals.append(finite_rho(b.anchor_cv, b.x4_error) - finite_rho(b[method], b.x4_error))
            vals = np.asarray(vals); vals = vals[np.isfinite(vals)]
            deltas.append({"dataset": ds, "comparator": method,
                           "spearman_delta_anchor_cv_minus_comparator": finite_rho(g.anchor_cv, g.x4_error) - finite_rho(g[method], g.x4_error),
                           "cluster_95ci": [float(np.quantile(vals, .025)), float(np.quantile(vals, .975))]})
        full = finite_rho(g.anchor_cv, g.x4_error)
        for c in clusters:
            q = g[g.patient_cluster != c]
            influence.append({"dataset": ds, "left_out_cluster": c, "full_spearman": full,
                              "leave_one_cluster_out_spearman": finite_rho(q.anchor_cv, q.x4_error)})
    pd.DataFrame([{**q, "risk_at_coverage": json.dumps(q["risk_at_coverage"])} for q in summaries]).to_csv(OUT / "plan6_anchor_cv_explanation_summary.csv", index=False)
    pd.DataFrame(deltas).to_csv(OUT / "plan6_anchor_cv_baseline_deltas.csv", index=False)
    pd.DataFrame(influence).to_csv(OUT / "plan6_anchor_cv_loo_influence.csv", index=False)
    payload = {
        "experiment": "P6-E06",
        "status": "FROZEN CONFIRMATION / score unchanged",
        "datasets": sorted(x.dataset.unique()),
        "anchor_cv_identity": "MAE of half the acquired-slice second difference under the frozen target mask",
        "max_abs_difference_recomputed_vs_frozen": float(np.max(np.abs(x.anchor_cv_recomputed - x.anchor_cv))),
        "summaries": summaries,
        "paired_cluster_deltas": deltas,
    }
    (OUT / "plan6_anchor_cv_explanation.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    main()
