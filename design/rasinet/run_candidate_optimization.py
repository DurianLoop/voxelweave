from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import nibabel as nib
import numpy as np
import yaml
from scipy import ndimage, stats

from .cross_scale_protocol import ningxia_case_group, ningxia_test_group
from .icassp_statistics import ranking_metrics, safe_pearson
from .optimization_protocol import (
    ANALYTICAL, FAMILIES, PRIMARY_TARGETS, REPO_ROOT, UNIVERSAL_NEURAL,
    analytical_path, case_names, folds, gt_path, prediction_path, profile_sources,
)

OUT = Path(__file__).resolve().parent / "outputs" / "optimization"
PROTOCOL = Path(__file__).resolve().parent / "configs" / "selection_protocol.yaml"
DEV = (("ixi", 4), ("fastmri", 2), ("fastmri", 4), ("fastmri", 6))
VAL = (("ningxia", 2), ("ningxia", 4), ("ningxia", 6))
SCORES = (
    "median", "mean", "trimmed", "max", "q75", "q90", "center_mean",
    "center_median", "standardized_mad", "standardized_iqr", "relative",
    "gradient", "laplacian", "all_output_spread",
)
ATOMIC_SCORES = tuple(name for name in SCORES if name not in {"gradient", "laplacian"})
TAIL_PRIORITY = {"median", "standardized_mad", "relative", "all_output_spread"}
MASKS = ("target_0.01", "committee_union", "input_derived")
POOLS = (
    ("mean", "mean"), ("q90", "mean"), ("top10_mean", "mean"),
    ("mean", "max"), ("mean", "q90"), ("mean", "worst2_mean"),
    ("q90", "max"), ("q90", "q90"), ("top10_mean", "cvar90"),
)


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    records = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in records:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fields)
        writer.writeheader(); writer.writerows(records)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cid(spec: dict[str, Any]) -> str:
    payload = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return "c_" + hashlib.sha256(payload.encode()).hexdigest()[:12]


def load(path: Path) -> np.ndarray:
    data = nib.load(str(path)).get_fdata(dtype=np.float32)
    if data.ndim != 3 or not np.isfinite(data).all():
        raise ValueError(f"invalid volume {path}")
    return data


def generated(depth: int, scale: int) -> np.ndarray:
    return np.asarray([z for z in range(depth) if z % scale != 0], dtype=int)


def target_mask(volume: np.ndarray, indices: np.ndarray, fraction: float = .01) -> np.ndarray:
    threshold = max(1e-6, fraction * float(np.max(np.abs(volume[:, :, indices]))))
    return np.abs(volume) > threshold


def masks_for(target: np.ndarray, committee: dict[str, np.ndarray], indices: np.ndarray, scale: int) -> dict[str, np.ndarray]:
    tm = target_mask(target, indices)
    cms = [target_mask(v, indices) for v in committee.values()]
    union = np.logical_or.reduce(cms)
    anchors = np.asarray([z for z in range(target.shape[2]) if z % scale == 0], dtype=int)
    anchor_mask = target_mask(target, anchors)
    inp = np.empty_like(tm)
    for z in range(target.shape[2]):
        inp[:, :, z] = anchor_mask[:, :, anchors[np.argmin(np.abs(anchors - z))]]
    return {"target_0.01": tm, "committee_union": union, "input_derived": inp}


def gradient(a: np.ndarray) -> np.ndarray:
    gs = np.gradient(a, edge_order=1)
    return np.sqrt(sum(g * g for g in gs)).astype(np.float32)


