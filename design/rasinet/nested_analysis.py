from __future__ import annotations

import json
import math
import time
from collections import defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

from .icassp_statistics import ranking_metrics
from .optimization_protocol import ANALYTICAL, REPO_ROOT, UNIVERSAL_NEURAL, case_names, folds, prediction_path, profile_sources
from .cross_scale_protocol import ningxia_case_group


ROOT=Path(__file__).resolve().parent
OLD=ROOT/"outputs"/"optimization"
OUT=ROOT/"outputs"/"nested_optimization"
BASELINE_ID="c_c98f4ad5b505"
PRIMARY=("i3net","hat","swinir")


def safe_spearman(a,b):
    if np.std(a) <= 1e-12 or np.std(b) <= 1e-12:
        return 0.0
    value=stats.spearmanr(a,b).statistic
    return float(value) if np.isfinite(value) else 0.0


def transform(train: np.ndarray, values: np.ndarray, kind: str) -> np.ndarray:
    train=np.asarray(train,float); values=np.asarray(values,float)
    if kind in {"empirical_cdf","rank_gaussian"}:
        p=np.searchsorted(np.sort(train),values,side="right")/max(len(train),1)
        if kind=="rank_gaussian": return stats.norm.ppf(np.clip(p,1/(2*len(train)),1-1/(2*len(train))))
        return p
    med=float(np.median(train))
    if kind=="robust_z_iqr": scale=float(np.quantile(train,.75)-np.quantile(train,.25))
    else: scale=float(np.median(np.abs(train-med)))
    return (values-med)/max(scale,1e-6)


def relative(matrix: np.ndarray, mode: str) -> np.ndarray:
    center=np.median(matrix,axis=1,keepdims=True); out=matrix-center
    if mode=="centered_mad":
        scale=np.median(np.abs(out),axis=1,keepdims=True); out=out/np.maximum(scale,1e-6)
    return out


def attr_metrics(scores: np.ndarray, errors: np.ndarray) -> dict[str,float]:
    within=np.mean([safe_spearman(scores[i],errors[i]) for i in range(len(scores))])
    top1=np.mean(np.argmax(scores,axis=1)==np.argmax(errors,axis=1))
    matrix=np.asarray([[safe_spearman(scores[:,i],errors[:,j]) for j in range(scores.shape[1])] for i in range(scores.shape[1])])
    diag=float(np.mean(np.diag(matrix))); off=float(np.mean(matrix[~np.eye(len(matrix),dtype=bool)]))
    pooled=safe_spearman(scores.ravel(),errors.ravel())
    return {"matched_correlation":diag,"mismatched_correlation":off,"matched_advantage":diag-off,
            "within_case_spearman":float(within),"top1_accuracy":float(top1),"pooled_relative_correlation":pooled}


def selected_raw_matrix(scale:int, outer:str, role:str, pairs:pd.DataFrame, manifest:pd.DataFrame, registry:pd.DataFrame):
    cases=sorted(pairs[pairs.scale.eq(scale)].case.unique()); targets=list(UNIVERSAL_NEURAL)
    matrix=np.empty((len(cases),len(targets)))
    for ti,target in enumerate(targets):
        spec_id=manifest[(manifest.scale.eq(scale))&(manifest.outer_fold.eq(outer))&(manifest.target_model.eq(target))&(manifest.role.eq(role))].iloc[0].candidate_id
        spec=registry[registry.candidate_id.eq(spec_id)].iloc[0]
        group=pairs[(pairs.scale.eq(scale))&(pairs.target_model.eq(target))]
        pivot=group.pivot(index="case",columns="member",values=spec.feature).loc[cases]
        members=spec.members.split(";"); values=pivot[members].to_numpy(); weights=np.asarray([float(x) for x in spec.weights.split(";")])
        matrix[:,ti]=(values.sum(axis=1)-values.max(axis=1))/(values.shape[1]-1) if spec.weight_mode=="trim_max" and values.shape[1]>1 else values@weights
    return cases,targets,matrix


