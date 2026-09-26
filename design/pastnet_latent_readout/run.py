"""Patient-grouped frozen latent ridge screen. No validation or network updates."""
import argparse, json, time
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Subset
from pastnet_v2.common import PACKAGE, sha256, write_json
from pastnet_v2.run import load_model, code_hashes, seed_all
from pastnet_v2.data import IntervalDataset, device_batch

ROOT=Path(__file__).resolve().parent
CONTROL=PACKAGE/'runs/full_control_seed3407_vram20'
SPLIT=ROOT.parent/'pastnet_residual_audit/results/train_residual_v1/patient_split.json'
LABELS=('low','mid','high')


def project(x):
    h,w=x.shape[-2:]
    fy=torch.fft.fftfreq(h,device=x.device)[:,None]
    fx=torch.fft.rfftfreq(w,device=x.device)[None,:]
    radius=(fy.square()+fx.square()).sqrt()
    spec=torch.fft.rfft2(x.float(),norm='ortho')
    masks=(radius<.10,(radius>=.10)&(radius<.28),radius>=.28)
    return [torch.fft.irfft2(spec*m,s=(h,w),norm='ortho') for m in masks]


def sufficient(x,y,band):
    # Float32 products, followed by float64 accumulation. Bias exists at DC only.
    a=x.permute(0,2,3,1).reshape(-1,64)
    a=torch.cat([torch.ones_like(a[:,:1]) if band==0 else torch.zeros_like(a[:,:1]),a],1)
    b=y.reshape(-1,1)
    xx=(a.T@a)/len(a);xy=(a.T@b)[:,0]/len(a)
    return xx.double().cpu().numpy(),xy.double().cpu().numpy()


def solve(xx,xy,intercept):
    active=np.arange(65) if intercept else np.arange(1,65)
    variance=np.maximum(np.diag(xx)-xx[0]**2,1e-8) if intercept else np.maximum(np.diag(xx),1e-8)
    variance[0]=0
    system=(xx+.001*np.diag(variance))[np.ix_(active,active)]
    rhs=xy[active];solution=np.linalg.solve(system,rhs)
    error=float(np.linalg.norm(system@solution-rhs)/max(np.linalg.norm(rhs),1e-20))
    condition=float(np.linalg.cond(system));assert np.isfinite(condition) and error<=1e-6
    coef=np.zeros(65);coef[active]=solution
    return coef,dict(relative_equation_residual=error,condition_number=condition)


def readout(latent,coefficients,arm):
    def affine(c):
        weight=torch.as_tensor(c[1:],device=latent.device,dtype=torch.float32)
        return torch.einsum('qchw,c->qhw',latent.float(),weight)+float(c[0])
    if arm=='shared':raw=affine(coefficients['shared'])
    else:raw=sum(project(affine(coefficients[k]))[j] for j,k in enumerate(LABELS))
    return raw.clamp(-.05,.05),raw


def summarize(frame,checks,smoke):
    percase=frame.groupby(['group','arm','patient_id','case_id'])[['psnr','mse','mae','clip_fraction','correction_rms']].mean()
    patients=percase.groupby(['group','arm','patient_id']).mean().reset_index()
    check=patients[patients.group=='check']
    tables={a:check[check.arm==a].set_index('patient_id').sort_index() for a in ('baseline','shared','frequency')}
    baseline=tables['baseline'];candidate=tables['frequency'];count=len(baseline)
    assert all(t.index.equals(baseline.index) for t in tables.values())
    hard=baseline.psnr.nsmallest(int(np.ceil(count*.25))).index
    rng=np.random.default_rng(63191);draws=rng.integers(count,size=(10000,count));comparisons={}
    for name,threshold in [('baseline',.05),('shared',.03)]:
        d=(candidate.psnr-tables[name].psnr).to_numpy();boot=d[draws].mean(1)
        ci=np.quantile(boot,[.0125,.9875]);wins=int((d>0).sum())
        comparisons[name]=dict(delta=float(d.mean()),ci95=np.quantile(boot,[.025,.975]).tolist(),
            ci975=ci.tolist(),wins=wins,threshold=threshold,
            passed=bool(d.mean()>=threshold and ci[0]>0 and wins>=np.ceil(.6*count)))
    mae=float((candidate.mae-baseline.mae).mean());mse=float((candidate.mse-baseline.mse).mean())
    worst=float((candidate.psnr-baseline.psnr).loc[hard].mean())
    guards=dict(total=comparisons['baseline']['passed'],increment=comparisons['shared']['passed'],
        mae=mae<=1e-8,mse=mse<=0,hard_quartile=worst>=0,contracts=all(checks.values()),non_smoke=not smoke)
    means=patients.groupby(['group','arm'])[['psnr','mse','mae','clip_fraction','correction_rms']].mean()
    result=dict(check_patients=count,fit_patients=patients[patients.group=='fit'].patient_id.nunique(),
        means={f'{g}/{a}':{k:float(v) for k,v in row.items()} for (g,a),row in means.iterrows()},
        comparisons=comparisons,mae_delta=mae,mse_delta=mse,worst_quartile_psnr_delta=worst,
        guards=guards,eligible_for_registered_validation=all(guards.values()),full_authorized=False,
        validation_used=False,test_used=False,network_weights_updated=False,smoke=smoke)
    return patients,result


