"""C5-E013: compact exact overlap ladder, all-cohort eligibility replication."""
from __future__ import annotations
import itertools,json
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';RNG=np.random.default_rng(20260813);DIST=np.array([1.,2.,3.,4.]);REF=np.array([1,-1,1,-1]);W=1./DIST
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def cfgs():return {k:[np.array(s) for s in itertools.product([-1,1],repeat=4) if sum(np.array(s)==REF)==k and min(s)<0<max(s)] for k in range(5)}
def pred(v,z,s):
 x=s*DIST;y=np.stack([v[:,:,z+int(q)] for q in x]).astype(np.float64);X=np.stack([np.ones(4),x],1);A=np.linalg.inv(X.T@(W[:,None]*X))@X.T@np.diag(W);return np.tensordot(A[0],y,axes=(0,0))
def met(a,b,y,m):
 ea=(a-y)[m];eb=(b-y)[m];n1=float(ea@ea);n2=float(eb@eb);t=.5*(n1+n2);sh=float(np.sum(((ea+eb)/2)**2));dv=float(np.sum(((ea-eb)/2)**2));return {'error_cosine':float(ea@eb/np.sqrt(n1*n2)),'shared_fraction':sh/t,'observable_fraction':dv/t,'disagreement_mae':float(np.abs(a-b)[m].mean()),'pair_mae':float(.5*(np.abs(ea).mean()+np.abs(eb).mean()))}
def main():
 m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.factor.eq(4))&m.architecture.eq('hat')].drop_duplicates(['dataset','case_id']);cs=cfgs();rows=[]
 for r in m.itertuples():
  v=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32)
  for z in range(4,v.shape[2]-4):
   y=v[:,:,z];mask=np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6)
   if not np.any(mask):continue
   a=pred(v,z,REF)
   for k,ss in cs.items():
    q=[met(a,pred(v,z,s),y,mask) for s in ss];rows.append({'dataset':r.dataset,'case':r.case_id,'patient_cluster':r.patient_cluster,'z':z,'overlap':k,'configurations':len(ss),**{p:float(np.mean([e[p] for e in q])) for p in q[0]}})
  print('C5-E013',r.dataset,r.case_id,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/'compact_four_anchor_overlap_ladder_per_plane.csv',index=False);res=[]
 for ds,g in x.groupby('dataset'):
  lev=[]
  for k,q in g.groupby('overlap'):lev.append({'overlap':int(k),'configurations':int(q.configurations.iloc[0]),'planes':len(q),**{p+'_mean':float(q[p].mean()) for p in ['error_cosine','shared_fraction','observable_fraction','disagreement_mae']},'reliability_rho':rho(q.disagreement_mae,q.pair_mae)})
  clusters=g.patient_cluster.unique();groups={c:g[g.patient_cluster.eq(c)] for c in clusters};tr={p:[] for p in ['error_cosine','shared_fraction','observable_fraction','disagreement_mae']}
  for _ in range(5000):
   b=pd.concat([groups[c] for c in RNG.choice(clusters,len(clusters),replace=True)],ignore_index=True).groupby('overlap')[list(tr)].mean().reset_index()
   for p in tr:tr[p].append(float(stats.spearmanr(b.overlap,b[p]).statistic))
  res.append({'dataset':ds,'cases':int(g.case.nunique()),'patient_clusters':len(clusters),'levels':lev,'level_trends':{p:{'spearman_level_trend':float(stats.spearmanr([q['overlap'] for q in lev],[q[p+'_mean'] for q in lev]).statistic),'cluster_95ci':[float(np.quantile(v,.025)),float(np.quantile(v,.975))]} for p,v in tr.items()}})
 payload={'experiment':'C5-E013','status':'EXPLORATORY / eligibility-driven replication registered before computation','distance_multiset':[1,2,3,4],'rows':res};(OUT/'compact_four_anchor_overlap_ladder_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