def maps_for(
    target: np.ndarray,
    committee: dict[str, np.ndarray],
    all_outputs: dict[str, np.ndarray],
    needed: set[str] | None = None,
    target_name: str | None = None,
    gradients: dict[str, np.ndarray] | None = None,
    laplacians: dict[str, np.ndarray] | None = None,
) -> dict[str, np.ndarray]:
    needed = set(SCORES) if needed is None else set(needed)
    members = np.stack([committee[n] for n in sorted(committee)], axis=0)
    diffs = np.abs(members - target[None])
    names = tuple(sorted(committee))
    grad = lap = None
    if "gradient" in needed:
        tg = gradients[target_name] if gradients is not None and target_name is not None else gradient(target)
        peers = [gradients[n] if gradients is not None else gradient(committee[n]) for n in names]
        grad = np.median(np.stack([np.abs(tg - value) for value in peers]), axis=0)
    if "laplacian" in needed:
        tl = laplacians[target_name] if laplacians is not None and target_name is not None else ndimage.laplace(target, mode="nearest")
        peers = [laplacians[n] if laplacians is not None else ndimage.laplace(committee[n], mode="nearest") for n in names]
        lap = np.median(np.stack([np.abs(tl - value) for value in peers]), axis=0)
    result = {}
    if "median" in needed: result["median"] = np.median(diffs,axis=0)
    if "mean" in needed: result["mean"] = np.mean(diffs,axis=0)
    if "trimmed" in needed:
        ordered=np.sort(diffs,axis=0); result["trimmed"]=np.mean(ordered[1:-1],axis=0) if len(committee)>2 else np.mean(ordered,axis=0)
    if "max" in needed: result["max"]=np.max(diffs,axis=0)
    if "q75" in needed: result["q75"]=np.quantile(diffs,.75,axis=0)
    if "q90" in needed: result["q90"]=np.quantile(diffs,.90,axis=0)
    center=None
    if needed & {"center_median","standardized_mad","standardized_iqr"}: center=np.median(members,axis=0)
    if "center_mean" in needed: result["center_mean"]=np.abs(target-np.mean(members,axis=0))
    if "center_median" in needed: result["center_median"]=np.abs(target-center)
    if needed & {"standardized_mad","standardized_iqr","relative"}:
        spread_mad=np.median(np.abs(members-center[None]),axis=0) if center is not None else np.median(np.abs(members-np.median(members,axis=0)[None]),axis=0)
        positive=spread_mad[spread_mad>0]; epsilon=max(1e-6,.01*float(np.median(positive)) if positive.size else 1e-6)
        if "standardized_mad" in needed: result["standardized_mad"]=np.clip(np.abs(target-center)/(spread_mad+epsilon),0,20)
        if "standardized_iqr" in needed:
            q1,q3=np.quantile(members,[.25,.75],axis=0); result["standardized_iqr"]=np.clip(np.abs(target-center)/(q3-q1+epsilon),0,20)
        if "relative" in needed: result["relative"]=np.median(diffs/(np.abs(members)+np.abs(target[None])+epsilon),axis=0)
    if "all_output_spread" in needed: result["all_output_spread"]=np.std(np.stack([all_outputs[n] for n in sorted(all_outputs)],axis=0),axis=0)
    if grad is not None: result["gradient"] = grad
    if lap is not None: result["laplacian"] = lap
    return {name: value for name, value in result.items() if name in needed}


def pool(score: np.ndarray, mask: np.ndarray, indices: np.ndarray, voxel: str, exam: str) -> float:
    slices: list[float] = []
    for z in indices:
        values = score[:, :, z][mask[:, :, z]]
        if not values.size:
            continue
        if voxel == "mean": value = float(np.mean(values))
        elif voxel == "q90": value = float(np.quantile(values, .90))
        else:
            k = max(1, int(math.ceil(.10 * values.size)))
            value = float(np.mean(np.partition(values, values.size - k)[-k:]))
        slices.append(value)
    a = np.asarray(slices, dtype=float)
    if exam == "mean": return float(np.mean(a))
    if exam == "max": return float(np.max(a))
    if exam == "q90": return float(np.quantile(a, .90))
    if exam == "worst2_mean": return float(np.mean(np.sort(a)[-min(2, a.size):]))
    k = max(1, int(math.ceil(.10 * a.size)))
    return float(np.mean(np.sort(a)[-k:]))


