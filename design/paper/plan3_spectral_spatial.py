"""MECHANISTIC spectral/spatial decomposition on fixed matched planes."""
from __future__ import annotations
import json, sys
from dataclasses import replace
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import ndimage, stats

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'plan3_outputs'
sys.path.insert(0,str(ROOT/'design'))
from rasinet.cross_scale_physical import matches, planes
from rasinet.optimization_protocol import profile_sources, case_names, prediction_path, gt_path
TARGETS=('i3net','hat','swinir'); PAIRS=((2,4),(2,6),(4,6))

def src(ds,s,target):
 q=profile_sources(ds,s)[target]
 if ds=='ningxia' and s in (2,6): q=replace(q,root=ROOT/'baseline'/f'{q.root.name}_root_results_202607')
 return q

def corr(a,b):
 return float(stats.spearmanr(a,b).statistic) if len(a)>=3 and np.std(a)>0 and np.std(b)>0 else float('nan')

def components(a,b,ga,gb):
 # Half-resolution fixed analysis reduces compute; sigma=1 at analysis grid.
 a=a[::2,::2]; b=b[::2,::2]; ga=ga[::2,::2]; gb=gb[::2,::2]
 t=.01*max(float(np.max(np.abs(a))),float(np.max(np.abs(b))),1e-6); mask=(np.abs(a)>t)|(np.abs(b)>t)
 la=ndimage.gaussian_filter(a,1); lb=ndimage.gaussian_filter(b,1); lga=ndimage.gaussian_filter(ga,1); lgb=ndimage.gaussian_filter(gb,1)
 ha=a-la; hb=b-lb; hga=ga-lga; hgb=gb-lgb
 inc=np.abs(a-b); err=.5*(np.abs(a-ga)+np.abs(b-gb)); lowinc=np.abs(la-lb); lowerr=.5*(np.abs(la-lga)+np.abs(lb-lgb)); hiinc=np.abs(ha-hb); hierr=.5*(np.abs(ha-hga)+np.abs(hb-hgb))
 gy,gx=np.gradient(.5*(ga+gb)); edge=np.sqrt(gx*gx+gy*gy)
 return {"raw_error":float(err[mask].mean()),"raw_inc":float(inc[mask].mean()),"low_error":float(lowerr[mask].mean()),"low_inc":float(lowinc[mask].mean()),
         "high_error":float(hierr[mask].mean()),"high_inc":float(hiinc[mask].mean()),"edge_density":float(edge[mask].mean()),
         "pixel_raw_rho":corr(inc[mask],err[mask]),"pixel_low_rho":corr(lowinc[mask],lowerr[mask]),"pixel_high_rho":corr(hiinc[mask],hierr[mask])}

def run_dataset(ds):
 rows=[]; folds=(None,) if ds=='fastmri' else tuple(f'fold_{i:02d}' for i in range(8))
 sources={s:{m:src(ds,s,m) for m in TARGETS} for s in (2,4,6)}
 for fold in folds:
  cases=sorted(set.intersection(*[set(case_names(sources[s]['i3net'],fold)) for s in (2,4,6)]))
  if ds=='fastmri': cases=cases[8:] # same held-out confirmation split
  for case in cases:
   for m in TARGETS:
    imgs={s:nib.load(str(prediction_path(sources[s][m],fold,case))) for s in (2,4,6)}; pred={s:imgs[s].get_fdata(dtype=np.float32) for s in imgs}
    gt={s:nib.load(str(gt_path(sources[s]['i3net'],fold,case))).get_fdata(dtype=np.float32) for s in imgs}
    for a,b in PAIRS:
     mm=matches(planes(imgs[a],a),planes(imgs[b],b)); n=len(mm)
     for ordinal,(za,zb,distance,_) in enumerate(mm,1):
      c=components(pred[a][:,:,za],pred[b][:,:,zb],gt[a][:,:,za],gt[b][:,:,zb])
      rows.append({'dataset':ds,'case':case,'target_model':m,'pair':f'{a}-{b}','za':za,'zb':zb,'ordinal':ordinal,'n_positions':n,
                   'relative_position':(ordinal-1)/max(n-1,1),'plane_distance_mm':distance,**c})
   print(ds,fold,case,flush=True)
 return pd.DataFrame(rows)

def clustered_summary(x):
 rows=[]; rng=np.random.default_rng(20260902)
 for ds,g in x.groupby('dataset'):
  cases=np.array(sorted(g.case.unique())); by={c:g[g.case.eq(c)] for c in cases}
  def metric(q,col): return corr(q[f'{col}_inc'],q[f'{col}_error'])
  for band in ('raw','low','high'):
   obs=metric(g,band); vals=[]
   for _ in range(2000):
    b=pd.concat([by[c] for c in rng.choice(cases,len(cases),replace=True)],ignore_index=True); vals.append(metric(b,band))
   rows.append({'dataset':ds,'band':band,'plane_level_rho':obs,'cluster_bootstrap_95ci':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))],
                'median_pixel_rho':float(g[f'pixel_{band}_rho'].median())})
 return rows

def main():
 OUT.mkdir(exist_ok=True); x=pd.concat([run_dataset('fastmri'),run_dataset('ningxia')],ignore_index=True); x.to_csv(OUT/'spectral_spatial_per_plane.csv',index=False)
 result={'rows':len(x),'cases':x.groupby('dataset').case.nunique().to_dict(),'spectral':clustered_summary(x),'cohort_descriptors':[]}
 for ds,g in x.groupby('dataset'):
  result['cohort_descriptors'].append({'dataset':ds,'median_raw_error':float(g.raw_error.median()),'median_high_error_fraction':float((g.high_error/g.raw_error).median()),
    'median_high_inc_fraction':float((g.high_inc/g.raw_inc).median()),'rho_edge_density_error':corr(g.edge_density,g.raw_error),
    'rho_relative_position_error':corr(g.relative_position,g.raw_error),'rho_relative_position_inc':corr(g.relative_position,g.raw_inc)})
 (OUT/'spectral_spatial_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
