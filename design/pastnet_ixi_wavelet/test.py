"""One fixed candidate and the existing IXI I3Net; matched inference/metric contract."""
import argparse,json,time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from skimage.transform import resize
from pastnet_v2.data import device_batch
from pastnet_v2.metrics import quality
from pastnet_v2.run import seed_all
from pastnet_v2.common import sha256,write_json
from i3net_strict_reference.model import Reference
from .data import IXIDataset,ROOT,MANIFEST
from .run import load_model,hashes
I3=ROOT.parents[1]/'baseline/ixi_i3net/runs/full_test115_stable/checkpoints/i3net_epoch_best.pth'

@torch.no_grad()
def i3net_volume(network,v):
    sparse=torch.from_numpy(np.array(v[:,:,::4],copy=True)).unsqueeze(0).cuda()
    out=torch.zeros(1,256,256,4*(sparse.shape[-1]-1)+1,device='cuda');counts=torch.zeros_like(out[:,:,:1])
    # Original complete 4->13 windows, including the trained per-window clamp.
    for start in range(sparse.shape[-1]-3):
        pred=network(sparse[...,start:start+4].contiguous()).float().clamp(0,1)
        out[...,start*4:start*4+13]+=pred;counts[...,start*4:start*4+13]+=1
    if not (counts>0).all():raise ValueError('I3Net coverage failure')
    return (out/counts)[0].cpu().numpy()

@torch.no_grad()
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--smoke',action='store_true');a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    m=json.loads((a.run/'manifest.json').read_text());done=json.loads((a.run/'completion.json').read_text())
    if not done['completed'] or m['smoke']!=a.smoke or m['code_hashes']!=hashes():raise ValueError('Unfinished, smoke or changed model')
    if done['best_sha256']!=sha256(a.run/'best.pth') or m['data_sha256']!=sha256(MANIFEST):raise ValueError('Weights/data changed')
    split='val' if a.smoke else 'test'
    # Persist fixed checkpoint identity before opening test images.
    a.out.mkdir(parents=True)
    write_json(a.out/'lock.json',dict(candidate_sha256=done['best_sha256'],i3net_sha256=sha256(I3),code_hashes=hashes(),
        seed=m['seed'],split=split,exploratory_user_selected=True,three_seed_confirmed=False))
    seed_all(m['seed']);candidate=load_model('wavelet3',a.run/'best.pth').cuda().eval()
    payload=torch.load(I3,map_location='cpu',weights_only=False);ref=Reference().cuda().eval()
    ref.network.load_state_dict(payload['model_state_dict'],strict=True)
    ds=IXIDataset(MANIFEST,split,limit=1 if a.smoke else None,allow_locked_test=not a.smoke)
    if not a.smoke and len(ds.records)!=115:raise ValueError('Expected 115 locked test patients')
    rows=[];costs=[]
    for i,rec in enumerate(ds.records):
        v=ds.volume(i);n_intervals=(v.shape[2]-1)//4;depth=n_intervals*4+1
        pred=np.empty((256,256,depth),np.float32);pred[:,:,::4]=v[:,:,0:depth:4]
        torch.cuda.reset_peak_memory_stats();t=time.perf_counter()
        for z in range(0,depth-4,4):
            from pastnet_v2.data import build_sample
            b=build_sample(v,rec,z);b=device_batch({k:x[None] for k,x in b.items() if isinstance(x,torch.Tensor) and k!='target'},torch.device('cuda'))
            with torch.autocast('cuda'):y=candidate(b).float().clamp(0,1)[0,:,0].cpu().numpy()
            pred[:,:,z+1:z+4]=y.transpose(1,2,0)
        torch.cuda.synchronize();past_seconds=time.perf_counter()-t;past_mem=torch.cuda.max_memory_allocated()/2**30
        torch.cuda.reset_peak_memory_stats();t=time.perf_counter();ir=i3net_volume(ref.network,v)
        torch.cuda.synchronize();i3_seconds=time.perf_counter()-t;i3_mem=torch.cuda.max_memory_allocated()/2**30
        spacing=np.array(rec['geometry']['spacing'][:2])*np.array(rec['shape'][:2])/256
        for z in range(depth):
            if z%4==0:continue
            for method,array in [('past_wavelet',pred),('i3net',ir)]:
                rows.append(dict(method=method,patient_id=rec['patient_id'],z=z,**quality(array[:,:,z],v[:,:,z],spacing)))
        costs.append(dict(patient_id=rec['patient_id'],missing_slices=n_intervals*3,past_seconds=past_seconds,i3_seconds=i3_seconds,
            past_peak_gib=past_mem,i3_peak_gib=i3_mem))
        print(f'{split} {i+1}/{len(ds.records)} {rec["patient_id"]}',flush=True)
        pd.DataFrame(rows).to_csv(a.out/'per_slice.csv',index=False)
    df=pd.DataFrame(rows);metrics=list(quality(np.zeros((8,8)),np.zeros((8,8))))
    if not np.isfinite(df[metrics].to_numpy()).all():raise FloatingPointError('Nonfinite quality; no silent patient exclusion')
    patients=df.groupby(['method','patient_id'])[metrics].mean();patients.to_csv(a.out/'per_patient.csv')
    x=patients.loc['past_wavelet'].sort_index();y=patients.loc['i3net'].sort_index();assert x.index.equals(y.index)
    rng=np.random.default_rng(73019);draws=rng.integers(0,len(x),(10000,len(x)));report={}
    lower={'mae','mse','hd95_proxy','tail10_mse'}
    for k in metrics:
        d=(x[k]-y[k]).to_numpy();report[k]=dict(past_mean=float(x[k].mean()),i3net_mean=float(y[k].mean()),delta=float(d.mean()),
            ci95=np.quantile(d[draws].mean(1),[.025,.975]).tolist(),past_patient_wins=int(((d<0) if k in lower else (d>0)).sum()))
    hard=y.nsmallest(max(1,int(np.ceil(len(y)*.25))),'psnr').index
    write_json(a.out/'report.json',dict(completed=True,smoke=a.smoke,patients=len(x),metrics=report,
        hard_quartile_delta=float((x.loc[hard,'psnr']-y.loc[hard,'psnr']).mean()),
        same_scoring='256 squared, observed minmax, missing slices, both outputs clamped [0,1] before overlap fusion, patient mean',
        limitations='different historical training normalization/pretraining/loss/budget; one seed; no SOTA claim',sota_claim=False))
    write_json(a.out/'efficiency.json',dict(cases=costs,scope='end-to-end per-volume inference with CPU copies; both models resident; no metric/IO/cache time',
        past_amp=True,i3net_amp=False,not_same_as_forward_only_benchmark=True))
if __name__=='__main__':main()
