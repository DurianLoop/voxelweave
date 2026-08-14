"""P6-E11: three-cohort x2/x4/x6 analytical factor robustness."""
from __future__ import annotations
import json
from pathlib import Path
import nibabel as nib
import numpy as np,pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();MASTER=HERE.parents[1];PAPER=HERE.parents[3];MAN=PAPER/'CVPR'/'CVPR_UPGRADE'/'DATA_MANIFEST.csv';OUT=MASTER/'experiments';OUT.mkdir(parents=True,exist_ok=True)
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>2 and np.std(a)>0 and np.std(b)>0 else np.nan
m=pd.read_csv(MAN);m=m[(m.factor==4)&(m.architecture=='hat')].drop_duplicates(['dataset','case_id']);rows=[]
for ir,r in enumerate(m.itertuples(),1):
 v=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32)
 for factor in (2,4,6):
  anchors=np.arange(0,v.shape[2],factor)
  for z in range(v.shape[2]):
   if z%factor==0:continue
   left=anchors[anchors<z];right=anchors[anchors>z]
   if len(left)<1 or len(right)<1:continue
   l0=left[-1];r0=right[0];rel=(z-l0)/(r0-l0)
   linear=(1-rel)*v[:,:,l0]+rel*v[:,:,r0];nearest=v[:,:,l0 if (z-l0)<=(r0-z) else r0]
   y=v[:,:,z];mask=np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6)
   ea=(linear-y)[mask].astype(float);eb=(nearest-y)[mask].astype(float);n1=ea@ea;n2=eb@eb;tot=.5*(n1+n2);sh=np.sum(((ea+eb)/2)**2);ob=np.sum(((ea-eb)/2)**2)
   rows.append({'dataset':r.dataset,'case':r.case_id,'patient_cluster':r.patient_cluster,'factor':factor,'z':z,'linear_mae':np.abs(ea).mean(),'nearest_mae':np.abs(eb).mean(),'pair_mae':.5*(np.abs(ea).mean()+np.abs(eb).mean()),'disagreement_mae':np.abs(ea-eb).mean(),'error_cosine':ea@eb/np.sqrt(n1*n2),'shared_fraction':sh/tot,'observable_fraction':ob/tot})
 print(f'P6-E11 {ir}/{len(m)} {r.dataset} {r.case_id}',flush=True)
x=pd.DataFrame(rows);x.to_csv(OUT/'p6_e11_analytic_factor_per_plane.csv',index=False);summary=[];rng=np.random.default_rng(20260813)
for (ds,f),g in x.groupby(['dataset','factor']):
 clusters=g.patient_cluster.unique();by={c:g[g.patient_cluster==c] for c in clusters};rec={'dataset':ds,'factor':f,'cases':g.case.nunique(),'patient_clusters':len(clusters),'planes':len(g)}
 for c in ['linear_mae','nearest_mae','pair_mae','disagreement_mae','error_cosine','shared_fraction','observable_fraction']:
  vals=[]
  for _ in range(2000):
   b=pd.concat([by[k] for k in rng.choice(clusters,len(clusters),replace=True)],ignore_index=True);vals.append(b[c].mean())
  rec[c+'_mean']=g[c].mean();rec[c+'_ci_low']=np.quantile(vals,.025);rec[c+'_ci_high']=np.quantile(vals,.975)
 rec['reliability_rho']=rho(g.disagreement_mae,g.pair_mae);summary.append(rec)
s=pd.DataFrame(summary);s.to_csv(OUT/'p6_e11_analytic_factor_summary.csv',index=False)
tr=[]
for ds,g in s.groupby('dataset'):
 for metric in ['pair_mae_mean','shared_fraction_mean','observable_fraction_mean','disagreement_mae_mean','reliability_rho']:
  tr.append({'dataset':ds,'metric':metric,'spearman_vs_factor':rho(g['factor'],g[metric]),'x2':g.loc[g['factor']==2,metric].iloc[0],'x4':g.loc[g['factor']==4,metric].iloc[0],'x6':g.loc[g['factor']==6,metric].iloc[0]})
pd.DataFrame(tr).to_csv(OUT/'p6_e11_analytic_factor_trends.csv',index=False)
payload={'experiment':'P6-E11','status':'COMPLETE','coverage':['fastmri','ixi','ningxia'],'factors':[2,4,6],'estimators':['two-anchor linear','nearest-anchor replication'],'scope':'analytical estimator generality; does not substitute for unavailable IXI neural x2/x6 outputs; four-anchor cubic is infeasible at x6 for the shallow fastMRI/NingXia volumes','outputs':['p6_e11_analytic_factor_per_plane.csv','p6_e11_analytic_factor_summary.csv','p6_e11_analytic_factor_trends.csv']};(OUT/'p6_e11_analytic_factor.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(s.to_string(index=False));print(pd.DataFrame(tr).to_string(index=False))
