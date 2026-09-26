import argparse
import time
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from pastnet_v2.common import write_json,sha256
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.run import seed_all
from .model import Reference
from .run import DATA

def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=__import__('pathlib').Path,required=True)
    p.add_argument('--out',type=__import__('pathlib').Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    seed_all(3407);m=Reference().cuda().eval()
    saved=torch.load(a.checkpoint,map_location='cpu',weights_only=False)
    assert saved['variant']=='i3net_strict';m.load_state_dict(saved['model_state_dict']);del saved
    ds=IntervalDataset(DATA,'val',anchors=4,limit=1)
    b=device_batch(next(iter(DataLoader(ds,batch_size=1))),torch.device('cuda'))
    times=[]
    with torch.inference_mode(),torch.autocast('cuda'):
        for _ in range(10):m(b)
        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
        for _ in range(30):
            t=time.perf_counter();m(b);torch.cuda.synchronize();times.append((time.perf_counter()-t)*1000)
    peak=torch.cuda.max_memory_allocated()/2**30
    flops=[0];handles=[]
    def hook(module,inputs,output):
        if isinstance(module,(nn.Conv2d,nn.Conv3d)):
            flops[0]+=2*output.numel()*module.in_channels//module.groups*np.prod(module.kernel_size)
        else:flops[0]+=2*output.numel()*module.in_features
    for module in m.modules():
        if isinstance(module,(nn.Conv2d,nn.Conv3d,nn.Linear)):handles.append(module.register_forward_hook(hook))
    with torch.inference_mode(),torch.autocast('cuda'):m(b)
    for h in handles:h.remove()
    write_json(a.out,dict(variant='i3net_strict',best_sha256=sha256(a.checkpoint),device=torch.cuda.get_device_name(0),
        parameters=sum(p.numel() for p in m.parameters()),conv_linear_gflops_interval=float(flops[0]/1e9),
        conv_linear_gflops_slice=float(flops[0]/3e9),flops_coverage='Conv/Linear MAC x2 only; excludes DCT matmul, normalization, rearrangement and elementwise ops; NOT total FLOPs',
        latency_ms_interval_median=float(np.median(times)),latency_ms_slice_median=float(np.median(times)/3),
        latency_ms_interval_p95=float(np.quantile(times,.95)),peak_forward_gib=peak,
        contract=dict(shape=[1,3,13,256,256],consumed_input_shape=[1,4,1,256,256],amp=True,warmup=10,repetitions=30,
            scope='forward only; generates 13 positions and returns 3 central missing slices; excludes IO/resize/metrics',torch=torch.__version__)))

if __name__=='__main__':main()
