"""Two matched convex residual fits differing only in a training MAE constraint."""
import json,importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from scipy.optimize import minimize
from pastnet_v2.common import write_json,sha256
from pastnet_v2.run import seed_all,code_hashes

ROOT=Path(__file__).resolve().parent
CACHE=ROOT.parent/'pastnet_residual_audit/results/train_residual_v1'
SOURCE=ROOT.parent/'pastnet_residual_audit/run_probe.py'
spec=importlib.util.spec_from_file_location('prior_probe',SOURCE)
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)


def up_features(d,j):
    low=prior.feature_maps(d['low'][j],d['anchors'],d['valid'],(j+1)/4)[:,:,:5]
    return F.interpolate(torch.tensor(low,dtype=torch.float32).permute(2,0,1)[None],
        size=d['pred'][j].shape,mode='bilinear',align_corners=False)[0].permute(1,2,0).reshape(-1,5)


def solve_phase(records,fit,j):
    subset=[r for r in records if r['patient_id'] in fit]
    counts=pd.DataFrame(subset).groupby('patient_id').size().to_dict()
    xs=[];ys=[];ws=[]
    for r in subset:
        with np.load(r['path']) as d:
            x=up_features(d,j).cuda();y=torch.tensor((d['target'][j]-d['pred'][j]).ravel(),device='cuda')
            xs.append(x);ys.append(y);ws.append(torch.full_like(y,1/(len(fit)*counts[r['patient_id']]*len(y))))
    x=torch.cat(xs);y=torch.cat(ys);w=torch.cat(ws);del xs,ys,ws
    mean=(x*w[:,None]).sum(0);var=((x-mean).square()*w[:,None]).sum(0)
    mean[0]=0;std=var.sqrt().clamp_min(1e-6);std[0]=1
    x=(x-mean)/std
    mse0=float((y.double().square()*w).sum());mae0=float((y.double().abs()*w).sum())
    cache={}
    def evaluate(beta):
        key=beta.tobytes()
        if cache.get('key')==key:return cache['value']
        b=torch.tensor(beta,dtype=torch.float32,device='cuda')
        correction=.01*(x@b);e=correction-y
        loss=float((e.double().square()*w).sum())/mse0+.001*float(np.dot(beta[1:],beta[1:]))
        grad=(.02*(x.T@(w*e))/mse0).cpu().numpy().astype(np.float64);grad[1:]+=.002*beta[1:]
        mae_delta=float(((e.double().abs()-y.double().abs())*w).sum())
        mae_grad=(.01*(x.T@(w*e.sign()))).cpu().numpy().astype(np.float64)
        idx=correction.abs().argmax();maxabs=float(correction[idx].abs())
        bound_grad=(-.01*x[idx]*correction[idx].sign()/.05).cpu().numpy().astype(np.float64)
        value=(loss,grad,-mae_delta/mae0,-mae_grad/mae0,1-maxabs/.05,bound_grad,mae_delta,maxabs)
        cache.update(key=key,value=value);return value
    fits={}
    for arm in ('mse','mae_constrained'):
        constraints=[dict(type='ineq',fun=lambda b:evaluate(b)[4],jac=lambda b:evaluate(b)[5])]
        if arm=='mae_constrained':constraints.append(dict(type='ineq',fun=lambda b:evaluate(b)[2],jac=lambda b:evaluate(b)[3]))
        solution=minimize(lambda b:evaluate(b)[0],np.zeros(5),jac=lambda b:evaluate(b)[1],method='SLSQP',constraints=constraints,
                          options=dict(maxiter=150,ftol=1e-9))
        v=evaluate(solution.x)
        # Convert back to raw feature coefficients for independently evaluated inference.
        std_np=std.cpu().numpy();mean_np=mean.cpu().numpy()
        raw=.01*solution.x/std_np;raw[0]-=float(np.sum(.01*solution.x*mean_np/std_np))
        fits[arm]=dict(coefficients=raw.tolist(),beta=solution.x.tolist(),converged=bool(solution.success),
            message=str(solution.message),iterations=int(solution.nit),train_mae_delta=v[6],max_abs_fit_correction=v[7],
            feasible=bool(v[7]<=.050001 and (arm=='mse' or v[6]<=1e-8)),train_mse_baseline=mse0,train_mae_baseline=mae0)
        print(json.dumps(dict(phase=(j+1)/4,arm=arm,**fits[arm])),flush=True)
    del x,y,w;torch.cuda.empty_cache()
    return fits


