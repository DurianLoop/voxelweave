"""MECHANISTIC / SYNTHETIC asymmetric context deletion on frozen fastMRI HAT x4.

The first acquired slice is replaced by its neighbor. This intentionally changes
the measurement and is used only to test boundary-context sensitivity.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'plan3_outputs'
sys.path.insert(0,str(ROOT/'baseline'))
sys.path.insert(0,str(ROOT/'design'))
from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator
from rasinet.optimization_protocol import profile_sources,case_names,sparse_path,prediction_path,gt_path

def mae(a,b,zs):
 vals=[]
 for z in zs:
  m=np.abs(b[:,:,z])>.01*max(float(np.max(np.abs(b[:,:,z]))),1e-6); vals.append(float(np.mean(np.abs(a[:,:,z][m]-b[:,:,z][m]))))
 return float(np.mean(vals))
def main():
 src=profile_sources('fastmri',4)['hat']; ref=profile_sources('fastmri',4)['i3net']; cases=sorted(case_names(src,None))[8:12]
 ckpt=src.run_dir()/ 'checkpoints'/'hat_epoch_best.pth'; model=FastMRIHAT2p5DInterpolator(ckpt)
 rows=[]
 for case in cases:
  sp=nib.load(str(sparse_path(ref,None,case))).get_fdata(dtype=np.float32); original=nib.load(str(prediction_path(src,None,case))).get_fdata(dtype=np.float32); gt=nib.load(str(gt_path(ref,None,case))).get_fdata(dtype=np.float32)
  altered=sp.copy(); altered[:,:,0]=sp[:,:,1]; pred=model.interpolate_volume(altered,stride=4)
  first=[1,2,3]; interior=[z for z in range(1,pred.shape[2]) if z%4 and z not in first]
  rows.append({'case':case,'original_first_error':mae(original,gt,first),'deleted_first_error':mae(pred,gt,first),
   'original_interior_error':mae(original,gt,interior),'deleted_interior_error':mae(pred,gt,interior),
   'first_output_change':mae(pred,original,first),'interior_output_change':mae(pred,original,interior)})
  print('synthetic',case,flush=True)
 x=pd.DataFrame(rows); x['first_error_increase']=x.deleted_first_error-x.original_first_error; x['interior_error_increase']=x.deleted_interior_error-x.original_interior_error; x.to_csv(OUT/'asymmetric_context_deletion.csv',index=False)
 result={'label':'MECHANISTIC / SYNTHETIC','cases':len(x),'mean_first_error_increase':float(x.first_error_increase.mean()),'mean_interior_error_increase':float(x.interior_error_increase.mean()),
  'mean_first_output_change':float(x.first_output_change.mean()),'mean_interior_output_change':float(x.interior_output_change.mean())}
 (OUT/'asymmetric_context_deletion.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
