"""Real-data and invariance checks; results are not performance evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import time

import torch
from torch.utils.data import DataLoader
from .common import G086,PACKAGE,write_json
from .data import IntervalDataset,device_batch
from .losses import objective,smooth_cvar,reverse_batch
from .model import PASTNetV2,VARIANTS
from .vendor.model_ma3aggressive import PASTNetMA3Aggressive2p5D


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=PACKAGE/'results/smoke.json')
    a=p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    torch.set_num_threads(4); torch.manual_seed(3407)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    payload=torch.load(G086,map_location='cpu',weights_only=False)
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','val',image_size=64,limit=1)
    batch=device_batch(next(iter(DataLoader(ds,batch_size=1))),device)
    old=PASTNetMA3Aggressive2p5D(**payload['model_config']).to(device).eval()
    old.load_state_dict(payload['model_state_dict'],strict=True)
    with torch.no_grad():
        reference=old(batch['cond'])
    del old
    results={}
    for variant in VARIANTS:
        count=VARIANTS[variant][-1]
        dataset=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','val',image_size=64,anchors=count,limit=1)
        data=device_batch(next(iter(DataLoader(dataset,batch_size=1))),device)
        model=PASTNetV2(variant).to(device).eval()
        mapping=model.load_g086(payload)
        with torch.no_grad():
            pred=model(data)
            parity=float((pred-reference).abs().max())
            assert parity<1e-6,(variant,parity)
            altered=dict(data,target=torch.randn_like(data['target']))
            assert torch.equal(pred,model(altered)),'Target leaked to model'
            if count==6:
                altered=dict(data,anchors=data['anchors'].clone())
                altered['anchors'][data['valid']==0]=1000
                assert torch.equal(pred,model(altered)),'Invalid anchors affect identity model'
            twice=reverse_batch(reverse_batch(data))
            for key in ('cond','anchors','valid','physical','anchor_z'):
                assert torch.allclose(data[key],twice[key],atol=1e-5),key
        model.train()
        loss,parts=objective(model,data,1,80,soft_risk=VARIANTS[variant][3])
        loss.backward()
        grads=[p.grad for p in model.parameters() if p.grad is not None]
        assert grads and all(torch.isfinite(g).all() for g in grads)
        new_grads={n:float(p.grad.abs().max()) for n,p in model.named_parameters()
                   if p.grad is not None and ('adapter' in n or 'frequency_decoder' in n)}
        if variant!='control':
            assert max(new_grads.values())>0,(variant,'dead adapters')
        torch.optim.AdamW(model.parameters(),lr=1e-4).step()
        if variant=='correspondence':
            model.eval()
            with torch.no_grad():
                after=model(data)
                changed=dict(data,physical=data['physical'].clone())
                changed['physical'][:,:,0:3]+=1
                assert float((after-model(changed)).abs().max())>0,'Physical adapter insensitive after update'
                changed=dict(data,anchors=data['anchors'].clone())
                changed['anchors'][data['valid']==0]=1000
                assert torch.allclose(after,model(changed),atol=1e-6),'Invalid anchor mask fails after learning'
        results[variant]=dict(parity_max_abs=parity,loss=parts['loss'],mapping=mapping,
                              parameters=sum(p.numel() for p in model.parameters()))
        del model,loss,grads
        print(f'smoke {variant}: passed',flush=True)
    # Smooth CVaR finite gradients for exact reconstruction, ties and huge errors.
    for x in (torch.zeros(2,1,8,8),torch.ones(2,1,8,8),torch.full((2,1,8,8),1e4)):
        x=x.to(device).requires_grad_()
        loss=smooth_cvar(x)
        loss.backward()
        assert torch.isfinite(loss) and torch.isfinite(x.grad).all()
    # Actual production resolution, AMP backward with all proposed switches.
    dataset=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',anchors=6,limit=1)
    data=device_batch(next(iter(DataLoader(dataset,batch_size=1))),device)
    model=PASTNetV2('context').to(device)
    model.load_g086(payload)
    if device.type=='cuda':
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    t0=time.perf_counter()
    with torch.autocast(device.type,enabled=device.type=='cuda'):
        loss,_=objective(model,data,40,80,soft_risk=True)
    loss.backward()
    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
    if device.type=='cuda':
        torch.cuda.synchronize()
    results['full_resolution_backward']=dict(shape=[1,3,13,256,256],seconds=time.perf_counter()-t0,
        peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30 if device.type=='cuda' else None,
        loss=float(loss.detach()))
    write_json(a.out,dict(smoke_only=True,device=str(device),torch_version=torch.__version__,checks=results))
    print(results['full_resolution_backward'],flush=True)


if __name__=='__main__':
    main()
