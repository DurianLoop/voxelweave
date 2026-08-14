"""Deployable test: split an acquired x2 grid into two disjoint x4 contexts.

No additional slices are needed.  The disagreement of frozen x4 models is
evaluated against the error of the standard frozen x2 reconstruction on the
same missing odd target planes and compared with ordinary x2-x4 PC.
"""
from __future__ import annotations
import json,sys
from dataclasses import replace
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];P3=HERE/'plan3_outputs';P4=HERE/'plan4_outputs'
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]
from rasinet.optimization_protocol import profile_sources,prediction_path,gt_path
from rasinet.icassp_statistics import ranking_metrics
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def main():
 d=pd.concat([pd.read_csv(P4/'disjoint_anchor_per_plane.csv'),pd.read_csv(P4/'ningxia_disjoint_per_plane.csv').assign(dataset='ningxia')],ignore_index=True)
 rows=[]
 for (ds,case,model),g in d.groupby(['dataset','case','target_model']):
  fold=None if ds=='fastmri' else g.fold.iloc[0];src=profile_sources(ds,2)[model];ref=profile_sources(ds,2)['i3net']
  if ds=='ningxia':
   src=replace(src,root=ROOT/'baseline'/f'{src.root.name}_root_results_202607');ref=replace(ref,root=ROOT/'baseline'/f'{ref.root.name}_root_results_202607')
  pred=nib.load(str(prediction_path(src,fold,case))).get_fdata(dtype=np.float32);gt=nib.load(str(gt_path(ref,fold,case))).get_fdata(dtype=np.float32)
  for r in g.itertuples():
   z=int(r.z)
   if z>=pred.shape[2]:continue
   a=pred[:,:,z];thr=.01*max(float(np.max(np.abs(a))),1e-6);mask=np.abs(a)>thr
   rows.append({'dataset':ds,'case':case,'target_model':model,'z':z,'disjoint_score':r.disjoint_inconsistency,'x2_error':float(np.abs(a-gt[:,:,z])[mask].mean())})
 x=pd.DataFrame(rows)
 o=pd.read_csv(P3/'spectral_spatial_per_plane.csv');o=o[(o.pair.eq('2-4'))&o.target_model.isin(['hat','swinir'])].rename(columns={'za':'z','raw_inc':'ordinary_pc','raw_error':'ordinary_error'})
 x=x.merge(o[['dataset','case','target_model','z','ordinary_pc']],on=['dataset','case','target_model','z'],how='left')
 x.to_csv(P4/'interleaved_x2_per_plane.csv',index=False);result=[];rng=np.random.default_rng(20260813)
 for (ds,model),g in x.groupby(['dataset','target_model']):
  g=g.dropna(subset=['disjoint_score','ordinary_pc','x2_error']).copy()
  rz=rho(g.disjoint_score,g.x2_error);ro=rho(g.ordinary_pc,g.x2_error);cases=np.array(sorted(g.case.unique()));by={c:g[g.case.eq(c)] for c in cases};diff=[]
  for _ in range(5000):
   b=pd.concat([by[c] for c in rng.choice(cases,len(cases),replace=True)],ignore_index=True);diff.append(rho(b.disjoint_score,b.x2_error)-rho(b.ordinary_pc,b.x2_error))
  c=g.groupby('case',as_index=False).agg(disjoint=('disjoint_score','median'),ordinary=('ordinary_pc','median'),error=('x2_error','median'))
  result.append({'dataset':ds,'target_model':model,'cases':len(c),'planes':len(g),'disjoint_plane_rho':rz,'ordinary_pc_plane_rho':ro,'delta_rho':rz-ro,
                 'case_cluster_95ci':[float(np.nanquantile(diff,.025)),float(np.nanquantile(diff,.975))],
                 'disjoint_case_rho':rho(c.disjoint,c.error),'ordinary_pc_case_rho':rho(c.ordinary,c.error),
                 **{'disjoint_'+k:v for k,v in ranking_metrics(c.error,c.disjoint).items()},**{'ordinary_'+k:v for k,v in ranking_metrics(c.error,c.ordinary).items()}})
 out={'method':'Interleaved-Grid Consistency (IGC): split existing x2 anchors into phase-0/phase-2 x4 subsets','requires_additional_acquisition':False,'rows':result}
 (P4/'interleaved_x2_summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
