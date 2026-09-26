"""C5-E007 frozen extension after pilot pass: SwinIR fastMRI, both models NingXia/IXI."""
from __future__ import annotations
import json,sys
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1];OUT=UP/'outputs';sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def model(ds,target,ck):
 if ds=='fastmri':
  from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator;return FastMRISwinIR2p5DInterpolator(ck)
 if target=='hat':
  from ixi_hat_2p5d.train import HAT2p5DInterpolator;return HAT2p5DInterpolator(ck)
 from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator;return SwinIR2p5DInterpolator(ck)
def main():
 m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.factor.eq(4))&(((m.dataset.eq('fastmri'))&m.architecture.eq('swinir'))|((m.dataset.isin(['ningxia','ixi']))&m.architecture.isin(['hat','swinir'])))]
 rows=[]
 for (ds,target,split),g in m.groupby(['dataset','architecture','split']):
  if ds=='fastmri':ck=ROOT/'baseline'/'fastmri_brain_swinir_2p5d'/'runs'/'full'/'checkpoints'/'swinir_epoch_best.pth'
  elif ds=='ningxia':ck=ROOT/'baseline'/f'ningxia_t2_{target}_2p5d_cv'/'runs'/split.replace('OOF_','')/'full'/'checkpoints'/f'{target}_epoch_best.pth'
  else:
   ck=ROOT/'baseline'/f'ixi_{target}_2p5d'/'runs'/'full_test115'/'checkpoints'/f'{target}_epoch_best.pth'
   if not ck.exists():ck=ROOT/'baseline'/f'ixi_{target}_2p5d'/'runs'/'full'/'checkpoints'/f'{target}_epoch_best.pth'
  net=model(ds,target,ck)
  for r in g.itertuples():
   gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);p0=nib.load(r.source_file).get_fdata(dtype=np.float32);s4=gt[:,:,::4]
   pe=net.interpolate_volume(np.ascontiguousarray(s4[:,:,::2]),stride=8);po=net.interpolate_volume(np.ascontiguousarray(s4[:,:,1::2]),stride=8);usable=min(gt.shape[2],p0.shape[2],pe.shape[2],po.shape[2]+4)
   for z in range(4,usable):
    if z%8 not in (2,6):continue
    a=pe[:,:,z];b=po[:,:,z-4];y=gt[:,:,z];base=p0[:,:,z];thr=.01*max(float(np.max(np.abs(base))),1e-6);mask=np.abs(base)>thr;ea=(a-y)[mask].astype(float);eb=(b-y)[mask].astype(float)
    rows.append({'dataset':ds,'case':r.case_id,'patient_cluster':r.patient_cluster,'model':target,'z':z,'score':float(np.abs(a-b)[mask].mean()),'x4_error':float(np.abs(base-y)[mask].mean()),'error_cosine':float(ea@eb/np.sqrt((ea@ea)*(eb@eb)))})
   print('C5-E007 extension',ds,target,r.case_id,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/'acquired_anchor_bipartition_extension_per_plane.csv',index=False);c=x.groupby(['dataset','case','patient_cluster','model'],as_index=False).agg(score=('score','median'),x4_error=('x4_error','median'),error_cosine=('error_cosine','mean'))
 benefit=pd.read_csv(PAPER/'plan4_outputs'/'adaptive_acquisition_per_case.csv').rename(columns={'target_model':'model'})[['dataset','case','model','benefit_x4_to_x2']];c=c.merge(benefit,on=['dataset','case','model'],how='left');c.to_csv(OUT/'acquired_anchor_bipartition_extension_per_case.csv',index=False)
 out=[]
 for ds,g in c.groupby('dataset'):
  rec={'dataset':ds,'cases':g.case.nunique(),'patient_clusters':g.patient_cluster.nunique(),'models':g.model.nunique(),'planes':len(x[x.dataset.eq(ds)]),'rho_score_vs_x4_error':rho(g.score,g.x4_error),'mean_error_cosine':float(g.error_cosine.mean())}
  if g.benefit_x4_to_x2.notna().all():rec['rho_score_vs_benefit']=rho(g.score,g.benefit_x4_to_x2)
  else:rec['rho_score_vs_benefit']='NOT RUN: no stored IXI x2 benefit'
  out.append(rec)
 payload={'experiment':'C5-E007','stage':'frozen_extension','status':'EXPLORATORY','rows':out};(OUT/'acquired_anchor_bipartition_extension_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
