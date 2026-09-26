"""Patient-cluster corrections for frozen NingXia evidence.

Historical files remain immutable. This script only resamples the eight NX
patient prefixes and writes superseding inferential summaries into Track A.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve(); TMI=HERE.parents[1]; PAPER=HERE.parents[3]
OUT=TMI/'tables'; OUT.mkdir(parents=True,exist_ok=True)
RNG=np.random.default_rng(20260813)

def rho(a,b):
 return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def cluster_boot(groups,fn,n=5000):
 keys=np.array(sorted(groups)); vals=[]
 for _ in range(n):
  draw=RNG.choice(keys,len(keys),replace=True)
  b=pd.concat([groups[k].assign(_draw=i) for i,k in enumerate(draw)],ignore_index=True)
  vals.append(fn(b))
 return [float(np.nanquantile(vals,.025)),float(np.nanquantile(vals,.975))]

def overlap():
 x=pd.read_csv(PAPER/'plan4_outputs'/'overlap_zero_vs_max_paired.csv');x=x[x.dataset.eq('ningxia')].copy()
 x['patient']=x.case.str.split('_').str[0]; groups={k:g for k,g in x.groupby('patient')}
 rows=[]
 for name,g in [('pooled',x)]+list(x.groupby('target_model')):
  gs={k:q for k,q in g.groupby('patient')}
  rr=lambda q,c:rho(q.groupby('target_model')[c].rank(pct=True),q.phase0_error)
  fn=lambda q:rr(q,'disjoint_inconsistency')-rr(q,'max_shared_inconsistency')
  rows.append({'architecture':name,'patients':g.patient.nunique(),'series':g.case.nunique(),'planes':len(g),
   'rho_zero':rr(g,'disjoint_inconsistency'),'rho_max':rr(g,'max_shared_inconsistency'),
   'delta':fn(g),'patient_cluster_95ci':cluster_boot(gs,fn)})
 return rows

def adaptive():
 x=pd.read_csv(PAPER/'plan4_outputs'/'adaptive_acquisition_per_case.csv');x=x[x.dataset.eq('ningxia')].copy();x['patient']=x.case.str.split('_').str[0]
 fn=lambda q:rho(q.score,q.benefit_x4_to_x2);gs={k:g for k,g in x.groupby('patient')}
 return {'patients':x.patient.nunique(),'series':x.case.nunique(),'model_series_units':len(x),'rho':fn(x),'patient_cluster_95ci':cluster_boot(gs,fn)}

def aurc(error,score):
 order=np.argsort(score);risk=np.cumsum(np.asarray(error)[order])/np.arange(1,len(error)+1);a=float(risk.mean())
 oracle=float((np.cumsum(np.sort(error))/np.arange(1,len(error)+1)).mean());rev=float((np.cumsum(np.sort(error)[::-1])/np.arange(1,len(error)+1)).mean())
 return (a-oracle)/(rev-oracle) if rev>oracle else 0.
def tta():
 x=pd.read_csv(PAPER/'plan3_outputs'/'tta_all_per_case.csv');x=x[x.dataset.eq('ningxia')].copy();x['patient']=x.case.str.split('_').str[0]
 def statistic(q):
  ds=[]
  for _,g in q.groupby(['scale','target_model']):ds.append(aurc(g.common_error,g.pc)-aurc(g.common_error,g.tta))
  return float(np.mean(ds))
 obs=statistic(x);patients=np.array(sorted(x.patient.unique()));null=[]
 for _ in range(10000):
  z=x.copy();sw=set(patients[RNG.random(len(patients))<.5]);m=z.patient.isin(sw);a=z.loc[m,'pc'].copy();z.loc[m,'pc']=z.loc[m,'tta'].values;z.loc[m,'tta']=a.values;null.append(statistic(z))
 return {'patients':len(patients),'series':x.case.nunique(),'profiles':9,'mean_delta_pc_minus_tta_nAURC':obs,
  'patient_clustered_swap_p_two_sided':float((1+np.sum(np.abs(null)>=abs(obs)))/(len(null)+1)),'permutations':len(null)}

def main():
 result={'status':'SUPERSEDING INFERENCE; point estimates unchanged','seed':20260813,'bootstrap_replicates':5000,
  'overlap_zero_vs_reversal_max':overlap(),'adaptive_benefit':adaptive(),'pc_vs_tta':tta()}
 (OUT/'ningxia_patient_cluster_corrections.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
