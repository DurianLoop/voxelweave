"""CONFIRMATORY-compatible fastMRI x4 HAT four-view flip TTA comparator."""
from __future__ import annotations
import json,sys,time
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'plan3_outputs'
sys.path.insert(0,str(ROOT/'baseline')); sys.path.insert(0,str(ROOT/'design'))
from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator
from rasinet.optimization_protocol import profile_sources,case_names,sparse_path,prediction_path,gt_path
from rasinet.icassp_statistics import ranking_metrics
VIEWS=((),(0,),(1,),(0,1))
def main():
 target='i3net' if '--i3net' in sys.argv else ('swinir' if '--swinir' in sys.argv else 'hat')
 scale=next((int(a.split('=',1)[1]) for a in sys.argv if a.startswith('--scale=')),4)
 src=profile_sources('fastmri',scale)[target]; ref=profile_sources('fastmri',scale)['i3net']; cases=case_names(src,None)
 if target=='hat': model=FastMRIHAT2p5DInterpolator(src.run_dir()/'checkpoints/hat_epoch_best.pth')
 elif target=='swinir':
  from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator
  model=FastMRISwinIR2p5DInterpolator(src.run_dir()/'checkpoints/swinir_epoch_best.pth')
 else:
  from ixi_i3net.train import I3NetInterpolator
  model=I3NetInterpolator(src.run_dir()/'checkpoints/i3net_epoch_best.pth',label='fastMRI')
 rows=[]
 pc=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/cross_scale_consistency_per_case.csv'); pc=pc[(pc.dataset.eq('fastmri'))&pc.scale.eq(scale)&pc.target_model.eq(target)].set_index('case')
 for i,case in enumerate(cases,1):
  sparse=nib.load(str(sparse_path(ref,None,case))).get_fdata(dtype=np.float32); preds=[]
  for axes in VIEWS:
   v=np.ascontiguousarray(np.flip(sparse,axis=axes)) if axes else sparse; p=model.interpolate_volume(v,stride=scale); preds.append(np.ascontiguousarray(np.flip(p,axis=axes)) if axes else p)
  std=np.std(np.stack(preds),axis=0); original=nib.load(str(prediction_path(src,None,case))).get_fdata(dtype=np.float32); gt=nib.load(str(gt_path(ref,None,case))).get_fdata(dtype=np.float32); zs=[z for z in range(original.shape[2]) if z%scale]
  mask=np.abs(original[:,:,zs])>.01*max(float(np.max(np.abs(original[:,:,zs]))),1e-6)
  rows.append({'case':case,'target_model':target,'common_error':float(pc.loc[case,'common_error']),'tta':float(std[:,:,zs][mask].mean()),'pc':float(pc.loc[case,'consistency'])}); print(target,'TTA',i,len(cases),case,flush=True)
 x=pd.DataFrame(rows); x['scale']=scale; x.to_csv(OUT/f'{target}_x{scale}_tta_per_case.csv',index=False); result={m:ranking_metrics(x.common_error,x[m]) for m in ('tta','pc')}
 # Paired rank-swap randomization.
 a=x.tta.rank().to_numpy();b=x.pc.rank().to_numpy(); y=x.common_error.to_numpy(); obs=ranking_metrics(y,b)['normalized_aurc']-ranking_metrics(y,a)['normalized_aurc']; rng=np.random.default_rng(20260906); null=[]
 for _ in range(10000):
  take=rng.random(len(x))<.5; aa=a.copy();bb=b.copy();aa[take],bb[take]=bb[take],aa[take];null.append(ranking_metrics(y,bb)['normalized_aurc']-ranking_metrics(y,aa)['normalized_aurc'])
 result['paired']={'delta_pc_minus_tta_nAURC':float(obs),'two_sided_p':float((1+np.sum(np.abs(null)>=abs(obs)))/10001)}
 (OUT/f'{target}_x{scale}_tta_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
