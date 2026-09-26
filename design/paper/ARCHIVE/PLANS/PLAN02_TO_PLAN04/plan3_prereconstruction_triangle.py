"""Plan-3: acquired-context signals and three-context disagreement geometry.

PRE-RECONSTRUCTION features use sparse inputs only. Triangle analysis is
retrospective/mechanistic and does not modify PC-v1.
"""
from __future__ import annotations
import json, sys
from dataclasses import replace
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'plan3_outputs'; P2=HERE/'plan2_outputs'
sys.path.insert(0,str(ROOT/'design'))
from rasinet.optimization_protocol import profile_sources, case_names, sparse_path
from rasinet.icassp_statistics import ranking_metrics

TARGETS=('i3net','hat','swinir'); SCALES=(2,4,6)

def source(ds,s):
    q=profile_sources(ds,s)['i3net']
    if ds=='ningxia' and s in (2,6): q=replace(q,root=ROOT/'baseline'/f'{q.root.name}_root_results_202607')
    return q

def sparse_features(v, affine):
    v=np.asarray(v,dtype=np.float32); fg=np.abs(v)>max(1e-6,.01*float(np.max(np.abs(v))))
    vals=v[fg]; dif=np.diff(v,axis=2)
    # All fixed a priori and obtainable before reconstruction.
    adj_mae=float(np.mean(np.abs(dif))); adj_rmse=float(np.sqrt(np.mean(dif*dif)))
    gx=np.diff(v,axis=0); gy=np.diff(v,axis=1)
    grad=float(.5*(np.mean(np.abs(gx))+np.mean(np.abs(gy))))
    down=v[::4,::4,:]; spec=np.abs(np.fft.rfft2(down,axes=(0,1)))**2
    h,w=down.shape[:2]; fy=np.fft.fftfreq(h)[:,None]; fx=np.fft.rfftfreq(w)[None,:]; rad=np.sqrt(fy*fy+fx*fx)
    high=float(spec[rad>.2].sum()/max(spec.sum(),1e-12))
    return {'input_adj_mae':adj_mae,'input_adj_rmse':adj_rmse,'input_gradient':grad,'input_highfreq_fraction':high,
            'input_dynamic_range':float(np.percentile(vals,99)-np.percentile(vals,1)),
            'sparse_depth':v.shape[2],'context_spacing_mm':float(np.linalg.norm(affine[:3,2]))}

def load_labels():
    fast=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/common_errors_per_case_development.csv')
    fast=fast[fast.dataset.eq('fastmri')&fast.target_model.isin(TARGETS)][['dataset','case','scale','target_model','common_error']]
    ning=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/all_finalist_outer_predictions.csv')
    ning=ning[ning.method.eq('physical_consistency')][['case','scale','target_model','common_error']].drop_duplicates(); ning.insert(0,'dataset','ningxia')
    return pd.concat([fast,ning],ignore_index=True)

def prereconstruction(labels):
    rows=[]
    for ds in ('fastmri','ningxia'):
      for s in SCALES:
       src=source(ds,s)
       folds=(None,) if ds=='fastmri' else tuple(f'fold_{i:02d}' for i in range(8))
       for fold in folds:
        for case in case_names(src,fold):
         img=nib.load(str(sparse_path(src,fold,case))); rows.append({'dataset':ds,'case':case,'scale':s,**sparse_features(img.get_fdata(dtype=np.float32),img.affine)})
    feat=pd.DataFrame(rows).drop_duplicates(['dataset','case','scale']); panel=labels.merge(feat,on=['dataset','case','scale'])
    panel.to_csv(OUT/'prereconstruction_features.csv',index=False)
    features=['input_adj_mae','input_adj_rmse','input_gradient','input_highfreq_fraction','input_dynamic_range','sparse_depth','context_spacing_mm']
    metrics=[]
    for (ds,s,m),g in panel.groupby(['dataset','scale','target_model']):
      for f in features:
       if g[f].nunique()<3: continue
       z=ranking_metrics(g.common_error,g[f]); metrics.append({'dataset':ds,'scale':s,'target_model':m,'feature':f,**z})
    met=pd.DataFrame(metrics); met.to_csv(OUT/'prereconstruction_profile_metrics.csv',index=False)
    agg=met.groupby(['dataset','feature'],as_index=False)[['normalized_aurc','case_spearman','case_kendall']].mean()
    agg.to_csv(OUT/'prereconstruction_aggregate.csv',index=False)
    return {'rows':len(panel),'aggregate':agg.to_dict('records')}

def triangle(labels):
    fast=pd.read_csv(P2/'context_controls/per_case.csv'); fast=fast[(fast.variant.eq('raw'))&fast.scale.astype(str).str.startswith('pair_')]
    fast=fast[['case','target_model','scale','score']].rename(columns={'scale':'pair','score':'d'}); fast['pair']=fast.pair.str.replace('pair_','').str.replace('_','-'); fast['dataset']='fastmri'
    ning=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/cross_scale_physical_pair_scores.csv')
    ning=ning[(ning.dataset.eq('ningxia'))&ning.target_model.isin(TARGETS)][['case','target_model','scale_a','scale_b','consistency']]
    ning['pair']=ning.scale_a.astype(str)+'-'+ning.scale_b.astype(str); ning=ning.rename(columns={'consistency':'d'})[['case','target_model','pair','d']]; ning['dataset']='ningxia'
    edges=pd.concat([fast,ning],ignore_index=True).drop_duplicates(['dataset','case','target_model','pair'])
    wide=edges.pivot(index=['dataset','case','target_model'],columns='pair',values='d').reset_index()
    wide['mean_edge']=wide[['2-4','2-6','4-6']].mean(axis=1); wide['diameter']=wide[['2-4','2-6','4-6']].max(axis=1)
    wide['anisotropy']=(wide[['2-4','2-6','4-6']].max(axis=1)-wide[['2-4','2-6','4-6']].min(axis=1))/wide.mean_edge.clip(lower=1e-12)
    for s in SCALES:
      involved=[p for p in ('2-4','2-6','4-6') if str(s) in p]; wide[f'node_{s}']=wide[involved].sum(axis=1)
    lab=labels.pivot_table(index=['dataset','case','target_model'],columns='scale',values='common_error').reset_index(); lab.columns=[str(x) for x in lab.columns]
    x=wide.merge(lab,on=['dataset','case','target_model']); x['predicted_outlier']=x[[f'node_{s}' for s in SCALES]].idxmax(axis=1).str[-1:].astype(int); x['true_worst']=x[[str(s) for s in SCALES]].idxmax(axis=1).astype(int); x['correct']=x.predicted_outlier.eq(x.true_worst)
    x.to_csv(OUT/'multicontext_triangle_per_case.csv',index=False)
    results=[]
    for ds,g in x.groupby('dataset'):
      target_error=g[[str(s) for s in SCALES]].mean(axis=1)
      results.append({'dataset':ds,'n':len(g),'outlier_attribution_accuracy':float(g.correct.mean()),
        'mean_edge_error_rho':float(stats.spearmanr(g.mean_edge,target_error).statistic),
        'diameter_error_rho':float(stats.spearmanr(g.diameter,target_error).statistic),
        'anisotropy_error_rho':float(stats.spearmanr(g.anisotropy,target_error).statistic)})
    pd.DataFrame(results).to_csv(OUT/'multicontext_triangle_summary.csv',index=False)
    return results

def main():
    OUT.mkdir(exist_ok=True); labels=load_labels(); result={'prereconstruction':prereconstruction(labels),'triangle':triangle(labels)}
    (OUT/'prereconstruction_triangle_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
