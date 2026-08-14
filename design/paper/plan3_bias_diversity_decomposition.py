"""Exact squared-error decomposition across reconstruction contexts.

For k predictions, mean_i ||f_i-y||^2 = ||mean(f)-y||^2 + mean_i ||f_i-mean(f)||^2.
The first term is shared/consensus error; the second is observable context diversity.
"""
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
from rasinet.optimization_protocol import profile_sources,case_names,prediction_path,gt_path
TARGETS=('i3net','hat','swinir')
def src(ds,s,m):
 q=profile_sources(ds,s)[m]
 if ds=='ningxia' and s in (2,6):q=replace(q,root=ROOT/'baseline'/f'{q.root.name}_root_results_202607')
 return q
def rho(a,b):return float(stats.spearmanr(a,b).statistic)
def run(ds):
 rows=[]; sources={s:{m:src(ds,s,m) for m in TARGETS} for s in (2,4,6)}; folds=(None,) if ds=='fastmri' else tuple(f'fold_{i:02d}' for i in range(8))
 for fold in folds:
  cases=sorted(set.intersection(*[set(case_names(sources[s]['i3net'],fold)) for s in (2,4,6)]))
  for case in cases:
   for m in TARGETS:
    pred={s:nib.load(str(prediction_path(sources[s][m],fold,case))).get_fdata(dtype=np.float32) for s in (2,4,6)}
    gt={s:nib.load(str(gt_path(sources[s]['i3net'],fold,case))).get_fdata(dtype=np.float32) for s in (2,4,6)}
    # Exact common physical generated indices are z not divisible by any scale: 1,5,7,11,...
    zs=[z for z in range(min(v.shape[2] for v in pred.values())) if all(z%s for s in (2,4,6))]
    P=np.stack([pred[s][:,:,zs] for s in (2,4,6)]); Y=np.mean(np.stack([gt[s][:,:,zs] for s in (2,4,6)]),axis=0)
    mean=P.mean(axis=0); mask=np.abs(Y)>.01*max(float(np.max(np.abs(Y))),1e-6)
    total=float(np.mean((P[:,mask]-Y[mask])**2)); shared=float(np.mean((mean[mask]-Y[mask])**2)); diversity=float(np.mean((P[:,mask]-mean[mask])**2))
    rows.append({'dataset':ds,'case':case,'target_model':m,'planes':len(zs),'total_context_mse':total,'shared_consensus_mse':shared,'observable_diversity_mse':diversity,
     'identity_residual':total-shared-diversity,'diversity_fraction':diversity/max(total,1e-12),'shared_fraction':shared/max(total,1e-12)})
   print('decomp',ds,fold,case,flush=True)
 return pd.DataFrame(rows)
def main():
 x=pd.concat([run('fastmri'),run('ningxia')],ignore_index=True); x.to_csv(OUT/'bias_diversity_per_case.csv',index=False); rows=[]
 for ds,g in x.groupby('dataset'):
  rows.append({'dataset':ds,'cases':g.case.nunique(),'median_shared_fraction':float(g.shared_fraction.median()),'median_diversity_fraction':float(g.diversity_fraction.median()),
   'p90_diversity_fraction':float(g.diversity_fraction.quantile(.9)),'max_abs_identity_residual':float(g.identity_residual.abs().max()),
   'rho_diversity_total_error':rho(g.observable_diversity_mse,g.total_context_mse),'rho_shared_total_error':rho(g.shared_consensus_mse,g.total_context_mse)})
 result={'summary':rows}; pd.DataFrame(rows).to_csv(OUT/'bias_diversity_summary.csv',index=False); (OUT/'bias_diversity_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
