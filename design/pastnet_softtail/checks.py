import argparse,gc,json,math,time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader,Subset
from pastnet_v2.common import PACKAGE,write_json,sha256
from pastnet_v2.run import seed_all
from pastnet_v2.losses import objective as original_objective
from pastnet_v2.data import IntervalDataset,device_batch
from .run import ROOT,load_model,code_hashes
from .losses import objective,tail_risk,TAU


def data(size=256):
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',image_size=size)
    cases=[next(i for i,r in enumerate(ds.records) if r['case_id']==name) for name in
           ('100850027829_t2_axial_2_concats','100944022770_ax_t2')]
    indices=[next(i for i,x in enumerate(ds.items) if x==(case,z)) for case in cases for z in (0,4)]
    return [device_batch(b,torch.device('cuda')) for b in DataLoader(Subset(ds,indices),batch_size=2)]


def weights(error,soft):
    x=error.square().detach().requires_grad_()
    risk=tail_risk(x,soft)
    return torch.autograd.grad(risk,x)[0].detach()*x.shape[0]


def contracts():
    seed_all(3407);batch=data(64)[0];model=load_model('hard_tail').cuda().eval()
    old,_=original_objective(model,batch,4,80,False)
    oldgrads=torch.autograd.grad(old,tuple(model.parameters()),allow_unused=True)
    new,_=objective(model,batch,4,80,False)
    newgrads=torch.autograd.grad(new,tuple(model.parameters()),allow_unused=True)
    torch.testing.assert_close(old,new,atol=0,rtol=0)
    difference=0.
    for a,b in zip(oldgrads,newgrads):
        assert (a is None)==(b is None)
        if a is not None:
            torch.testing.assert_close(a,b,atol=1e-7,rtol=1e-5)
            difference=max(difference,float((a-b).abs().max()))
    with torch.no_grad():
        initial=model(batch);without=dict(batch);without.pop('target');assert torch.equal(model(without),initial)
        softmodel=load_model('soft_tail').cuda().eval();assert torch.equal(softmodel(batch),initial)
        assert all(torch.equal(v,softmodel.state_dict()[k]) for k,v in model.state_dict().items())
        hard,_=objective(model,batch,4,80,False);soft,_=objective(model,batch,4,80,True)
        e=(initial-batch['target']).flatten(0,1)
        torch.testing.assert_close(soft-hard,.2*(tail_risk(e.square(),True)-tail_risk(e.square(),False)),atol=5e-9,rtol=1e-4)
    x=torch.rand(2,1,10,10,device='cuda')*.08;x.requires_grad_()
    soft=tail_risk(x,True);hard=tail_risk(x,False);w=torch.autograd.grad(soft,x)[0]*2
    p=.1;n=100;k=10;entropy=-p*math.log(p)-(1-p)*math.log(1-p)
    assert bool((w>=0).all()) and float(w.max())<=1/k+1e-7
    mass_error=float((w.flatten(1).sum(1)-1).abs().max());assert mass_error<5e-6
    assert -1e-7<=float((soft-hard).detach())<=TAU*entropy/p+1e-6
    assert abs(float((tail_risk(x,True,1e-6)-hard).detach()))<1e-5
    # Independent float64 stationary point and fixed-eta directional derivative.
    v=x.detach().double().cpu().numpy().reshape(2,-1)
    low=v.min(1,keepdims=True)-20*TAU;high=v.max(1,keepdims=True)+20*TAU
    for _ in range(60):
        eta=(low+high)/2;mass=(1/(1+np.exp(-(v-eta)/TAU))).mean(1,keepdims=True)
        low=np.where(mass>p,eta,low);high=np.where(mass>p,high,eta)
    eta=(low+high)/2
    direction=np.random.default_rng(8721).normal(size=v.shape)
    def f(a):return (eta+TAU*np.logaddexp(0,(a-eta)/TAU).mean(1,keepdims=True)/p).mean()
    numeric=(f(v+1e-6*direction)-f(v-1e-6*direction))/(2e-6)
    automatic=float((w.double().cpu().numpy().reshape(2,-1)*direction).sum()/2)
    assert abs(numeric-automatic)<1e-6,(numeric,automatic)
    result=dict(passed=True,hard_loss_exact=True,hard_parameter_gradient_max_difference=difference,
        only_risk_term_changed=True,forward_and_initialization_exact=True,target_not_read=True,
        risk_mass_error=mass_error,nonnegative_bounded_weights=True,small_tau_limit=True,
        smooth_bound=True,directional_derivative_error=abs(numeric-automatic),parameters=sum(p.numel() for p in model.parameters()))
    del model,softmodel,batch,oldgrads,newgrads;gc.collect();torch.cuda.empty_cache();return result


