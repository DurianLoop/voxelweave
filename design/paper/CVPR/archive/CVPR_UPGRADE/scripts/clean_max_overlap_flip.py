"""C5-E003: clean maximum-overlap control using one in-plane flip.

The same x4 measurements, z order, target, distances, network, and preprocessing
are retained. Only an in-plane equivariance view is changed and mapped back.
"""
from __future__ import annotations
import json,sys
import argparse
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1];OUT=UP/'outputs'
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]
def model(ds,target,ck):
 if ds=='fastmri':
  if target=='hat':
   from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator;return FastMRIHAT2p5DInterpolator(ck)
  from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator;return FastMRISwinIR2p5DInterpolator(ck)
 if target=='hat':
  from ixi_hat_2p5d.train import HAT2p5DInterpolator;return HAT2p5DInterpolator(ck)
 from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator;return SwinIR2p5DInterpolator(ck)
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def vals(a,b,y,mask):
 e1=(a-y)[mask].astype(float);e2=(b-y)[mask].astype(float);n1=e1@e1;n2=e2@e2;total=.5*(n1+n2);shared=np.sum(((e1+e2)/2)**2);div=np.sum(((e1-e2)/2)**2)
 return {'score':float(np.abs(e1-e2).mean()),'error':float(.5*(np.abs(e1).mean()+np.abs(e2).mean())),'cosine':float(e1@e2/np.sqrt(n1*n2)),'shared_fraction':float(shared/total),'observable_fraction':float(div/total)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',default='all');a=ap.parse_args()
 m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.factor.eq(4))&m.architecture.isin(['hat','swinir'])]
 if a.dataset!='all':m=m[m.dataset.eq(a.dataset)]
 rows=[]
 for (ds,target,split),g in m.groupby(['dataset','architecture','split']):
  if ds=='fastmri':ck=ROOT/'baseline'/('fastmri_brain_'+('hat_2p5d' if target=='hat' else 'swinir_2p5d'))/'runs'/'full'/'checkpoints'/f'{target}_epoch_best.pth'
  elif ds=='ningxia':ck=ROOT/'baseline'/f'ningxia_t2_{target}_2p5d_cv'/'runs'/split.replace('OOF_','')/'full'/'checkpoints'/f'{target}_epoch_best.pth'
  else:
   ck=ROOT/'baseline'/f'ixi_{target}_2p5d'/'runs'/'full_test115'/'checkpoints'/f'{target}_epoch_best.pth'
   if not ck.exists():ck=ROOT/'baseline'/f'ixi_{target}_2p5d'/'runs'/'full'/'checkpoints'/f'{target}_epoch_best.pth'
  net=model(ds,target,ck)
  for r in g.itertuples():
   gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);p0=nib.load(r.source_file).get_fdata(dtype=np.float32);s=gt[:,:,::4]
   pf=net.interpolate_volume(np.ascontiguousarray(s[::-1,:,:]),stride=4)[::-1,:,:]
   for z in range(min(gt.shape[2],p0.shape[2],pf.shape[2])):
    if z%4 not in (1,3):continue
    pred0=p0[:,:,z];thr=.01*max(float(np.max(np.abs(pred0))),1e-6);mask=np.abs(pred0)>thr
    rows.append({'dataset':ds,'case_id':r.case_id,'patient_cluster':r.patient_cluster,'model':target,'z':z,'overlap':2,**vals(pred0,pf[:,:,z],gt[:,:,z],mask)})
   print('C5-E003',ds,target,r.case_id,flush=True)
 x=pd.DataFrame(rows);dest=OUT/(f'clean_max_overlap_{a.dataset}_per_plane.csv' if a.dataset!='all' else 'clean_max_overlap_per_plane.csv');x.to_csv(dest,index=False)
 if a.dataset=='ixi':
  zsrc=pd.read_csv(OUT/'overlap_covariance_ixi_per_plane.csv');zsrc=zsrc[zsrc.overlap.eq(0)]
  zero=zsrc.rename(columns={'disagreement_mae':'zero_score','mae':'endpoint'})
 else:
  zero=pd.concat([pd.read_csv(PAPER/'plan4_outputs'/'disjoint_anchor_per_plane.csv'),pd.read_csv(PAPER/'plan4_outputs'/'ningxia_disjoint_per_plane.csv').assign(dataset='ningxia')],ignore_index=True).rename(columns={'case':'case_id','target_model':'model','disjoint_inconsistency':'zero_score','phase0_error':'endpoint'})
 q=zero[['dataset','case_id','model','z','zero_score','endpoint']].merge(x,on=['dataset','case_id','model','z']);rng=np.random.default_rng(20260813);out=[]
 for ds,g in q.groupby('dataset'):
  rz=rho(g.zero_score,g.endpoint);rm=rho(g.score,g.endpoint);clusters=np.array(sorted(g.patient_cluster.unique()));by={c:g[g.patient_cluster.eq(c)] for c in clusters};boot=[]
  for _ in range(5000):
   b=pd.concat([by[c] for c in rng.choice(clusters,len(clusters),replace=True)],ignore_index=True);boot.append(rho(b.zero_score,b.endpoint)-rho(b.score,b.endpoint))
  out.append({'dataset':ds,'cases':g.case_id.nunique(),'patient_clusters':len(clusters),'planes':len(g),'zero_rho':rz,'clean_max_rho':rm,'delta':rz-rm,'cluster_95ci':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
   'max_error_cosine_mean':float(g.cosine.mean()),'max_shared_fraction_mean':float(g.shared_fraction.mean()),'max_observable_fraction_mean':float(g.observable_fraction.mean()),'max_raw_score_median':float(g.score.median()),'zero_raw_score_median':float(g.zero_score.median())})
 result={'experiment':'C5-E003','status':'EXPLORATORY MECHANISTIC','control':'same anchors/z-order/distances; horizontal flip equivariance','rows':out};(OUT/(f'clean_max_overlap_{a.dataset}_summary.json' if a.dataset!='all' else 'clean_max_overlap_summary.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
