"""Fixed trained model, train-only diagnosis; no candidate selection on validation."""
import json
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader,Subset
from pastnet_v2.common import PACKAGE,sha256,write_json
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.run import load_model,seed_all
from .run import ROOT,code_hashes
from .transforms import transform,spatial
def main():
    seed_all(3407);ckpt=PACKAGE/'runs/full_control_seed3407_vram20/best.pth'
    model=load_model('control',ckpt).cuda().eval()
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',anchors=4)
    ids=[i for i,(_,z) in enumerate(ds.items) if z==4];rows=[]
    with torch.inference_mode(),torch.autocast('cuda'):
        for i,batch in enumerate(DataLoader(Subset(ds,ids),batch_size=1)):
            b=device_batch(batch,torch.device('cuda'));views=[]
            for action in range(8):views.append(spatial(model(transform(b,action)).float(),action,inverse=True))
            y=b['target'];base=(views[0]-y).square().mean().item()
            row=dict(patient_id=batch['patient_id'][0],case_id=batch['case_id'][0],z=4,canonical_mse=base,
                other_mse=float(torch.stack([(v-y).square().mean() for v in views[1:]]).mean()),
                defect=float(torch.stack([(v-views[0]).square().mean() for v in views[1:]]).mean()),
                average_mse=float((torch.stack(views).mean(0)-y).square().mean()))
            rows.append(row)
            if (i+1)%16==0:print(f'{i+1}/{len(ids)} training series',flush=True)
    frame=pd.DataFrame(rows);ROOT.joinpath('results').mkdir(exist_ok=True)
    frame.to_csv(ROOT/'results/probe_per_case.csv',index=False)
    patient=frame.groupby('patient_id')[['canonical_mse','other_mse','defect','average_mse']].mean()
    patient.to_csv(ROOT/'results/probe_per_patient.csv');means=patient.mean()
    ratio=float((patient.defect/patient.canonical_mse).mean())
    other=float((patient.other_mse/patient.canonical_mse).mean())
    assert len(frame)==112 and len(patient)==111 and np.isfinite(patient.to_numpy()).all()
    write_json(ROOT/'results/probe.json',dict(passed=bool(ratio>=.05 or other>=1.1),series=112,patients=111,
        mean_patient_defect_ratio=ratio,mean_patient_rotated_mse_ratio=other,mean_metrics=dict(means),
        averaging_delta_db=float((10*np.log10(patient.canonical_mse/patient.average_mse)).mean()),
        scope='train-only mechanism diagnostic; trained-on patients; eight-view average NOT a candidate or information bound',
        checkpoint_sha256=sha256(ckpt),code_hashes=code_hashes()))
    print(json.dumps(dict(ratio=ratio,other=other,means=dict(means)),indent=2))
if __name__=='__main__':main()
