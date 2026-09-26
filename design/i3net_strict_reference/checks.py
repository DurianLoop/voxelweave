import json
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import sha256,write_json
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.run import seed_all
from .model import Reference
from .run import DATA,PACKAGE,hashes,learning_rate,RECIPE

def main():
    seed_all(3407)
    source=json.loads((PACKAGE/'results/source_check.json').read_text())
    for row in source:
        name=row['file'].split('/')[-1]
        path=PACKAGE/('reference' if name.endswith('.json') else 'vendor')/name
        assert row['normalized_equal'] and row['remote_checked'] and sha256(path)==row['local_sha256']
    ds=IntervalDataset(DATA,'train',anchors=4,limit=1)
    b=device_batch(next(iter(DataLoader(ds,batch_size=1))),torch.device('cuda'))
    m=Reference(0).cuda().train()
    # Baseline uses the unmodified vendor forward. Keep gradients on CPU so
    # checkpoint and non-checkpoint graphs never coexist on the GPU.
    def forward_grad(groups):
        m.network.checkpoint_groups=groups;m.zero_grad(set_to_none=True)
        with torch.autocast('cuda'):
            y=m(b);loss=torch.nn.functional.l1_loss(y.float(),b['target'])
        loss.backward()
        gradients={n:p.grad.detach().cpu().clone() for n,p in m.named_parameters() if p.grad is not None}
        assert all(torch.isfinite(g).all() for g in gradients.values())
        return y.detach().cpu(),gradients
    original,grads=forward_grad(0)
    diffs={}
    for groups in (1,2,8):
        y,other=forward_grad(groups)
        assert torch.equal(y,original) and other.keys()==grads.keys()
        error=max((other[n]-grads[n]).abs().max().item() for n in grads)
        assert error==0.,error
        diffs[str(groups)]=error
        del other
    m.zero_grad(set_to_none=True);m.eval()
    with torch.no_grad(),torch.autocast('cuda'):
        sparse=b['anchors'][:,:,0].permute(0,2,3,1).contiguous()
        dense=m.network(sparse);pred=m({'anchors':b['anchors']})
        assert dense.shape==(1,256,256,13) and pred.shape==(1,3,1,256,256)
        assert torch.equal(dense[...,5:8].permute(0,3,1,2).unsqueeze(2),pred)
        assert torch.equal(dense[...,::4],sparse.to(dense.dtype))
        assert torch.equal(m(dict(b,target=torch.full_like(b['target'],float('nan')),
                                 cond=torch.full_like(b['cond'],float('nan')))),pred)
    assert abs(learning_rate(0,RECIPE)-3e-6)<1e-12
    assert abs(learning_rate(14,RECIPE)-3e-4)<1e-12
    assert abs(learning_rate(299,RECIPE)-3e-5)<1e-12
    result=dict(passed=True,source_verified=True,central_mapping=True,observed_copy='exact in output dtype under AMP',
        target_cond_not_read=True,full_shape=[1,256,256,4],checkpoint_output_bitwise_equal=True,
        checkpoint_gradient_max_abs=diffs,parameters=sum(p.numel() for p in m.parameters()),
        finite_gradients=True,lr_endpoints_passed=True,code_hashes=hashes())
    write_json(PACKAGE/'results/checks.json',result);print(json.dumps({k:v for k,v in result.items() if k!='code_hashes'},indent=2))

if __name__=='__main__':main()