@torch.no_grad()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--smoke',action='store_true');args=parser.parse_args()
    out=ROOT/'results'/('smoke' if args.smoke else 'v1')
    if (out/'summary.json').exists():raise FileExistsError(out)
    out.mkdir(parents=True,exist_ok=True);seed_all(3407);torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32=False
    m=json.loads((CONTROL/'manifest.json').read_text(encoding='utf-8'))
    c=json.loads((CONTROL/'completion.json').read_text(encoding='utf-8'))
    assert m['code_hashes']==code_hashes() and c['best_sha256']==sha256(CONTROL/'best.pth')
    assert m['data_sha256']==sha256(m['data_manifest'])
    split=json.loads(SPLIT.read_text(encoding='utf-8'));fit=set(split['fit']);check=set(split['check'])
    assert not fit&check
    if args.smoke:fit=set(sorted(fit)[:2]);check=set(sorted(check)[:2])
    ds=IntervalDataset(m['data_manifest'],'train')
    assert {r['patient_id'] for r in ds.records}==set(split['fit'])|set(split['check'])
    indices=[i for i,(case,z) in enumerate(ds.items) if z%4==0 and ds.records[case]['patient_id'] in fit|check
             and (not args.smoke or z==0)]
    fit_indices=[i for i in indices if ds.records[ds.items[i][0]]['patient_id'] in fit]
    interval_counts=Counter(ds.items[i][0] for i in fit_indices)
    series_counts=Counter(ds.records[case]['patient_id'] for case in interval_counts)
    signature=dict(script_sha256=sha256(__file__),protocol_sha256=sha256(ROOT/'PROTOCOL_ZH.md'),
        original_source_hashes=code_hashes(),checkpoint_sha256=c['best_sha256'],data_sha256=m['data_sha256'],
        split_sha256=sha256(SPLIT),fit=sorted(fit),check=sorted(check),fit_intervals=len(fit_indices),
        total_intervals=len(indices),smoke=args.smoke,validation_used=False,test_used=False)
    write_json(out/'manifest.json',signature)
    model=load_model('control',CONTROL/'best.pth').cuda().eval();captured=[]
    def capture(module,inputs):captured.append(inputs[0])
    handle=model.base.single.decoder.register_forward_pre_hook(capture)
    def forward(batch):
        captured.clear();b=device_batch(batch,torch.device('cuda'))
        with torch.autocast('cuda'):pred=model(b).float()[0,:,0]
        assert len(captured)==2
        return captured[-1].float(),pred,b['target'][0,:,0]
    xx=[np.zeros((65,65)) for _ in LABELS];xy=[np.zeros(65) for _ in LABELS]
    checks=dict(patient_disjoint=True,mixed_latent_capture=True,source_integrity=True)
    start=time.perf_counter();torch.cuda.reset_peak_memory_stats()
    try:
        for n,(idx,batch) in enumerate(zip(fit_indices,DataLoader(Subset(ds,fit_indices),batch_size=1))):
            latent,pred,target=forward(batch);residual=target-pred
            pieces=project(latent);rpieces=project(residual)
            case=ds.items[idx][0];patient=ds.records[case]['patient_id']
            weight=1/(len(fit)*series_counts[patient]*interval_counts[case])
            stats=[sufficient(x,y,j) for j,(x,y) in enumerate(zip(pieces,rpieces))]
            if n==0:
                torch.testing.assert_close(sum(pieces),latent,atol=1e-4,rtol=1e-4)
                torch.testing.assert_close(sum(x.square().mean() for x in pieces),latent.square().mean(),atol=1e-5,rtol=1e-5)
                a=latent.permute(0,2,3,1).reshape(-1,64).double().cpu().numpy()
                a=np.concatenate([np.ones((len(a),1)),a],1);y=residual.reshape(-1).double().cpu().numpy()
                reference_xx=a.T@a/len(a);reference_xy=a.T@y/len(a)
                ex=float(np.linalg.norm(sum(s[0] for s in stats)-reference_xx)/np.linalg.norm(reference_xx))
                ey=float(np.linalg.norm(sum(s[1] for s in stats)-reference_xy)/max(np.linalg.norm(reference_xy),1e-20))
                assert ex<1e-5 and ey<1e-5,(ex,ey)
                co=np.random.default_rng(71).normal(0,.001,65)
                shared,_=readout(latent,dict(shared=co),'shared')
                freq,_=readout(latent,{k:co for k in LABELS},'frequency')
                torch.testing.assert_close(shared,freq,atol=1e-6,rtol=1e-4)
                zero,_=readout(latent,dict(shared=np.zeros(65)),'shared');assert torch.count_nonzero(zero)==0
                checks.update(fft_reconstruction=True,parseval=True,sufficient_statistics_float64=True,
                    tied_coefficients_equal_shared=True,zero_readout_exact=True)
                write_json(out/'numerical_contracts.json',dict(xx_relative_error=ex,xy_relative_error=ey,checks=checks))
            for j in range(3):xx[j]+=weight*stats[j][0];xy[j]+=weight*stats[j][1]
            if (n+1)%20==0:print(f'Fit sufficient statistics {n+1}/{len(fit_indices)}',flush=True)
        coefficients={};solvers={}
        coefficients['shared'],solvers['shared']=solve(sum(xx),sum(xy),True)
        for j,k in enumerate(LABELS):coefficients[k],solvers[k]=solve(xx[j],xy[j],j==0)
        checks['solvers']=True
        np.savez(out/'coefficients.npz',**coefficients)
        np.savez(out/'sufficient_statistics.npz',**{f'xx_{k}':xx[j] for j,k in enumerate(LABELS)},
                 **{f'xy_{k}':xy[j] for j,k in enumerate(LABELS)})
        write_json(out/'solvers.json',solvers)
        rows=[]
        for n,batch in enumerate(DataLoader(Subset(ds,indices),batch_size=1)):
            latent,pred,target=forward(batch);patient=batch['patient_id'][0]
            for arm in ('baseline','shared','frequency'):
                if arm=='baseline':correction=raw=torch.zeros_like(pred)
                else:correction,raw=readout(latent,coefficients,arm)
                error=(pred+correction-target).double()
                for j in range(3):
                    mse=float(error[j].square().mean())
                    rows.append(dict(patient_id=patient,case_id=batch['case_id'][0],z=int(batch['z'][0])+j+1,
                        group='fit' if patient in fit else 'check',arm=arm,psnr=-10*np.log10(max(mse,1e-12)),
                        mse=mse,mae=float(error[j].abs().mean()),clip_fraction=float((raw[j].abs()>.05).float().mean()),
                        correction_rms=float(correction[j].square().mean().sqrt())))
            if (n+1)%40==0:print(f'Frozen readout evaluation {n+1}/{len(indices)}',flush=True)
        frame=pd.DataFrame(rows);frame.to_csv(out/'per_slice.csv',index=False)
        patients,result=summarize(frame,checks,args.smoke);patients.to_csv(out/'per_patient.csv',index=False)
        result.update(elapsed_seconds=time.perf_counter()-start,peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
            fit_intervals=len(fit_indices),total_intervals=len(indices),effective_parameters={'shared':65,'frequency':193})
        write_json(out/'summary.json',result);print(json.dumps(result,indent=2),flush=True)
    finally:handle.remove()


if __name__=='__main__':main()
