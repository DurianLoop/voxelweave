from __future__ import annotations

from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

from .icassp_statistics import ranking_metrics
from .optimization_protocol import REPO_ROOT, UNIVERSAL_NEURAL, case_names, folds, prediction_path, profile_sources


ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"/"nested_optimization"


def generated(depth,scale): return [z for z in range(depth) if z%scale]


def planes(image,scale):
    return {z:image.affine[:3,3]+image.affine[:3,2]*z for z in generated(image.shape[2],scale)}


def matches(a,b,tolerance=1e-3):
    result=[]
    for za,pa in a.items():
        distances=[(float(np.linalg.norm(pa-pb)),zb) for zb,pb in b.items()]
        if distances:
            distance,zb=min(distances)
            if distance<=tolerance: result.append((za,zb,distance,pa))
    return result


def mask2(a,b):
    threshold=.01*max(float(np.max(np.abs(a))),float(np.max(np.abs(b))),1e-6)
    return (np.abs(a)>threshold)|(np.abs(b)>threshold)


def main() -> None:
    per_pair=[]; audit=[]
    for dataset in ("fastmri","ningxia"):
      sources={s:profile_sources(dataset,s) for s in (2,4,6)}
      for fold in folds(dataset):
        common=set(case_names(sources[2]["i3net"],fold))
        for scale in (4,6): common &= set(case_names(sources[scale]["i3net"],fold))
        for case in sorted(common):
          for target in UNIVERSAL_NEURAL:
            images={s:nib.load(str(prediction_path(sources[s][target],fold,case))) for s in (2,4,6)}
            for a,b in ((2,4),(2,6),(4,6)):
                matched=matches(planes(images[a],a),planes(images[b],b))
                affine_delta=float(np.max(np.abs(images[a].affine-images[b].affine)))
                row={"dataset":dataset,"fold":fold or "none","case":case,"target_model":target,"scale_a":a,"scale_b":b,
                     "shape_a":"x".join(map(str,images[a].shape)),"shape_b":"x".join(map(str,images[b].shape)),
                     "affine_max_abs_delta":affine_delta,"matched_generated_planes":len(matched),
                     "max_plane_distance_mm":max([m[2] for m in matched],default=float("nan"))}
                if not matched:
                    row.update(status="no_common_generated_physical_plane",consistency=float("nan"))
                elif images[a].shape[:2]!=images[b].shape[:2]:
                    row.update(status="in_plane_shape_mismatch",consistency=float("nan"))
                else:
                    va=images[a].get_fdata(dtype=np.float32); vb=images[b].get_fdata(dtype=np.float32); values=[]
                    for za,zb,_,_ in matched:
                        ma=mask2(va[:,:,za],vb[:,:,zb]); values.append(float(np.mean(np.abs(va[:,:,za][ma]-vb[:,:,zb][ma]))))
                    row.update(status="matched_physical_planes",consistency=float(np.median(values)))
                per_pair.append(row)
                if len(audit)<12: audit.append(row)
    pair=pd.DataFrame(per_pair); pair.to_csv(OUT/"cross_scale_physical_pair_scores.csv",index=False)
    matched_pair=pair[pair.status.eq("matched_physical_planes")].copy()
    # A scale-specific score uses only physical comparisons that involve that
    # scale. This preserves the evaluation-profile identity when joining error.
    case_rows=[]
    for row in matched_pair.itertuples(index=False):
        for evaluation_scale in (row.scale_a,row.scale_b):
            case_rows.append({"dataset":row.dataset,"fold":row.fold,"case":row.case,
                              "target_model":row.target_model,"scale":evaluation_scale,
                              "scale_pair":f"{row.scale_a}-{row.scale_b}",
                              "consistency":row.consistency})
    case=(pd.DataFrame(case_rows)
          .groupby(["dataset","fold","case","target_model","scale"],as_index=False)
          .agg(consistency=("consistency","median"),matched_scale_pairs=("scale_pair","nunique")))
    results=[]
    errors=[]
    for suffix in ("development","ningxia"):
        path=OUT/f"common_errors_per_case_{suffix}.csv"
        if path.exists(): errors.append(pd.read_csv(path))
    error=pd.concat(errors,ignore_index=True)
    expanded=case.merge(error,on=["dataset","fold","case","target_model","scale"],how="inner")
    robust_path=OUT/"ningxia_robust_predictions.csv"
    nested_path=robust_path if robust_path.exists() else OUT/"ningxia_nested_predictions.csv"
    if nested_path.exists():
        nested=pd.read_csv(nested_path)
        preferred="robust_nested_triage" if robust_path.exists() else "nested_triage"
        nested=nested[nested.method.eq(preferred)][["scale","case","target_model","triage_score"]]
        expanded=expanded.merge(nested,on=["scale","case","target_model"],how="left")
    else:
        expanded["triage_score"] = np.nan
    # The pre-specified cross-model baseline is the appropriate rank-hybrid
    # comparator for the three primary targets. Robust nested predictions are
    # retained only as a fallback for extended targets lacking baseline maps.
    old=OUT.parent/"optimization"/"finalist_validation_per_case.csv"
    if old.exists():
        baseline=pd.read_csv(old)
        baseline=baseline[baseline.candidate_id.eq("c_c98f4ad5b505")][["scale","case","target_model","score"]]
        baseline=baseline.rename(columns={"score":"frozen_baseline_score"})
        expanded=expanded.merge(baseline,on=["scale","case","target_model"],how="left")
        expanded["hybrid_source_score"]=expanded.frozen_baseline_score.fillna(expanded.triage_score)
    else:
        expanded["hybrid_source_score"]=expanded.triage_score
    expanded["consistency_rank"] = expanded.groupby(["dataset","scale","target_model"]).consistency.rank(pct=True)
    expanded["disagreement_rank"] = expanded.groupby(["dataset","scale","target_model"]).hybrid_source_score.rank(pct=True)
    expanded["hybrid_score"] = .5*expanded.consistency_rank + .5*expanded.disagreement_rank.fillna(expanded.consistency_rank)
    expanded.to_csv(OUT/"cross_scale_consistency_per_case.csv",index=False)
    for (dataset,scale,target),g in expanded.groupby(["dataset","scale","target_model"]):
        for method,column in (("physical_consistency","consistency"),("frozen_disagreement_plus_physical_rank","hybrid_score")):
            results.append({"dataset":dataset,"scale":scale,"target_model":target,"method":method,"n":len(g),**ranking_metrics(g.common_error.to_numpy(),g[column].to_numpy())})
    pd.DataFrame(results).to_csv(OUT/"cross_scale_consistency_results.csv",index=False)
    matched_count=int(pair.status.eq("matched_physical_planes").sum())
    text=f"""# Cross-Scale Physical Alignment Audit

Array depth is not used as the feasibility criterion. For every case, scale, and target, the physical origin of slice index `z` is computed as `affine[:3,3] + affine[:3,2] * z`. Generated planes are matched only when their world-coordinate origins differ by at most 0.001 mm and both planes are generated at their respective scales.

- Pair records: {len(pair)}
- Physically matched records: {matched_count}
- Unmatched records: {len(pair)-matched_count}
- Scale pairs: ×2/×4, ×2/×6, ×4/×6.
- Observed anchors are excluded before matching.
- Different array depths restrict the shared physical extent but do not by themselves make matching impossible.
- No interpolation or post-validation resampling is used.

Example-level coordinates, affine deltas, shapes, matched-plane counts, and consistency values are stored in `cross_scale_physical_pair_scores.csv`.
"""
    (ROOT/"cross_scale_physical_alignment_audit.md").write_text(text,encoding="utf-8")
    print(f"physical pairs={len(pair)} matched={matched_count} case rows={len(case)}")


if __name__=="__main__": main()
