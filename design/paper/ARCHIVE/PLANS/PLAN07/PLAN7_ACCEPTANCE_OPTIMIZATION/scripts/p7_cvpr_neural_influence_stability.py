"""P7-CV-E02: prespecified neural finite-difference influence stability audit."""
from __future__ import annotations
import argparse, gc, importlib.util, json, sys, time
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from skimage.transform import resize

HERE = Path(__file__).resolve(); P7 = HERE.parents[1]; PAPER = P7.parent
CV = PAPER / "CVPR" / "CVPR_UPGRADE"; OUT = P7 / "outputs"
BASE_SCRIPT = CV / "scripts" / "plan6_neural_shared_influence.py"
REF = (-2, 2); CONTEXTS = [REF, (-2, 1), (-2, 3), (-1, 2), (-3, 2)]
SEEDS = tuple(range(7101, 7109)); BASELINE = "rad_pos_eps010_n4"

spec = importlib.util.spec_from_file_location("p6inf", BASE_SCRIPT)
p6 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p6)


def rho(a, b):
    a=np.asarray(a,float); b=np.asarray(b,float); ok=np.isfinite(a)&np.isfinite(b)
    return float(stats.spearmanr(a[ok],b[ok]).statistic) if ok.sum()>4 and np.std(a[ok]) and np.std(b[ok]) else np.nan


def patterns(kind):
    ans=[]
    for seed in SEEDS:
        rng=np.random.default_rng(seed)
        if kind=="rademacher": q=rng.choice([-1.,1.],size=(256,256)).astype(np.float32)
        else: q=rng.normal(size=(256,256)).astype(np.float32)
        q-=q.mean(); q/=max(float(q.std()),1e-8); ans.append(q)
    return ans


RAD=patterns("rademacher"); GAUSS=patterns("gaussian")
SPECS = [
    ("rad_pos_eps005_n4", RAD[:4], .005, 1.),
    ("rad_pos_eps010_n1", RAD[:1], .010, 1.),
    ("rad_pos_eps010_n2", RAD[:2], .010, 1.),
    (BASELINE, RAD[:4], .010, 1.),
    ("rad_pos_eps010_n8", RAD[:8], .010, 1.),
    ("rad_pos_eps020_n4", RAD[:4], .020, 1.),
    ("rad_neg_eps010_n4", RAD[:4], .010, -1.),
    ("gauss_pos_eps010_n4", GAUSS[:4], .010, 1.),
]


