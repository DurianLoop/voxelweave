"""Analytical interpolation replication of the disjoint-lattice witness."""
from __future__ import annotations
import json,sys
from dataclasses import replace
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from scipy.interpolate import CubicSpline
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=HERE/'plan4_outputs'
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design')]
from rasinet.optimization_protocol import profile_sources,case_names,gt_path
from rasinet.icassp_statistics import ranking_metrics
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def interp(gt,phase,kind):
 z=np.arange(phase,gt.shape[2],4);v=gt[:,:,z]
 if kind=='linear':
  out=np.empty_like(gt)
  for q in range(gt.shape[2]):
   j=np.searchsorted(z,q);j=min(max(j,1),len(z)-1);t=(q-z[j-1])/(z[j]-z[j-1]);out[:,:,q]=(1-t)*v[:,:,j-1]+t*v[:,:,j]
  return out
 return CubicSpline(z,v,axis=2,bc_type='natural',extrapolate=True)(np.arange(gt.shape[2])).astype(np.float32)
def main():
 rows=[]
 for ds in ('fastmri','ningxia'):
  ref=profile_sources(ds,4)['i3net'];folds=[None] if ds=='fastmri' else [f'fold_{i:02d}' for i in range(8)]
  for fold in folds:
   for case in case_names(ref,fold):
    gt=nib.load(str(gt_path(ref,fold,case))).get_fdata(dtype=np.float32)
    for kind in ('linear','cubic'):
     p0=interp(gt,0,kind);p2=interp(gt,2,kind)
     for z in range(2,gt.shape[2]-2):
      if z%4 not in (1,3):continue
      a,b,y=p0[:,:,z],p2[:,:,z],gt[:,:,z];thr=.01*max(float(np.max(np.abs(a))),1e-6);mask=np.abs(a)>thr
      inc=np.abs(a-b);err=np.abs(a-y)
      rows.append({'dataset':ds,'case':case,'method':kind,'z':z,'score':float(inc[mask].mean()),'error':float(err[mask].mean()),'pixel_rho':rho(inc[mask],err[mask])})
    print('analytical',ds,fold,case,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/'analytical_disjoint_per_plane.csv',index=False);c=x.groupby(['dataset','case','method'],as_index=False).agg(score=('score','median'),error=('error','median'),pixel_rho=('pixel_rho','median'))
 result=[]
 for (ds,m),g in c.groupby(['dataset','method']):result.append({'dataset':ds,'method':m,**ranking_metrics(g.error,g.score),'median_pixel_rho':float(g.pixel_rho.median())})
 out={'anchor_overlap':0,'same_target':True,'profiles':result};(OUT/'analytical_disjoint_summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
