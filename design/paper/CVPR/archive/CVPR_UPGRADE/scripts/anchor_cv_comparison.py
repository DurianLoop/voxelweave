"""C5-E011 locked comparator and budget analysis from completed scores."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];OUT=UP/'outputs';RNG=np.random.default_rng(20260813);BUDGETS=(.1,.2,.3,.5)
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def gain(s,y,b):k=max(1,int(np.ceil(b*len(s))));ix=np.argpartition(s,-k)[-k:];return float(np.mean(y[ix]))
def main():
 x=pd.read_csv(OUT/'anchor_cross_validation_per_case.csv');ana=pd.read_csv(OUT/'analytical_acquired_anchor_bipartition_per_case.csv').rename(columns={'score':'bipartition_score'})[['dataset','case','model','bipartition_score']]
 plan=pd.read_csv(PAPER/'plan4_outputs'/'adaptive_acquisition_per_case.csv').rename(columns={'target_model':'model','score':'phase_grid_score'})[['dataset','case','model','phase_grid_score']]
 j=pd.read_csv(PAPER/'plan3_outputs'/'joint_witness_per_case.csv');j=j[(j.scale.eq(4))&j.target_model.isin(['hat','swinir'])].rename(columns={'target_model':'model'})[['dataset','case','model','input_adj_rmse']].drop_duplicates()
 x=x.merge(ana,on=['dataset','case','model']).merge(plan,on=['dataset','case','model'],how='left').merge(j,on=['dataset','case','model'],how='left')
 rows=[];budgets=[]
 for ds,g in x.groupby('dataset'):
  endpoints=['x4_error']+(['benefit_x4_to_x2'] if g.benefit_x4_to_x2.notna().all() else [])
  for y in endpoints:
   for f in ['score','bipartition_score','phase_grid_score','input_adj_rmse']:
    if g[f].notna().all():rows.append({'dataset':ds,'endpoint':y,'method':f,'rho':rho(g[f],g[y])})
  if 'benefit_x4_to_x2' not in endpoints:continue
  q=g.groupby(['case','patient_cluster'],as_index=False).agg({'benefit_x4_to_x2':'mean','score':'median','bipartition_score':'median','phase_grid_score':'median','input_adj_rmse':'median'});q=q.reset_index(drop=True);cs=q.patient_cluster.unique();groups={c:np.flatnonzero(q.patient_cluster.to_numpy()==c) for c in cs};y=q.benefit_x4_to_x2.to_numpy()
  for b in BUDGETS:
   random=float(y.mean());oracle=gain(y,y,b)
   for f in ['score','bipartition_score','phase_grid_score','input_adj_rmse']:
    s=q[f].to_numpy();v=gain(s,y,b);boot=[]
    for _ in range(5000):
     ix=np.concatenate([groups[c] for c in RNG.choice(cs,len(cs),replace=True)]);boot.append(gain(s[ix],y[ix],b)-float(y[ix].mean()))
    budgets.append({'dataset':ds,'budget':b,'method':f,'selected_gain':v,'gain_above_random':v-random,'fraction_oracle_above_random':(v-random)/(oracle-random),'cluster_95ci_gain_above_random':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))]})
 payload={'experiment':'C5-E011','status':'LOCKED POST-SCORE COMPARISON; comparator set preregistered','correlations':rows,'budgets':budgets};pd.DataFrame(rows).to_csv(OUT/'anchor_cv_comparison_correlations.csv',index=False);pd.DataFrame(budgets).to_csv(OUT/'anchor_cv_comparison_budgets.csv',index=False);(OUT/'anchor_cv_comparison.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
