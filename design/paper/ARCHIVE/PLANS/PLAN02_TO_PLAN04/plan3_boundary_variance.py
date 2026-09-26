"""Plan-3 mechanistic analyses: boundary position, variance decomposition, architecture sharing.

Labels: MECHANISTIC / RETROSPECTIVE. No score tuning is performed.
"""
from __future__ import annotations

import json
from itertools import permutations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "plan3_outputs"
P2 = HERE / "plan2_outputs"
ROOT = HERE.parents[1]


def rho(a, b):
    return float(stats.spearmanr(a, b).statistic) if len(a) >= 3 else float("nan")


def boundary_analysis() -> dict:
    frames = []
    for dataset, path in {
        "fastmri": P2 / "localization" / "confirmation" / "per_plane.csv",
        "ningxia": P2 / "localization" / "ningxia_confirmation" / "per_plane.csv",
    }.items():
        f = pd.read_csv(path)
        f["dataset"] = dataset
        frames.append(f)
    x = pd.concat(frames, ignore_index=True)
    keys = ["dataset", "case", "target_model", "pair"]
    x["ordinal"] = x.groupby(keys)["za"].rank(method="dense").astype(int)
    x["n_positions"] = x.groupby(keys)["za"].transform("nunique").astype(int)
    x["relative_position"] = (x.ordinal - 1) / np.maximum(x.n_positions - 1, 1)
    x["position"] = np.where(x.ordinal.eq(1), "first", np.where(x.ordinal.eq(x.n_positions), "last", "interior"))
    x["error_pct"] = x.groupby(["dataset", "target_model", "pair"])["mean_error"].rank(pct=True)
    x["pc_pct"] = x.groupby(["dataset", "target_model", "pair"])["mean_inconsistency"].rank(pct=True)
    x["stable_wrong"] = (x.error_pct >= .75) & (x.pc_pct <= .25)
    x.to_csv(OUT / "boundary_position_per_plane.csv", index=False)
    grouped = x.groupby(["dataset", "pair", "position"], as_index=False).agg(
        planes=("mean_error", "size"), cases=("case", "nunique"), mean_error=("mean_error", "mean"),
        median_error=("mean_error", "median"), mean_inconsistency=("mean_inconsistency", "mean"),
        stable_wrong=("stable_wrong", "sum"))
    grouped["stable_wrong_rate"] = grouped.stable_wrong / grouped.planes
    grouped.to_csv(OUT / "boundary_position_summary.csv", index=False)

    # Conditional odds via exact 2x2 tables, plus case-clustered bootstrap of first-minus-other rate.
    tests = []
    rng = np.random.default_rng(20260830)
    for (dataset, pair), g in x.groupby(["dataset", "pair"]):
        first = g.position.eq("first")
        table = [[int((first & g.stable_wrong).sum()), int((first & ~g.stable_wrong).sum())],
                 [int((~first & g.stable_wrong).sum()), int((~first & ~g.stable_wrong).sum())]]
        odds, p = stats.fisher_exact(table)
        cases = np.array(sorted(g.case.unique()))
        # Pre-aggregate four sufficient counts per case; this is exactly the same
        # case-cluster bootstrap without repeated DataFrame concatenation.
        counts = np.array([[int((q.position.eq("first") & q.stable_wrong).sum()), int(q.position.eq("first").sum()),
                            int((~q.position.eq("first") & q.stable_wrong).sum()), int((~q.position.eq("first")).sum())]
                           for _, q in g.groupby("case")], dtype=float)
        draws = rng.integers(0, len(cases), size=(5000, len(cases)))
        totals = counts[draws].sum(axis=1)
        deltas = totals[:,0] / np.maximum(totals[:,1],1) - totals[:,2] / np.maximum(totals[:,3],1)
        tests.append({"dataset": dataset, "pair": pair, "table": table, "odds_ratio": odds, "fisher_p": p,
                      "first_minus_other_rate": float(g.loc[first, "stable_wrong"].mean() - g.loc[~first, "stable_wrong"].mean()),
                      "cluster_bootstrap_95ci": [float(np.quantile(deltas,.025)), float(np.quantile(deltas,.975))]})
    return {"records": len(x), "tests": tests,
            "source_trace": {"generated_rule": "z % scale != 0", "matching": "world-plane origin <= 0.001 mm",
             "hat_swinir_inference": "each sparse interval uses bilateral left/right anchors and offsets 1..stride-1",
             "i3net_inference": "overlapping sparse windows are averaged; uncovered slices raise an error",
             "interpretation": "z=1 is a real superior-volume/first-interval location, not padding or unmatched indexing"}}


