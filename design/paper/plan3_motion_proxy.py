"""MECHANISTIC pre-reconstruction translation/misalignment proxy across acquired slices."""
from __future__ import annotations
import json,sys
from dataclasses import replace
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from skimage.registration import phase_cross_correlation
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'plan3_outputs'
sys.path.insert(0,str(ROOT/'design'))
from rasinet.optimization_protocol import profile_sources,case_names,sparse_path
def src(ds,s):
 q=profile_sources(ds,s)['i3net']
 if ds=='ningxia' and s in (2,6):q=replace(q,root=ROOT/'baseline'/f'{q.root.name}_root_results_202607')
 return q
def rho(a,b):return float(stats.spearmanr(a,b).statistic)
def motion(v):
 shifts=[]; residual=[]
 for z in range(v.shape[2]-1):
  a=v[::4,::4,z]; b=v[::4,::4,z+1]; scale=max(np.percentile(np.abs(np.r_[a.ravel(),b.ravel()]),99),1e-6); a=a/scale;b=b/scale
  sh,err,_=phase_cross_correlation(a,b,upsample_factor=2,normalization=None); shifts.append(float(np.linalg.norm(sh)*4)); residual.append(float(err))
 return {'input_translation_px':float(np.median(shifts)),'input_registration_error':float(np.median(residual)),'input_translation_p90':float(np.quantile(shifts,.9))}
def main():
 rows=[]
 for ds in ('fastmri','ningxia','ixi'):
  scales=(4,) if ds=='ixi' else (2,4,6)
  for s in scales:
   q=src(ds,s); folds=(None,) if ds!='ningxia' else tuple(f'fold_{i:02d}' for i in range(8))
   for fold in folds:
    for case in case_names(q,fold):
     img=nib.load(str(sparse_path(q,fold,case))); rows.append({'dataset':ds,'case':case,'scale':s,**motion(img.get_fdata(dtype=np.float32))})
   print('motion',ds,s,flush=True)
 f=pd.DataFrame(rows).drop_duplicates(['dataset','case','scale']); f.to_csv(OUT/'motion_proxy_features.csv',index=False)
 labels=pd.concat([pd.read_csv(OUT/'error_balanced_panel.csv'),pd.read_csv(OUT/'ixi_prereconstruction_panel.csv')[['dataset','case','scale','target_model','common_error']]],ignore_index=True)
 x=labels.merge(f,on=['dataset','case','scale']); result=[]
 for ds,g in x.groupby('dataset'):
  for feat in ('input_translation_px','input_registration_error','input_translation_p90'):
   result.append({'dataset':ds,'feature':feat,'mean_profile_rho':float(np.mean([rho(q[feat],q.common_error) for _,q in g.groupby(['scale','target_model'])]))})
 pd.DataFrame(result).to_csv(OUT/'motion_proxy_summary.csv',index=False); (OUT/'motion_proxy_summary.json').write_text(json.dumps({'results':result},indent=2),encoding='utf-8'); print(json.dumps({'results':result},indent=2))
if __name__=='__main__':main()
