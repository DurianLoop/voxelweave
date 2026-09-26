"""MECHANISTIC controlled target-preserving intervention with disjoint x4 anchor lattices.

Phase-0 anchors are z=0,4,8,...; phase-2 anchors are z=2,6,10,... .
Targets z mod 4 in {1,3} are unobserved in both contexts and the lattices share
zero anchors. Dense GT is used only to synthesize the alternative acquisition
and evaluate it; it never enters the disagreement score.
"""
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
def model_for(target,src):
 ck=src.run_dir()/'checkpoints'/f'{target}_epoch_best.pth'
 if target=='i3net':
  from ixi_i3net.train import I3NetInterpolator;return I3NetInterpolator(ck,label='fastMRI-phase2')
 if target=='hat':
  from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator;return FastMRIHAT2p5DInterpolator(ck)
 from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator;return FastMRISwinIR2p5DInterpolator(ck)
def corr(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>2 and np.std(a)>0 and np.std(b)>0 else float('nan')
def main():
 OUT.mkdir(exist_ok=True);ref=profile_sources('fastmri',4)['i3net'];cases=case_names(ref,None);rows=[]
 for target in TARGETS:
  src=profile_sources('fastmri',4)[target];model=model_for(target,src)
  for ci,case in enumerate(cases,1):
   gt=nib.load(str(gt_path(ref,None,case))).get_fdata(dtype=np.float32);p0=nib.load(str(prediction_path(src,None,case))).get_fdata(dtype=np.float32)
   sparse2=gt[:,:,PHASE::SCALE];p2local=model.interpolate_volume(sparse2,stride=SCALE)
   max_original=min(gt.shape[2]-1,PHASE+p2local.shape[2]-1);zs=[z for z in range(PHASE,max_original+1) if z%4 in (1,3)]
   plane=[]
   for z in zs:
    q0=p0[:,:,z];q2=p2local[:,:,z-PHASE];y=gt[:,:,z];thr=.01*max(float(np.max(np.abs(q0))),1e-6);mask=np.abs(q0)>thr
    inc=np.abs(q0-q2);e0=np.abs(q0-y);e2=np.abs(q2-y);err=.5*(e0+e2)
    plane.append({'dataset':'fastmri','case':case,'target_model':target,'z':z,'phase_position':z%4,'disjoint_inconsistency':float(inc[mask].mean()),
     'phase0_error':float(e0[mask].mean()),'phase2_error':float(e2[mask].mean()),'mean_error':float(err[mask].mean()),'pixel_rho':corr(inc[mask],err[mask])})
   rows.extend(plane);print('disjoint',target,ci,len(cases),case,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/'disjoint_anchor_per_plane.csv',index=False)
 case=x.groupby(['case','target_model'],as_index=False).agg(score=('disjoint_inconsistency','median'),error=('mean_error','median'),phase0_error=('phase0_error','median'),phase2_error=('phase2_error','median'),pixel_rho=('pixel_rho','median'))
 case.to_csv(OUT/'disjoint_anchor_per_case.csv',index=False);profiles=[]
 for m,g in case.groupby('target_model'):profiles.append({'target_model':m,**ranking_metrics(g.error,g.score),'median_pixel_rho':float(g.pixel_rho.median())})
 # Plane stable-wrong and shared-anchor comparator on the same held-out cohort scale.
 x['error_pct']=x.groupby('target_model').mean_error.rank(pct=True);x['score_pct']=x.groupby('target_model').disjoint_inconsistency.rank(pct=True);x['stable_wrong']=(x.error_pct>=.75)&(x.score_pct<=.25)
 result={'label':'MECHANISTIC / SYNTHETIC ALTERNATIVE ACQUISITION','target_preserved':True,'anchor_overlap':0,'cases':case.case.nunique(),'planes':len(x),
  'profiles':profiles,'case_level_mean_rho':float(np.mean([p['case_spearman'] for p in profiles])),'stable_wrong_planes':int(x.stable_wrong.sum()),
  'median_pixel_rho':float(x.pixel_rho.median()),'phase2_minus_phase0_error':float((x.phase2_error-x.phase0_error).mean()),
  'infeasible_architecture':{'i3net':'phase-shifted fastMRI x4 inputs have only three anchors for most cases; frozen I3Net requires four and correctly rejects uncovered output. No artificial padding was introduced.'}}
 (OUT/'disjoint_anchor_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
