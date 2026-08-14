"""Same-case/same-plane comparison of zero vs maximum shared-anchor witnesses."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "plan4_outputs"


def rho(a, b):
    return float(stats.spearmanr(a, b).statistic) if len(a) > 3 and np.std(a) > 0 and np.std(b) > 0 else float("nan")


def auroc(y, score):
    y = np.asarray(y, dtype=bool); score = np.asarray(score)
    return float((stats.rankdata(score)[y].sum() - y.sum() * (y.sum()+1) / 2) / (y.sum() * (~y).sum()))


def auprc(y, score):
    y = np.asarray(y, dtype=bool); order = np.argsort(-np.asarray(score)); yy = y[order]
    return float(np.mean(np.cumsum(yy)[yy] / (np.flatnonzero(yy)+1)))


def metrics(g, score):
    s = g.groupby("target_model")[score].rank(pct=True)
    e = g.phase0_error
    failure = e >= e.groupby(g.target_model).transform(lambda x: x.quantile(.75))
    return {"rho": rho(s, e), "failure_auroc": auroc(failure, s),
            "failure_auprc": auprc(failure, s),
            "top_error_recall_at_25pct": float((s[failure] >= .75).mean()),
            "stable_wrong_rate": float(((s <= .25) & failure).mean())}


def main():
    zero = pd.concat([
        pd.read_csv(OUT / "disjoint_anchor_per_plane.csv"),
        pd.read_csv(OUT / "ningxia_disjoint_per_plane.csv").assign(dataset="ningxia")], ignore_index=True)
    maximum = pd.read_csv(OUT / "max_shared_per_plane.csv")
    keys = ["dataset", "case", "target_model", "z"]
    x = zero[keys + ["disjoint_inconsistency", "phase0_error", "pixel_rho"]].merge(
        maximum[keys + ["max_shared_inconsistency", "phase0_error", "pixel_rho"]], on=keys,
        suffixes=("_zero", "_maximum"), validate="one_to_one")
    # Endpoint must be numerically identical: both are errors of stored phase-0 prediction.
    x["endpoint_absdiff"] = np.abs(x.phase0_error_zero - x.phase0_error_maximum)
    x["phase0_error"] = x.phase0_error_zero
    x.to_csv(OUT / "overlap_zero_vs_max_paired.csv", index=False)
    rng = np.random.default_rng(20260813)
    rows = []
    for dataset, g in x.groupby("dataset"):
        mz, mm = metrics(g, "disjoint_inconsistency"), metrics(g, "max_shared_inconsistency")
        cases = np.array(sorted(g.case.unique()))
        by_case = {c: g[g.case.eq(c)] for c in cases}
        deltas = []
        for _ in range(5000):
            b = pd.concat([by_case[c] for c in rng.choice(cases, len(cases), replace=True)], ignore_index=True)
            deltas.append(metrics(b, "disjoint_inconsistency")["rho"] - metrics(b, "max_shared_inconsistency")["rho"])
        # Paired per-case ranking, complementary to repeated plane observations.
        c = g.groupby(["case", "target_model"], as_index=False).agg(
            zero=("disjoint_inconsistency", "median"), maximum=("max_shared_inconsistency", "median"), error=("phase0_error", "median"))
        crz = rho(c.groupby("target_model").zero.rank(pct=True), c.error)
        crm = rho(c.groupby("target_model").maximum.rank(pct=True), c.error)
        rows.append({"dataset": dataset, "cases": len(cases), "planes": len(g), "zero_shared": mz,
                     "maximum_shared": mm, "delta_plane_rho": mz["rho"] - mm["rho"],
                     "case_cluster_95ci": [float(np.nanquantile(deltas, .025)), float(np.nanquantile(deltas, .975))],
                     "zero_case_rho": crz, "maximum_case_rho": crm, "delta_case_rho": crz-crm,
                     "median_pixel_rho_zero": float(g.pixel_rho_zero.median()),
                     "median_pixel_rho_maximum": float(g.pixel_rho_maximum.median()),
                     "max_endpoint_absdiff": float(g.endpoint_absdiff.max())})
        for model,g0 in g.groupby('target_model'):
            z0,m0=metrics(g0,'disjoint_inconsistency'),metrics(g0,'max_shared_inconsistency');cs=np.array(sorted(g0.case.unique()));bc={c:g0[g0.case.eq(c)] for c in cs};dd=[]
            for _ in range(5000):
                b=pd.concat([bc[c] for c in rng.choice(cs,len(cs),replace=True)],ignore_index=True)
                dd.append(metrics(b,'disjoint_inconsistency')['rho']-metrics(b,'max_shared_inconsistency')['rho'])
            rows.append({'dataset':dataset,'target_model':model,'cases':len(cs),'planes':len(g0),'zero_shared':z0,'maximum_shared':m0,
                         'delta_plane_rho':z0['rho']-m0['rho'],'case_cluster_95ci':[float(np.nanquantile(dd,.025)),float(np.nanquantile(dd,.975))],
                         'median_raw_score_zero':float(g0.disjoint_inconsistency.median()),'median_raw_score_maximum':float(g0.max_shared_inconsistency.median()),
                         'raw_score_ratio_zero_over_maximum':float(g0.disjoint_inconsistency.median()/g0.max_shared_inconsistency.median()),
                         'max_endpoint_absdiff':float(g0.endpoint_absdiff.max())})
    result = {"comparison": "zero versus maximum shared anchors; same target/case/model/plane", "rows": rows}
    pd.json_normalize(rows).to_csv(OUT / "overlap_zero_vs_max_summary.csv", index=False)
    (OUT / "overlap_zero_vs_max_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
