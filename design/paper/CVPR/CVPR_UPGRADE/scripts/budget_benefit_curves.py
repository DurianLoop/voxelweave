"""C5-E004: prespecified case/model-unit retrospective densification curves."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];OUT=UP/'outputs';OUT.mkdir(exist_ok=True)
BUDGETS=(.10,.20,.30,.50);RNG=np.random.default_rng(20260813)

def gain(g,score,budget):
 k=max(1,int(np.ceil(budget*len(g))));return float(g.nlargest(k,score).benefit_x4_to_x2.mean())
def gain_arrays(score,benefit,budget):
 k=max(1,int(np.ceil(budget*len(score))));ix=np.argpartition(score,-k)[-k:];return float(np.mean(benefit[ix]))
def random_expected(g,budget):
 # Selection is exchangeable; expected selected benefit is the cohort mean.
 return float(g.benefit_x4_to_x2.mean())
def main():
 x=pd.read_csv(PAPER/'plan4_outputs'/'adaptive_acquisition_per_case.csv')
 mx=pd.read_csv(PAPER/'plan4_outputs'/'max_shared_per_case.csv').rename(columns={'score':'max_shared'})
 j=pd.read_csv(PAPER/'plan3_outputs'/'joint_witness_per_case.csv');j=j[(j.scale.eq(4))&j.target_model.isin(['hat','swinir'])][['dataset','case','target_model','pc','input_adj_rmse']].drop_duplicates()
 t=pd.read_csv(PAPER/'plan3_outputs'/'tta_all_per_case.csv');t=t[(t.scale.eq(4))&t.target_model.isin(['hat','swinir'])][['dataset','case','target_model','tta']]
 # Frozen committee is available for both cohorts in Plan-2 source panels.
 src=PAPER.parent/'rasinet'/'outputs';fb=[]
 q=pd.read_csv(src/'nested_optimization'/'all_finalist_outer_predictions.csv');q=q[(q.method.eq('frozen_baseline'))&(q.scale.eq(4))&q.target_model.isin(['hat','swinir'])]
 fb.append(q[['case','target_model','triage_score']].assign(dataset='ningxia').rename(columns={'triage_score':'committee'}))
 q=pd.read_csv(src/'multiscale'/'per_case_scores.csv');q=q[(q.dataset.eq('fastmri'))&(q.scale.eq(4))&q.target.isin(['hat','swinir'])&(q.method.eq('target_median'))]
 fb.append(q[['dataset','case_id','target','case_score']].rename(columns={'case_id':'case','target':'target_model','case_score':'committee'}))
 fb=pd.concat(fb,ignore_index=True)
 x=x.merge(mx[['dataset','case','target_model','max_shared']],on=['dataset','case','target_model']).merge(j,on=['dataset','case','target_model']).merge(t,on=['dataset','case','target_model']).merge(fb,on=['dataset','case','target_model'])
 # Allocation unit is an acquired examination/series, not a model-case row.
 # Aggregate the two frozen model realizations before policy ranking.
 x=x.groupby(['dataset','case'],as_index=False).agg({
  'benefit_x4_to_x2':'mean','score':'median','max_shared':'median','pc':'median',
  'tta':'median','committee':'median','input_adj_rmse':'median'})
 x['patient_cluster']=np.where(x.dataset.eq('ningxia'),x.case.str.split('_').str[0],x.case)
 features=['score','max_shared','pc','tta','committee','input_adj_rmse'];rows=[]
 for ds,g in x.groupby('dataset'):
  for b in BUDGETS:
   rand=random_expected(g,b);oracle=gain(g,'benefit_x4_to_x2',b)
   rows.append({'dataset':ds,'budget':b,'policy':'random_expected','selected_gain':rand,'gain_above_random':0.,'fraction_oracle_above_random':0.})
   rows.append({'dataset':ds,'budget':b,'policy':'oracle','selected_gain':oracle,'gain_above_random':oracle-rand,'fraction_oracle_above_random':1.})
   for f in features:
    v=gain(g,f,b);rows.append({'dataset':ds,'budget':b,'policy':f,'selected_gain':v,'gain_above_random':v-rand,'fraction_oracle_above_random':(v-rand)/(oracle-rand) if oracle!=rand else np.nan})
 curves=pd.DataFrame(rows);curves.to_csv(OUT/'budget_benefit_curves.csv',index=False)
 # Cluster bootstrap uncertainty for policy minus random at every budget.
 ci=[]
 for (ds,b,policy),r in curves[~curves.policy.isin(['random_expected','oracle'])].groupby(['dataset','budget','policy']):
  g=x[x.dataset.eq(ds)].reset_index(drop=True);clusters=np.array(sorted(g.patient_cluster.unique()));by={c:np.flatnonzero(g.patient_cluster.to_numpy()==c) for c in clusters};boot=[]
  sf=g[policy].to_numpy(float);bf=g.benefit_x4_to_x2.to_numpy(float)
  for _ in range(5000):
   draw=RNG.choice(clusters,len(clusters),replace=True);ix=np.concatenate([by[c] for c in draw]);boot.append(gain_arrays(sf[ix],bf[ix],b)-float(np.mean(bf[ix])))
  ci.append({'dataset':ds,'budget':b,'policy':policy,'cluster_95ci_gain_above_random':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],'patient_clusters':len(clusters)})
 payload={'experiment':'C5-E004','status':'EXPLORATORY RETROSPECTIVE ACQUISITION SIMULATION','budgets':BUDGETS,'unit':'examination/series after median model-score aggregation; patient-cluster inference','curves':rows,'intervals':ci}
 (OUT/'budget_benefit_curves.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