def main():
    seed_all(3407);out=ROOT/'results/v1'
    if out.exists():raise FileExistsError(out)
    manifest=json.loads((CACHE/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['script_sha256']==sha256(SOURCE) and manifest['original_source_hashes']==code_hashes()
    assert manifest['protocol_sha256']==sha256(SOURCE.parent/'PROTOCOL_ZH.md')
    split=json.loads((CACHE/'patient_split.json').read_text(encoding='utf-8'));fit=set(split['fit']);check=set(split['check']);assert not fit&check
    records=pd.read_csv(CACHE/'cache_index.csv',dtype={'patient_id':str}).to_dict('records')
    out.mkdir(parents=True)
    write_json(out/'manifest.json',dict(script_sha256=sha256(__file__),protocol_sha256=sha256(ROOT/'PROTOCOL_ZH.md'),
        cache_manifest_sha256=sha256(CACHE/'manifest.json'),patient_split_sha256=sha256(CACHE/'patient_split.json'),test_used=False))
    phases=[]
    for j in range(3):
        phases.append(solve_phase(records,fit,j));write_json(out/'fits.json',phases)
    rows=[]
    for r in records:
        if r['patient_id'] not in check:continue
        with np.load(r['path']) as d:
            for j in range(3):
                x=up_features(d,j).numpy();target=d['target'][j].ravel();pred=d['pred'][j].ravel()
                for arm in ('baseline','mse','mae_constrained'):
                    correction=np.zeros_like(pred) if arm=='baseline' else (x@np.array(phases[j][arm]['coefficients'])).clip(-.05,.05)
                    e=pred.astype(np.float64)+correction-target;mse=float(np.mean(e*e))
                    rows.append(dict(patient_id=r['patient_id'],case_id=r['case_id'],phase=(j+1)/4,z=r['z']+j+1,
                        arm=arm,psnr=float(-10*np.log10(max(mse,1e-12))),mae=float(np.abs(e).mean()),mse=mse))
    df=pd.DataFrame(rows);df.to_csv(out/'check_per_slice.csv',index=False)
    p=df.groupby(['arm','patient_id','case_id'])[['psnr','mae','mse']].mean().groupby(['arm','patient_id']).mean().reset_index()
    p.to_csv(out/'check_per_patient.csv',index=False)
    frames={a:p[p.arm==a].set_index('patient_id').sort_index() for a in ('baseline','mse','mae_constrained')}
    base=frames['baseline'];hard=base.psnr.nsmallest(int(np.ceil(len(base)*.25))).index
    rng=np.random.default_rng(73019);draw=rng.integers(len(base),size=(10000,len(base)))
    result=dict(check_patients=len(check),baseline_psnr=float(base.psnr.mean()),comparisons={})
    for arm,parent in (('mse','baseline'),('mae_constrained','baseline'),('mae_constrained','mse')):
        a=frames[arm];b=frames[parent];assert a.index.equals(b.index)
        d=(a.psnr-b.psnr).to_numpy();ci=np.quantile(d[draw].mean(1),[.025,.975]).tolist()
        result['comparisons'][arm+'_vs_'+parent]=dict(psnr_delta=float(d.mean()),ci95=ci,wins=int((d>0).sum()),mae_delta=float((a.mae-b.mae).mean()))
    c=result['comparisons']['mae_constrained_vs_baseline'];worst=float((frames['mae_constrained'].psnr-base.psnr).loc[hard].mean())
    solver_ok=all(p['mae_constrained']['converged'] and p['mae_constrained']['feasible'] for p in phases)
    result['guards']=dict(solver=solver_ok,effect=c['psnr_delta']>=.05,ci=c['ci95'][0]>0,wins=c['wins']>=np.ceil(.6*len(base)),mae=c['mae_delta']<=1e-8,hard=worst>=0)
    result['guards']={k:bool(v) for k,v in result['guards'].items()}
    result['eligible_for_validation']=all(result['guards'].values());result['hard_quartile_psnr_delta']=worst
    result['peak_gpu_gib']=torch.cuda.max_memory_allocated()/2**30
    write_json(out/'summary.json',result);print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
