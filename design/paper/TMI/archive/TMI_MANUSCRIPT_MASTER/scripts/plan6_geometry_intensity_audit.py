"""P6-E03: three-cohort geometry and intensity operating-range audit."""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();MASTER=HERE.parents[1];PAPER=HERE.parents[3];CV=PAPER/'CVPR'/'CVPR_UPGRADE';OUT=MASTER/'experiments';FIG=MASTER/'figures';OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
TOLS=(1e-6,1e-5,1e-4,1e-3,1e-2,.1)

def robust(v):
 q=v[np.isfinite(v)&(np.abs(v)>0)];lo,hi=np.percentile(q,[1,99]);return float(lo),float(max(hi-lo,1e-6))
def rho(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float);ok=np.isfinite(a)&np.isfinite(b)
 return float(stats.spearmanr(a[ok],b[ok]).statistic) if ok.sum()>5 and np.std(a[ok])>0 and np.std(b[ok])>0 else np.nan
def boot_delta(g,a,b,reps=2000):
 rng=np.random.default_rng(20260813);g=g.reset_index(drop=True);groups=[g.index[g.patient_cluster.eq(c)].to_numpy() for c in g.patient_cluster.unique()];vals=[]
 for _ in range(reps):
  ix=np.concatenate([groups[j] for j in rng.integers(0,len(groups),len(groups))]);vals.append(rho(g[a].to_numpy()[ix],g.endpoint_raw.to_numpy()[ix])-rho(g[b].to_numpy()[ix],g.endpoint_independent.to_numpy()[ix]))
 return [float(np.nanquantile(vals,.025)),float(np.nanquantile(vals,.975))]

m=pd.read_csv(CV/'DATA_MANIFEST.csv');m=m[(m.factor==4)&m.architecture.isin(['hat','swinir'])]
geometry=[];case_rows=[]
for i,((ds,case),g) in enumerate(m.groupby(['dataset','case_id']),1):
 if set(g.architecture)!= {'hat','swinir'}:continue
 r0=g.iloc[0];gt_img=nib.load(r0.ground_truth_file);gt=gt_img.get_fdata(dtype=np.float32);pred={}
 for _,r in g.iterrows():
  im=nib.load(r.source_file);pred[r.architecture]=im.get_fdata(dtype=np.float32)
  a=gt_img.affine;b=im.affine;normal_a=a[:3,2]/np.linalg.norm(a[:3,2]);normal_b=b[:3,2]/np.linalg.norm(b[:3,2]);angle=np.degrees(np.arccos(np.clip(abs(normal_a@normal_b),-1,1)))
  depth=min(gt.shape[2],pred[r.architecture].shape[2]);dist=[]
  for z in range(depth):dist.append(np.linalg.norm((a@np.array([0,0,z,1]))[:3]-(b@np.array([0,0,z,1]))[:3]))
  rec={'dataset':ds,'case':case,'patient_cluster':r.patient_cluster,'model':r.architecture,'gt_shape':str(gt.shape),'prediction_shape':str(pred[r.architecture].shape),'shape_equal':gt.shape==pred[r.architecture].shape,'orientation_gt':''.join(nib.aff2axcodes(a)),'orientation_prediction':''.join(nib.aff2axcodes(b)),'orientation_equal':nib.aff2axcodes(a)==nib.aff2axcodes(b),'affine_max_abs_delta':float(np.max(np.abs(a-b))),'normal_angle_deg':float(angle),'max_corresponding_plane_distance_mm':float(max(dist))}
  for tol in TOLS:rec[f'planes_matched_at_{tol:g}mm']=int(np.sum(np.asarray(dist)<=tol))
  rec['planes_total']=depth;geometry.append(rec)
 h=pred['hat'];s=pred['swinir'];depth=min(gt.shape[2],h.shape[2],s.shape[2]);anchors=gt[:,:,::4];center,scale=robust(anchors)
 hc,sc,gc=(h-center)/scale,(s-center)/scale,(gt-center)/scale
 centers={};scaled={}
 for name,v in [('hat',h),('swinir',s),('gt',gt)]:centers[name],scaled[name]=robust(v)
 hi=(h-centers['hat'])/scaled['hat'];si=(s-centers['swinir'])/scaled['swinir'];gi=(gt-centers['gt'])/scaled['gt']
 planes=[]
 for z in range(1,depth-1):
  if z%4==0:continue
  y=gt[:,:,z];mask=np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6)
  if not mask.any():continue
  planes.append({'raw_score':float(np.abs(h[:,:,z]-s[:,:,z])[mask].mean()),'raw_endpoint':float(.5*(np.abs(h[:,:,z]-y)[mask].mean()+np.abs(s[:,:,z]-y)[mask].mean())),'pooled_score':float(np.abs(hc[:,:,z]-sc[:,:,z])[mask].mean()),'pooled_endpoint':float(.5*(np.abs(hc[:,:,z]-gc[:,:,z])[mask].mean()+np.abs(sc[:,:,z]-gc[:,:,z])[mask].mean())),'ind_score':float(np.abs(hi[:,:,z]-si[:,:,z])[mask].mean()),'ind_endpoint':float(.5*(np.abs(hi[:,:,z]-gi[:,:,z])[mask].mean()+np.abs(si[:,:,z]-gi[:,:,z])[mask].mean()))})
 q=pd.DataFrame(planes);case_rows.append({'dataset':ds,'case':case,'patient_cluster':r0.patient_cluster,'planes':len(q),'robust_scale':scale,'score_raw':q.raw_score.median(),'endpoint_raw':q.raw_endpoint.median(),'score_pooled':q.pooled_score.median(),'endpoint_pooled':q.pooled_endpoint.median(),'score_independent':q.ind_score.median(),'endpoint_independent':q.ind_endpoint.median()})
 print(f'P6-E03 {i}/{m.groupby(["dataset","case_id"]).ngroups} {ds} {case}',flush=True)