def cond(norm,z,ctx,anchor,pats,eps,sign):
    l=resize(norm[:,:,z+ctx[0]],(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32)
    r=resize(norm[:,:,z+ctx[1]],(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32)
    rel=float(-ctx[0])/(ctx[1]-ctx[0]); out=[]
    for pat in pats:
        ll=l.copy(); rr=r.copy()
        if anchor==ctx[0]: ll=np.clip(ll+sign*eps*pat,0,1)
        if anchor==ctx[1]: rr=np.clip(rr+sign*eps*pat,0,1)
        coarse=(1-rel)*ll+rel*rr
        out.append(np.stack([ll,rr,coarse,np.full((256,256),rel,np.float32)]))
    return out


def infer_batched(net, conds, batch_size):
    """Bound peak GPU memory while preserving deterministic input order."""
    out=[]
    for start in range(0,len(conds),batch_size):
        out.extend(p6.batch_residual(net,conds[start:start+batch_size]))
    return np.asarray(out)


def one_case(net,gt,z,batch_size):
    lo=float(np.nanmin(gt)); hi=float(np.nanmax(gt)); norm=((gt-lo)/(hi-lo+1e-8)).astype(np.float32)
    y=gt[:,:,z]; mask=np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6)
    preds={}
    for ctx in CONTEXTS:
        c=p6.prepare_cond(norm,z,ctx)[0]; res=p6.batch_residual(net,[c])[0]
        q=np.clip(c[2]+res,0,1); preds[ctx]=resize(q,gt.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo
    outcomes={ctx:p6.metrics(preds[REF],preds[ctx],y,mask) for ctx in CONTEXTS[1:]}
    rows=[]
    for label,pats,eps,sign in SPECS:
        responses={ctx:{} for ctx in CONTEXTS}; all_conds=[]; metadata=[]
        for ctx in CONTEXTS:
            for anchor in ctx:
                cs=cond(norm,z,ctx,anchor,pats,eps,sign)
                start=len(all_conds); all_conds.extend(cs); metadata.append((ctx,anchor,start,len(cs)))
        rr=infer_batched(net,all_conds,batch_size)
        for ctx,anchor,start,count in metadata:
            vec=[]
            for c,res in zip(all_conds[start:start+count],rr[start:start+count]):
                q=np.clip(c[2]+res,0,1); q=resize(q,gt.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo
                vec.append((q-preds[ctx])[mask].astype(np.float32))
            responses[ctx][z+anchor]=vec
        for ctx in CONTEXTS[1:]:
            dots=na=nb=0.
            for k in range(len(pats)):
                for v in responses[REF].values(): na+=float(v[k]@v[k])
                for v in responses[ctx].values(): nb+=float(v[k]@v[k])
                for pos in set(responses[REF])&set(responses[ctx]): dots+=float(responses[REF][pos][k]@responses[ctx][pos][k])
            influence=dots/np.sqrt(na*nb) if na*nb>0 else 0.
            rows.append({"condition":label,"context":str(ctx),"neural_influence":influence,**outcomes[ctx]})
    return rows


def plane_audit():
    raw=pd.read_csv(CV/"outputs"/"plan6_neural_shared_influence_confirm3_per_case_config.csv")
    raw=raw[raw.context.isin([str(q) for q in CONTEXTS[1:]])].copy()
    raw["plane_order"]=raw.groupby(["dataset","model","case"])["z"].rank(method="dense").astype(int)
    rows=[]
    for (ds,model,order),g in raw.groupby(["dataset","model","plane_order"]):
        rows.append({"dataset":ds,"model":model,"plane_order":order,"cases":g.case.nunique(),
                     "rho_error_cosine":rho(g.neural_influence_cosine,g.error_cosine),
                     "rho_shared_fraction":rho(g.neural_influence_cosine,g.shared_fraction),
                     "rho_observable_fraction":rho(g.neural_influence_cosine,g.observable_fraction)})
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dataset",default="all"); ap.add_argument("--device",default="cuda")
    ap.add_argument("--batch-size",type=int,default=4,help="maximum perturbed inputs resident on the accelerator")
    ap.add_argument("--no-resume",action="store_true",help="discard an existing dataset-specific checkpoint")
    a=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True); m=pd.read_csv(CV/"DATA_MANIFEST.csv")
    m=m[(m.factor==4)&m.architecture.isin(["hat","swinir"])]
    if a.dataset!="all":m=m[m.dataset.eq(a.dataset)]
    suffix="" if a.dataset=="all" else "_"+a.dataset
    out_csv=OUT/f"p7_cvpr_neural_influence_stability_per_case_context{suffix}.csv"
    existing=pd.DataFrame()
    if out_csv.exists() and not a.no_resume:
        existing=pd.read_csv(out_csv)
    rows=existing.to_dict("records") if len(existing) else []
    done=set(zip(existing.dataset,existing.model,existing.case)) if len(existing) else set()
    current_key=None; net=None; t0=time.perf_counter()
    for i,r in enumerate(m.itertuples(),1):
        if (r.dataset,r.architecture,r.case_id) in done:
            print(f"P7-CV-E02 {i}/{len(m)} SKIP {r.dataset} {r.architecture} {r.case_id}",flush=True); continue
        ck=p6.checkpoint(r,r.architecture); key=(r.dataset,r.architecture,str(ck))
        if key!=current_key:
            if net is not None:
                del net; gc.collect()
                if a.device.startswith("cuda"): p6.torch.cuda.empty_cache()
            net=p6.load_net(r.dataset,r.architecture,ck,a.device); current_key=key
        gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32); z=int(round((3+gt.shape[2]-4)/2))
        tt=time.perf_counter()
        case_rows=[{"dataset":r.dataset,"case":r.case_id,"patient_cluster":r.patient_cluster,"model":r.architecture,"z":z,**q}
                   for q in one_case(net,gt,z,a.batch_size)]
        rows.extend(case_rows)
        checkpoint=pd.DataFrame(rows); tmp=out_csv.with_suffix(out_csv.suffix+".tmp")
        checkpoint.to_csv(tmp,index=False); tmp.replace(out_csv)
        print(f"P7-CV-E02 {i}/{len(m)} {r.dataset} {r.architecture} {r.case_id} {time.perf_counter()-tt:.2f}s",flush=True)
    x=pd.DataFrame(rows)
    summary=[]
    for (ds,model),g in x.groupby(["dataset","model"]):
        keys=["case","context"]; base=g[g.condition.eq(BASELINE)][keys+["neural_influence"]].rename(columns={"neural_influence":"base"})
        for condition,q in g.groupby("condition"):
            z=q.merge(base,on=keys)
            summary.append({"dataset":ds,"model":model,"condition":condition,"cases":q.case.nunique(),
                            "rank_stability_vs_baseline":rho(z.neural_influence,z.base),
                            "rho_error_cosine":rho(q.neural_influence,q.error_cosine),
                            "rho_shared_fraction":rho(q.neural_influence,q.shared_fraction),
                            "rho_observable_fraction":rho(q.neural_influence,q.observable_fraction)})
    s=pd.DataFrame(summary); s.to_csv(OUT/f"p7_cvpr_neural_influence_stability_summary{suffix}.csv",index=False)
    planes=plane_audit(); planes.to_csv(OUT/"p7_cvpr_neural_influence_plane_stability.csv",index=False)
    nonbase=s[s.condition.ne(BASELINE)]
    gate_by_condition={c:{"strata":int(len(q)),"at_least_085":int((q.rank_stability_vs_baseline>=.85).sum()),
                          "minimum":float(q.rank_stability_vs_baseline.min()),
                          "passed":bool(len(q)==6 and (q.rank_stability_vs_baseline>=.85).sum()>=5 and (q.rank_stability_vs_baseline>=.70).all())}
                       for c,q in nonbase.groupby("condition")}
    passed=bool(gate_by_condition and all(v["passed"] for v in gate_by_condition.values())) if a.dataset=="all" else None
    payload={"experiment":"P7-CV-E02","status":"COMPLETE" if a.dataset=="all" else "PARTIAL",
             "prespecified_primary_gate":"rank stability >=0.85 in at least 5/6 strata per condition and no stratum <0.70",
             "primary_gate_passed":passed,"gate_by_condition":gate_by_condition,"baseline":BASELINE,
             "batch_size":a.batch_size,"resumable_case_checkpoint":str(out_csv),"elapsed_seconds":time.perf_counter()-t0,
             "scope":"central-plane full cohorts for amplitude/sign/field/directions; reused frozen three-plane outputs for plane audit"}
    (OUT/f"p7_cvpr_neural_influence_stability{suffix}.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload,indent=2)); print(s.to_string(index=False)); print(planes.to_string(index=False))


if __name__=="__main__":main()
