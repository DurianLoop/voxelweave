"""MECHANISTIC NingXia OOF replication of disjoint x4 phase lattices."""
from __future__ import annotations
import json,sys
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=HERE/'plan4_outputs'
sys.path.insert(0,str(ROOT/'baseline'));sys.path.insert(0,str(ROOT/'design'));sys.path.insert(0,str(ROOT/'pre'))
from rasinet.optimization_protocol import profile_sources,case_names,prediction_path,gt_path
from rasinet.icassp_statistics import ranking_metrics
TARGETS=('hat','swinir');SCALE=4;PHASE=2
def model_for(target,ck):
 if target=='hat':
  from ixi_hat_2p5d.train import HAT2p5DInterpolator;return HAT2p5DInterpolator(ck)
 from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator;return SwinIR2p5DInterpolator(ck)
def corr(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>2 and np.std(a)>0 and np.std(b)>0 else float('nan')
def main():
 OUT.mkdir(exist_ok=True);ref=profile_sources('ningxia',4)['i3net'];rows=[]
 for target in TARGETS:
  src=profile_sources('ningxia',4)[target]
  for fi in range(8):
   fold=f'fold_{fi:02d}';model=model_for(target,src.run_dir(fold)/'checkpoints'/f'{target}_epoch_best.pth')
   for case in case_names(src,fold):
    gt=nib.load(str(gt_path(ref,fold,case))).get_fdata(dtype=np.float32);p0=nib.load(str(prediction_path(src,fold,case))).get_fdata(dtype=np.float32);p2=model.interpolate_volume(gt[:,:,PHASE::SCALE],stride=SCALE)
    maxz=min(gt.shape[2]-1,PHASE+p2.shape[2]-1);zs=[z for z in range(PHASE,maxz+1) if z%4 in (1,3)]
    for z in zs:
     a=p0[:,:,z];b=p2[:,:,z-PHASE];y=gt[:,:,z];thr=.01*max(float(np.max(np.abs(a))),1e-6);mask=np.abs(a)>thr;inc=np.abs(a-b);err=.5*(np.abs(a-y)+np.abs(b-y))
     rows.append({'fold':fold,'case':case,'target_model':target,'z':z,'phase_position':z%4,'disjoint_inconsistency':float(inc[mask].mean()),'mean_error':float(err[mask].mean()),'phase0_error':float(np.abs(a-y)[mask].mean()),'phase2_error':float(np.abs(b-y)[mask].mean()),'pixel_rho':corr(inc[mask],err[mask])})
    print('disjoint NX',target,fold,case,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/'ningxia_disjoint_per_plane.csv',index=False);case=x.groupby(['case','target_model'],as_index=False).agg(score=('disjoint_inconsistency','median'),error=('mean_error','median'),pixel_rho=('pixel_rho','median'));case.to_csv(OUT/'ningxia_disjoint_per_case.csv',index=False)
 profiles=[{'target_model':m,**ranking_metrics(g.error,g.score),'median_pixel_rho':float(g.pixel_rho.median())} for m,g in case.groupby('target_model')]
 x['error_pct']=x.groupby('target_model').mean_error.rank(pct=True);x['score_pct']=x.groupby('target_model').disjoint_inconsistency.rank(pct=True);x['stable_wrong']=(x.error_pct>=.75)&(x.score_pct<=.25)
 result={'label':'MECHANISTIC / SYNTHETIC ALTERNATIVE ACQUISITION OOF','cases':case.case.nunique(),'planes':len(x),'anchor_overlap':0,'profiles':profiles,'stable_wrong_planes':int(x.stable_wrong.sum()),'median_pixel_rho':float(x.pixel_rho.median())}
 (OUT/'ningxia_disjoint_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
