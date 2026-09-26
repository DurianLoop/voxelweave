"""C5-E009: budget curves for the target-unavailable acquired-anchor score."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';BUDGETS=(.1,.2,.3,.5);RNG=np.random.default_rng(20260813)
def gain(score,benefit,b):
 k=max(1,int(np.ceil(b*len(score))));ix=np.argpartition(score,-k)[-k:];return float(np.mean(benefit[ix]))
def main():
 x=pd.read_csv(OUT/'analytical_acquired_anchor_bipartition_per_case.csv')
 x=x[x.benefit_x4_to_x2.notna()].groupby(['dataset','case','patient_cluster'],as_index=False).agg(score=('score','median'),benefit=('benefit_x4_to_x2','mean'))
 baseline=pd.read_csv(OUT/'budget_benefit_curves.csv');rows=[];intervals=[]
 for ds,g in x.groupby('dataset'):
  g=g.reset_index(drop=True);s=g.score.to_numpy();y=g.benefit.to_numpy();clusters=g.patient_cluster.unique();groups={c:np.flatnonzero(g.patient_cluster.to_numpy()==c) for c in clusters}
  for b in BUDGETS:
   random=float(y.mean());oracle=gain(y,y,b);selected=gain(s,y,b)
   best=baseline[(baseline.dataset.eq(ds))&baseline.budget.eq(b)&~baseline.policy.isin(['random_expected','oracle'])].sort_values('selected_gain',ascending=False).iloc[0]
   rows.append({'dataset':ds,'budget':b,'policy':'acquired_anchor_linear_bipartition','selected_gain':selected,'gain_above_random':selected-random,'fraction_oracle_above_random':(selected-random)/(oracle-random),'best_existing_policy':best.policy,'best_existing_selected_gain':float(best.selected_gain)})
   boot=[]
   for _ in range(5000):
    draw=RNG.choice(clusters,len(clusters),replace=True);ix=np.concatenate([groups[c] for c in draw]);boot.append(gain(s[ix],y[ix],b)-float(y[ix].mean()))
   intervals.append({'dataset':ds,'budget':b,'cluster_95ci_gain_above_random':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],'patient_clusters':len(clusters)})
 payload={'experiment':'C5-E009','status':'EXPLORATORY RETROSPECTIVE ACQUISITION SIMULATION','rows':rows,'intervals':intervals}
 pd.DataFrame(rows).to_csv(OUT/'bipartition_budget_curves.csv',index=False);(OUT/'bipartition_budget_curves.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
