import json
import torch
from torch import nn
from torch.utils.data import DataLoader
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.common import G086,write_json
from pastnet_v2.run import load_model as old_load,seed_all,is_new
from pastnet_series_integrity.prepare import MANIFEST
from .model import haar,inverse_haar,WaveletDepthwise
from .run import ROOT,load_model,code_hashes

def main():
    seed_all(3407);errors=[];energy=[]
    for shape in ((2,3,64,64),(1,3,65,63)):
        x=torch.randn(shape,device='cuda');bands,hw=haar(x)
        errors.append((inverse_haar(bands,hw)-x).abs().max().item())
        energy.append(float((bands.square().sum()-x.square().sum()).abs()/x.square().sum()))
    assert max(errors)<1e-5 and max(energy)<1e-5
    layer=WaveletDepthwise(nn.Conv2d(1,1,3,padding=1,groups=1,bias=False),3).cuda()
    with torch.no_grad():
        layer.weight.zero_();layer.weight[:,:,1,1]=1
        x=torch.randn(1,1,65,63,device='cuda');identity=(layer.tree(x,3)-x).abs().max().item();assert identity<1e-5
        layer.weight.fill_(1/9);impulse=torch.zeros(1,1,64,64,device='cuda');impulse[:,:,32,32]=1
        spread=layer.tree(impulse,3);outside=spread.clone();outside[:,:,31:34,31:34]=0
        support=int((outside.abs()>1e-7).sum());assert support>0
    del layer
    ds=IntervalDataset(MANIFEST,'train',image_size=64,limit=1)
    b=device_batch(next(iter(DataLoader(ds,batch_size=1))),torch.device('cuda'))
    m=load_model('wavelet3').cuda();base=old_load('control').cuda()
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
            if is_new(n):p.fill_(.1)
    m.base.single.checkpoint_blocks=0;g=grads(m)
    m.base.single.checkpoint_blocks=5;h=grads(m)
    cp_error=max((g[n]-h[n]).abs().max().item() for n in g);assert cp_error<=1e-7,cp_error
    result=dict(passed=True,haar_reconstruction_max=errors,parseval_relative_errors=energy,recursive_identity_error=identity,
        nonlocal_impulse_support_pixels=support,old_tensors_mapped=len(old),initial_prediction_bitwise_equal=True,
        original_gradient_max_abs=error,initial_gain_gradient_max=gain_grad,nonzero_gain_checkpoint_gradient_max_abs=cp_error,
        target_not_read=True,parameters=sum(p.numel() for p in m.parameters()),new_parameters=sum(p.numel() for n,p in m.named_parameters() if is_new(n)),code_hashes=code_hashes())
    write_json(ROOT/'results/checks.json',result);print(json.dumps({k:v for k,v in result.items() if k!='code_hashes'},indent=2))
if __name__=='__main__':main()