def pool_grid(score: np.ndarray, mask: np.ndarray, indices: np.ndarray) -> dict[tuple[str, str], float]:
    per_voxel = {name: [] for name in ("mean", "q90", "top10_mean")}
    for z in indices:
        values = score[:, :, z][mask[:, :, z]]
        if not values.size: continue
        per_voxel["mean"].append(float(np.mean(values)))
        per_voxel["q90"].append(float(np.quantile(values, .90)))
        k=max(1,int(math.ceil(.10*values.size)))
        per_voxel["top10_mean"].append(float(np.mean(np.partition(values,values.size-k)[-k:])))
    result={}
    for voxel, values in per_voxel.items():
        a=np.asarray(values,dtype=float)
        result[(voxel,"mean")]=float(np.mean(a)); result[(voxel,"max")]=float(np.max(a)); result[(voxel,"q90")]=float(np.quantile(a,.90))
        result[(voxel,"worst2_mean")]=float(np.mean(np.sort(a)[-min(2,a.size):]))
        k=max(1,int(math.ceil(.10*a.size))); result[(voxel,"cvar90")]=float(np.mean(np.sort(a)[-k:]))
    return result


def committee_members(kind: str, target: str, available: set[str], high_fidelity: tuple[str, ...] = ()) -> tuple[str, ...]:
    primary = set(PRIMARY_TARGETS) | set(ANALYTICAL)
    definitions = {
        "frozen_primary": primary,
        "full_universal": set(UNIVERSAL_NEURAL) | set(ANALYTICAL),
        "neural_only": set(UNIVERSAL_NEURAL),
        "analytical_only": set(ANALYTICAL),
        "family_balanced": {"i3net", "hat", "smamba_unet", "arssr", "ressrdiff", "linear", "cubic"},
        "analytical_anchor": {"linear", "cubic", "i3net", "hat"},
        "low_cost": {"linear", "cubic", "i3net"},
        "high_fidelity": set(high_fidelity) | set(ANALYTICAL),
    }
    selected = tuple(sorted((definitions[kind] & available) - {target}))
    if not selected:
        raise ValueError(f"empty committee {kind}/{target}")
    return selected


def iter_cases(dataset: str, scale: int):
    sources = profile_sources(dataset, scale); ref = sources["i3net"]
    for fold in folds(dataset):
        held = ningxia_test_group(REPO_ROOT, fold) if fold else ""
        for case in case_names(ref, fold):
            if fold and ningxia_case_group(case) != held:
                raise ValueError(f"OOF failure {fold}/{case}")
            yield sources, ref, fold, case


def load_case(sources, ref, fold, case) -> tuple[dict[str, np.ndarray], np.ndarray]:
    outputs = {name: load(prediction_path(src, fold, case)) for name, src in sources.items()}
    outputs.update({m: load(analytical_path(ref, fold, m, case)) for m in ANALYTICAL})
    return outputs, load(gt_path(ref, fold, case))


