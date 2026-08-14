"""Architecture-family analysis on the full available fastMRI model bank."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'plan3_outputs'

def rho(a,b): return float(stats.spearmanr(a,b).statistic)
def main():
 x=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/common_errors_per_case_development.csv')
 x=x[x.dataset.eq('fastmri')].copy(); x.to_csv(OUT/'full_model_bank_error_panel.csv',index=False)
 models=sorted(x.target_model.unique()); neural=[m for m in models if m not in ('linear','cubic')]
 corrs=[]
 for s,g in x.groupby('scale'):
  c=g.pivot(index='case',columns='target_model',values='common_error').corr(method='spearman'); c.to_csv(OUT/f'fastmri_x{s}_full_model_error_correlations.csv')
  for i,a in enumerate(models):
   for b in models[i+1:]: corrs.append({'scale':s,'model_a':a,'model_b':b,'rho':float(c.loc[a,b]),'both_neural':a in neural and b in neural})
 cdf=pd.DataFrame(corrs); cdf.to_csv(OUT/'full_model_pair_correlations.csv',index=False)
 ranks=x.assign(rank=lambda z:z.groupby(['case','scale']).common_error.rank()).pivot_table(index=['case','scale'],columns='target_model',values='rank')
 # How often architecture ordering changes does not erase shared case difficulty.
 winners=ranks.idxmin(axis=1).value_counts(); case_cons=x.groupby('case').common_error.median(); cell=x.copy(); cell['peer_median']=cell.apply(lambda r: float(x[(x.case.eq(r.case))&(x.scale.eq(r.scale))&~x.target_model.eq(r.target_model)].common_error.median()),axis=1)
 result={'models':models,'neural_models':neural,'pairwise_neural_rho_median':float(cdf[cdf.both_neural].rho.median()),
  'pairwise_neural_rho_range':[float(cdf[cdf.both_neural].rho.min()),float(cdf[cdf.both_neural].rho.max())],
  'winner_counts':{str(k):int(v) for k,v in winners.items()},'cell_error_vs_other_model_median_rho':rho(cell.common_error,cell.peer_median),
  'case_consensus_sd':float(case_cons.std())}
 (OUT/'model_family_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
