"""Plan-3 physical scaling regimes, shared difficulty, and bound sharpness."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent; OUT=HERE/'plan3_outputs'

def rho(a,b): return float(stats.spearmanr(a,b).statistic)

def scaling():
 feat=pd.read_csv(OUT/'prereconstruction_features.csv')[['dataset','case','scale','context_spacing_mm']].drop_duplicates()
 x=pd.read_csv(OUT/'error_balanced_panel.csv').merge(feat,on=['dataset','case','scale'])
 x['effective_anchor_spacing_mm']=x.scale*x.context_spacing_mm
 rows=[]; case_rows=[]
 for (ds,m),g in x.groupby(['dataset','target_model']):
  piv=g.pivot(index='case',columns='scale',values='common_error')
  rows.append({'dataset':ds,'target_model':m,'cases':len(piv),'strict_monotonic_fraction':float(((piv[2]<piv[4])&(piv[4]<piv[6])).mean()),
   'x6_worst_fraction':float(piv[6].eq(piv.max(axis=1)).mean()),'median_ratio_x4_x2':float((piv[4]/piv[2]).median()),'median_ratio_x6_x4':float((piv[6]/piv[4]).median())})
  for case,q in g.groupby('case'):
   slope=np.polyfit(q.effective_anchor_spacing_mm,q.common_error,1)[0]
   case_rows.append({'dataset':ds,'case':case,'target_model':m,'spacing_error_slope':float(slope),'rho_spacing_error':rho(q.effective_anchor_spacing_mm,q.common_error)})
 pd.DataFrame(rows).to_csv(OUT/'scaling_regimes.csv',index=False); pd.DataFrame(case_rows).to_csv(OUT/'case_scaling_slopes.csv',index=False)
 return rows

def shared_decomposition():
 x=pd.read_csv(OUT/'error_balanced_panel.csv'); rows=[]
 for ds,g in x.groupby('dataset'):
  piv=g.pivot_table(index='case',columns=['target_model','scale'],values='common_error')
  # Leave-one-cell-out consensus prevents a cell from trivially predicting itself.
  vals=[]
  for _,r in g.iterrows():
   peers=g[(g.dataset.eq(ds))&g.case.eq(r.case)&~((g.target_model.eq(r.target_model))&g.scale.eq(r.scale))].common_error
   vals.append(float(peers.median()))
  g=g.copy(); g['peer_consensus']=vals
  overall=rho(g.peer_consensus,g.common_error)
  within=[]
  for _,q in g.groupby(['scale','target_model']): within.append(rho(q.peer_consensus,q.common_error))
  residual=g.common_error-g.peer_consensus
  rows.append({'dataset':ds,'leave_one_cell_out_peer_rho':overall,'mean_profile_peer_rho':float(np.mean(within)),
   'median_abs_residual_fraction':float(np.median(np.abs(residual)/np.maximum(g.common_error,1e-12))),
   'shared_consensus_variance_fraction':float(1-np.var(residual)/np.var(g.common_error))})
 pd.DataFrame(rows).to_csv(OUT/'shared_difficulty_decomposition.csv',index=False); return rows

def bounds():
 x=pd.read_csv(OUT/'spectral_spatial_per_plane.csv'); rows=[]
 for band in ('raw','low','high'):
  # avg_error=(ea+eb)/2 and discrepancy<=ea+eb, so ratio below is lower-bound sharpness in [0,1].
  ratio=x[f'{band}_inc']/(2*x[f'{band}_error']).clip(lower=1e-12)
  x[f'{band}_bound_sharpness']=ratio
  for ds,g in x.groupby('dataset'):
   z=g[f'{band}_bound_sharpness']
   rows.append({'dataset':ds,'band':band,'median_sharpness':float(z.median()),'p90_sharpness':float(z.quantile(.9)),
    'max_sharpness':float(z.max()),'violations_over_one':int((z>1.00001).sum()),'rho_sharpness_error':rho(z,g[f'{band}_error'])})
 x.to_csv(OUT/'bound_sharpness_per_plane.csv',index=False); pd.DataFrame(rows).to_csv(OUT/'bound_sharpness_summary.csv',index=False); return rows

def main():
 result={'scaling':scaling(),'shared_difficulty':shared_decomposition(),'bound_sharpness':bounds()}
 (OUT/'scaling_decomposition_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
