import json
import torch
from pastnet_v2.common import write_json
from .run import ROOT,hashes,amp_recovery

def main():
    result_dir=ROOT/'results';result_dir.mkdir(exist_ok=True)
    p=torch.nn.Parameter(torch.tensor([1.],device='cuda'));opt=torch.optim.Adam([p],lr=.001)
    with amp_recovery(result_dir/'synthetic_updates.jsonl') as events:
        s=torch.amp.GradScaler('cuda',init_scale=4194304.)
        loss=(p*1e35).sum();assert torch.isfinite(loss)
        s.scale(loss).backward();s.unscale_(opt)
        before=p.detach().clone()
        torch.nn.utils.clip_grad_norm_([p],1.,error_if_nonfinite=True)
        s.step(opt);s.update()
        assert torch.equal(p,before) and len(opt.state)==0 and s.get_scale()==2097152.
        opt.zero_grad(set_to_none=True)
        s.scale((p-2).square().sum()).backward();s.unscale_(opt)
        torch.nn.utils.clip_grad_norm_([p],1.,error_if_nonfinite=True);s.step(opt);s.update()
        assert torch.isfinite(p).all() and not torch.equal(p,before) and float(opt.state[p]['step'])==1
        assert events[0]['overflow'] and not events[0]['optimizer_applied'] and events[1]['optimizer_applied']
    # Finite gradients: same clipping, Adam, scaler and resulting parameter.
    def finite(wrapped):
        from contextlib import nullcontext
        q=torch.nn.Parameter(torch.tensor([1.],device='cuda'));o=torch.optim.Adam([q],lr=.001)
        with amp_recovery(result_dir/'finite_updates.jsonl') if wrapped else nullcontext():
            sc=torch.amp.GradScaler('cuda',init_scale=4096.)
            sc.scale((q-2).square().sum()).backward();sc.unscale_(o)
            norm=torch.nn.utils.clip_grad_norm_([q],1.,error_if_nonfinite=True);sc.step(o);sc.update()
            return q.detach(),norm,sc.state_dict(),o.state[q]
    a,b=finite(False),finite(True)
    assert torch.equal(a[0],b[0]) and torch.equal(a[1],b[1]) and a[2]==b[2]
    assert all(torch.equal(a[3][k],b[3][k]) for k in a[3])
    result=dict(passed=True,overflow_does_not_change_parameters_or_adam=True,scale_backoff_verified=True,
        next_finite_update_succeeds=True,finite_path_bitwise_equal=True,recovery_hashes=hashes())
    write_json(result_dir/'checks.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
