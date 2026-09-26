import json
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import PACKAGE,G086,write_json
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.run import seed_all,load_model as old_load
from .run import ROOT,load_model,code_hashes
from .model import DirectionContext,spatial

def main():
    seed_all(3407);ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',anchors=4,image_size=64,limit=1)
    batch=device_batch(next(iter(DataLoader(ds,batch_size=1))),torch.device('cuda'))
    branch=DirectionContext().cuda().eval()
    with torch.no_grad():
        branch.project.weight.normal_(0,.02);branch.project.bias.normal_(0,.01)
        x=batch['cond'].flatten(0,1);y=branch(x);errors=[]
        for g in range(8):
            error=(spatial(branch(spatial(x,g)),g,True)-y).abs().max().item()
            assert error<=1e-5,(g,error)
            errors.append(error)
        assert y.abs().max()>.0001
        plain_response=branch(x,False)
        plain_equivariance_error=(spatial(branch(spatial(x,1),False),1,True)-plain_response).abs().max().item()
        sharing_effect=(y-plain_response).abs().max().item()
        assert plain_equivariance_error>1e-6 and sharing_effect>1e-6
        modified=x.clone();modified[:,0]=999;modified[:,3]=-999
        assert torch.equal(branch(modified),branch(x))
    del branch
    shared=load_model('shared').cuda().eval();plain=load_model('plain').cuda().eval();base=old_load('control').cuda().eval()
    assert sum(p.numel() for p in shared.parameters())==sum(p.numel() for p in plain.parameters())
    old=torch.load(G086,map_location='cpu',weights_only=False)['model_state_dict']
    assert all(torch.equal(shared.state_dict()[k].cpu(),v) for k,v in old.items())
    before={k:v.clone() for k,v in batch.items() if isinstance(v,torch.Tensor)}
    with torch.no_grad(),torch.autocast('cuda'):
        expected=base(batch);actual=shared(batch)
        assert torch.equal(expected,actual) and torch.equal(expected,plain(batch))
        assert torch.equal(actual,shared(dict(batch,target=torch.full_like(batch['target'],float('nan')))))
    assert all(torch.equal(v,batch[k]) for k,v in before.items())
    write_json(ROOT/'results/checks.json',dict(passed=True,nonzero_branch_equivariance_max_abs=errors,
        branch_response_nonzero=True,plain_equivariance_error=plain_equivariance_error,nonzero_sharing_effect=sharing_effect,
        raw_invalid_outer_slots_not_read_by_branch=True,initial_output_bitwise_equal=True,
        target_not_read=True,input_unchanged=True,old_tensors_mapped=len(old),parameters=sum(p.numel() for p in shared.parameters()),
        new_parameters=sum(p.numel() for p in shared.direction_adapter.parameters()),code_hashes=code_hashes()))
    print(dict(passed=True,equivariance_max=max(errors),mapped=len(old)))
if __name__=='__main__':main()
