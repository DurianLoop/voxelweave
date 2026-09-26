import argparse,gc,json,time
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader,Subset
from pastnet_v2.common import PACKAGE,write_json
from pastnet_v2.run import seed_all,load_model as load_control
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.losses import objective,reverse_batch
from .model import AnchorPlaneBlock
from .run import ROOT,load_model,code_hashes


def data(size=256):
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',image_size=size,limit=2)
    indices=[next(i for i,x in enumerate(ds.items) if x==(case,z)) for case in (0,1) for z in (0,4)]
    batches=[device_batch(x,torch.device('cuda')) for x in DataLoader(Subset(ds,indices),batch_size=2)]
    return batches,[(ds.records[c]['case_id'],z) for c,z in (ds.items[i] for i in indices)]


def contracts():
    seed_all(3407);batches,_=data(64);batch=batches[0]
    model=load_model('crossview').cuda().eval();control=load_control('control').cuda().eval()
    with torch.no_grad():
        p=model(batch);assert torch.equal(p,control(batch))
        model.crossview_adapter.project.weight.normal_(0,.02)
        p=model(batch);without=dict(batch);without.pop('target');assert torch.equal(model(without),p)
        metadata=dict(batch,physical=torch.randn_like(batch['physical']),anchor_z=torch.randn_like(batch['anchor_z']))
        assert torch.equal(model(metadata),p)
        twice=reverse_batch(reverse_batch(batch))
        for k in ('cond','anchors','valid','physical','anchor_z'):torch.testing.assert_close(twice[k],batch[k],atol=1e-5,rtol=1e-5)
        # Test the new path with invalid *feature* values changed, independent of
        # the frozen original branch's documented repeated endpoint convention.
        features=[torch.randn(1,64,64,64,device='cuda') for _ in range(5)]
        valid=torch.tensor([[0.,1.,1.,1.]],device='cuda');q=torch.tensor([.5],device='cuda')
        a=model.crossview_adapter(features,valid,q,True)
        features[0]=features[0]+1000
        assert torch.equal(model.crossview_adapter(features,valid,q,True),a)
        block=AnchorPlaneBlock().cuda().eval();f=torch.randn(1,24,4,8,8,device='cuda');valid=torch.ones(1,4,device='cuda')
        changed=f.clone();changed[:,:,0]+=torch.randn_like(changed[:,:,0])
        d_cross=float((block(f,valid,True)[:,:,1]-block(changed,valid,True)[:,:,1]).abs().max())
        d_single=float((block(f,valid,False)[:,:,1]-block(changed,valid,False)[:,:,1]).abs().max())
        assert d_cross>0 and d_single==0
    seed_all(3407);a=load_model('crossview');seed_all(3407);b=load_model('per_anchor')
    assert all(torch.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items())
    result=dict(initial_g086_exact=True,target_not_read=True,metadata_ignored=True,reverse_contract=True,
                invalid_new_path_features_ignored=True,cross_anchor_influence=d_cross,per_anchor_influence=d_single,
                matched_initialization=True,parameters=sum(p.numel() for p in a.parameters()),
                new_parameters=sum(p.numel() for n,p in a.named_parameters() if 'adapter' in n))
    del model,control,batches,batch,block,a,b;gc.collect();torch.cuda.empty_cache()
    return result


def benchmark(variant,blocks):
    seed_all(3407);batches,_=data();batch=batches[0]
    model=load_model(variant).cuda().train();model.base.single.checkpoint_blocks=blocks
    opt=torch.optim.AdamW(model.parameters(),lr=2e-5,weight_decay=2e-5,betas=(.9,.99))
    scaler=torch.amp.GradScaler('cuda',init_scale=4096);times=[]
    torch.cuda.reset_peak_memory_stats()
    for step in range(5):
        opt.zero_grad(set_to_none=True);torch.cuda.synchronize();t=time.perf_counter()
        with torch.autocast('cuda'):loss,_=objective(model,batch,4,80)
        scaler.scale(loss).backward();scaler.unscale_(opt);torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
        scaler.step(opt);scaler.update();torch.cuda.synchronize()
        if step>=2:times.append((time.perf_counter()-t)/2)
    result=dict(variant=variant,checkpoint_blocks=blocks,peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,median_ms_interval=float(np.median(times)*1000),
                finite_updates=True,scope='Full objective with symmetry, all parameters; batch2 updates each batch, no IO; 2 warmups + 3 timed steps')
    del opt,scaler,model,batch,batches;gc.collect();torch.cuda.empty_cache();return result


@torch.no_grad()
def measured_errors(model,batches):
    model.eval();mse=[];mae=[]
    for batch in batches:
        with torch.autocast('cuda'):p=model(batch).float()
        e=p-batch['target'];mse.append(float(e.square().mean()));mae.append(float(e.abs().mean()))
    return dict(mse=float(np.mean(mse)),mae=float(np.mean(mae)))


def capacity(blocks):
    checks=contracts();seed_all(3407);batches,items=data()
    model=load_model('crossview').cuda();model.base.single.checkpoint_blocks=blocks
    for n,p in model.named_parameters():p.requires_grad_('crossview_adapter' in n)
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=.001,weight_decay=2e-5,betas=(.9,.99))
    scaler=torch.amp.GradScaler('cuda',init_scale=4096)
    initial=measured_errors(model,batches);history=[];start=time.perf_counter()
    for step in range(96):
        model.train();opt.zero_grad(set_to_none=True);batch=batches[step%2]
        with torch.autocast('cuda'):loss,_=objective(model,batch,4,80)
        scaler.scale(loss).backward();scaler.unscale_(opt);torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
        scaler.step(opt);scaler.update()
        history.append(float(loss.detach()))
        if (step+1)%24==0:print(f'Capacity step {step+1}/96 loss={history[-1]:.6f}',flush=True)
    final=measured_errors(model,batches)
    ratio=1-final['mse']/initial['mse']
    return dict(passed=bool(ratio>=.05 and final['mae']<=initial['mae']),contracts=checks,initial=initial,final=final,
        relative_mse_reduction=ratio,steps=96,train_intervals=items,elapsed_seconds=time.perf_counter()-start,
        losses=history,code_hashes=code_hashes(),checkpoint_saved=False,test_used=False,validation_used=False,
        caveat='Four training intervals, frozen G086, only new path updated. Capacity sanity check, NOT generalization or SOTA evidence.')


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['contracts','bench','capacity']);p.add_argument('--checkpoint-blocks',type=int,default=6)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    if a.action=='contracts':result=contracts()
    elif a.action=='capacity':result=capacity(a.checkpoint_blocks)
    else:
        result=[]
        for variant in ('crossview','per_anchor'):
            entry=benchmark(variant,a.checkpoint_blocks);print(json.dumps(entry),flush=True);result.append(entry)
    write_json(a.out,result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('losses','code_hashes')} if isinstance(result,dict) else result,indent=2),flush=True)


if __name__=='__main__':main()
