"""P6-E12: three-cohort examination-level risk-coverage comparisons."""
from __future__ import annotations
import json
from pathlib import Path
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np,pandas as pd

HERE=Path(__file__).resolve();MASTER=HERE.parents[1];PAPER=HERE.parents[3];CV=PAPER/'CVPR'/'CVPR_UPGRADE';OUT=MASTER/'experiments';FIG=MASTER/'figures';OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
COV=(.1,.2,.3,.5,.7,.9,1.0);rng=np.random.default_rng(20260813)
def mask(v):return np.abs(v)>.01*max(float(np.max(np.abs(v))),1e-6)
def risk(y,s,c):
 k=max(1,int(np.ceil(len(y)*c)));return float(np.mean(np.asarray(y)[np.argsort(np.asarray(s))[:k]]))

# Disjoint and max-shared scores/endpoints from identical physical-plane pairs.
ov=pd.concat([pd.read_csv(CV/'outputs'/'overlap_covariance_per_plane.csv'),pd.read_csv(CV/'outputs'/'overlap_covariance_ixi_per_plane.csv')],ignore_index=True)
agg=ov.groupby(['dataset','case_id','patient_cluster','condition'],as_index=False).agg(score=('disagreement_mae','median'),endpoint=('mae','median'))
wide=agg.pivot(index=['dataset','case_id','patient_cluster'],columns='condition',values=['score','endpoint']).reset_index();wide.columns=['_'.join([str(q) for q in c if q]) for c in wide.columns]
wide=wide.rename(columns={'case_id':'case','score_disjoint_phase':'Measurement-disjoint','score_max_shared_reversal':'Max-shared','endpoint_disjoint_phase':'error_disjoint','endpoint_max_shared_reversal':'error_shared'})

# Committee disagreement uses the already frozen HAT/SwinIR x4 predictions.
m=pd.read_csv(CV/'DATA_MANIFEST.csv');m=m[(m.factor==4)&m.architecture.isin(['hat','swinir'])];com=[]
for (ds,case),g in m.groupby(['dataset','case_id']):
 if set(g.architecture)!= {'hat','swinir'}:continue
 h=nib.load(g[g.architecture=='hat'].iloc[0].source_file).get_fdata(dtype=np.float32);s=nib.load(g[g.architecture=='swinir'].iloc[0].source_file).get_fdata(dtype=np.float32);gt=nib.load(g.iloc[0].ground_truth_file).get_fdata(dtype=np.float32);vals=[];errs=[]
 for z in range(1,min(h.shape[2],s.shape[2],gt.shape[2])-1):
  if z%4==0:continue
  mm=mask(gt[:,:,z]);vals.append(np.abs(h[:,:,z]-s[:,:,z])[mm].mean());errs.append(.5*(np.abs(h[:,:,z]-gt[:,:,z])[mm].mean()+np.abs(s[:,:,z]-gt[:,:,z])[mm].mean()))
 com.append({'dataset':ds,'case':case,'Committee':float(np.median(vals)),'committee_error':float(np.median(errs))})
wide=wide.merge(pd.DataFrame(com),on=['dataset','case'])

