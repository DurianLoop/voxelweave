"""C5-E011: acquired-anchor leave-one-out cross-validation residual."""
from __future__ import annotations
import json
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];OUT=UP/'outputs';RNG=np.random.default_rng(20260813)
def rho(a,b):
 return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def cluster_ci(g,y,reps=5000):
 g=g.reset_index(drop=True);cs=g.patient_cluster.unique();groups=[g.index[g.patient_cluster.eq(c)].to_numpy() for c in cs];a=g.score.to_numpy();b=g[y].to_numpy();v=[]
 for _ in range(reps):
  ix=np.concatenate([groups[j] for j in RNG.integers(0,len(groups),len(groups))]);r=rho(a[ix],b[ix])
  if np.isfinite(r):v.append(r)
 return [float(x) for x in np.quantile(v,[.025,.975])]
def main():
 m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.factor.eq(4))&m.architecture.isin(['hat','swinir'])]
 rows=[]
 # The score is model-independent; compute it once per case, but retain model-specific stored endpoints.
 cache={}
 for r in m.itertuples():
  key=(r.dataset,r.case_id)
  if key not in cache:
   gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);res=[]
   anchors=list(range(0,gt.shape[2],4))
   for j in range(1,len(anchors)-1):
    z=anchors[j];pred=.5*(gt[:,:,anchors[j-1]]+gt[:,:,anchors[j+1]]);target=gt[:,:,z]
    thr=.01*max(float(np.max(np.abs(target))),1e-6);mask=np.abs(target)>thr
    if np.any(mask):res.append({'z':z,'residual':float(np.abs(pred-target)[mask].mean())})
   cache[key]=res
  base=nib.load(r.source_file).get_fdata(dtype=np.float32);gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);local=[]
  residual_by_z={q['z']:q['residual'] for q in cache[key]}
  for z in range(1,min(base.shape[2],gt.shape[2])):
   if z%4==0:continue
   left=(z//4)*4;right=left+4
   available=[residual_by_z[q] for q in (left,right) if q in residual_by_z]
   if not available:continue
   bz=base[:,:,z];thr=.01*max(float(np.max(np.abs(bz))),1e-6);mask=np.abs(bz)>thr
   if np.any(mask):local.append({'z':z,'local_score':float(np.mean(available)),'x4_error':float(np.abs(bz-gt[:,:,z])[mask].mean())})
  if cache[key] and local:
   rows.append({'dataset':r.dataset,'case':r.case_id,'patient_cluster':r.patient_cluster,'model':r.architecture,'anchor_count':len(cache[key]),'target_planes':len(local),'score':float(np.median([q['residual'] for q in cache[key]])),'x4_error':float(np.median([q['x4_error'] for q in local])),'local_rho':rho(np.array([q['local_score'] for q in local]),np.array([q['x4_error'] for q in local]))})
  print('C5-E011',r.dataset,r.architecture,r.case_id,flush=True)
 x=pd.DataFrame(rows);benefit=pd.read_csv(PAPER/'plan4_outputs'/'adaptive_acquisition_per_case.csv').rename(columns={'target_model':'model'})[['dataset','case','model','benefit_x4_to_x2']];x=x.merge(benefit,on=['dataset','case','model'],how='left');x.to_csv(OUT/'anchor_cross_validation_per_case.csv',index=False)
 summary=[]
 for ds,g in x.groupby('dataset'):
  rec={'dataset':ds,'cases':int(g.case.nunique()),'patient_clusters':int(g.patient_cluster.nunique()),'models':int(g.model.nunique()),'rho_score_vs_x4_error':rho(g.score,g.x4_error),'rho_score_vs_x4_error_cluster_95ci':cluster_ci(g,'x4_error'),'median_within_case_local_rho':float(g.local_rho.median())}
  if g.benefit_x4_to_x2.notna().all():rec.update({'rho_score_vs_benefit':rho(g.score,g.benefit_x4_to_x2),'rho_score_vs_benefit_cluster_95ci':cluster_ci(g,'benefit_x4_to_x2')})
  else:rec['rho_score_vs_benefit']='NOT RUN: no stored IXI x2 benefit'
  summary.append(rec)
 payload={'experiment':'C5-E011','status':'EXPLORATORY / registered before computation','score_information':'only acquired x4 anchors','rows':summary};(OUT/'anchor_cross_validation_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
