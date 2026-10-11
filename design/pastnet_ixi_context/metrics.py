"""Main-table PSNR/SSIM range, on the same fixed observed normalization."""
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from skimage.metrics import structural_similarity
from pastnet_v2.metrics import quality
from pastnet_v2.common import write_json
from .data import device_batch


def measure(pred,target,spacing,intensity_scale=1.):
    result=quality(pred,target,spacing)
    data_range=float(np.max(target)-np.min(target))
    if data_range<=0:data_range=1./intensity_scale
    result['psnr']+=20*np.log10(data_range)
    result['ssim']=float(structural_similarity(np.asarray(target,np.float64),np.asarray(pred,np.float64),data_range=data_range))
    return result


@torch.no_grad()
def evaluate(model,dataset,device,out=None):
    model.eval();rows=[]
    for batch in DataLoader(dataset,batch_size=1,shuffle=False):
        data=device_batch(batch,device)
        with torch.autocast(device.type,enabled=device.type=='cuda'):
            prediction=model(data).float().clamp(0,1)[0,:,0].cpu().numpy()
        target=batch['target'][0,:,0].numpy()
        for j in range(3):
            spacing=np.exp2(batch['physical'][0,j,:2].numpy())
            rows.append(dict(patient_id=batch['patient_id'][0],case_id=batch['case_id'][0],z=int(batch['z'][0])+j+1,
                phase=(j+1)/4,**measure(prediction[j],target[j],spacing,float(batch['intensity_scale'][0]))))
    frame=pd.DataFrame(rows);cols=list(quality(np.zeros((8,8)),np.zeros((8,8))))
    if not np.isfinite(frame[cols].to_numpy()).all():raise FloatingPointError('Nonfinite metric; no exclusion')
    patients=frame.groupby('patient_id')[cols].mean()
    if out:
        out=Path(out);out.mkdir(parents=True,exist_ok=True)
        frame.to_csv(out/'per_slice.csv',index=False);patients.to_csv(out/'per_patient.csv')
        write_json(out/'summary.json',dict(patients.mean()))
        write_json(out/'contract.json',dict(primary='main-table per-GT-slice data_range PSNR/SSIM, missing slices, equal patient mean',
            normalization='observed-only minmax',output_clamp=True,mae_mse_units='normalized; raw units require case-wise inverse scale',
            proxy='threshold .1; HD95 in mm, not old-table auto-mask metrics',split=dataset.split))
    return dict(patients.mean())