# Acquired-input baseline, averaged over the duplicate architecture endpoints.
inp=pd.read_csv(CV/'outputs'/'plan6_anchor_cv_explanation_per_case.csv').groupby(['dataset','case','patient_cluster'],as_index=False).agg(**{'Adjacent-anchor MAE':('adjacent_mae','first'),'x4_error':('x4_error','mean')})
wide=wide.merge(inp[['dataset','case','Adjacent-anchor MAE','x4_error']],on=['dataset','case'])
wide['endpoint']=wide.x4_error;wide.to_csv(OUT/'p6_e12_risk_per_case.csv',index=False)
methods=['Measurement-disjoint','Max-shared','Committee','Adjacent-anchor MAE'];fixed=[];curve=[];summary=[]
for ds,g in wide.groupby('dataset'):
 g=g.reset_index(drop=True);clusters=g.patient_cluster.unique();groups=[g.index[g.patient_cluster.eq(c)].to_numpy() for c in clusters];y=g.endpoint.to_numpy(float);oracle=np.cumsum(np.sort(y))/np.arange(1,len(y)+1);reverse=np.cumsum(np.sort(y)[::-1])/np.arange(1,len(y)+1)
 for method in methods:
  s=g[method].to_numpy(float);order=np.argsort(s);rr=np.cumsum(y[order])/np.arange(1,len(y)+1);naurc=float((rr.mean()-oracle.mean())/(reverse.mean()-oracle.mean()));summary.append({'dataset':ds,'method':method,'cases':len(g),'patient_clusters':len(clusters),'spearman':float(pd.Series(s).corr(pd.Series(y),method='spearman')),'nAURC':naurc})
  for k,v in enumerate(rr,1):curve.append({'dataset':ds,'method':method,'coverage':k/len(y),'retained_risk':v})
  for cov in COV:
   p=risk(y,s,cov);boots=[]
   for _ in range(2000):
    ix=np.concatenate([groups[j] for j in rng.integers(0,len(groups),len(groups))]);boots.append(risk(y[ix],s[ix],cov))
   fixed.append({'dataset':ds,'method':method,'coverage':cov,'retained_risk':p,'cluster_ci_low':float(np.quantile(boots,.025)),'cluster_ci_high':float(np.quantile(boots,.975)),'random_risk':float(y.mean()),'oracle_risk':risk(y,y,cov)})
pd.DataFrame(summary).to_csv(OUT/'p6_e12_risk_summary.csv',index=False);pd.DataFrame(curve).to_csv(OUT/'p6_e12_risk_full_curves.csv',index=False);pd.DataFrame(fixed).to_csv(OUT/'p6_e12_risk_fixed_coverages.csv',index=False)
colors={'Measurement-disjoint':'#1f5fa8','Max-shared':'#d05b3e','Committee':'#629f53','Adjacent-anchor MAE':'#7b5aa6'};fig,axs=plt.subplots(1,3,figsize=(10.2,3.1),sharey=False)
cur=pd.DataFrame(curve)
for ax,ds in zip(axs,['fastmri','ixi','ningxia']):
 for method,c in colors.items():
  q=cur[(cur.dataset==ds)&(cur.method==method)];ax.plot(q.coverage,q.retained_risk,color=c,lw=1.5,label=method)
 ax.set_title(ds);ax.set_xlabel('Retained examination coverage');ax.grid(alpha=.2)
axs[0].set_ylabel('Retained x4 MAE');axs[0].legend(frameon=False,fontsize=7);fig.suptitle('Risk–coverage depends on how prediction dependence is constructed',fontsize=10);fig.tight_layout();fig.savefig(FIG/'p6_e12_risk_coverage.pdf',bbox_inches='tight');fig.savefig(FIG/'p6_e12_risk_coverage.png',dpi=300,bbox_inches='tight');plt.close(fig)
payload={'experiment':'P6-E12','status':'COMPLETE','coverage':['fastmri','ixi','ningxia'],'methods':methods,'endpoint':'independently stored mean HAT/SwinIR x4 examination MAE; no score-specific error is included in the common endpoint','tta_status':'excluded: definition-matched IXI TTA output unavailable; fastMRI+NingXia-only comparison prohibited by coverage invariant','interpretation':'retrospective selective triage, not clinical abstention validation','outputs':['p6_e12_risk_per_case.csv','p6_e12_risk_summary.csv','p6_e12_risk_full_curves.csv','p6_e12_risk_fixed_coverages.csv'],'figure':'../figures/p6_e12_risk_coverage.pdf'}
(OUT/'p6_e12_risk_coverage.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(pd.DataFrame(summary).to_string(index=False));print(json.dumps(payload,indent=2))
