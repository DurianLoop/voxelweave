from __future__ import annotations
import argparse
from pathlib import Path
import time
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from pastnet_v2.common import PACKAGE,write_json
from pastnet_v2.data import IntervalDataset,device_batch
from .model import VARIANTS,GlobalCorrespondence
from .run import load_model
from pastnet_v2.run import seed_all


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--variant',choices=list(VARIANTS),required=True)
    p.add_argument('--checkpoint',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    seed_all(3407)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model=load_model(a.variant,a.checkpoint).to(device).eval()
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','val',anchors=VARIANTS[a.variant][-1],limit=1)
    batch=device_batch(next(iter(DataLoader(ds,batch_size=1))),device)
    times=[]
    with torch.inference_mode(),torch.autocast(device.type,enabled=device.type=='cuda'):
        for _ in range(10):
            model(batch)
        if device.type=='cuda':
            torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
        for _ in range(30):
            t=time.perf_counter();model(batch)
            if device.type=='cuda':
                torch.cuda.synchronize()
            times.append((time.perf_counter()-t)*1000)
    flops=[0]; handles=[]
    def hook(module,inputs,output):
        if isinstance(module,(nn.Conv2d,nn.Conv3d)):
            flops[0]+=2*output.numel()*module.in_channels//module.groups*np.prod(module.kernel_size)
        elif isinstance(module,nn.Linear):
            flops[0]+=2*output.numel()*module.in_features
        elif isinstance(module,GlobalCorrespondence):
            b=output.shape[0];n=(output.shape[-2]//8)*(output.shape[-1]//8)
            flops[0]+=4*4*b*n*n*32
    for module in model.modules():
        if isinstance(module,(nn.Conv2d,nn.Conv3d,nn.Linear,GlobalCorrespondence)):
            handles.append(module.register_forward_hook(hook))
    with torch.inference_mode(),torch.autocast(device.type,enabled=device.type=='cuda'):
        model(batch)
    for h in handles:
        h.remove()
    write_json(a.out,dict(variant=a.variant,device=torch.cuda.get_device_name(0) if device.type=='cuda' else 'cpu',
        parameters=sum(p.numel() for p in model.parameters()),
        conv_linear_gflops_interval=float(flops[0]/1e9),conv_linear_gflops_slice=float(flops[0]/3e9),
        flops_coverage='Conv2d/3d and Linear MAC x2, plus dense SDPA QK/AV MAC x2 for four anchors; excludes FFT, unfold, matching reductions and elementwise ops; not total FLOPs',
        latency_ms_interval_median=float(np.median(times)),latency_ms_slice_median=float(np.median(times)/3),
        latency_ms_interval_p95=float(np.quantile(times,.95)),
        peak_forward_gib=torch.cuda.max_memory_allocated()/2**30 if device.type=='cuda' else 0.,
        contract=dict(shape=[1,3,13,256,256],amp=device.type=='cuda',warmup=10,repetitions=30,
                      scope='forward only, three missing slices, excludes IO/resize/metrics',torch=torch.__version__)))


if __name__=='__main__':
    main()
