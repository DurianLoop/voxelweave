"""P7-TMI-E02: clustered endpoint-family contrast for consensus blindness."""

from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy import stats


HERE = Path(__file__).resolve(); P7 = HERE.parents[1]; PAPER = P7.parent
SOURCE = PAPER / "TMI" / "TMI_MANUSCRIPT_MASTER" / "experiments" / "p6_e01_metric_robustness_per_plane.csv"
OUT = P7 / "outputs"; BOOTSTRAPS = 5000; SEED = 20260813
FAMILIES = {
    "intensity_low_frequency": ("mae", "rmse", "mse", "lowfreq_mae"),
    "structural_high_frequency": ("ssim_error", "gradient_mae", "highfreq_mae"),
}


def rho(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    return float(stats.spearmanr(a[ok], b[ok]).statistic) if ok.sum() > 4 and np.std(a[ok]) and np.std(b[ok]) else np.nan


def effects(frame):
    out = {}
    for endpoint in sum((list(v) for v in FAMILIES.values()), []):
        vals = {}
        for condition in ("disjoint", "max_shared"):
            q = frame[frame.condition.eq(condition)]
            vals[condition] = rho(q.disagreement_mae, q[endpoint])
        out[endpoint] = vals["disjoint"] - vals["max_shared"]
    return out


def cluster_rank_moments(frame, endpoint):
    """Per-cluster sufficient statistics for weighted Pearson correlation of global ranks."""
    x = stats.rankdata(frame.disagreement_mae.to_numpy(float))
    y = stats.rankdata(frame[endpoint].to_numpy(float))
    cluster = frame.patient_cluster.astype(str).to_numpy()
    rows = []
    for value in pd.unique(cluster):
        keep = cluster == value; xx = x[keep]; yy = y[keep]
        rows.append([keep.sum(), xx.sum(), yy.sum(), (xx * xx).sum(), (yy * yy).sum(), (xx * yy).sum()])
    return np.asarray(rows, float)


def weighted_corr_from_moments(moment, weights):
    q = weights @ moment
    n, sx, sy, sxx, syy, sxy = (q[:, j] for j in range(6))
    cov = sxy - sx * sy / n
    vx = sxx - sx * sx / n; vy = syy - sy * sy / n
    return cov / np.sqrt(np.maximum(vx * vy, 1e-30))


def main():
    OUT.mkdir(parents=True, exist_ok=True); data = pd.read_csv(SOURCE); rng = np.random.default_rng(SEED)
    endpoint_rows = []; family_rows = []
    for (dataset, model), frame in data.groupby(["dataset", "model"], sort=False):
        clusters = frame.patient_cluster.astype(str).unique(); observed = effects(frame)
        weights = rng.exponential(1.0, size=(BOOTSTRAPS, len(clusters)))
        boots = {}
        for endpoint in observed:
            correlations = {}
            for condition in ("disjoint", "max_shared"):
                q = frame[frame.condition.eq(condition)]
                correlations[condition] = weighted_corr_from_moments(cluster_rank_moments(q, endpoint), weights)
            boots[endpoint] = correlations["disjoint"] - correlations["max_shared"]
        family_boot = (
            np.mean([boots[q] for q in FAMILIES["intensity_low_frequency"]], axis=0)
            - np.mean([boots[q] for q in FAMILIES["structural_high_frequency"]], axis=0)
        )
        for endpoint, value in observed.items():
            b = np.asarray(boots[endpoint], float)
            endpoint_rows.append({"dataset": dataset, "model": model, "patient_clusters": len(clusters), "endpoint": endpoint,
                                  "family": next(k for k, v in FAMILIES.items() if endpoint in v), "delta_disjoint_minus_shared": value,
                                  "cluster_ci_low": float(np.nanquantile(b, .025)), "cluster_ci_high": float(np.nanquantile(b, .975))})
        low = float(np.mean([observed[q] for q in FAMILIES["intensity_low_frequency"]]))
        high = float(np.mean([observed[q] for q in FAMILIES["structural_high_frequency"]]))
        b = np.asarray(family_boot, float)
        family_rows.append({"dataset": dataset, "model": model, "patient_clusters": len(clusters),
                            "mean_intensity_lowfreq_effect": low, "mean_structural_highfreq_effect": high,
                            "family_contrast_low_minus_high": low - high,
                            "cluster_ci_low": float(np.nanquantile(b, .025)), "cluster_ci_high": float(np.nanquantile(b, .975))})
    endpoint = pd.DataFrame(endpoint_rows); family = pd.DataFrame(family_rows)
    endpoint.to_csv(OUT / "p7_tmi_metric_endpoint_effects.csv", index=False); family.to_csv(OUT / "p7_tmi_metric_family_contrast.csv", index=False)
    payload = {"experiment": "P7-TMI-E02", "status": "COMPLETE", "families": FAMILIES,
               "estimand": "mean endpoint Spearman advantage of disjoint over max-shared; family contrast intensity/low-frequency minus structural/high-frequency",
               "inference": "5000-draw examination/patient-cluster Bayesian bootstrap on globally ranked plane observations", "outputs": ["p7_tmi_metric_endpoint_effects.csv", "p7_tmi_metric_family_contrast.csv"]}
    (OUT / "p7_tmi_metric_mechanism.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(endpoint.to_string(index=False)); print("\nFAMILY CONTRAST\n", family.to_string(index=False))


if __name__ == "__main__": main()
