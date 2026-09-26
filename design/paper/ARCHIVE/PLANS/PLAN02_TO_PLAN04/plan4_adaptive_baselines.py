"""Paired adaptive-acquisition comparison against ordinary PC and simple baselines."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;P3=HERE/'plan3_outputs';P4=HERE/'plan4_outputs'
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def main():
 x=pd.read_csv(P4/'adaptive_acquisition_per_case.csv');mx=pd.read_csv(P4/'max_shared_per_case.csv').rename(columns={'score':'max_shared_score'})
 j=pd.read_csv(P3/'joint_witness_per_case.csv');j=j[(j.scale.eq(4))&j.target_model.isin(['hat','swinir'])][['dataset','case','target_model','pc','input_adj_rmse','input_change_normalized']].drop_duplicates()
 x=x.merge(mx[['dataset','case','target_model','max_shared_score']],on=['dataset','case','target_model']).merge(j,on=['dataset','case','target_model'])
 rows=[];rng=np.random.default_rng(20260813);features=['score','max_shared_score','pc','input_adj_rmse','input_change_normalized']
 for ds,g in x.groupby('dataset'):
  cases=np.array(sorted(g.case.unique()));by={c:g[g.case.eq(c)] for c in cases};base=rho(g.score,g.benefit_x4_to_x2)
  for f in features:
   rf=rho(g[f],g.benefit_x4_to_x2);delta=[]
   for _ in range(5000):
    b=pd.concat([by[c] for c in rng.choice(cases,len(cases),replace=True)],ignore_index=True);delta.append(rho(b.score,b.benefit_x4_to_x2)-rho(b[f],b.benefit_x4_to_x2))
   k=max(1,int(np.ceil(.25*len(g))));gain=g.nlargest(k,f).benefit_x4_to_x2.mean();random=g.benefit_x4_to_x2.mean();oracle=g.nlargest(k,'benefit_x4_to_x2').benefit_x4_to_x2.mean()
   rows.append({'dataset':ds,'score':f,'rho_vs_benefit':rf,'disjoint_minus_score_rho':base-rf,'case_cluster_95ci_delta':[float(np.nanquantile(delta,.025)),float(np.nanquantile(delta,.975))],
                'top_quartile_policy_gain':float(gain),'fraction_oracle_gain_above_random':float((gain-random)/(oracle-random))})
 result={'rows':rows};pd.DataFrame(rows).to_csv(P4/'adaptive_acquisition_baselines.csv',index=False);(P4/'adaptive_acquisition_baselines.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
