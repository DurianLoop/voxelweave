"""Contract tests and real 256-square two-direction training memory/throughput."""
import argparse,gc,time,json
import numpy as np
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import PACKAGE,G086,write_json
from pastnet_v2.data import IntervalDataset,device_batch,build_sample
from pastnet_v2.losses import objective,reverse_batch
from pastnet_v2.run import seed_all
from pastnet_v2.model import PASTNetV2
from .model import TrajectoryPASTNet,trajectory_weights
from .run import load_model,code_hashes


def contracts():
    seed_all(3407);device=torch.device('cuda')
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',image_size=64,anchors=6,limit=1)
    batch=device_batch(next(iter(DataLoader(ds,batch_size=1))),device)
    original=PASTNetV2('control').to(device).eval()
    original.load_g086(torch.load(G086,map_location='cpu',weights_only=False))
    b4=dict(batch,anchors=batch['anchors'][:,1:5],valid=batch['valid'][:,1:5],anchor_z=batch['anchor_z'][:,1:5])
    with torch.no_grad():baseline=original(b4)
    results={}
    for variant in ('trajectory_local','trajectory_extended'):
        model=load_model(variant).to(device).eval()
        with torch.no_grad():
            prediction=model(batch);delta=float((prediction-baseline).abs().max())
            assert delta==0,delta
            missing=dict(batch);missing.pop('target')
            assert torch.equal(model(missing),prediction)
            # Nonzero projection is essential: zero-init alone can conceal leakage.
            model.trajectory_adapter.project.weight.normal_(0,.02)
            prediction=model(batch)
            far=dict(batch,anchors=batch['anchors'].clone());far['anchors'][:,5]+=.3
            far_delta=float((model(far)-prediction).abs().max())
            if variant=='trajectory_local':assert far_delta==0,far_delta
            else:assert far_delta>1e-7,far_delta
            invalid=dict(batch,anchors=batch['anchors'].clone())
            invalid['anchors'][batch['valid']==0]=12345
            assert torch.equal(model(invalid),prediction)
            geo=dict(batch,physical=torch.randn_like(batch['physical']),anchor_z=torch.randn_like(batch['anchor_z']))
            assert torch.equal(model(geo),prediction)
            twice=reverse_batch(reverse_batch(batch))
            for k in ('cond','anchors','valid','physical','anchor_z'):
                torch.testing.assert_close(twice[k],batch[k],atol=1e-5,rtol=1e-5)
            results[variant]=dict(initial_g086_max_abs=delta,far_perturbation_max_abs=far_delta,
                                  target_not_read=True,masked_values_ignored=True,geometry_ignored=True)
        del model;gc.collect();torch.cuda.empty_cache()
    # No missing target pixel may alter any input, including at extreme intensity.
    r=ds.records[0];v=np.random.default_rng(9).uniform(0,1,(64,64,r['shape'][2])).astype('float32')
    altered=v.copy();altered[:,:,1::4]=1e6;altered[:,:,2::4]=-1e6;altered[:,:,3::4]=77
    x=build_sample(v,r,0,64,6);y=build_sample(altered,r,0,64,6)
    for k in ('cond','anchors','valid','physical','anchor_z'):assert torch.equal(x[k],y[k])
    w=trajectory_weights(torch.tensor([[0.,0.,1.,1.,1.,1.]],device=device),torch.tensor([[.25,.5,.75]],device=device))
    torch.testing.assert_close(w.sum(-1),torch.tensor([1.,0.,0.],device=device).expand(1,3,3),atol=1e-5,rtol=1e-5)
    results['sparse_target_extrema_invariance']=True
    results['constant_trajectory_exact']=True
    del original;gc.collect();torch.cuda.empty_cache()
    return results


def train_bench(variant,blocks):
    seed_all(3407);device=torch.device('cuda')
    model=load_model(variant).to(device).train();model.base.single.checkpoint_blocks=blocks
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',anchors=6,limit=1,sample_limit=2)
    batch=device_batch(next(iter(DataLoader(ds,batch_size=2))),device)
    opt=torch.optim.AdamW(model.parameters(),lr=2e-5,weight_decay=2e-5,betas=(.9,.99))
    scaler=torch.amp.GradScaler('cuda',init_scale=4096)
    times=[];losses=[];encoder_grad=[]
    torch.cuda.reset_peak_memory_stats()
    for step in range(7):
        torch.cuda.synchronize();start=time.perf_counter();opt.zero_grad(set_to_none=True)
        with torch.autocast('cuda'):loss,_=objective(model,batch,4,80,False)
        scaler.scale(loss).backward();scaler.unscale_(opt)
        norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
        encoder_grad.append(float(model.trajectory_adapter.encoder[0].weight.grad.abs().sum()))
        scaler.step(opt);scaler.update();torch.cuda.synchronize()
        if step>=2:times.append((time.perf_counter()-start)/2)
        losses.append(float(loss.detach()));assert torch.isfinite(norm)
    assert encoder_grad[-1]>0,'Trajectory encoder must learn after projection opens'
    result=dict(variant=variant,checkpoint_blocks=blocks,batch=2,steps=7,
                device=torch.cuda.get_device_name(),peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
                median_ms_interval=float(np.median(times)*1000),losses=losses,encoder_grad_l1=encoder_grad,
                scope='Two warmup + five timed full objective fwd/reverse/backward steps; excludes IO; benchmark updates every batch, full accumulates 8 batches')
    del opt,scaler,model,batch;gc.collect();torch.cuda.empty_cache()
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=__import__('pathlib').Path,required=True)
    p.add_argument('--checkpoint-blocks',type=int,default=5);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    result={'contracts':contracts(),'train_bench':[],'source_hashes':code_hashes()}
    print('All input/initialization contracts passed',flush=True)
    for variant in ('trajectory_local','trajectory_extended'):
        r=train_bench(variant,a.checkpoint_blocks);result['train_bench'].append(r)
        print(json.dumps(r),flush=True)
    write_json(a.out,result)


if __name__=='__main__':main()
