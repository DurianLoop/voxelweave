"""P7-CV-E03: development-frozen multi-anchor jackknife audit."""

from pathlib import Path
import json

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats


HERE = Path(__file__).resolve()
P7 = HERE.parents[1]
PAPER = P7.parent
CV = PAPER / "CVPR" / "CVPR_UPGRADE"
MANIFEST = CV / "DATA_MANIFEST.csv"
PLAN6 = CV / "outputs" / "plan6_anchor_cv_explanation_per_case.csv"
PC = CV / "outputs" / "orthogonal_two_component_per_case.csv"
OUT = P7 / "outputs"
CANDIDATES = ("jackknife_mean", "jackknife_q90", "jackknife_iqr", "jackknife_mad")
BOOTSTRAPS = 5000
SEED = 20260813


def rho(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return np.nan
    return float(stats.spearmanr(a[ok], b[ok]).statistic)


def partial_rho(x, y, controls):
    x = np.asarray(x, float); y = np.asarray(y, float); c = np.asarray(controls, float)
    ok = np.isfinite(x) & np.isfinite(y) & np.all(np.isfinite(c), axis=1)
    if ok.sum() < 8:
        return np.nan
    rx = stats.rankdata(x[ok]); ry = stats.rankdata(y[ok])
    rc = np.column_stack([stats.rankdata(c[ok, j]) for j in range(c.shape[1])])
    design = np.column_stack([np.ones(ok.sum()), rc])
    ex = rx - design @ np.linalg.lstsq(design, rx, rcond=None)[0]
    ey = ry - design @ np.linalg.lstsq(design, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1]) if np.std(ex) and np.std(ey) else np.nan


