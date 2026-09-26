"""C5-E011 paired clustered Spearman differences versus locked comparators."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];OUT=UP/'outputs';RNG=np.random.default_rng(20260813)
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def main():
 x=pd.read_csv(OUT/'anchor_cross_validation_per_case.csv');ana=pd.read_csv(OUT/'analytical_acquired_anchor_bipartition_per_case.csv').rename(columns={'score':'bipartition_score'})[['dataset','case','model','bipartition_score']];plan=pd.read_csv(PAPER/'plan4_outputs'/'adaptive_acquisition_per_case.csv').rename(columns={'target_model':'model','score':'phase_grid_score'})[['dataset','case','model','phase_grid_score']];j=pd.read_csv(PAPER/'plan3_outputs'/'joint_witness_per_case.csv');j=j[(j.scale.eq(4))&j.target_model.isin(['hat','swinir'])].rename(columns={'target_model':'model'})[['dataset','case','model','input_adj_rmse']].drop_duplicates();x=x.merge(ana,on=['dataset','case','model']).merge(plan,on=['dataset','case','model'],how='left').merge(j,on=['dataset','case','model'],how='left');rows=[]
 for ds,g in x.groupby('dataset'):
  g=g.reset_index(drop=True);cs=g.patient_cluster.unique();groups=[g.index[g.patient_cluster.eq(c)].to_numpy() for c in cs];ends=['x4_error']+(['benefit_x4_to_x2'] if g.benefit_x4_to_x2.notna().all() else [])
  for y in ends:
   for f in ['bipartition_score','phase_grid_score','input_adj_rmse']:
    if not g[f].notna().all():continue
    point=rho(g.score,g[y])-rho(g[f],g[y]);boot=[]
    for _ in range(5000):
     ix=np.concatenate([groups[j] for j in RNG.integers(0,len(groups),len(groups))]);d=rho(g.score.to_numpy()[ix],g[y].to_numpy()[ix])-rho(g[f].to_numpy()[ix],g[y].to_numpy()[ix])
     if np.isfinite(d):boot.append(d)
    rows.append({'dataset':ds,'endpoint':y,'anchor_cv_minus':f,'delta_rho':point,'cluster_95ci':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))]})
 payload={'experiment':'C5-E011','status':'paired clustered comparison; locked comparator set','rows':rows};(OUT/'anchor_cv_paired_deltas.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
