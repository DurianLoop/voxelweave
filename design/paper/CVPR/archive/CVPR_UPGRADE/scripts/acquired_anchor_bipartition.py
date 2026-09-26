"""C5-E007 pilot: disjoint contexts from already acquired x4 anchors only."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1];OUT=UP/'outputs';sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def model(ds,target,ck):
 if ds=='fastmri':
  if target=='hat':
   from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator;return FastMRIHAT2p5DInterpolator(ck)
  from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator;return FastMRISwinIR2p5DInterpolator(ck)
 if target=='hat':
  from ixi_hat_2p5d.train import HAT2p5DInterpolator;return HAT2p5DInterpolator(ck)
 from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator;return SwinIR2p5DInterpolator(ck)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['pilot','full'],default='pilot');args=ap.parse_args();m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.dataset.eq('fastmri'))&(m.factor.eq(4))&m.architecture.eq('hat')]
 cases=sorted(m.case_id.unique());m=m[m.case_id.isin(cases[:8] if args.stage=='pilot' else cases[8:])]
 rows=[]
 for (ds,target),g in m.groupby(['dataset','architecture']):
  ck=ROOT/'baseline'/'fastmri_brain_hat_2p5d'/'runs'/'full'/'checkpoints'/'hat_epoch_best.pth';net=model(ds,target,ck)
  for r in g.itertuples():
   gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);p0=nib.load(r.source_file).get_fdata(dtype=np.float32);s4=gt[:,:,::4]
   pe=net.interpolate_volume(np.ascontiguousarray(s4[:,:,::2]),stride=8);po=net.interpolate_volume(np.ascontiguousarray(s4[:,:,1::2]),stride=8)
   usable=min(gt.shape[2],p0.shape[2],pe.shape[2],po.shape[2]+4)
   for z in range(4,usable):
    if z%8 not in (2,6):continue
    a=pe[:,:,z];b=po[:,:,z-4];y=gt[:,:,z];base=p0[:,:,z];thr=.01*max(float(np.max(np.abs(base))),1e-6);mask=np.abs(base)>thr
    ea=(a-y)[mask].astype(float);eb=(b-y)[mask].astype(float)
    rows.append({'dataset':ds,'case':r.case_id,'model':target,'z':z,'score':float(np.abs(a-b)[mask].mean()),'x4_error':float(np.abs(base-y)[mask].mean()),
     'subcontext_mean_error':float(.5*(np.abs(ea).mean()+np.abs(eb).mean())),'error_cosine':float(ea@eb/np.sqrt((ea@ea)*(eb@eb))),
     'distance_pair_a':'2,6','distance_pair_b':'2,6','overlap':0})
   print('C5-E007',args.stage,r.case_id,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/f'acquired_anchor_bipartition_{args.stage}_per_plane.csv',index=False)
 c=x.groupby(['case','model'],as_index=False).agg(score=('score','median'),x4_error=('x4_error','median'),error_cosine=('error_cosine','mean'))
 benefit=pd.read_csv(PAPER/'plan4_outputs'/'adaptive_acquisition_per_case.csv');benefit=benefit[benefit.target_model.eq('hat')][['case','benefit_x4_to_x2']];c=c.merge(benefit,on='case');c.to_csv(OUT/f'acquired_anchor_bipartition_{args.stage}_per_case.csv',index=False)
 payload={'experiment':'C5-E007','stage':args.stage,'status':'EXPLORATORY','cases':c.case.nunique(),'planes':len(x),'plane_rho_score_vs_x4_error':rho(x.score,x.x4_error),
  'case_rho_score_vs_benefit':rho(c.score,c.benefit_x4_to_x2),'mean_error_cosine':float(x.error_cosine.mean())}
 if args.stage=='pilot':payload['pilot_gate_passed']=bool(payload['case_rho_score_vs_benefit']>.5 and payload['plane_rho_score_vs_x4_error']>0)
 (OUT/f'acquired_anchor_bipartition_{args.stage}_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
