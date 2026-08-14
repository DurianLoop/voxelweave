"""EXPLORATORY fixed multi-witness composition and stable-error coverage."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent; OUT=HERE/'plan3_outputs'; P2=HERE/'plan2_outputs'; ROOT=HERE.parents[1]

def rho(a,b): return float(stats.spearmanr(a,b).statistic)
def nAURC(y,s):
 o=np.argsort(s); risk=np.cumsum(np.asarray(y)[o])/np.arange(1,len(y)+1); aurc=risk.mean()
 oracle=(np.cumsum(np.sort(y))/np.arange(1,len(y)+1)).mean(); rng=np.mean(y)
 return float((aurc-oracle)/max(rng-oracle,1e-12))

def scores():
 feat=pd.read_csv(OUT/'prereconstruction_features.csv'); feat['input_change_normalized']=feat.input_adj_rmse/feat.input_dynamic_range.clip(lower=1e-12)
 labels=pd.read_csv(OUT/'error_balanced_panel.csv')
 # PC examination scores.
 fastpc=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/cross_scale_consistency_per_case.csv')
 fastpc=fastpc[fastpc.dataset.eq('fastmri')][['dataset','case','scale','target_model','consistency']].rename(columns={'consistency':'pc'})
 ning=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/all_finalist_outer_predictions.csv')
 ning=ning[ning.method.eq('physical_consistency')][['case','scale','target_model','triage_score']].rename(columns={'triage_score':'pc'}); ning.insert(0,'dataset','ningxia')
 pc=pd.concat([fastpc,ning],ignore_index=True)
 x=labels.merge(feat[['dataset','case','scale','input_adj_rmse','input_dynamic_range','input_change_normalized']],on=['dataset','case','scale']).merge(pc,on=['dataset','case','scale','target_model'])
 # Within-profile percentile ranks put heterogeneous witnesses on a common ordinal scale.
 for col in ('pc','input_adj_rmse','input_dynamic_range','input_change_normalized'):
  x[col+'_rank']=x.groupby(['dataset','scale','target_model'])[col].rank(pct=True)
 x['pc_plus_input']=.5*(x.pc_rank+x.input_change_normalized_rank)
 x['pc_plus_range']=.5*(x.pc_rank+x.input_dynamic_range_rank)
 return x

def evaluate(x):
 methods=['pc_rank','input_adj_rmse_rank','input_dynamic_range_rank','input_change_normalized_rank','pc_plus_input','pc_plus_range']; rows=[]
 for ds,g in x.groupby('dataset'):
  cases=sorted(g.case.unique()); split={'derivation':cases[:len(cases)//2],'confirmation':cases[len(cases)//2:]}
  for part,ids in split.items():
   q=g[g.case.isin(ids)]
   for method in methods:
    vals=[]
    for _,z in q.groupby(['scale','target_model']): vals.append((nAURC(z.common_error,z[method]),rho(z.common_error,z[method])))
    rows.append({'dataset':ds,'split':part,'cases':len(ids),'method':method,'normalized_aurc':float(np.mean([v[0] for v in vals])),'spearman':float(np.mean([v[1] for v in vals]))})
 return rows

def blind_spots(x):
 rows=[]
 for ds,g in x.groupby('dataset'):
  g=g.copy(); g['error_pct']=g.groupby(['scale','target_model']).common_error.rank(pct=True); g['pc_pct']=g.groupby(['scale','target_model']).pc.rank(pct=True)
  blind=g[(g.error_pct>=.75)&(g.pc_pct<=.25)]
  for method in ('input_adj_rmse_rank','input_dynamic_range_rank','input_change_normalized_rank','pc_plus_input','pc_plus_range'):
   rows.append({'dataset':ds,'blind_spots':len(blind),'method':method,'flagged_top_quartile':int((blind[method]>=.75).sum()),
                'recall':float((blind[method]>=.75).mean()) if len(blind) else float('nan')})
 return rows

def main():
 x=scores(); x.to_csv(OUT/'joint_witness_per_case.csv',index=False); result={'split_evaluation':evaluate(x),'stable_wrong_coverage':blind_spots(x)}
 (OUT/'joint_witness_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); pd.DataFrame(result['split_evaluation']).to_csv(OUT/'joint_witness_split_metrics.csv',index=False); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
