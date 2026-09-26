"""P6-E01: multi-endpoint reliability under disjoint and shared contexts."""
from __future__ import annotations
import json,sys,time
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import ndimage,stats
from skimage.metrics import structural_similarity

HERE=Path(__file__).resolve();MASTER=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1];CV=PAPER/'CVPR'/'CVPR_UPGRADE';OUT=MASTER/'experiments'
OUT.mkdir(parents=True,exist_ok=True);sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]

def load_net(ds,model,ck):
 if ds=='fastmri':
  if model=='hat':from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator as C
  else:from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator as C
 elif model=='hat':from ixi_hat_2p5d.train import HAT2p5DInterpolator as C
 else:from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator as C
 return C(ck)

def checkpoint(r):
 m=r.architecture
 if r.dataset=='fastmri':return ROOT/'baseline'/f'fastmri_brain_{m}_2p5d'/'runs'/'full'/'checkpoints'/f'{m}_epoch_best.pth'
 if r.dataset=='ixi':
  p=ROOT/'baseline'/f'ixi_{m}_2p5d'/'runs'/'full_test115'/'checkpoints'/f'{m}_epoch_best.pth';return p if p.exists() else ROOT/'baseline'/f'ixi_{m}_2p5d'/'runs'/'full'/'checkpoints'/f'{m}_epoch_best.pth'
 return ROOT/'baseline'/f'ningxia_t2_{m}_2p5d_cv'/'runs'/str(r.split).replace('OOF_','')/'full'/'checkpoints'/f'{m}_epoch_best.pth'

def fg(y):return np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6)
def endpoint(p,y,mask):
 d=(p-y).astype(np.float64);scale=max(float(np.max(y)-np.min(y)),1e-6)
 gp=np.hypot(ndimage.sobel(p,0),ndimage.sobel(p,1));gy=np.hypot(ndimage.sobel(y,0),ndimage.sobel(y,1));lp=ndimage.gaussian_filter(p,2);ly=ndimage.gaussian_filter(y,2)
 return {'mae':float(np.abs(d)[mask].mean()),'rmse':float(np.sqrt(np.mean(d[mask]**2))),'mse':float(np.mean(d[mask]**2)),
         'ssim_error':float(1-structural_similarity(p,y,data_range=scale)),'gradient_mae':float(np.abs(gp-gy)[mask].mean()),
         'lowfreq_mae':float(np.abs(lp-ly)[mask].mean()),'highfreq_mae':float(np.abs((p-lp)-(y-ly))[mask].mean())}
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>5 and np.std(a)>0 and np.std(b)>0 else np.nan

m=pd.read_csv(CV/'DATA_MANIFEST.csv');m=m[(m.factor==4)&m.architecture.isin(['hat','swinir'])];nets={};rows=[];t0=time.perf_counter()
for i,r in enumerate(m.itertuples(),1):
 key=(r.dataset,r.architecture,str(checkpoint(r)))
 if key not in nets:nets[key]=load_net(r.dataset,r.architecture,checkpoint(r))
 gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);p0=nib.load(r.source_file).get_fdata(dtype=np.float32);net=nets[key]
 p2=net.interpolate_volume(np.ascontiguousarray(gt[:,:,2::4]),stride=4);prev=net.interpolate_volume(np.ascontiguousarray(gt[:,:,::4][:,:,::-1]),stride=4)[:,:,::-1]
 candidates=[z for z in range(3,min(gt.shape[2],p0.shape[2],prev.shape[2],p2.shape[2]+2)-2) if z%4 in (1,3)]
 zs=sorted(set(candidates[int(round(v))] for v in np.linspace(0,len(candidates)-1,5)[1:-1]))
 for z in zs:
  y=gt[:,:,z];mask=fg(y)
  for cond,a,b in [('disjoint',p0[:,:,z],p2[:,:,z-2]),('max_shared',p0[:,:,z],prev[:,:,z])]:
   ea=endpoint(a,y,mask);eb=endpoint(b,y,mask);rec={k:.5*(ea[k]+eb[k]) for k in ea};rec['disagreement_mae']=float(np.abs(a-b)[mask].mean())
   rows.append({'dataset':r.dataset,'case':r.case_id,'patient_cluster':r.patient_cluster,'model':r.architecture,'z':z,'condition':cond,**rec})
 print(f'P6-E01 {i}/{len(m)} {r.dataset} {r.architecture} {r.case_id}',flush=True)
x=pd.DataFrame(rows);x.to_csv(OUT/'p6_e01_metric_robustness_per_plane.csv',index=False)
endpoints=['mae','rmse','mse','ssim_error','gradient_mae','lowfreq_mae','highfreq_mae'];summary=[];rng=np.random.default_rng(20260813)
for (ds,model),g in x.groupby(['dataset','model']):
 z=g[g.condition=='disjoint'];h=g[g.condition=='max_shared'];clusters=g.patient_cluster.unique();by={c:g[g.patient_cluster==c] for c in clusters}
 for ep in endpoints:
  rz=rho(z.disagreement_mae,z[ep]);rh=rho(h.disagreement_mae,h[ep]);boots=[]
  for _ in range(2000):
   b=pd.concat([by[c] for c in rng.choice(clusters,len(clusters),replace=True)],ignore_index=True);bz=b[b.condition=='disjoint'];bh=b[b.condition=='max_shared'];boots.append(rho(bz.disagreement_mae,bz[ep])-rho(bh.disagreement_mae,bh[ep]))
  summary.append({'dataset':ds,'model':model,'endpoint':ep,'disjoint_rho':rz,'max_shared_rho':rh,'delta_disjoint_minus_shared':rz-rh,'cluster_ci_low':float(np.nanquantile(boots,.025)),'cluster_ci_high':float(np.nanquantile(boots,.975))})
s=pd.DataFrame(summary);s.to_csv(OUT/'p6_e01_metric_robustness_summary.csv',index=False)
payload={'experiment':'P6-E01','status':'COMPLETE','coverage':['fastmri','ixi','ningxia'],'models':['hat','swinir'],'planes_per_case':3,'endpoints':endpoints,
 'confirmation_rule':'disjoint-minus-shared ranking rho positive for a majority of endpoints in every stratum; all endpoints reported',
 'strata_majority_positive':bool(s.assign(pos=s.delta_disjoint_minus_shared>0).groupby(['dataset','model']).pos.mean().gt(.5).all()),'elapsed_seconds':time.perf_counter()-t0,
 'outputs':['p6_e01_metric_robustness_per_plane.csv','p6_e01_metric_robustness_summary.csv']}
(OUT/'p6_e01_metric_robustness.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(s.to_string(index=False));print(json.dumps(payload,indent=2))