def load_errors() -> pd.DataFrame:
    fast = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "nested_optimization" / "common_errors_per_case_development.csv")
    fast = fast[fast.dataset.eq("fastmri") & fast.target_model.isin(["i3net","hat","swinir"])][["dataset","case","scale","target_model","common_error"]]
    ning = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "nested_optimization" / "all_finalist_outer_predictions.csv")
    ning = ning[ning.method.eq("physical_consistency")][["case","scale","target_model","common_error"]].drop_duplicates()
    ning.insert(0, "dataset", "ningxia")
    return pd.concat([fast, ning], ignore_index=True)


def orthogonal_variance(g: pd.DataFrame) -> dict:
    cases, models, scales = sorted(g.case.unique()), sorted(g.target_model.unique()), sorted(g.scale.unique())
    a = g.pivot_table(index="case", columns=["target_model","scale"], values="common_error").loc[cases]
    y = np.stack([[a.loc[c,(m,s)] for s in scales] for c in cases for m in models]).reshape(len(cases),len(models),len(scales))
    mu = y.mean(); c = y.mean((1,2))-mu; m=y.mean((0,2))-mu; s=y.mean((0,1))-mu
    cm=y.mean(2)-mu-c[:,None]-m[None,:]
    cs=y.mean(1)-mu-c[:,None]-s[None,:]
    ms=y.mean(0)-mu-m[:,None]-s[None,:]
    resid=y-(mu+c[:,None,None]+m[None,:,None]+s[None,None,:]+cm[:,:,None]+cs[:,None,:]+ms[None,:,:])
    ss={"case":len(models)*len(scales)*np.sum(c*c), "model":len(cases)*len(scales)*np.sum(m*m),
        "scale":len(cases)*len(models)*np.sum(s*s), "case_model":len(scales)*np.sum(cm*cm),
        "case_scale":len(models)*np.sum(cs*cs), "model_scale":len(cases)*np.sum(ms*ms), "three_way_residual":np.sum(resid*resid)}
    total=np.sum((y-mu)**2)
    return {k:float(v/total) for k,v in ss.items()}


def variance_analysis() -> dict:
    x=load_errors(); x.to_csv(OUT / "error_balanced_panel.csv",index=False)
    payload={}
    for dataset,g in x.groupby("dataset"):
        model_corr=g.pivot_table(index=["case","scale"],columns="target_model",values="common_error").corr(method="spearman")
        scale_corr=g.pivot_table(index=["case","target_model"],columns="scale",values="common_error").corr(method="spearman")
        case_latent=g.groupby("case").common_error.mean()
        architecture_residual=g.assign(residual=lambda z:z.common_error-z.groupby(["case","scale"]).common_error.transform("mean"))
        payload[dataset]={"n_cases":int(g.case.nunique()),"variance_fraction":orthogonal_variance(g),
            "model_error_spearman":model_corr.to_dict(),"scale_error_spearman":scale_corr.to_dict(),
            "latent_difficulty_sd":float(case_latent.std()),"architecture_residual_sd":float(architecture_residual.residual.std())}
        model_corr.to_csv(OUT/f"{dataset}_architecture_error_correlations.csv")
        scale_corr.to_csv(OUT/f"{dataset}_factor_error_correlations.csv")
    return payload


def main():
    OUT.mkdir(exist_ok=True)
    result={"boundary":boundary_analysis(),"variance":variance_analysis()}
    (OUT/"boundary_variance_summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__ == "__main__": main()
