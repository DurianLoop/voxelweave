"""Resource-only measurement. Does not save or choose trained weights."""
import argparse
import time
import torch
from torch.utils.data import DataLoader
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.common import write_json
from pastnet_v2.run import seed_all
from .model import Reference
from .run import DATA,PACKAGE

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',type=int,required=True);p.add_argument('--groups',type=int,default=0)
    p.add_argument('--accumulation',type=int,default=1)
    a=p.parse_args();seed_all(3407);m=Reference(a.groups).cuda().train()
    ds=IntervalDataset(DATA,'train',anchors=4,limit=1)
    b=device_batch(next(iter(DataLoader(ds,batch_size=a.batch))),torch.device('cuda'))
    opt=torch.optim.Adam(m.parameters(),lr=3e-4);scaler=torch.amp.GradScaler('cuda',init_scale=4096.)
    result=dict(micro_batch=a.batch,checkpoint_groups=a.groups,actual_batch=b['anchors'].shape[0],accumulation=a.accumulation)
    try:
        times=[];torch.cuda.reset_peak_memory_stats()
        for step in range(4):
            t=time.perf_counter();opt.zero_grad(set_to_none=True)
            for _ in range(a.accumulation):
                with torch.autocast('cuda'):loss=torch.nn.functional.l1_loss(m(b).float(),b['target'])
                scaler.scale(loss/a.accumulation).backward()
            scaler.unscale_(opt)
            norm=torch.nn.utils.clip_grad_norm_(m.parameters(),1.,error_if_nonfinite=True)
            scaler.step(opt);scaler.update();torch.cuda.synchronize();times.append(time.perf_counter()-t)
            print(f'step={step} loss={loss.item():.6f} grad={float(norm):.4f} time={times[-1]:.3f}',flush=True)
        result.update(passed=True,peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
            peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,steady_seconds_per_sample=sum(times[1:])/3/a.batch/a.accumulation,
            times=times,parameters=sum(p.numel() for p in m.parameters()))
    except torch.cuda.OutOfMemoryError as e:result.update(passed=False,error='CUDA OOM',detail=str(e)[:300])
    write_json(PACKAGE/f'results/bench_b{a.batch}_g{a.groups}_a{a.accumulation}.json',result);print(result)

if __name__=='__main__':main()