def attribution() -> tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    pairs=pd.read_csv(OUT/"pair_features_per_case_ningxia.csv")
    errors_long=pd.read_csv(OUT/"common_errors_per_case_ningxia.csv")
    manifest=pd.read_csv(OUT/"ningxia_nested_selection_manifest.csv")
    robust_manifest=OUT/"ningxia_robust_selection_manifest.csv"
    if robust_manifest.exists():
        manifest=pd.concat([manifest,pd.read_csv(robust_manifest)],ignore_index=True)
    registry=pd.read_csv(OUT/"candidate_registry.csv")
    fold_map=pairs.drop_duplicates("case").set_index("case").fold
    inner_records=[]; outer_records=[]; shared_records=[]
    roles=["nested_triage","nested_low_cost"]
    if robust_manifest.exists(): roles += ["robust_nested_triage","robust_nested_low_cost"]
    for role in roles:
      for scale in (2,4,6):
        err=errors_long[errors_long.scale.eq(scale)].pivot(index="case",columns="target_model",values="common_error")
        for outer in sorted(fold_map.unique()):
            cases,targets,raw=selected_raw_matrix(scale,outer,role,pairs,manifest,registry)
            inner_idx=np.asarray([i for i,c in enumerate(cases) if fold_map.loc[c]!=outer]); outer_idx=np.asarray([i for i,c in enumerate(cases) if fold_map.loc[c]==outer])
            error_matrix=err.loc[cases,targets].to_numpy()
            options=[]
            calibrated_cache={}
            for cal in ("empirical_cdf","robust_z_iqr","robust_z_mad","rank_gaussian"):
                calibrated=np.column_stack([transform(raw[inner_idx,j],raw[:,j],cal) for j in range(len(targets))])
                calibrated_cache[cal]=calibrated
                for rel in ("centered","centered_mad"):
                    metrics=attr_metrics(relative(calibrated[inner_idx],rel),error_matrix[inner_idx])
                    options.append({"role":role,"scale":scale,"outer_fold":outer,"calibration":cal,"relative_mode":rel,**metrics})
            options=pd.DataFrame(options)
            for metric,weight in (("matched_advantage",-1.),("within_case_spearman",-1.),("top1_accuracy",-.5)):
                options[f"rank_{metric}"]=options[metric].rank(method="min",ascending=False)
                options["selection_J"]=options.get("selection_J",0)+(-weight)*options[f"rank_{metric}"]
            chosen=options.sort_values("selection_J").iloc[0]; options["selected"]=False; options.loc[chosen.name,"selected"]=True
            inner_records.extend(options.to_dict("records"))
            calibrated=calibrated_cache[chosen.calibration]; attr=relative(calibrated,chosen.relative_mode)
            for idx in outer_idx:
                shared=float(np.median(calibrated[idx])); shared_error=float(np.median(error_matrix[idx]))
                shared_records.append({"role":role,"scale":scale,"outer_fold":outer,"case":cases[idx],"shared_score":shared,"shared_error":shared_error})
                for j,target in enumerate(targets):
                    outer_records.append({"role":role,"scale":scale,"outer_fold":outer,"case":cases[idx],"target_model":target,
                                          "calibration":chosen.calibration,"relative_mode":chosen.relative_mode,
                                          "attribution_score":attr[idx,j],"common_error":error_matrix[idx,j]})
    inner=pd.DataFrame(inner_records); outer=pd.DataFrame(outer_records); shared=pd.DataFrame(shared_records)
    # Attribution-specific selection compares both nested score/committee roles,
    # not only calibration transforms chosen within each role.
    role_options=inner[inner.selected].copy()
    costs=[]
    for row in role_options.itertuples(index=False):
        members=manifest[(manifest.role.eq(row.role))&(manifest.scale.eq(row.scale))&(manifest.outer_fold.eq(row.outer_fold))].members
        costs.append(float(np.mean([sum(v not in ANALYTICAL for v in value.split(";")) for value in members])))
    role_options["cost_proxy"]=costs; role_options["selected_attribution_final"]=False
    selections=[]
    for (scale,outer_fold),g in role_options.groupby(["scale","outer_fold"]):
        g=g.copy(); g["final_J"]=0.0
        for metric,weight,ascending in (("matched_advantage",1.,False),("within_case_spearman",1.,False),
                                        ("top1_accuracy",.5,False),("cost_proxy",.1,True)):
            g["final_J"] += weight*g[metric].rank(method="min",ascending=ascending)
        chosen=g.sort_values("final_J").iloc[0]
        role_options.loc[chosen.name,"selected_attribution_final"]=True
        selections.append({"scale":scale,"outer_fold":outer_fold,"role":chosen.role,
                           "calibration":chosen.calibration,"relative_mode":chosen.relative_mode,
                           "selection_J":chosen.final_J,"selection_used_outer_labels":False})
    selection=pd.DataFrame(selections)
    inner=inner.merge(role_options[["role","scale","outer_fold","calibration","relative_mode","selected_attribution_final"]],
                      on=["role","scale","outer_fold","calibration","relative_mode"],how="left")
    final_outer=outer.merge(selection,on=["scale","outer_fold","role","calibration","relative_mode"],how="inner")
    outer.to_csv(OUT/"target_attribution_all_candidate_predictions.csv",index=False)
    final_outer.to_csv(OUT/"target_attribution_nested_predictions.csv",index=False)
    selection.to_csv(OUT/"target_attribution_selection_manifest.csv",index=False)
    inner.to_csv(OUT/"target_attribution_inner_selection.csv",index=False)
    results=[]
    for scale,g in final_outer.groupby("scale"):
        s=g.pivot(index="case",columns="target_model",values="attribution_score").loc[:,list(UNIVERSAL_NEURAL)].to_numpy()
        e=g.pivot(index="case",columns="target_model",values="common_error").loc[:,list(UNIVERSAL_NEURAL)].to_numpy()
        results.append({"role":"nested_attribution","scale":scale,"n":s.shape[0],**attr_metrics(s,e)})
    for (role,scale),g in shared.groupby(["role","scale"]):
        results.append({"role":role+"_shared","scale":scale,"n":len(g),**ranking_metrics(g.shared_error.to_numpy(),g.shared_score.to_numpy())})
    result=pd.DataFrame(results); result.to_csv(OUT/"target_attribution_nested_results.csv",index=False)
    return inner,outer,shared