def summarize(per_case: list[dict[str, Any]], stage: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in per_case:
        grouped[(row["candidate_id"], row["dataset"], int(row["scale"]), row["target_model"])].append(row)
    profiles: list[dict[str, Any]] = []
    by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (candidate, dataset, scale, target), rows in grouped.items():
        errors = np.asarray([r["error"] for r in rows]); scores = np.asarray([r["score"] for r in rows])
        metrics = ranking_metrics(errors, scores)
        record = {"candidate_id": candidate, "dataset": dataset, "scale": scale, "target_model": target, "n": len(rows), **metrics}
        profiles.append(record); by_candidate[candidate].append(record)
    aggregates: list[dict[str, Any]] = []
    for candidate, rows in by_candidate.items():
        n = np.asarray([r["normalized_aurc"] for r in rows]); rho = np.asarray([r["case_spearman"] for r in rows])
        rrr = np.asarray([r["rrr_50"] for r in rows])
        aggregates.append({"candidate_id": candidate, "stage": stage, "profile_count": len(rows), "mean_nAURC": float(np.mean(n)), "median_nAURC": float(np.median(n)), "worst_nAURC": float(np.max(n)), "mean_rho": float(np.mean(rho)), "mean_RRR50": float(np.mean(rrr)), "std_nAURC": float(np.std(n))})
    for metric, weight in (("mean_nAURC", 1.0), ("worst_nAURC", .5), ("std_nAURC", .25)):
        ordered = sorted(aggregates, key=lambda x: x[metric])
        for rank, row in enumerate(ordered, 1): row.setdefault("selection_J", 0.0); row["selection_J"] += weight * rank
    return profiles, sorted(aggregates, key=lambda x: x["selection_J"])


def atomic_case_job(job: tuple[str, int, str | None, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    dataset,scale,fold,case=job; sources=profile_sources(dataset,scale); ref=sources["i3net"]
    outputs,gt=load_case(sources,ref,fold,case); indices=generated(gt.shape[2],scale); rows=[]; fidelity=[]
    for model,prediction in outputs.items():
        support=target_mask(prediction,indices); fidelity.append({"dataset":dataset,"scale":scale,"case":case,"model":model,"mae":float(np.mean(np.abs(prediction[:,:,indices][support[:,:,indices]]-gt[:,:,indices][support[:,:,indices]])))})
    for target in PRIMARY_TARGETS:
        tv=outputs[target]; names=committee_members("frozen_primary",target,set(outputs)); committee={n:outputs[n] for n in names}
        maps=maps_for(tv,committee,outputs,needed=set(ATOMIC_SCORES),target_name=target); ms=masks_for(tv,committee,indices,scale)
        es=ms["target_0.01"][:,:,indices]; error=float(np.mean(np.abs(tv[:,:,indices][es]-gt[:,:,indices][es])))
        for score_name in ATOMIC_SCORES:
            for mask_name in MASKS:
                options=POOLS if score_name in TAIL_PRIORITY else (("mean","mean"),)
                pooled=pool_grid(maps[score_name],ms[mask_name],indices) if score_name in TAIL_PRIORITY else None
                for voxel,exam in options:
                    spec={"score_family":score_name,"mask":mask_name,"voxel_pooling":voxel,"examination_pooling":exam,"committee_type":"frozen_primary"}
                    value=pooled[(voxel,exam)] if pooled is not None else pool(maps[score_name],ms[mask_name],indices,voxel,exam)
                    rows.append({"candidate_id":cid(spec),"dataset":dataset,"scale":scale,"case":case,"target_model":target,"score":value,"error":error})
    return rows,fidelity


def atomic_development() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    rows: list[dict[str, Any]] = []; specs: dict[str, dict[str, Any]] = {}; fidelity: list[dict[str, Any]] = []
    start = time.time()
    jobs=[]
    for dataset,scale in DEV:
        for _,_,fold,case in iter_cases(dataset,scale): jobs.append((dataset,scale,fold,case))
    with ProcessPoolExecutor(max_workers=3) as executor:
        for index,(case_rows,case_fidelity) in enumerate(executor.map(atomic_case_job,jobs),1):
            rows.extend(case_rows); fidelity.extend(case_fidelity)
            print(f"atomic {index}/{len(jobs)} rows={len(rows)} elapsed={time.time()-start:.1f}s",flush=True)
    for score_name in ATOMIC_SCORES:
        for mask_name in MASKS:
            options=POOLS if score_name in TAIL_PRIORITY else (("mean","mean"),)
            for voxel,exam in options:
                spec={"score_family":score_name,"mask":mask_name,"voxel_pooling":voxel,"examination_pooling":exam,"committee_type":"frozen_primary"}; specs[cid(spec)]=spec
    write_csv(OUT / "atomic_per_case.csv", rows); write_csv(OUT / "development_fidelity_per_case.csv", fidelity)
    profiles, aggregate = summarize(rows, "atomic")
    write_csv(OUT / "score_search_results.csv", profiles); write_csv(OUT / "pooling_search_results.csv", aggregate)
    return rows, aggregate, specs


def high_fidelity_members() -> tuple[str, ...]:
    rows = read_csv(OUT / "development_fidelity_per_case.csv")
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row["dataset"] == "fastmri" and row["model"] not in ANALYTICAL:
            grouped[row["model"]].append(float(row["mae"]))
    return tuple(name for name, _ in sorted(grouped.items(), key=lambda x: np.mean(x[1]))[:4])


def committee_case_job(job: tuple[str,int,str|None,str,list[dict[str,Any]],tuple[str,...]]) -> list[dict[str,Any]]:
    dataset,scale,fold,case,top_specs,high=job; sources=profile_sources(dataset,scale); ref=sources["i3net"]
    outputs,gt=load_case(sources,ref,fold,case); indices=generated(gt.shape[2],scale); rows=[]
    kinds=("frozen_primary","full_universal","neural_only","analytical_only","family_balanced","analytical_anchor","low_cost","high_fidelity")
    needed={s["score_family"] for s in top_specs}
    gradients={n:gradient(v) for n,v in outputs.items()} if "gradient" in needed else None
    laplacians={n:ndimage.laplace(v,mode="nearest") for n,v in outputs.items()} if "laplacian" in needed else None
    for target in PRIMARY_TARGETS:
        tv=outputs[target]
        target_cache={}
        for kind in kinds:
            names=committee_members(kind,target,set(outputs),high); committee={n:outputs[n] for n in names}
            if names not in target_cache:
                target_cache[names]=(maps_for(tv,committee,outputs,needed=needed,target_name=target,gradients=gradients,laplacians=laplacians),masks_for(tv,committee,indices,scale),{})
            maps,ms,cache=target_cache[names]
            es=target_mask(tv,indices)[:,:,indices]; error=float(np.mean(np.abs(tv[:,:,indices][es]-gt[:,:,indices][es])))
            for base in top_specs:
                key=(base["score_family"],base["mask"])
                if key not in cache: cache[key]=pool_grid(maps[key[0]],ms[key[1]],indices)
                spec={**base,"committee_type":kind}; candidate=cid(spec)
                rows.append({"candidate_id":candidate,"dataset":dataset,"scale":scale,"case":case,"target_model":target,"score":cache[key][(base["voxel_pooling"],base["examination_pooling"])],"error":error,"committee_members":";".join(names)})
    return rows


def committee_development(top_specs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    rows: list[dict[str, Any]] = []; specs: dict[str, dict[str, Any]] = {}; high = high_fidelity_members()
    kinds = ("frozen_primary", "full_universal", "neural_only", "analytical_only", "family_balanced", "analytical_anchor", "low_cost", "high_fidelity")
    jobs=[]
    for dataset,scale in DEV:
        for _,_,fold,case in iter_cases(dataset,scale): jobs.append((dataset,scale,fold,case,top_specs,high))
    start=time.time()
    with ProcessPoolExecutor(max_workers=3) as executor:
        for index,case_rows in enumerate(executor.map(committee_case_job,jobs),1):
            rows.extend(case_rows); print(f"committee {index}/{len(jobs)} rows={len(rows)} elapsed={time.time()-start:.1f}s",flush=True)
    for base in top_specs:
        for kind in kinds:
            spec={**base,"committee_type":kind}; specs[cid(spec)]=spec
    write_csv(OUT / "committee_per_case.csv", rows)
    profiles, aggregate = summarize(rows, "committee")
    write_csv(OUT / "committee_search_results.csv", profiles)
    write_csv(OUT / "candidate_screening_results.csv", aggregate)
    return rows, specs


def add_decomposition(rows: list[dict[str, Any]], specs: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    grouped: dict[tuple[str, str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows: grouped[(row["candidate_id"], row["dataset"], int(row["scale"]), row["case"])].append(row)
    out = list(rows)
    for (base_id, dataset, scale, case), group in grouped.items():
        if len(group) != len(PRIMARY_TARGETS): continue
        values = np.asarray([float(r["score"]) for r in group]); med = float(np.median(values)); mad = float(np.median(np.abs(values-med)))
        az = (values-med) / max(mad, 1e-6)
        for alpha in (0.0, .25, .5, .75, 1.0):
            spec = {**specs[base_id], "decomposition": "shared_plus_target_z", "alpha": alpha}
            candidate = cid(spec); specs[candidate] = spec
            for index, row in enumerate(group):
                out.append({**row, "candidate_id": candidate, "score": alpha*med + (1-alpha)*float(az[index])})
    return out, specs


def bootstrap_finalists(rows: list[dict[str, Any]], finalist_ids: list[str], stage: str, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["candidate_id"] in finalist_ids: grouped[(row["candidate_id"], row["dataset"], int(row["scale"]), row["target_model"])].append(row)
    summaries=[]; boots=[]
    for key, group in grouped.items():
        candidate,dataset,scale,target=key; errors=np.asarray([float(r["error"]) for r in group]); scores=np.asarray([float(r["score"]) for r in group]); point=ranking_metrics(errors,scores)
        rng=np.random.default_rng(seed + scale + sum(map(ord,target))); samples=[]
        for rep in range(2000):
            idx=rng.integers(0,len(group),len(group)); metric=ranking_metrics(errors[idx],scores[idx]); samples.append(metric)
            boots.append({"stage":stage,"candidate_id":candidate,"dataset":dataset,"scale":scale,"target_model":target,"replicate":rep,**metric})
        record={"stage":stage,"candidate_id":candidate,"dataset":dataset,"scale":scale,"target_model":target,"n":len(group)}
        for name,value in point.items():
            vals=np.asarray([s[name] for s in samples]); record[name]=value; record[f"{name}_lo"]=float(np.percentile(vals,2.5)); record[f"{name}_hi"]=float(np.percentile(vals,97.5))
        summaries.append(record)
    return summaries,boots


def development() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/"atomic_per_case.csv").exists() and (OUT/"pooling_search_results.csv").exists():
        atomic_agg=[{k:(float(v) if k not in {"candidate_id","stage"} else v) for k,v in row.items()} for row in read_csv(OUT/"pooling_search_results.csv")]
        atomic_specs={}
        for score_name in ATOMIC_SCORES:
            for mask_name in MASKS:
                options=POOLS if score_name in TAIL_PRIORITY else (("mean","mean"),)
                for voxel,exam in options:
                    spec={"score_family":score_name,"mask":mask_name,"voxel_pooling":voxel,"examination_pooling":exam,"committee_type":"frozen_primary"}; atomic_specs[cid(spec)]=spec
        print("resuming from complete atomic cache",flush=True)
    else:
        _, atomic_agg, atomic_specs = atomic_development()
    top25 = atomic_agg[:25]
    # The five best distinct atomic definitions seed committee search; all 25 remain registered.
    baseline_spec={"score_family":"median","mask":"target_0.01","voxel_pooling":"mean","examination_pooling":"mean","committee_type":"frozen_primary"}
    top_specs=[baseline_spec]; seen={"median"}
    for row in top25:
        spec=atomic_specs[row["candidate_id"]]
        if spec not in top_specs and (spec["score_family"] not in seen or len(top_specs)<2):
            top_specs.append(spec); seen.add(spec["score_family"])
        if len(top_specs)==5: break
    committee_rows, specs = committee_development(top_specs)
    combined, specs = add_decomposition(committee_rows, specs)
    profiles, aggregate = summarize(combined, "development_final")
    write_csv(OUT / "finalist_development_all_candidates.csv", profiles)
    # Universal, low-cost, and decomposition finalists are frozen independently.
    spec_by_id=specs
    universal=next(r for r in aggregate if spec_by_id[r["candidate_id"]].get("committee_type") not in {"low_cost","analytical_only"} and "decomposition" not in spec_by_id[r["candidate_id"]])
    low=next(r for r in aggregate if spec_by_id[r["candidate_id"]].get("committee_type") in {"low_cost","analytical_anchor"} and "decomposition" not in spec_by_id[r["candidate_id"]])
    decomposed=next(r for r in aggregate if "decomposition" in spec_by_id[r["candidate_id"]])
    baseline_id=cid(baseline_spec); spec_by_id[baseline_id]=baseline_spec
    finalist_ids=[baseline_id,universal["candidate_id"],low["candidate_id"],decomposed["candidate_id"]]
    # Ensure baseline rows exist even when it was not among the five Stage-B seeds.
    if not any(r["candidate_id"]==baseline_id for r in combined):
        raise RuntimeError("baseline missing from committee search; increase atomic seed coverage")
    summary,boot=bootstrap_finalists(combined,finalist_ids,"development",20260732)
    write_csv(OUT/"finalist_development_results.csv",summary); write_csv(OUT/"finalist_development_bootstrap.csv",boot)
    freeze={"frozen_at":datetime.now(timezone.utc).isoformat(),"validation_results_observed_after_this_file":False,"finalists":[{"role":role,"candidate_id":fid,**spec_by_id[fid]} for role,fid in zip(("baseline","universal","low_cost","decomposition"),finalist_ids)],"high_fidelity_members":list(high_fidelity_members())}
    (OUT/"frozen_finalists.yaml").write_text(yaml.safe_dump(freeze,sort_keys=False),encoding="utf-8")
    registry=[]
    selected=set(finalist_ids)
    for candidate,spec in {**atomic_specs,**spec_by_id}.items():
        agg=next((r for r in aggregate if r["candidate_id"]==candidate),None)
        registry.append({"candidate_id":candidate,**spec,"development_profiles":"ixi_x4;fastmri_x2;fastmri_x4;fastmri_x6","validation_status":"frozen_pending" if candidate in selected else "not_selected","mean_dev_nAURC":agg["mean_nAURC"] if agg else "","worst_dev_nAURC":agg["worst_nAURC"] if agg else "","mean_dev_rho":agg["mean_rho"] if agg else "","committee_size":"variable","selected_stage":"finalist" if candidate in selected else "screening","exclusion_reason":"" if candidate in selected else "not_selected_by_frozen_rule","timestamp":freeze["frozen_at"]})
    write_csv(OUT/"candidate_registry.csv",registry)
    print(json.dumps(freeze,indent=2))


def validation_case_job(job: tuple[str,int,str|None,str,list[dict[str,Any]],tuple[str,...]]) -> list[dict[str,Any]]:
    dataset,scale,fold,case,finalist_specs,high=job; sources=profile_sources(dataset,scale); ref=sources["i3net"]
    outputs,gt=load_case(sources,ref,fold,case); indices=generated(gt.shape[2],scale); case_rows=[]
    for target in PRIMARY_TARGETS:
        tv=outputs[target]; cache={}
        es=target_mask(tv,indices)[:,:,indices]; error=float(np.mean(np.abs(tv[:,:,indices][es]-gt[:,:,indices][es])))
        for item in finalist_specs:
            role=item["role"]; kind=item["committee_type"]; names=committee_members(kind,target,set(outputs),high)
            key=(names,item["score_family"],item["mask"])
            if key not in cache:
                committee={n:outputs[n] for n in names}; maps=maps_for(tv,committee,outputs,needed={item["score_family"]},target_name=target); ms=masks_for(tv,committee,indices,scale)
                score_map=maps[item["score_family"]]; mask=ms[item["mask"]]
                raw=pool(score_map,mask,indices,item["voxel_pooling"],item["examination_pooling"])
                corr=safe_pearson(score_map[:,:,indices][mask[:,:,indices]],np.abs(tv[:,:,indices][mask[:,:,indices]]-gt[:,:,indices][mask[:,:,indices]])); cache[key]=(raw,corr)
            raw,corr=cache[key]
            case_rows.append({"candidate_id":item["candidate_id"],"role":role,"dataset":dataset,"scale":scale,"case":case,"target_model":target,"score":raw,"error":error,"pixel_corr":corr,"committee_members":";".join(names),"alpha":item.get("alpha","")})
    decomposition=[r for r in case_rows if r["role"]=="decomposition"]
    if decomposition:
        values=np.asarray([float(r["score"]) for r in decomposition]); med=float(np.median(values)); mad=max(float(np.median(np.abs(values-med))),1e-6)
        for row in decomposition:
            alpha=float(row["alpha"]); row["score"]=alpha*med+(1-alpha)*(float(row["score"])-med)/mad
    return case_rows


def evaluate_specs(profiles, finalist_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows=[]; high=tuple(yaml.safe_load((OUT/"frozen_finalists.yaml").read_text())["high_fidelity_members"]); jobs=[]
    for dataset,scale in profiles:
        for _,_,fold,case in iter_cases(dataset,scale): jobs.append((dataset,scale,fold,case,finalist_specs,high))
    start=time.time()
    with ProcessPoolExecutor(max_workers=3) as executor:
        for index,case_rows in enumerate(executor.map(validation_case_job,jobs),1):
            rows.extend(case_rows); print(f"validation {index}/{len(jobs)} rows={len(rows)} elapsed={time.time()-start:.1f}s",flush=True)
    return rows


def paired_bootstrap(rows: list[dict[str,Any]], specs: list[dict[str,Any]]) -> list[dict[str,Any]]:
    by_key=defaultdict(list)
    for row in rows: by_key[(row["dataset"],row["scale"],row["target_model"],row["role"])].append(row)
    output=[]; baseline="baseline"
    roles=[s["role"] for s in specs if s["role"]!=baseline]
    for dataset,scale,target,role in {(k[0],k[1],k[2],k[3]) for k in by_key if k[3] in roles}:
        a=sorted(by_key[(dataset,scale,target,role)],key=lambda r:r["case"]); b=sorted(by_key[(dataset,scale,target,baseline)],key=lambda r:r["case"])
        errors=np.asarray([float(r["error"]) for r in a]); sa=np.asarray([float(r["score"]) for r in a]); sb=np.asarray([float(r["score"]) for r in b]); rng=np.random.default_rng(20260733+int(scale)); diffs=[]
        for rep in range(2000):
            idx=rng.integers(0,len(a),len(a)); delta=ranking_metrics(errors[idx],sa[idx])["normalized_aurc"]-ranking_metrics(errors[idx],sb[idx])["normalized_aurc"]; diffs.append(delta); output.append({"dataset":dataset,"scale":scale,"target_model":target,"role":role,"replicate":rep,"delta_nAURC":delta})
    return output


def validation() -> None:
    freeze=yaml.safe_load((OUT/"frozen_finalists.yaml").read_text(encoding="utf-8")); specs=freeze["finalists"]
    rows=evaluate_specs(VAL,specs); write_csv(OUT/"finalist_validation_per_case.csv",rows)
    ids=[s["candidate_id"] for s in specs]; summary,boot=bootstrap_finalists(rows,ids,"validation",20260733)
    write_csv(OUT/"finalist_validation_results.csv",summary); write_csv(OUT/"finalist_validation_bootstrap.csv",boot)
    paired=paired_bootstrap(rows,specs); write_csv(OUT/"finalist_paired_bootstrap.csv",paired)
    freeze["validation_results_observed_after_this_file"]=True; freeze["validation_completed_at"]=datetime.now(timezone.utc).isoformat(); (OUT/"frozen_finalists_validated.yaml").write_text(yaml.safe_dump(freeze,sort_keys=False),encoding="utf-8")
    print(f"validation rows={len(rows)} summaries={len(summary)}")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--stage",choices=("development","validation"),required=True); args=parser.parse_args()
    if args.stage=="development": development()
    else: validation()


if __name__=="__main__": main()
