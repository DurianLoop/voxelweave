"""P7-TMI-E01: fixed-coverage MRI QA false-retention audit."""

from pathlib import Path
import json

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve()
P7 = HERE.parents[1]
PAPER = P7.parent
SOURCE = PAPER / "TMI" / "TMI_MANUSCRIPT_MASTER" / "experiments" / "p6_e12_risk_per_case.csv"
OUT = P7 / "outputs"
COVERAGES = (0.3, 0.5, 0.7, 0.9)
METHODS = ("Measurement-disjoint", "Max-shared", "Committee", "Adjacent-anchor MAE")
BOOTSTRAPS = 5000
SEED = 20260813


def retained_indices(score, coverage):
    k = max(1, int(np.ceil(len(score) * coverage)))
    return np.argsort(np.asarray(score, float), kind="stable")[:k]


def event_stats_arrays(score, endpoint, coverage, error_cut):
    retained = retained_indices(score, coverage)
    high = np.asarray(endpoint, float) >= error_cut
    false_retained = int(high[retained].sum())
    high_total = int(high.sum())
    return {
        "retained_n": int(len(retained)),
        "high_error_n": high_total,
        "false_retained_n": false_retained,
        "false_retained_rate_among_high_error": false_retained / high_total if high_total else np.nan,
        "precision_of_flagged": float(high[np.setdiff1d(np.arange(len(high)), retained)].mean())
        if len(retained) < len(high)
        else np.nan,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(SOURCE)
    rng = np.random.default_rng(SEED)
    rows = []
    deltas = []
    for dataset, frame in data.groupby("dataset", sort=False):
        frame = frame.reset_index(drop=True)
        cluster_labels = frame.patient_cluster.astype(str).to_numpy()
        clusters = pd.unique(cluster_labels)
        groups = {c: np.flatnonzero(cluster_labels == c) for c in clusters}
        endpoint = frame.endpoint.to_numpy(float)
        method_values = {m: frame[m].to_numpy(float) for m in METHODS}
        # A cohort-defined top quartile is a QA severity label, not a score threshold.
        error_cut = float(frame.endpoint.quantile(0.75))
        for coverage in COVERAGES:
            observed = {m: event_stats_arrays(method_values[m], endpoint, coverage, error_cut) for m in METHODS}
            boot = {m: [] for m in METHODS}
            delta_boot = {m: [] for m in METHODS if m != "Measurement-disjoint"}
            for _ in range(BOOTSTRAPS):
                chosen = rng.choice(clusters, len(clusters), replace=True)
                ix = np.concatenate([groups[c] for c in chosen])
                # Preserve the frozen cohort severity threshold; do not redefine "high error" per resample.
                vals = {
                    m: event_stats_arrays(method_values[m][ix], endpoint[ix], coverage, error_cut)["false_retained_rate_among_high_error"]
                    for m in METHODS
                }
                for m, v in vals.items():
                    boot[m].append(v)
                for m in delta_boot:
                    delta_boot[m].append(vals[m] - vals["Measurement-disjoint"])
            for method in METHODS:
                b = np.asarray(boot[method], float)
                rows.append({
                    "dataset": dataset,
                    "patient_clusters": int(len(clusters)),
                    "coverage": coverage,
                    "high_error_threshold_q75": error_cut,
                    "method": method,
                    **observed[method],
                    "cluster_ci_low": float(np.nanquantile(b, 0.025)),
                    "cluster_ci_high": float(np.nanquantile(b, 0.975)),
                })
            for comparator, b in delta_boot.items():
                arr = np.asarray(b, float)
                deltas.append({
                    "dataset": dataset,
                    "coverage": coverage,
                    "comparator": comparator,
                    "observed_false_retention_rate_delta_comparator_minus_disjoint": (
                        observed[comparator]["false_retained_rate_among_high_error"]
                        - observed["Measurement-disjoint"]["false_retained_rate_among_high_error"]
                    ),
                    "cluster_ci_low": float(np.nanquantile(arr, 0.025)),
                    "cluster_ci_high": float(np.nanquantile(arr, 0.975)),
                })
    result = pd.DataFrame(rows)
    delta = pd.DataFrame(deltas)
    result.to_csv(OUT / "p7_tmi_operational_false_retention.csv", index=False)
    delta.to_csv(OUT / "p7_tmi_operational_false_retention_deltas.csv", index=False)
    payload = {
        "experiment": "P7-TMI-E01",
        "status": "COMPLETE",
        "severity_definition": "cohort top quartile of common x4 examination MAE",
        "decision": "retain lowest score examinations at prespecified 30/50/70/90% coverage",
        "inference": "5000 examination/patient-cluster bootstrap replicates with frozen cohort error threshold",
        "coverage": ["fastmri", "ixi", "ningxia"],
        "interpretation": "retrospective MRI reconstruction QA; not diagnostic or patient-safety validation",
        "outputs": ["p7_tmi_operational_false_retention.csv", "p7_tmi_operational_false_retention_deltas.csv"],
    }
    (OUT / "p7_tmi_operational_false_retention.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(result.to_string(index=False))
    print("\nPAIRED DELTAS\n", delta.to_string(index=False))


if __name__ == "__main__":
    main()