def baseline_and_comparators(pred:pd.DataFrame, shared:pd.DataFrame) -> pd.DataFrame:
    errors=pd.read_csv(OUT/"common_errors_per_case_ningxia.csv")
    pairs=pd.read_csv(OUT/"pair_features_per_case_ningxia.csv")
    old=pd.read_csv(OLD/"finalist_validation_per_case.csv")
    old=old[old.candidate_id.eq(BASELINE_ID)][["scale","case","target_model","score"]]
    common=errors[errors.target_model.isin(PRIMARY)][["scale","case","target_model","common_error"]]
    base=old.merge(common,on=["scale","case","target_model"]); base["method"]="frozen_baseline"; base=base.rename(columns={"score":"triage_score"})
    mean_rows=[]
    primary=set(PRIMARY)|set(ANALYTICAL)
    for (scale,case,target),g in pairs[pairs.target_model.isin(PRIMARY)].groupby(["scale","case","target_model"]):
        members=sorted((primary-{target})&set(g.member)); score=float(g.set_index("member").loc[members,"intensity_mean__target_0.01"].mean())
        err=float(common[(common.scale.eq(scale))&(common.case.eq(case))&(common.target_model.eq(target))].common_error.iloc[0])
        mean_rows.append({"scale":scale,"case":case,"target_model":target,"triage_score":score,"common_error":err,"method":"mean_disagreement"})
    shared_role="robust_nested_triage" if shared.role.eq("robust_nested_triage").any() else "nested_triage"
    shared_map=shared[shared.role.eq(shared_role)][["scale","case","shared_score"]].drop_duplicates()
    shared_cmp=common.merge(shared_map,on=["scale","case"]); shared_cmp["method"]="shared_difficulty"; shared_cmp=shared_cmp.rename(columns={"shared_score":"triage_score"})
    selected=pred[pred.target_model.isin(PRIMARY)][["method","scale","case","target_model","triage_score","common_error"]]
    frames=[selected,base[["method","scale","case","target_model","triage_score","common_error"]],
            pd.DataFrame(mean_rows),shared_cmp[["method","scale","case","target_model","triage_score","common_error"]]]
    physical_path=OUT/"cross_scale_consistency_per_case.csv"
    if physical_path.exists():
        physical=pd.read_csv(physical_path)
        physical=physical[physical.dataset.eq("ningxia")&physical.target_model.isin(PRIMARY)]
        for method,column in (("physical_consistency","consistency"),
                              ("frozen_plus_physical","hybrid_score")):
            p=physical[["scale","case","target_model","common_error",column]].rename(columns={column:"triage_score"})
            p["method"]=method; frames.append(p[["method","scale","case","target_model","triage_score","common_error"]])
    return pd.concat(frames,ignore_index=True)