geom=pd.DataFrame(geometry);cases=pd.DataFrame(case_rows);geom.to_csv(OUT/'p6_e03_geometry_per_output.csv',index=False);cases.to_csv(OUT/'p6_e03_intensity_per_case.csv',index=False)
gs=[]
for ds,g in geom.groupby('dataset'):
 rec={'dataset':ds,'cases':g.case.nunique(),'outputs':len(g),'all_shapes_equal':bool(g.shape_equal.all()),'all_orientations_equal':bool(g.orientation_equal.all()),'max_affine_abs_delta':g.affine_max_abs_delta.max(),'max_normal_angle_deg':g.normal_angle_deg.max(),'max_plane_distance_mm':g.max_corresponding_plane_distance_mm.max()}
 for tol in TOLS:rec[f'matched_fraction_at_{tol:g}mm']=g[f'planes_matched_at_{tol:g}mm'].sum()/g.planes_total.sum()
 gs.append(rec)
geom_summary=pd.DataFrame(gs);geom_summary.to_csv(OUT/'p6_e03_geometry_summary.csv',index=False)

ints=[]
for ds,g in cases.groupby('dataset'):
 for strategy,sc,ep in [('raw','score_raw','endpoint_raw'),('pooled_common','score_pooled','endpoint_pooled'),('independent_output','score_independent','endpoint_independent')]:
  ints.append({'dataset':ds,'strategy':strategy,'cases':len(g),'patient_clusters':g.patient_cluster.nunique(),'reliability_rho':rho(g[sc],g[ep]),'score_rank_vs_raw':rho(g.score_raw,g[sc]),'endpoint_rank_vs_raw':rho(g.endpoint_raw,g[ep])})
int_summary=pd.DataFrame(ints);int_summary.to_csv(OUT/'p6_e03_intensity_summary.csv',index=False)

# Re-evaluate the overlap contrast after a single common case scale; this preserves physical comparability.
ov=pd.read_csv(MASTER/'experiments'/'p6_e02_consensus_per_plane.csv');scale=cases[['dataset','case','robust_scale']].rename(columns={'case':'case_id'});ov=ov.merge(scale,on=['dataset','case_id']);ov['disagreement_pooled']=ov.disagreement_mae/ov.robust_scale;ov['error_pooled']=ov.mae/ov.robust_scale
over=[]
for (ds,model),g in ov.groupby(['dataset','model']):
 for strategy,sc,ep in [('raw','disagreement_mae','mae'),('pooled_common','disagreement_pooled','error_pooled')]:
  z=g[g.condition=='disjoint_phase'];h=g[g.condition=='max_shared_reversal'];over.append({'dataset':ds,'model':model,'strategy':strategy,'rho_disjoint':rho(z[sc],z[ep]),'rho_max_shared':rho(h[sc],h[ep]),'delta_disjoint_minus_shared':rho(z[sc],z[ep])-rho(h[sc],h[ep])})
overlap_summary=pd.DataFrame(over);overlap_summary.to_csv(OUT/'p6_e03_overlap_normalization_summary.csv',index=False)

fig,axs=plt.subplots(1,3,figsize=(9.8,3.1),sharey=True)
for ax,(ds,g) in zip(axs,cases.groupby('dataset')):
 ax.scatter(g.score_raw,g.endpoint_raw,s=15,alpha=.65,label='Raw common scale');ax.set_title(ds);ax.set_xlabel('HAT–SwinIR disagreement');ax.grid(alpha=.2)
axs[0].set_ylabel('Paired reconstruction MAE');fig.suptitle('Raw intensity scale strongly structures examination-level disagreement',fontsize=10);fig.tight_layout();fig.savefig(FIG/'p6_e03_intensity_audit.pdf',bbox_inches='tight');fig.savefig(FIG/'p6_e03_intensity_audit.png',dpi=300,bbox_inches='tight');plt.close(fig)

payload={'experiment':'P6-E03','status':'COMPLETE','coverage':['fastmri','ixi','ningxia'],'geometry_tolerances_mm':TOLS,'intensity_strategies':['raw common scale','pooled common per-case scale','independent output normalization (sensitivity only)'],'pooled_overlap_sign_preserved_all_strata':bool((overlap_summary[overlap_summary.strategy=='pooled_common'].delta_disjoint_minus_shared>0).all()),'independent_normalization_interpretation':'invalid for calibrated cross-output discrepancy; included only to show operating boundary','outputs':['p6_e03_geometry_per_output.csv','p6_e03_geometry_summary.csv','p6_e03_intensity_per_case.csv','p6_e03_intensity_summary.csv','p6_e03_overlap_normalization_summary.csv'],'figure':'../figures/p6_e03_intensity_audit.pdf'}
(OUT/'p6_e03_geometry_intensity.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(geom_summary.to_string(index=False));print(int_summary.to_string(index=False));print(overlap_summary.to_string(index=False));print(json.dumps(payload,indent=2))
