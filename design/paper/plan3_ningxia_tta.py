"""NingXia OOF four-view flip-TTA for one target/factor (Plan-3)."""
from __future__ import annotations
import argparse,json,sys
from dataclasses import replace
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=HERE/'plan3_outputs'
sys.path.insert(0,str(ROOT/'baseline'));sys.path.insert(0,str(ROOT/'design'))
from rasinet.optimization_protocol import profile_sources,case_names,sparse_path,prediction_path,gt_path
from rasinet.icassp_statistics import ranking_metrics
VIEWS=((),(0,),(1,),(0,1))
def source(scale,target):
 q=profile_sources('ningxia',scale)[target]
 if scale in (2,6):q=replace(q,root=ROOT/'baseline'/f'{q.root.name}_root_results_202607')
 return q
def loader(target,ckpt):
 if target=='hat':
  from ixi_hat_2p5d.train import HAT2p5DInterpolator;return HAT2p5DInterpolator(ckpt)
 if target=='swinir':
  from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator;return SwinIR2p5DInterpolator(ckpt)
 from ixi_i3net.train import I3NetInterpolator;return I3NetInterpolator(ckpt,label='NingXia')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--target',required=True);ap.add_argument('--scale',type=int,required=True);a=ap.parse_args();src=source(a.scale,a.target);ref=source(a.scale,'i3net')
 pc=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/all_finalist_outer_predictions.csv');pc=pc[(pc.method.eq('physical_consistency'))&pc.scale.eq(a.scale)&pc.target_model.eq(a.target)].set_index('case');rows=[]
 for fi in range(8):
  fold=f'fold_{fi:02d}'; ck=src.run_dir(fold)/'checkpoints'/f'{a.target}_epoch_best.pth';model=loader(a.target,ck)
  for case in case_names(src,fold):
   sparse=nib.load(str(sparse_path(ref,fold,case))).get_fdata(dtype=np.float32);preds=[]
   for axes in VIEWS:
    v=np.ascontiguousarray(np.flip(sparse,axis=axes)) if axes else sparse;p=model.interpolate_volume(v,stride=a.scale);preds.append(np.ascontiguousarray(np.flip(p,axis=axes)) if axes else p)
   std=np.std(np.stack(preds),axis=0);orig=nib.load(str(prediction_path(src,fold,case))).get_fdata(dtype=np.float32);zs=[z for z in range(orig.shape[2]) if z%a.scale];mask=np.abs(orig[:,:,zs])>.01*max(float(np.max(np.abs(orig[:,:,zs]))),1e-6)
   rows.append({'fold':fold,'case':case,'target_model':a.target,'scale':a.scale,'common_error':float(pc.loc[case,'common_error']),'tta':float(std[:,:,zs][mask].mean()),'pc':float(pc.loc[case,'triage_score'])});print(a.target,a.scale,fold,case,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/f'ningxia_{a.target}_x{a.scale}_tta.csv',index=False);result={m:ranking_metrics(x.common_error,x[m]) for m in ('tta','pc')};(OUT/f'ningxia_{a.target}_x{a.scale}_tta.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
