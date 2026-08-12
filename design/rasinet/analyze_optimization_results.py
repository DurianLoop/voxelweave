from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from scipy import stats

from .icassp_statistics import ranking_metrics
from .optimization_protocol import PRIMARY_TARGETS, case_names, folds, prediction_path, profile_sources
from .run_candidate_optimization import OUT, cid, generated, load, target_mask, write_csv


def attribution(rows: list[dict[str, Any]], stage: str) -> list[dict[str, Any]]:
    grouped=defaultdict(list)
    for row in rows: grouped[(row["candidate_id"],row["dataset"],int(row["scale"]))].append(row)
    output=[]
    for (candidate,dataset,scale),group in grouped.items():
        by_target={target:sorted([r for r in group if r["target_model"]==target],key=lambda r:r["case"]) for target in PRIMARY_TARGETS}
        if any(not by_target[t] for t in PRIMARY_TARGETS): continue
        cases=[r["case"] for r in by_target[PRIMARY_TARGETS[0]]]
        matrices=[]
        for rep in range(2001):
            idx=np.arange(len(cases)) if rep==0 else np.random.default_rng(20260740+rep).integers(0,len(cases),len(cases))
            matrix=np.zeros((3,3))
            for i,st in enumerate(PRIMARY_TARGETS):
                scores=np.asarray([float(r["score"]) for r in by_target[st]])[idx]
                for j,et in enumerate(PRIMARY_TARGETS):
                    errors=np.asarray([float(r["error"]) for r in by_target[et]])[idx]
                    matrix[i,j]=stats.spearmanr(scores,errors).statistic if np.std(scores)>1e-12 else 0.0
            matched=float(np.mean(np.diag(matrix))); mismatched=float(np.mean(matrix[~np.eye(3,dtype=bool)])); matrices.append((matched,mismatched,matched-mismatched,matrix))
        advantages=np.asarray([m[2] for m in matrices[1:]])
        score_array=np.stack([[float(r["score"]) for r in by_target[t]] for t in PRIMARY_TARGETS],axis=1)
        error_array=np.stack([[float(r["error"]) for r in by_target[t]] for t in PRIMARY_TARGETS],axis=1)
        top1=float(np.mean(np.argmax(score_array,axis=1)==np.argmax(error_array,axis=1)))
        within=[stats.spearmanr(score_array[i],error_array[i]).statistic for i in range(len(cases))]
        output.append({"stage":stage,"candidate_id":candidate,"dataset":dataset,"scale":scale,"n":len(cases),"matched_correlation":matrices[0][0],"mismatched_correlation":matrices[0][1],"matched_advantage":matrices[0][2],"matched_advantage_lo":float(np.percentile(advantages,2.5)),"matched_advantage_hi":float(np.percentile(advantages,97.5)),"row_wins":sum(matrices[0][3][i,i]>np.mean(np.delete(matrices[0][3][i],i)) for i in range(3)),"top1_accuracy":top1,"within_case_model_spearman":float(np.nanmean(within))})
    return output


