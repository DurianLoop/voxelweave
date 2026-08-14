"""C5-E010: paired clean-overlap stable-wrong prevalence."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';RNG=np.random.default_rng(20260813)
def load_pair(zero_path,max_path):
 z=pd.read_csv(zero_path);z=z[z.overlap.eq(0)][['dataset','case_id','patient_cluster','model','z','disagreement_mae','mae']].rename(columns={'disagreement_mae':'score_zero','mae':'error_zero'})
 h=pd.read_csv(max_path)[['dataset','case_id','patient_cluster','model','z','score','error']].rename(columns={'score':'score_max','error':'error_max'})
 return z.merge(h,on=['dataset','case_id','patient_cluster','model','z'],validate='one_to_one')
def main():
 a=load_pair(OUT/'overlap_covariance_per_plane.csv',OUT/'clean_max_overlap_per_plane.csv')
 b=load_pair(OUT/'overlap_covariance_ixi_per_plane.csv',OUT/'clean_max_overlap_ixi_per_plane.csv')
 x=pd.concat([a,b],ignore_index=True);rows=[]
 for ds,g in x.groupby('dataset'):
  flags=[]
  for model,q in g.groupby('model'):
   e=float(q.error_zero.quantile(.75));s=float(q.score_zero.quantile(.25));q=q.copy();q['zero']=((q.error_zero>=e)&(q.score_zero<=s)).astype(float);q['max']=((q.error_max>=e)&(q.score_max<=s)).astype(float);flags.append(q)
  q=pd.concat(flags,ignore_index=True);delta=float((q['max']-q.zero).mean());clusters=q.patient_cluster.unique();groups={c:q[q.patient_cluster.eq(c)] for c in clusters};boot=[]
  for _ in range(5000):
   r=pd.concat([groups[c] for c in RNG.choice(clusters,len(clusters),replace=True)],ignore_index=True);boot.append(float((r['max']-r.zero).mean()))
  rows.append({'dataset':ds,'cases':int(q.case_id.nunique()),'patient_clusters':len(clusters),'planes':len(q),'zero_prevalence':float(q.zero.mean()),'clean_max_prevalence':float(q['max'].mean()),'max_minus_zero':delta,'cluster_95ci':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))]})
 payload={'experiment':'C5-E010','status':'EXPLORATORY / threshold registered before computation','definition':'error >= zero-condition model-specific Q75 and score <= zero-condition model-specific Q25','rows':rows};(OUT/'stable_wrong_prevalence.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
