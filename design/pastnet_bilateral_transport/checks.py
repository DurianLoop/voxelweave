import json
import torch
from torch import nn
from torch.utils.data import DataLoader
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.common import G086,write_json
from pastnet_v2.run import load_model as old_load,seed_all,is_new
from pastnet_series_integrity.prepare import MANIFEST
from .model import BilateralTransport
from .run import ROOT,load_model,code_hashes

def main():
    seed_all(3407)
    layer=BilateralTransport().cuda()
    x=torch.randn(3,16,24,24,device='cuda')
    shifted=layer.sample(x,layer.left_stencil)
    identity=(shifted[:,:,12]-x).abs().max().item();assert identity==0
    one=torch.ones_like(x)
    constant=(layer.sample(one,layer.left_stencil)[...,3:-3,3:-3]-1).abs().max().item();assert constant==0
    right=torch.roll(x,2,-1)
    matched,disagreement,w=layer.transport(x,right,True)
    mass=(w.sum(1)-1).abs().max().item();assert mass<1e-5
    sampled=layer.sample(torch.ones_like(x[:,:1]),layer.left_stencil)[:,0]
    sampled_r=layer.sample(torch.ones_like(x[:,:1]),layer.right_stencil)[:,0]
    invalid=(sampled<.999)|(sampled_r<.999)
    assert w[invalid].abs().max()==0
    stationary=(x+right)/2;truth=torch.roll(x,1,-1)
    mse=lambda a:float((a[1,:,4:-4,4:-4]-truth[1,:,4:-4,4:-4]).square().mean().detach())
    ratio=mse(matched)/mse(stationary);assert ratio<=.5,ratio
    rev=layer.transport(right.flip(0),x.flip(0))[0].flip(0)
    reversal=(rev-matched).abs().max().item();assert reversal<1e-5,reversal
    del layer,x,right,matched,disagreement,w,shifted
    ds=IntervalDataset(MANIFEST,'train',image_size=64,limit=1)
    b=device_batch(next(iter(DataLoader(ds,batch_size=1))),torch.device('cuda'))
    m=load_model('bilateral').cuda();base=old_load('control').cuda()
    old=torch.load(G086,map_location='cpu',weights_only=False)['model_state_dict']
    assert all(torch.equal(m.state_dict()[k].cpu(),v) for k,v in old.items())
    m.eval();base.eval()
    with torch.no_grad(),torch.autocast('cuda'):
        pred=m(b);assert torch.equal(pred,base(b))
        assert torch.equal(pred,m(dict(b,target=torch.full_like(b['target'],float('nan')))))
    def grads(model):
        model.zero_grad(set_to_none=True)
        with torch.autocast('cuda'):loss=(model(b).float()-b['target']).square().mean()
        loss.backward()
        return {n:p.grad.detach().cpu().clone() for n,p in model.named_parameters() if p.grad is not None}
    m.train();base.train();m.base.single.checkpoint_blocks=base.base.single.checkpoint_blocks=0
    g=grads(m);ref=grads(base)
    error=max((g[n]-ref[n]).abs().max().item() for n in ref)
    assert error<=1e-7,error
    gain_grad=max(v.abs().max().item() for n,v in g.items() if is_new(n));assert gain_grad>0
    del base,g,ref
    with torch.no_grad():
        for n,p in m.named_parameters():
            if 'bilateral_adapter.project' in n:p.fill_(.001)
    m.base.single.checkpoint_blocks=0;g=grads(m)
    m.base.single.checkpoint_blocks=5;h=grads(m)
    cp_error=max((g[n]-h[n]).abs().max().item() for n in g);assert cp_error<=1e-6,cp_error
    result=dict(passed=True,zero_displacement_error=identity,constant_interior_error=constant,
        probability_sum_error=mass,invalid_candidate_probability_zero=True,synthetic_translation_mse_ratio=ratio,
        bilateral_reversal_max_abs=reversal,old_tensors_mapped=len(old),initial_prediction_bitwise_equal=True,
        original_gradient_max_abs=error,initial_new_gradient_max=gain_grad,nonzero_projection_checkpoint_gradient_max_abs=cp_error,
        target_not_read=True,parameters=sum(p.numel() for p in m.parameters()),new_parameters=sum(p.numel() for n,p in m.named_parameters() if is_new(n)),code_hashes=code_hashes())
    write_json(ROOT/'results/checks.json',result);print(json.dumps({k:v for k,v in result.items() if k!='code_hashes'},indent=2))
if __name__=='__main__':main()
