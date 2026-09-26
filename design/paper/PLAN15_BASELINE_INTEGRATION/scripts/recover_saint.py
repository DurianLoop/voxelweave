"""Recover overwritten SAINT summary cells from preserved predictions, read-only."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd,nibabel as nib
from skimage.metrics import peak_signal_noise_ratio,structural_similarity
P=Path(__file__).resolve().parents[1];ROOT=P.parent.parents[1];OUT=P/'outputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];sources=[]
for factor in [2,6]:
    base=ROOT/f'baseline/fastmri_brain_saint/runs/full_x{factor}'
    gts=sorted((base/'eval_gt').glob('*.nii.gz'));assert len(gts)==24
    for gt in gts:
        matches=list((base/'saint_outputs').glob('*'+gt.name));assert len(matches)==1,(gt,matches)
        pp=matches[0];g=nib.load(gt).get_fdata(dtype=np.float32);p=nib.load(pp).get_fdata(dtype=np.float32);assert g.shape==p.shape
        assert np.allclose(nib.load(gt).affine,nib.load(pp).affine)
        values=[]
        for z in range(g.shape[2]):
            if z%factor==0:continue
            a=g[:,:,z];b=p[:,:,z];dr=float(a.max()-a.min());dr=dr if dr>0 else 1.0
            diff=b-a
            values.append([peak_signal_noise_ratio(a,b,data_range=dr),structural_similarity(a,b,data_range=dr),float(np.mean(abs(diff))),float(np.mean(diff**2)),float(np.corrcoef(a.ravel(),b.ravel())[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0])
        rows.append(dict(dataset='fastMRI',model='saint',scale=factor,case=gt.name,generated_slices=len(values),**dict(zip(['psnr','ssim','mae','mse','ncc'],np.mean(values,axis=0)))))
        sources.extend({'path':str(x.relative_to(ROOT)),'sha256':sha(x)} for x in [gt,pp])
r=pd.DataFrame(rows);r.to_csv(OUT/'saint_recovered_per_case.csv',index=False)
summary=r.groupby(['dataset','model','scale'])[['psnr','ssim','mae','mse','ncc']].mean().reset_index();summary.to_csv(OUT/'saint_recovered_summary.csv',index=False)
(OUT/'saint_recovery_manifest.json').write_text(json.dumps({'sources':sources,'script_sha256':sha(Path(__file__)),'protocol_sha256':sha(P/'PROTOCOL.md'),'metric_source_sha256':sha(ROOT/'pre/topcow_diffusion/metrics.py')},indent=2))
print(summary.to_string(index=False))
