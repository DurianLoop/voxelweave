import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pastnet_v2.common import write_json
from pastnet_ixi_context.metrics import measure
from .data import device_batch


def interval_batch(dataset,patient,start,device):
    samples=[dataset.sample(patient,start,interval) for interval in range(3)]
    return device_batch({k:torch.stack([s[k] for s in samples]) for k,v in samples[0].items()
        if isinstance(v,torch.Tensor) and k!='target'},device)


@torch.no_grad()
def evaluate(model,teacher,dataset,out=None):
    if model is not None:model.eval()
    rows=[];cost=[];device=torch.device('cuda')
    for i,record in enumerate(dataset.records):
        v=dataset.volume(i);depth=4*((v.shape[2]-1)//4)+1
        total=np.zeros((256,256,depth),np.float32);count=np.zeros(depth,np.int32)
        seconds=0.;torch.cuda.reset_peak_memory_stats()
        for start in range(0,depth-12,4):
            s=dataset.sample(i,start,0);anchors=s['teacher_anchors'][None].cuda()
            torch.cuda.synchronize();t=time.perf_counter();prediction,feature=teacher(anchors)
            if model is None:
                window=prediction[0].cpu().numpy()
            else:
                window=prediction[0].cpu().numpy().copy()
                b=interval_batch(dataset,i,start,device)
                # All three intervals share one frozen teacher computation; FP32 scoring.
                queries=model(b,prediction.expand(3,-1,-1,-1),feature.expand(3,-1,-1,-1)).clamp(0,1)[:,:,0].cpu().numpy()
                for interval,y in enumerate(queries):
                    window[:,:,interval*4+1:interval*4+4]=y.transpose(1,2,0)
            torch.cuda.synchronize();seconds+=time.perf_counter()-t
            total[:,:,start:start+13]+=window;count[start:start+13]+=1
        assert (count>0).all();total/=count[None,None,:]
        spacing=np.array(record['geometry']['spacing'][:2])*np.array(record['shape'][:2])/256
        for z in range(depth):
            if z%4==0:continue
            q=measure(total[:,:,z],v[:,:,z],spacing,dataset.intensity_scale(i))
            rows.append(dict(patient_id=record['patient_id'],z=z,**q))
        cost.append(dict(patient_id=record['patient_id'],missing_slices=int(sum(z%4!=0 for z in range(depth))),
            seconds=seconds,peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30))
        print(f'validation {i+1}/{len(dataset.records)} {record["patient_id"]}',flush=True)
    frame=pd.DataFrame(rows);columns=[x for x in frame if x not in ('patient_id','z')]
    assert np.isfinite(frame[columns].to_numpy()).all()
    patients=frame.groupby('patient_id')[columns].mean();summary=dict(patients.mean())
    if out:
        out=Path(out);out.mkdir(parents=True,exist_ok=True)
        frame.to_csv(out/'per_slice.csv',index=False);patients.to_csv(out/'per_patient.csv')
        pd.DataFrame(cost).to_csv(out/'efficiency.csv',index=False);write_json(out/'summary.json',summary)
        write_json(out/'contract.json',dict(split='val',patients=len(patients),missing_slices=len(frame),
            precision='FP32 for both frozen I3Net and bridge',scoring='per-GT-slice range, per-window clamp then uniform overlap fusion, patient mean',
            bridge_interval_batch=3 if model is not None else None,
            mae_mse_units='observed-minmax normalized',mask='.1 threshold proxy, HD95 mm',test_used=False,
            efficiency='includes bridge input packing and CPU transfers; excludes initial volume IO and quality metrics'))
    return summary
