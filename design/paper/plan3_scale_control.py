"""CONFIRMATORY scale-control for pre-reconstruction anchor-change signals."""
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
 if ds=='ningxia' and s in (2,6):q=replace(q,root=ROOT/'baseline'/f'{q.root.name}_root_results_202607')
 return q
def find_gt(ds,s,case):
 q=src(ds,s)
 if ds!='ningxia':return gt_path(q,None,case)
 for i in range(8):
  p=gt_path(q,f'fold_{i:02d}',case)
  if p.exists():return p
 raise FileNotFoundError(case)
def robust_range(v):
 fg=v[np.abs(v)>.01*max(float(np.max(np.abs(v))),1e-6)]; return float(np.percentile(fg,99)-np.percentile(fg,1))
def rho(a,b):return float(stats.spearmanr(a,b).statistic)
def main():
 panels=[pd.read_csv(OUT/'prereconstruction_features.csv'),pd.read_csv(OUT/'ixi_prereconstruction_panel.csv').drop(columns=['target_model','common_error'],errors='ignore').drop_duplicates(['dataset','case','scale'])]
 feat=pd.concat(panels,ignore_index=True).drop(columns=['common_error','range_normalized_error','target_model'],errors='ignore').drop_duplicates(['dataset','case','scale'])
 labels=pd.concat([pd.read_csv(OUT/'error_balanced_panel.csv'),pd.read_csv(OUT/'ixi_prereconstruction_panel.csv')[['dataset','case','scale','target_model','common_error']]],ignore_index=True)
 ranges=[]
 for i,r in feat.iterrows():
  p=find_gt(r.dataset,int(r.scale),r.case); v=nib.load(str(p)).get_fdata(dtype=np.float32); ranges.append({'dataset':r.dataset,'case':r.case,'scale':int(r.scale),'gt_range':robust_range(v)})
  if (i+1)%50==0:print('GT ranges',i+1,flush=True)
 ranges=pd.DataFrame(ranges); x=labels.merge(feat,on=['dataset','case','scale']).merge(ranges,on=['dataset','case','scale'])
 x['normalized_error']=x.common_error/x.gt_range.clip(lower=1e-12); x['normalized_anchor_rmse']=x.input_adj_rmse/x.input_dynamic_range.clip(lower=1e-12)
 x.to_csv(OUT/'scale_control_panel.csv',index=False)
 rows=[]; rng=np.random.default_rng(20260905)
 for ds,g in x.groupby('dataset'):
  cases=np.array(sorted(g.case.unique())); by={c:g[g.case.eq(c)] for c in cases}
  for feature in ('input_adj_rmse','input_dynamic_range','normalized_anchor_rmse'):
   for endpoint in ('common_error','normalized_error'):
    obs=np.mean([rho(q[feature],q[endpoint]) for _,q in g.groupby(['scale','target_model'])]); vals=[]
    for _ in range(500):
     b=pd.concat([by[c] for c in rng.choice(cases,len(cases),replace=True)],ignore_index=True)
     vals.append(np.mean([rho(q[feature],q[endpoint]) for _,q in b.groupby(['scale','target_model'])]))
    rows.append({'dataset':ds,'cases':len(cases),'feature':feature,'endpoint':endpoint,'mean_profile_rho':float(obs),'case_cluster_95ci':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]})
 result={'results':rows}; pd.DataFrame(rows).to_csv(OUT/'scale_control_summary.csv',index=False); (OUT/'scale_control_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
