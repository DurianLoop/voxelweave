import json,time
import torch
from torch.utils.data import DataLoader,Subset
from pastnet_v2.common import PACKAGE,write_json
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.losses import objective
from pastnet_v2.run import seed_all,is_new
from .run import ROOT,load_model,code_hashes
from pastnet_series_integrity.prepare import MANIFEST

def main():
    ds=IntervalDataset(MANIFEST,'train',anchors=4,limit=2)
    ids=[i for i,(rec,z) in enumerate(ds.items) if rec<2 and z in (0,4)]
    assert len(ids)==4
    batches=[device_batch(b,torch.device('cuda')) for b in DataLoader(Subset(ds,ids),batch_size=2)]
    records={}
    for variant in ('wavelet3','wavelet1'):
        seed_all(3407);m=load_model(variant).cuda();m.base.single.checkpoint_blocks=5
        groups=[dict(params=[p for n,p in m.named_parameters() if is_new(n)==new],lr=1e-4 if new else 2e-5) for new in (False,True)]
        opt=torch.optim.AdamW(groups,weight_decay=2e-5,betas=(.9,.99))
        scaler=torch.amp.GradScaler('cuda',init_scale=4096.)
        def measure():
            m.eval();mse=[];mae=[]
            with torch.no_grad(),torch.autocast('cuda'):
                for b in batches:
                    e=m(b).float()-b['target'];mse.append(float(e.square().mean()));mae.append(float(e.abs().mean()))
                delta=float(torch.stack([p.detach().abs().mean() for n,p in m.named_parameters() if is_new(n)]).mean())
            return dict(mse=sum(mse)/len(mse),mae=sum(mae)/len(mae),gain_abs=delta)
        before=measure();torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats();t0=time.perf_counter()
        new_grad_max=0.
        for step in range(96):
            m.train();opt.zero_grad(set_to_none=True)
            with torch.autocast('cuda'):loss,_=objective(m,batches[step%2],4,80,False)
            scaler.scale(loss).backward();scaler.unscale_(opt)
            new_grad_max=max(new_grad_max,max(p.grad.abs().max().item() for p in [p for n,p in m.named_parameters() if is_new(n)] if p.grad is not None))
            torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True)
            scaler.step(opt);scaler.update()
            if (step+1)%24==0:print(f'{variant} step={step+1}/96 loss={loss.item():.6f}',flush=True)
        after=measure()
        record=dict(before=before,after=after,mse_reduction=1-after['mse']/before['mse'],
            peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
            elapsed_seconds=time.perf_counter()-t0,new_gradient_max=new_grad_max)
        record['passed']=bool(record['mse_reduction']>=.05 and after['mae']<=before['mae'] and after['gain_abs']>0 and new_grad_max>0)
        records[variant]=record;print(json.dumps(record),flush=True)
        del m,opt,scaler;torch.cuda.empty_cache()
    write_json(ROOT/'results/capacity.json',dict(passed=records['wavelet3']['passed'],arms=records,steps=96,
        sample_cases=[ds.records[i]['case_id'] for i,z in (ds.items[j] for j in ids)],
        scope='fixed four train intervals; capacity only; do not select between arms from this test; no weights saved',code_hashes=code_hashes()))
if __name__=='__main__':main()
