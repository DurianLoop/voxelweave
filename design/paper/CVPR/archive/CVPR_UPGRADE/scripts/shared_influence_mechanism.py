"""C5-E014: test coefficient-vector shared influence versus raw overlap count."""
from __future__ import annotations
import itertools,json
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';RNG=np.random.default_rng(20260813);D=np.array([1.,2.,3.,4.]);REF=np.array([1,-1,1,-1]);W=1/D
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def coeff(s):
 x=s*D;X=np.stack([np.ones(4),x],1);return (np.linalg.inv(X.T@(W[:,None]*X))@X.T@np.diag(W))[0]
def geometry(s):
 ca=coeff(REF);cb=coeff(s);positions=sorted(set((REF*D).astype(int))|set((s*D).astype(int)));a=np.zeros(len(positions));b=np.zeros(len(positions))
 for p,c in zip((REF*D).astype(int),ca):a[positions.index(p)]=c
 for p,c in zip((s*D).astype(int),cb):b[positions.index(p)]=c
 return {'coefficient_cosine':float(a@b/np.sqrt((a@a)*(b@b))),'coefficient_dot':float(a@b),'common_abs_mass':float(sum(min(abs(a[i]),abs(b[i])) for i in range(len(a)))),'ca':ca,'cb':cb}
def pred(v,z,s,c):return np.tensordot(c,np.stack([v[:,:,z+int(q)] for q in s*D]).astype(np.float64),axes=(0,0))
def main():
 signs=[np.array(s) for s in itertools.product([-1,1],repeat=4) if min(s)<0<max(s)];geo=[geometry(s) for s in signs];m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.factor.eq(4))&m.architecture.eq('hat')].drop_duplicates(['dataset','case_id']);rows=[]
 for r in m.itertuples():
  v=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);acc={i:[] for i in range(len(signs))}
  for z in range(4,v.shape[2]-4):
   y=v[:,:,z];mask=np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6)
   if not np.any(mask):continue
   a=pred(v,z,REF,coeff(REF))
   for i,(s,g) in enumerate(zip(signs,geo)):
    b=pred(v,z,s,g['cb']);ea=(a-y)[mask];eb=(b-y)[mask];n1=float(ea@ea);n2=float(eb@eb);tot=.5*(n1+n2);sh=float(np.sum(((ea+eb)/2)**2));dv=float(np.sum(((ea-eb)/2)**2));acc[i].append((float(ea@eb/np.sqrt(n1*n2)),sh/tot,dv/tot,float(np.abs(a-b)[mask].mean())))
  for i,(s,g) in enumerate(zip(signs,geo)):
   q=np.array(acc[i]);rows.append({'dataset':r.dataset,'case':r.case_id,'patient_cluster':r.patient_cluster,'config_id':i,'signs':''.join('+' if z>0 else '-' for z in s),'overlap_count':int(np.sum(s==REF)),'coefficient_cosine':g['coefficient_cosine'],'coefficient_dot':g['coefficient_dot'],'common_abs_mass':g['common_abs_mass'],'planes':len(q),'error_cosine':float(q[:,0].mean()),'shared_fraction':float(q[:,1].mean()),'observable_fraction':float(q[:,2].mean()),'disagreement_mae':float(q[:,3].mean())})
  print('C5-E014',r.dataset,r.case_id,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/'shared_influence_per_case_config.csv',index=False);res=[];ys=['error_cosine','shared_fraction','observable_fraction','disagreement_mae']
 for ds,g in x.groupby('dataset'):
  c=g.groupby(['config_id','overlap_count','coefficient_cosine','coefficient_dot','common_abs_mass'],as_index=False)[ys].mean();assoc=[]
  for y in ys:
   assoc.append({'endpoint':y,'rho_overlap_count':rho(c.overlap_count,c[y]),'rho_coefficient_cosine':rho(c.coefficient_cosine,c[y]),'rho_coefficient_dot':rho(c.coefficient_dot,c[y]),'rho_common_abs_mass':rho(c.common_abs_mass,c[y])})
  clusters=g.patient_cluster.unique();groups={z:g[g.patient_cluster.eq(z)] for z in clusters};boot={y:[] for y in ys}
  for _ in range(5000):
   b=pd.concat([groups[z] for z in RNG.choice(clusters,len(clusters),replace=True)],ignore_index=True).groupby(['config_id','overlap_count','coefficient_cosine'],as_index=False)[ys].mean()
   for y in ys:boot[y].append(abs(rho(b.coefficient_cosine,b[y]))-abs(rho(b.overlap_count,b[y])))
  res.append({'dataset':ds,'cases':int(g.case.nunique()),'patient_clusters':len(clusters),'configurations':len(c),'associations':assoc,'abs_rho_advantage_influence_over_count_cluster_95ci':{y:[float(np.quantile(v,.025)),float(np.quantile(v,.975))] for y,v in boot.items()}})
 payload={'experiment':'C5-E014','status':'EXPLORATORY / registered after ladder falsification and before computation','rows':res};(OUT/'shared_influence_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
