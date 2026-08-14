"""C5-E012: exact five-level overlap ladder for a four-anchor local estimator."""
from __future__ import annotations
import itertools,json
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';RNG=np.random.default_rng(20260813)
DIST=np.array([2.,4.,6.,8.]);REF=np.array([1,-1,1,-1]);W=1./DIST
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def configs():
 out={}
 for k in range(5):
  v=[]
  for s in itertools.product([-1,1],repeat=4):
   s=np.array(s)
   if int(np.sum(s==REF))==k and np.any(s<0) and np.any(s>0):v.append(s)
  out[k]=v
 return out
def predict(vol,z,sign):
 x=sign*DIST;idx=(z+x.astype(int));y=np.stack([vol[:,:,q] for q in idx],axis=0).astype(np.float64)
 X=np.stack([np.ones(4),x],axis=1);A=np.linalg.inv(X.T@(W[:,None]*X))@X.T@np.diag(W)
 return np.tensordot(A[0],y,axes=(0,0))
def metrics(a,b,y,mask):
 ea=(a-y)[mask];eb=(b-y)[mask];n1=float(ea@ea);n2=float(eb@eb);total=.5*(n1+n2);shared=float(np.sum(((ea+eb)/2)**2));div=float(np.sum(((ea-eb)/2)**2))
 return {'error_cosine':float(ea@eb/np.sqrt(n1*n2)) if n1*n2>0 else np.nan,'shared_fraction':shared/total if total else np.nan,'observable_fraction':div/total if total else np.nan,'disagreement_mae':float(np.abs(a-b)[mask].mean()),'pair_mae':float(.5*(np.abs(ea).mean()+np.abs(eb).mean()))}
def main():
 m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.factor.eq(4))&m.architecture.eq('hat')].drop_duplicates(['dataset','case_id']);cfg=configs();rows=[]
 for r in m.itertuples():
  vol=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32)
  for z in range(8,vol.shape[2]-8):
   y=vol[:,:,z];thr=.01*max(float(np.max(np.abs(y))),1e-6);mask=np.abs(y)>thr
   if not np.any(mask):continue
   a=predict(vol,z,REF)
   for k,vs in cfg.items():
    mm=[metrics(a,predict(vol,z,s),y,mask) for s in vs]
    rows.append({'dataset':r.dataset,'case':r.case_id,'patient_cluster':r.patient_cluster,'z':z,'overlap':k,'configurations':len(vs),**{q:float(np.mean([p[q] for p in mm])) for q in mm[0]}})
  print('C5-E012',r.dataset,r.case_id,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/'four_anchor_overlap_ladder_per_plane.csv',index=False);summary=[]
 for ds,g in x.groupby('dataset'):
  levels=[]
  for k,q in g.groupby('overlap'):
   levels.append({'overlap':int(k),'configurations':int(q.configurations.iloc[0]),'planes':len(q),'error_cosine_mean':float(q.error_cosine.mean()),'shared_fraction_mean':float(q.shared_fraction.mean()),'observable_fraction_mean':float(q.observable_fraction.mean()),'disagreement_mae_mean':float(q.disagreement_mae.mean()),'reliability_rho':rho(q.disagreement_mae,q.pair_mae)})
  # Bootstrap endpoint slopes over all planes retained within sampled clusters.
  cs=g.patient_cluster.unique();groups={c:g[g.patient_cluster.eq(c)] for c in cs};boots={q:[] for q in ['error_cosine','shared_fraction','observable_fraction','disagreement_mae']}
  for _ in range(5000):
   b=pd.concat([groups[c] for c in RNG.choice(cs,len(cs),replace=True)],ignore_index=True);means=b.groupby('overlap')[list(boots)].mean().reset_index()
   for q in boots:boots[q].append(float(stats.spearmanr(means.overlap,means[q]).statistic))
  slopes={q:{'spearman_level_trend':float(stats.spearmanr([p['overlap'] for p in levels],[p[q+'_mean'] for p in levels]).statistic),'cluster_95ci':[float(np.quantile(v,.025)),float(np.quantile(v,.975))]} for q,v in boots.items()}
  summary.append({'dataset':ds,'cases':int(g.case.nunique()),'patient_clusters':len(cs),'levels':levels,'level_trends':slopes})
 payload={'experiment':'C5-E012','status':'EXPLORATORY / registered before computation','distance_multiset':[2,4,6,8],'reference_signs':['+','-','+','-'],'rows':summary};(OUT/'four_anchor_overlap_ladder_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