def cross_scale() -> list[dict[str, Any]]:
    baseline_id="c_c98f4ad5b505"
    dev=[r for r in csv.DictReader((OUT/"atomic_per_case.csv").open()) if r["candidate_id"]==baseline_id and r["dataset"]=="fastmri"]
    val=[r for r in csv.DictReader((OUT/"finalist_validation_per_case.csv").open()) if r["candidate_id"]==baseline_id]
    existing=dev+val; lookup={(r["dataset"],int(r["scale"]),r["target_model"],r["case"]):r for r in existing}
    per_case=[]; feasibility=[]
    for dataset in ("fastmri","ningxia"):
        sources={scale:profile_sources(dataset,scale) for scale in (2,4,6)}
        for fold in folds(dataset):
            common=set(case_names(sources[2]["i3net"],fold))
            for scale in (4,6): common &= set(case_names(sources[scale]["i3net"],fold))
            for case in sorted(common):
                for target in PRIMARY_TARGETS:
                    volumes={scale:load(prediction_path(sources[scale][target],fold,case)) for scale in (2,4,6)}
                    shapes={scale:"x".join(map(str,volumes[scale].shape)) for scale in (2,4,6)}
                    if len({v.shape for v in volumes.values()}) != 1:
                        feasibility.append({"dataset":dataset,"case":case,"target_model":target,"status":"not_feasible_shape_mismatch","shape_x2":shapes[2],"shape_x4":shapes[4],"shape_x6":shapes[6]})
                        continue
                    values=[]
                    for a,b in ((2,4),(2,6),(4,6)):
                        ia=set(generated(volumes[a].shape[2],a)); ib=set(generated(volumes[b].shape[2],b)); overlap=np.asarray(sorted(ia&ib),dtype=int)
                        mask=target_mask(volumes[a],overlap)|target_mask(volumes[b],overlap)
                        values.append(float(np.mean(np.abs(volumes[a][:,:,overlap][mask[:,:,overlap]]-volumes[b][:,:,overlap][mask[:,:,overlap]]))))
                    consistency=float(np.median(values))
                    for scale in (2,4,6):
                        row=lookup[(dataset,scale,target,case)]
                        per_case.append({"dataset":dataset,"scale":scale,"case":case,"target_model":target,"cross_scale_score":consistency,"baseline_score":float(row["score"]),"error":float(row["error"])})
    output=[]
    grouped=defaultdict(list)
    for row in per_case: grouped[(row["dataset"],row["scale"],row["target_model"])].append(row)
    for key,group in grouped.items():
        errors=np.asarray([r["error"] for r in group]); cs=np.asarray([r["cross_scale_score"] for r in group]); base=np.asarray([r["baseline_score"] for r in group])
        hybrid=.5*stats.rankdata(cs)/len(cs)+.5*stats.rankdata(base)/len(base)
        for method,scores in (("cross_scale_consistency",cs),("baseline_plus_cross_scale_rank",hybrid)):
            output.append({"dataset":key[0],"scale":key[1],"target_model":key[2],"method":method,"n":len(group),**ranking_metrics(errors,scores)})
    write_csv(OUT/"cross_scale_consistency_per_case.csv",per_case)
    write_csv(OUT/"cross_scale_consistency_feasibility.csv",feasibility)
    if not output:
        output.append({"dataset":"all","scale":"all","target_model":"all","method":"not_feasible_shape_mismatch","n":len(feasibility),"case_spearman":"","normalized_aurc":"","rrr_50":""})
    return output


def main() -> None:
    dev=list(csv.DictReader((OUT/"committee_per_case.csv").open()))
    # Add decomposition rows from the finalist table source when available.
    val=list(csv.DictReader((OUT/"finalist_validation_per_case.csv").open()))
    freeze=yaml.safe_load((OUT/"frozen_finalists.yaml").read_text())
    ids={item["candidate_id"] for item in freeze["finalists"]}
    dev=[r for r in dev if r["candidate_id"] in ids]
    decomp=next(item for item in freeze["finalists"] if item["role"]=="decomposition")
    base_spec={k:v for k,v in decomp.items() if k not in {"role","candidate_id","decomposition","alpha"}}
    base_id=cid(base_spec); base_rows=[r for r in csv.DictReader((OUT/"committee_per_case.csv").open()) if r["candidate_id"]==base_id]
    grouped=defaultdict(list)
    for row in base_rows: grouped[(row["dataset"],row["scale"],row["case"])].append(row)
    for group in grouped.values():
        shared=float(np.median([float(r["score"]) for r in group]))
        for row in group: dev.append({**row,"candidate_id":decomp["candidate_id"],"score":shared})
    write_csv(OUT/"target_attribution_results.csv",attribution(dev,"development")+attribution(val,"validation"))
    write_csv(OUT/"cross_scale_consistency_results.csv",cross_scale())
    print("optimization secondary analyses complete")


if __name__=="__main__": main()