def anchor_residuals(volume):
    anchors = list(range(0, volume.shape[2], 4))
    residuals = []
    for j in range(1, len(anchors) - 1):
        target = volume[:, :, anchors[j]].astype(np.float32)
        pred = 0.5 * (volume[:, :, anchors[j - 1]].astype(np.float32) + volume[:, :, anchors[j + 1]].astype(np.float32))
        mask = np.abs(target) > 0.01 * max(float(np.max(np.abs(target))), 1e-6)
        if np.any(mask):
            residuals.append(float(np.abs(pred - target)[mask].mean()))
    return np.asarray(residuals, float)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(MANIFEST)
    manifest = manifest[(manifest.factor == 4) & (manifest.architecture == "hat")].drop_duplicates(["dataset", "case_id"])
    base = pd.read_csv(PLAN6).groupby(["dataset", "case", "patient_cluster"], as_index=False).agg(
        x4_error=("x4_error", "mean"),
        anchor_cv=("anchor_cv", "first"),
        adjacent_mae=("adjacent_mae", "first"),
        robust_intensity_range=("robust_intensity_range", "first"),
        spacing_mm=("spacing_mm", "first"),
    )
    split = pd.read_csv(PC)[["dataset", "case", "split"]].drop_duplicates()
    records = []
    for row in manifest.itertuples():
        volume = nib.load(row.ground_truth_file).get_fdata(dtype=np.float32)
        values = anchor_residuals(volume)
        records.append({
            "dataset": row.dataset,
            "case": row.case_id,
            "patient_cluster": row.patient_cluster,
            "withheld_anchors": int(len(values)),
            "jackknife_median": float(np.median(values)),
            "jackknife_mean": float(np.mean(values)),
            "jackknife_q90": float(np.quantile(values, 0.9)),
            "jackknife_iqr": float(np.quantile(values, 0.75) - np.quantile(values, 0.25)),
            "jackknife_mad": float(np.median(np.abs(values - np.median(values)))),
        })
    features = pd.DataFrame(records).merge(base, on=["dataset", "case", "patient_cluster"]).merge(split, on=["dataset", "case"], how="left")
    features["split"] = features.split.fillna("transfer")
    features["evaluation_partition"] = np.where(
        (features.dataset == "fastmri") & (features.split == "development"), "development",
        np.where((features.dataset == "fastmri") & (features.split == "confirmation"), "confirmation", "transfer"),
    )
    reproduction_error = float(np.max(np.abs(features.jackknife_median - features.anchor_cv)))

    # Select one interpretable statistic on fastMRI development only.
    dev = features[(features.dataset == "fastmri") & (features.evaluation_partition == "development")]
    selection = []
    controls = np.column_stack([dev.adjacent_mae, dev.robust_intensity_range, dev.spacing_mm])
    for candidate in CANDIDATES:
        selection.append({
            "candidate": candidate,
            "development_spearman": rho(dev[candidate], dev.x4_error),
            "development_partial_rho_given_adjacent_scale_spacing": partial_rho(dev[candidate], dev.x4_error, controls),
        })
    selection.sort(key=lambda q: (-np.nan_to_num(q["development_partial_rho_given_adjacent_scale_spacing"], nan=-999), -np.nan_to_num(q["development_spearman"], nan=-999), q["candidate"]))
    selected = selection[0]["candidate"]
    for q in selection:
        q["selected"] = q["candidate"] == selected
    pd.DataFrame(selection).to_csv(OUT / "p7_cvpr_jackknife_development_freeze.csv", index=False)
    features["jackknife_v2"] = features[selected]
    features.to_csv(OUT / "p7_cvpr_multi_anchor_jackknife_per_case.csv", index=False)

    methods = ["jackknife_v2", "anchor_cv", "adjacent_mae"]
    rng = np.random.default_rng(SEED)
    summaries = []
    for (dataset, partition), group in features.groupby(["dataset", "evaluation_partition"], sort=False):
        clusters = group.patient_cluster.astype(str).unique()
        by = {c: group[group.patient_cluster.astype(str).eq(c)] for c in clusters}
        control = np.column_stack([group.adjacent_mae, group.robust_intensity_range, group.spacing_mm])
        observed_partial = partial_rho(group.jackknife_v2, group.x4_error, control)
        observed = {m: rho(group[m], group.x4_error) for m in methods}
        boot = {m: [] for m in methods}; partial_boot = []
        for _ in range(BOOTSTRAPS):
            sample = pd.concat([by[c] for c in rng.choice(clusters, len(clusters), replace=True)], ignore_index=True)
            for method in methods:
                boot[method].append(rho(sample[method], sample.x4_error))
            ctl = np.column_stack([sample.adjacent_mae, sample.robust_intensity_range, sample.spacing_mm])
            partial_boot.append(partial_rho(sample.jackknife_v2, sample.x4_error, ctl))
        for method in methods:
            arr = np.asarray(boot[method], float)
            summaries.append({
                "dataset": dataset, "partition": partition, "cases": int(group.case.nunique()),
                "patient_clusters": int(len(clusters)), "selected_statistic": selected, "method": method,
                "spearman_x4_error": observed[method],
                "cluster_ci_low": float(np.nanquantile(arr, 0.025)), "cluster_ci_high": float(np.nanquantile(arr, 0.975)),
                "partial_rho_given_adjacent_scale_spacing": observed_partial if method == "jackknife_v2" else np.nan,
                "partial_cluster_ci_low": float(np.nanquantile(partial_boot, 0.025)) if method == "jackknife_v2" else np.nan,
                "partial_cluster_ci_high": float(np.nanquantile(partial_boot, 0.975)) if method == "jackknife_v2" else np.nan,
                "rho_delta_vs_adjacent": observed[method] - observed["adjacent_mae"],
                "delta_vs_adjacent_ci_low": float(np.nanquantile(np.asarray(boot[method]) - np.asarray(boot["adjacent_mae"]), 0.025)),
                "delta_vs_adjacent_ci_high": float(np.nanquantile(np.asarray(boot[method]) - np.asarray(boot["adjacent_mae"]), 0.975)),
            })
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "p7_cvpr_multi_anchor_jackknife_summary.csv", index=False)
    payload = {
        "experiment": "P7-CV-E03", "status": "COMPLETE", "selected_statistic": selected,
        "candidate_meaning": {
            "jackknife_mean": "global acquired-anchor interpolation difficulty",
            "jackknife_q90": "upper-tail localized acquired-anchor failure",
            "jackknife_iqr": "between-position heterogeneity",
            "jackknife_mad": "robust between-position heterogeneity",
        },
        "selection_data": "12 fastMRI development examinations only",
        "locked_evaluation": "12 fastMRI confirmation examinations plus IXI and NingXia transfer cohorts",
        "maximum_abs_reproduction_error_anchor_cv_median": reproduction_error,
        "promotion_gate": "incremental conditional/out-of-sample information beyond adjacent difference on more than one cohort",
        "outputs": ["p7_cvpr_jackknife_development_freeze.csv", "p7_cvpr_multi_anchor_jackknife_per_case.csv", "p7_cvpr_multi_anchor_jackknife_summary.csv"],
    }
    (OUT / "p7_cvpr_multi_anchor_jackknife.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(pd.DataFrame(selection).to_string(index=False))
    print(summary.to_string(index=False))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