def stability():
    numerical=contracts();seed_all(3407)
    cache=ROOT.parent/'pastnet_residual_audit/results/train_residual_v1'
    source=json.loads((cache/'manifest.json').read_text())
    control=json.loads((PACKAGE/'runs/full_control_seed3407_vram20/completion.json').read_text())
    assert source['split']=='train' and source['checkpoint_sha256']==control['best_sha256']
    idx=pd.read_csv(cache/'cache_index.csv',dtype={'patient_id':str,'case_id':str})
    m=json.loads((PACKAGE/'manifests/fastmri/fold_00.json').read_text())
    assert set(idx.patient_id)=={r['patient_id'] for r in m['records'] if r['split']=='train'}
    assert len(idx)==340 and not idx.duplicated(['case_id','z']).any()
    rng=torch.Generator().manual_seed(93117);rows=[];max_mass=0.;started=time.perf_counter()
    for n,r in enumerate(idx.itertuples()):
        with np.load(r.path) as d:error=torch.from_numpy(d['pred']-d['target']).cuda()[:,None]
        perturb=torch.randn(error.shape,generator=rng).cuda()*.001
        calculated={}
        for soft in (False,True):
            w=weights(error,soft);g=2*error*w;changed=2*(error+perturb)*weights(error+perturb,soft)
            change=(changed-g).flatten(1).norm(dim=1)/g.flatten(1).norm(dim=1).clamp_min(1e-20)
            mass=float((w.flatten(1).sum(1)-1).abs().max());max_mass=max(max_mass,mass)
            assert mass<5e-6 and bool(torch.isfinite(g).all())
            calculated[soft]=(w,change)
        hardmask=calculated[False][0]>0;sw=calculated[True][0]
        for j in range(3):
            rows.append(dict(patient_id=r.patient_id,case_id=r.case_id,z=r.z+j+1,
                hard_gradient_change=float(calculated[False][1][j]),soft_gradient_change=float(calculated[True][1][j]),
                soft_effective_fraction=float(1/sw[j].square().sum()/sw[j].numel()),
                soft_mass_on_hard_tail=float(sw[j][hardmask[j]].sum())))
        if (n+1)%50==0:print(f'Train gradient stability {n+1}/340',flush=True)
    frame=pd.DataFrame(rows);frame.to_csv(ROOT/'results/stability_per_slice.csv',index=False)
    cols=['hard_gradient_change','soft_gradient_change','soft_effective_fraction','soft_mass_on_hard_tail']
    patients=frame.groupby(['patient_id','case_id'])[cols].mean().groupby('patient_id').mean()
    patients.to_csv(ROOT/'results/stability_per_patient.csv');average=patients.mean()
    reduction=1-average.soft_gradient_change/average.hard_gradient_change
    return dict(passed=bool(numerical['passed'] and reduction>=.20),contracts=numerical,
        means={k:float(v) for k,v in average.items()},relative_gradient_change_reduction=float(reduction),
        maximum_weight_mass_error=max_mass,patients=len(patients),intervals=len(idx),elapsed_seconds=time.perf_counter()-started,
        cache_manifest_sha256=sha256(cache/'manifest.json'),code_hashes=code_hashes(),validation_used=False,test_used=False)


@torch.no_grad()
def errors(model,batches):
    model.eval();values=[]
    for b in batches:
        with torch.autocast('cuda'):e=model(b).float()-b['target']
        values.append([float(e.square().mean()),float(e.abs().mean())])
    avg=np.mean(values,axis=0);return dict(mse=float(avg[0]),mae=float(avg[1]))


def train_check(variant,steps,blocks):
    seed_all(3407);batches=data();model=load_model(variant).cuda();model.base.single.checkpoint_blocks=blocks
    opt=torch.optim.AdamW(model.parameters(),lr=2e-5,weight_decay=2e-5,betas=(.9,.99))
    scaler=torch.amp.GradScaler('cuda',init_scale=4096);initial=errors(model,batches);losses=[];times=[]
    start=time.perf_counter();torch.cuda.reset_peak_memory_stats()
    for step in range(steps):
        model.train();opt.zero_grad(set_to_none=True);b=batches[step%2]
        torch.cuda.synchronize();t=time.perf_counter()
        with torch.autocast('cuda'):loss,_=objective(model,b,4,80,variant=='soft_tail')
        scaler.scale(loss).backward();scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
        scaler.step(opt);scaler.update();torch.cuda.synchronize()
        if step>=2:times.append((time.perf_counter()-t)/2*1000)
        losses.append(float(loss.detach()))
        if steps>5 and (step+1)%24==0:print(f'{variant} capacity {step+1}/{steps}',flush=True)
    final=errors(model,batches);reduction=1-final['mse']/initial['mse']
    result=dict(variant=variant,steps=steps,initial=initial,final=final,relative_mse_reduction=reduction,
        passed=bool(reduction>=.05 and final['mae']<=initial['mae']),elapsed_seconds=time.perf_counter()-start,
        peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
        median_ms_interval=float(np.median(times)),losses=losses,checkpoint_saved=False,checkpoint_blocks=blocks)
    del model,opt,scaler,batches;gc.collect();torch.cuda.empty_cache();return result


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['contracts','stability','capacity','bench'])
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if a.action=='contracts':result=contracts()
    elif a.action=='stability':result=stability()
    else:
        arms=[train_check(v,96 if a.action=='capacity' else 5,5) for v in ('hard_tail','soft_tail')]
        result=dict(passed=arms[1]['passed'] if a.action=='capacity' else True,arms=arms,
            code_hashes=code_hashes(),validation_used=False,test_used=False,checkpoint_saved=False)
    write_json(a.out,result)
    compact={k:v for k,v in result.items() if k!='code_hashes'}
    if 'arms' in compact:compact['arms']=[{k:v for k,v in arm.items() if k!='losses'} for arm in compact['arms']]
    print(json.dumps(compact,indent=2),flush=True)


if __name__=='__main__':main()
