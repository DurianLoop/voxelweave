"""Fixed train-patient split, no validation or test. Low-frequency linear probe."""
import hashlib,json
from pathlib import Path
import numpy as np
from pastnet_v2.data import IntervalDataset
from pastnet_v2.common import PACKAGE,write_json

ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','train',image_size=32,anchors=6)
patients=sorted({r['patient_id'] for r in ds.records},key=lambda p:hashlib.sha256(p.encode()).hexdigest())
fit=set(patients[::2]); hold=set(patients[1::2])
stats={}; cached=[]; coverage=[]
for i,(ri,z) in enumerate(ds.items):
    if z%4:continue
    b=ds[i]; a=b['anchors'][:,0].numpy().astype(np.float64); valid=b['valid'].numpy()
    isfit=b['patient_id'] in fit
    coverage.append(dict(patient=b['patient_id'],z=z,local=int(valid[1:5].sum()),extended=int(valid.sum())))
    for j in range(3):
        q=(j+1)/4; coarse=b['cond'][j,4].numpy(); y=(b['target'][j,0].numpy()-coarse).ravel()
        # Separate fixed boundary/phase strata; only observed intensities enter X.
        for arm in ('local','extended'):
            mask=valid.copy()
            if arm=='local':mask[[0,5]]=0
            x=np.stack([np.ones_like(coarse),*[(a[k]-coarse)*mask[k] for k in range(6)]],-1).reshape(-1,7)
            key=(arm,z,j)
            if isfit:
                xx,xy=stats.setdefault(key,(np.zeros((7,7)),np.zeros(7)))
                xx+=x.T@x;xy+=x.T@y
            else:cached.append((b['patient_id'],z,j,arm,x,y))
    if len(coverage)%30==0:print('intervals',len(coverage),flush=True)
weights={}
for k,(xx,xy) in stats.items():
    penalty=np.eye(7)*.001*np.trace(xx)/7;penalty[0,0]=0
    weights[k]=np.linalg.solve(xx+penalty,xy)
rows=[]
for patient,z,j,arm,x,y in cached:
    e=y-x@weights[(arm,z,j)]
    rows.append(dict(patient=patient,z=z,phase=(j+1)/4,arm=arm,mse=float(np.mean(e*e))))
import pandas as pd
df=pd.DataFrame(rows)
p=df.groupby(['patient','arm']).mse.mean().unstack()
rng=np.random.default_rng(3407);d=(p.local-p.extended).to_numpy()
ci=np.quantile(d[rng.integers(len(d),size=(10000,len(d)))].mean(1),[.025,.975]).tolist()
out=Path('design/pastnet_v2_context/results/train_information_probe')
out.mkdir(parents=True,exist_ok=False);df.to_csv(out/'heldout_train_per_interval.csv',index=False)
pd.DataFrame(coverage).to_csv(out/'coverage.csv',index=False)
result=dict(fit_patients=sorted(fit),heldout_train_patients=sorted(hold),image_size=32,
    ridge=.001,local_mse=float(p.local.mean()),extended_mse=float(p.extended.mean()),
    relative_mse_reduction=float(1-p.extended.mean()/p.local.mean()),
    paired_mse_reduction_ci95=ci,wins=int((d>0).sum()),n=len(d),
    by_z=df.groupby(['arm','z']).mse.mean().to_dict().__str__(),
    scope='Train-only patient-disjoint low-frequency linear probe. Not a G086 gain, not an information bound.')
write_json(out/'summary.json',result);print(json.dumps(result,indent=2),flush=True)