def bootstrap_finalists(allpred:pd.DataFrame) -> None:
    methods=sorted(allpred.method.unique()); profiles=sorted(set(zip(allpred.scale,allpred.target_model)))
    point=[]; boots=[]; rng=np.random.default_rng(20260821)
    indices={profile:[rng.integers(0,len(allpred[(allpred.scale.eq(profile[0]))&(allpred.target_model.eq(profile[1]))&(allpred.method.eq("frozen_baseline"))]),len(allpred[(allpred.scale.eq(profile[0]))&(allpred.target_model.eq(profile[1]))&(allpred.method.eq("frozen_baseline"))])) for _ in range(2000)] for profile in profiles}
    for method in methods:
      for scale,target in profiles:
        g=allpred[(allpred.method.eq(method))&(allpred.scale.eq(scale))&(allpred.target_model.eq(target))].sort_values("case")
        metric=ranking_metrics(g.common_error.to_numpy(),g.triage_score.to_numpy()); rec={"method":method,"scale":scale,"target_model":target,"n":len(g),**metric}
        samples=[]
        for rep,idx in enumerate(indices[(scale,target)]):
            m=ranking_metrics(g.common_error.to_numpy()[idx],g.triage_score.to_numpy()[idx]); samples.append(m)
            boots.append({"level":"profile","replicate":rep,"method":method,"scale":scale,"target_model":target,**m})
        for key in ("case_spearman","normalized_aurc","rrr_50"):
            rec[key+"_lo"],rec[key+"_hi"]=np.quantile([x[key] for x in samples],[.025,.975])
        point.append(rec)
    boot=pd.DataFrame(boots); comparisons=[]; aggregates=[]
    metric_names=("normalized_aurc","case_spearman","rrr_50")
    # Aggregate inside each aligned replicate. No profile-level samples are
    # flattened into a single percentile distribution.
    for (method,rep),g in boot.groupby(["method","replicate"]):
        for level,key,subset in (
            ("overall","all",g),
            *[("scale",str(scale),g[g.scale.eq(scale)]) for scale in sorted(g.scale.unique())],
            *[("target",target,g[g.target_model.eq(target)]) for target in sorted(g.target_model.unique())],
        ):
            aggregates.append({"level":level,"key":key,"replicate":rep,"method":method,
                               **{name:float(subset[name].mean()) for name in metric_names}})
    aggregate_boot=pd.DataFrame(aggregates)
    comparator_pairs=[
        ("nested_triage","frozen_baseline"),
        ("nested_triage","mean_disagreement"),
        ("nested_triage","shared_difficulty"),
        ("nested_triage","nested_low_cost"),
        ("nested_low_cost","frozen_baseline"),
        ("mean_disagreement","frozen_baseline"),
        ("shared_difficulty","frozen_baseline"),
    ]
    if "robust_nested_triage" in methods:
        comparator_pairs += [
            ("robust_nested_triage","frozen_baseline"),
            ("robust_nested_triage","mean_disagreement"),
            ("robust_nested_triage","shared_difficulty"),
            ("robust_nested_triage","robust_nested_low_cost"),
            ("robust_nested_low_cost","frozen_baseline"),
            ("robust_nested_triage","nested_triage"),
        ]
    if "physical_consistency" in methods:
        comparator_pairs += [
            ("physical_consistency","frozen_baseline"),
            ("physical_consistency","mean_disagreement"),
            ("frozen_plus_physical","frozen_baseline"),
            ("frozen_plus_physical","physical_consistency"),
        ]
    for method,comparator in comparator_pairs:
        left=aggregate_boot[aggregate_boot.method.eq(method)]
        right=aggregate_boot[aggregate_boot.method.eq(comparator)]
        merged=left.merge(right,on=["level","key","replicate"],suffixes=("_method","_comparator"))
        for row in merged.itertuples(index=False):
            comparisons.append({"level":row.level,"key":row.key,"replicate":row.replicate,
                                "method":method,"comparator":comparator,
                                **{f"delta_{name}":getattr(row,f"{name}_method")-getattr(row,f"{name}_comparator") for name in metric_names}})
    paired=pd.DataFrame(comparisons); paired.to_csv(OUT/"nested_paired_bootstrap.csv",index=False)
    point_frame=pd.DataFrame(point)
    point_frame.to_csv(OUT/"nested_finalist_results.csv",index=False)
    aggregate_boot.to_csv(OUT/"nested_aggregate_bootstrap.csv",index=False)
    point_aggregates=[]
    for method,g in point_frame.groupby("method"):
        for level,key,subset in (
            ("overall","all",g),
            *[("scale",str(scale),g[g.scale.eq(scale)]) for scale in sorted(g.scale.unique())],
            *[("target",target,g[g.target_model.eq(target)]) for target in sorted(g.target_model.unique())],
        ):
            point_aggregates.append({"level":level,"key":key,"method":method,
                                     **{name:float(subset[name].mean()) for name in metric_names}})
    point_aggregate=pd.DataFrame(point_aggregates)
    aggregate_summary=[]
    for (level,key,method),g in aggregate_boot.groupby(["level","key","method"]):
        row={"level":level,"key":key,"method":method}
        point_row=point_aggregate[(point_aggregate.level.eq(level))&(point_aggregate.key.eq(key))&point_aggregate.method.eq(method)].iloc[0]
        for name in metric_names:
            row[name]=point_row[name]; row[name+"_lo"]=g[name].quantile(.025); row[name+"_hi"]=g[name].quantile(.975)
        aggregate_summary.append(row)
    pd.DataFrame(aggregate_summary).to_csv(OUT/"nested_aggregate_results.csv",index=False)
    paired_summary=[]
    for (level,key,method,comparator),g in paired.groupby(["level","key","method","comparator"]):
        row={"level":level,"key":key,"method":method,"comparator":comparator}
        method_point=point_aggregate[(point_aggregate.level.eq(level))&(point_aggregate.key.eq(key))&point_aggregate.method.eq(method)].iloc[0]
        comparator_point=point_aggregate[(point_aggregate.level.eq(level))&(point_aggregate.key.eq(key))&point_aggregate.method.eq(comparator)].iloc[0]
        for name in metric_names:
            column=f"delta_{name}"; row[column]=method_point[name]-comparator_point[name]; row[column+"_lo"]=g[column].quantile(.025); row[column+"_hi"]=g[column].quantile(.975)
        paired_summary.append(row)
    pd.DataFrame(paired_summary).to_csv(OUT/"profile_aligned_paired_summary.csv",index=False)


