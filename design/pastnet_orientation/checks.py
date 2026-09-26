import json,copy
from unittest.mock import patch
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import PACKAGE,write_json
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.run import seed_all,load_model as old_load
from pastnet_v2.losses import objective as original,reverse_batch
from .run import ROOT,load_model,code_hashes
from .transforms import spatial,transform
from .losses import objective

def main():
    seed_all(3407);device=torch.device('cuda')
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',anchors=4,image_size=64,limit=1)
    b=device_batch(next(iter(DataLoader(ds,batch_size=1))),device)
    original_batch={k:v.clone() if isinstance(v,torch.Tensor) else v for k,v in b.items()}
    for a in range(8):
        t=transform(b,a)
        for key in ('cond','anchors','target'):assert torch.equal(spatial(t[key],a,True),b[key])
        coarse=(1-t['cond'][:,:,5:6])*t['cond'][:,:,1:2]+t['cond'][:,:,5:6]*t['cond'][:,:,2:3]
        assert torch.allclose(coarse,t['cond'][:,:,4:5],atol=1e-7,rtol=0)
        x=transform(reverse_batch(b),a);y=reverse_batch(t)
        for key in ('cond','anchors','physical','anchor_z','valid'):assert torch.equal(x[key],y[key]),(a,key)
        # Check orientation/spacing against actual world-coordinate finite differences.
        p=torch.zeros(1,3,17,device=device);p[...,0:3]=torch.tensor([0.,1.,0.],device=device)
        p[...,3:12]=torch.eye(3,device=device).flatten();p[...,12:14]=1
        rr,cc=torch.meshgrid(torch.arange(7.,device=device),torch.arange(7.,device=device),indexing='ij')
        world=torch.stack([rr,2*cc,torch.zeros_like(rr)])
        coords=spatial(world,a);pp=transform(dict(b,physical=p),a)['physical'][0,0]
        axes=pp[3:12].reshape(3,3)
        assert torch.equal(coords[:,1,0]-coords[:,0,0],axes[:,0]*2**pp[0])
        assert torch.equal(coords[:,0,1]-coords[:,0,0],axes[:,1]*2**pp[1])
    for key,v in b.items():
        if isinstance(v,torch.Tensor):assert torch.equal(v,original_batch[key])
    m=load_model('orientation').cuda().eval();control=old_load('control').cuda().eval()
    with torch.no_grad(),torch.autocast('cuda'):assert torch.equal(m(b),control(b))
    del control
    m.train();m.base.single.checkpoint_blocks=5
    def grads(fn):
        m.zero_grad(set_to_none=True)
        with torch.autocast('cuda'):loss,_=fn(m,b,4,80,False)
        loss.backward()
        return loss.item(),{n:p.grad.detach().cpu().clone() for n,p in m.named_parameters() if p.grad is not None}
    baseline,g=grads(original)
    with patch('torch.randint',return_value=torch.tensor(0)):value,h=grads(objective)
    assert baseline==value and g.keys()==h.keys()
    error=max((g[n]-h[n]).abs().max().item() for n in g);assert error==0
    del g,h;m.zero_grad(set_to_none=True)
    # Complete-size real loss/backprop for every action; shared memory contract.
    full=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',anchors=4,limit=1)
    b=device_batch(next(iter(DataLoader(full,batch_size=2))),device)
    opt=torch.optim.AdamW(m.parameters(),lr=2e-5,weight_decay=2e-5,betas=(.9,.99))
    scaler=torch.amp.GradScaler('cuda',init_scale=4096.)
    torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats();rows=[]
    for a in range(8):
        opt.zero_grad(set_to_none=True)
        with patch('torch.randint',return_value=torch.tensor(a)),torch.autocast('cuda'):
            loss,parts=objective(m,b,4,80,False)
        scaler.scale(loss).backward();scaler.unscale_(opt)
        norm=torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True)
        scaler.step(opt);scaler.update()
        rows.append(dict(action=a,loss=float(loss),gradient_norm=float(norm)))
        print(rows[-1],flush=True)
    # New random augmentation resumes from the existing trainer's saved CPU RNG.
    opt.zero_grad(set_to_none=True)
    initial=copy.deepcopy(m.state_dict());os=copy.deepcopy(opt.state_dict());ss=copy.deepcopy(scaler.state_dict())
    rng=torch.get_rng_state();cuda_rng=torch.cuda.get_rng_state_all()
    def step():
        opt.zero_grad(set_to_none=True)
        with torch.autocast('cuda'):loss,parts=objective(m,b,4,80,False)
        scaler.scale(loss).backward();scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True)
        scaler.step(opt);scaler.update();return parts
    first=step();after=copy.deepcopy(m.state_dict())
    m.load_state_dict(initial);opt.load_state_dict(os);scaler.load_state_dict(ss)
    torch.set_rng_state(rng);torch.cuda.set_rng_state_all(cuda_rng)
    second=step()
    assert first==second and all(torch.equal(v,m.state_dict()[k]) for k,v in after.items())
    write_json(ROOT/'results/checks.json',dict(passed=True,all_actions_roundtrip=True,geometry_finite_difference_verified=True,
        z_reversal_commutes=True,input_unchanged=True,eval_bitwise_equal=True,identity_loss_gradient_max_abs=error,
        full_size_finite_update_all_actions=rows,peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
        peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,random_action_optimizer_resume_exact=True,code_hashes=code_hashes()))
    print('All orientation contracts passed.')
if __name__=='__main__':main()
