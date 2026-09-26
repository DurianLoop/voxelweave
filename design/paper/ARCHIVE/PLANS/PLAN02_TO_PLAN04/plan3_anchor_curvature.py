"""MECHANISTIC retrospective test of anchor-path curvature at matched planes."""
from __future__ import annotations
import json,sys
from dataclasses import replace
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'plan3_outputs'
sys.path.insert(0,str(ROOT/'design'))
from rasinet.optimization_protocol import profile_sources,gt_path

def src(ds,s):
 q=profile_sources(ds,s)['i3net']
 if ds=='ningxia' and s in (2,6): q=replace(q,root=ROOT/'baseline'/f'{q.root.name}_root_results_202607')
 return q
def rho(a,b): return float(stats.spearmanr(a,b).statistic)
def main():
 x=pd.read_csv(OUT/'context_geometry_per_plane.csv'); rows=[]; cache={}
 for r in x.itertuples():
  fold=getattr(r,'fold',None) if hasattr(r,'fold') else None
  if isinstance(fold,float) and np.isnan(fold):fold=None
  # Original spectral table omitted fold; infer NingXia fold from unique case lookup once.
  for s,z in zip(map(int,r.pair.split('-')),(int(r.za),int(r.zb))):
   key=(r.dataset,r.case,s)
   if key not in cache:
    q=src(r.dataset,s); ff=None
    if r.dataset=='ningxia':
     for i in range(8):
      f=f'fold_{i:02d}'; p=gt_path(q,f,r.case)
      if p.exists(): ff=f; break
    cache[key]=nib.load(str(gt_path(q,ff,r.case))).get_fdata(dtype=np.float32)
   v=cache[key]; left=(z//s)*s; right=left+s; rel=(z-left)/s
   lin=(1-rel)*v[:,:,left]+rel*v[:,:,right]; target=v[:,:,z]
   mask=np.abs(target)>.01*max(float(np.max(np.abs(target))),1e-6)
   rows.append({'row_id':r.Index,'scale':s,'curvature':float(np.mean(np.abs(target[mask]-lin[mask]))),
                'anchor_change':float(np.mean(np.abs(v[:,:,right][mask]-v[:,:,left][mask])))})
 f=pd.DataFrame(rows).groupby('row_id').agg(anchor_curvature=('curvature','mean'),anchor_change=('anchor_change','mean')).reset_index()
 x=x.reset_index(names='row_id').merge(f,on='row_id'); x.to_csv(OUT/'anchor_curvature_per_plane.csv',index=False)
 summary=[]
 for (ds,pair),g in x.groupby(['dataset','pair']):
  sw=g.stable_wrong.astype(bool)
  summary.append({'dataset':ds,'pair':pair,'rho_curvature_error':rho(g.anchor_curvature,g.raw_error),'rho_curvature_inc':rho(g.anchor_curvature,g.raw_inc),
   'median_curvature':float(g.anchor_curvature.median()),'stable_wrong_n':int(sw.sum()),
   'stable_wrong_curvature_median':float(g.loc[sw,'anchor_curvature'].median()) if sw.any() else None,
   'other_curvature_median':float(g.loc[~sw,'anchor_curvature'].median())})
 result={'summary':summary}; pd.DataFrame(summary).to_csv(OUT/'anchor_curvature_summary.csv',index=False); (OUT/'anchor_curvature_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