def low_cost_pareto() -> None:
    manifest=pd.read_csv(OUT/"ningxia_nested_selection_manifest.csv")
    results=pd.read_csv(OUT/"ningxia_outer_fold_results.csv")
    if (OUT/"ningxia_robust_selection_manifest.csv").exists():
        manifest=pd.concat([manifest,pd.read_csv(OUT/"ningxia_robust_selection_manifest.csv")],ignore_index=True)
        results=pd.concat([results,pd.read_csv(OUT/"ningxia_robust_outer_fold_results.csv")],ignore_index=True)
    rows=[]
    for role,g in results.groupby("method"):
        m=manifest[manifest.role.eq(role)]; neural=m.members.str.split(";").map(lambda x:sum(v not in ANALYTICAL for v in x))
        rows.append({"method":role,"mean_nAURC":g.normalized_aurc.mean(),"worst_nAURC":g.normalized_aurc.max(),"mean_RRR50":g.rrr_50.mean(),"mean_neural_members":neural.mean(),"mean_committee_size":m.members.str.split(";").map(len).mean()})
    out=pd.DataFrame(rows); out["pareto_front"]=True; out.to_csv(OUT/"low_cost_pareto_frontier.csv",index=False)


def main() -> None:
    start=time.time(); _,_,shared=attribution()
    pred=pd.read_csv(OUT/"ningxia_nested_predictions.csv")
    if (OUT/"ningxia_robust_predictions.csv").exists():
        pred=pd.concat([pred,pd.read_csv(OUT/"ningxia_robust_predictions.csv")],ignore_index=True)
    allpred=baseline_and_comparators(pred,shared); allpred.to_csv(OUT/"all_finalist_outer_predictions.csv",index=False)
    bootstrap_finalists(allpred); low_cost_pareto()
    (OUT/"analysis_runtime.json").write_text(json.dumps({"seconds":time.time()-start},indent=2))
    print("nested analysis complete")


if __name__=="__main__": main()
