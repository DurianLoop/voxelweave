"""C5-E007 frozen clustered intervals from completed per-case outputs."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';RNG=np.random.default_rng(20260813)
def rho(a,b):
 return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def ci(g,y):
 g=g.reset_index(drop=True);clusters=g.patient_cluster.unique();groups=[g.index[g.patient_cluster.eq(c)].to_numpy() for c in clusters];a=g.score.to_numpy();b=g[y].to_numpy();v=[]
 for _ in range(5000):
  ix=np.concatenate([groups[j] for j in RNG.integers(0,len(groups),len(groups))]);r=rho(a[ix],b[ix])
  if np.isfinite(r):v.append(r)
 return [float(x) for x in np.quantile(v,[.025,.975])]
def main():
 pieces=[]
 for stage in ('pilot','full'):
  q=pd.read_csv(OUT/f'acquired_anchor_bipartition_{stage}_per_case.csv');q['dataset']='fastmri';q['patient_cluster']=q.case;q['stage']=stage;pieces.append(q)
 ext=OUT/'acquired_anchor_bipartition_extension_per_case.csv'
 if ext.exists():
  q=pd.read_csv(ext);q['stage']='extension';pieces.append(q)
 x=pd.concat(pieces,ignore_index=True);rows=[]
 for (stage,ds,model),g in x.groupby(['stage','dataset','model']):
  r={'stage':stage,'dataset':ds,'model':model,'cases':int(g.case.nunique()),'patient_clusters':int(g.patient_cluster.nunique()),'rho_score_vs_x4_error':rho(g.score,g.x4_error),'rho_score_vs_x4_error_cluster_95ci':ci(g,'x4_error')}
  if g.benefit_x4_to_x2.notna().all():r.update({'rho_score_vs_benefit':rho(g.score,g.benefit_x4_to_x2),'rho_score_vs_benefit_cluster_95ci':ci(g,'benefit_x4_to_x2')})
  else:r['rho_score_vs_benefit']='NOT RUN: no stored IXI x2 benefit'
  rows.append(r)
 payload={'experiment':'C5-E007','status':'EXPLORATORY pilot then frozen extension','rows':rows};(OUT/'acquired_anchor_bipartition_statistics.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
