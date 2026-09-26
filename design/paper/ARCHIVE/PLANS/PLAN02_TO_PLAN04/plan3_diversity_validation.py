"""Plan-3 confirmatory checks for input signals, triangle attribution, and intervention diversity."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent; OUT=HERE/'plan3_outputs'; P2=HERE/'plan2_outputs'; ROOT=HERE.parents[1]
FEATURES=('input_adj_rmse','input_dynamic_range')

def rank_metrics(y,s):
    return float(stats.spearmanr(y,s).statistic)

def clustered_ci(g, endpoint, feature, n=1000):
    cases=np.array(sorted(g.case.unique())); by={c:g[g.case.eq(c)] for c in cases}; rng=np.random.default_rng(20260831)
    vals=[]
    for _ in range(n):
        parts=[]
        for i,c in enumerate(rng.choice(cases,len(cases),replace=True)):
            q=by[c].copy(); q['case']=f'draw{i}'; parts.append(q)
        b=pd.concat(parts,ignore_index=True)
        # Equal-weight fixed scale/model profiles.
        vals.append(np.mean([rank_metrics(q[endpoint],q[feature]) for _,q in b.groupby(['scale','target_model'])]))
    obs=np.mean([rank_metrics(q[endpoint],q[feature]) for _,q in g.groupby(['scale','target_model'])])
    return {'rho':float(obs),'ci':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]}

def input_validation():
    x=pd.read_csv(OUT/'prereconstruction_features.csv')
    # Ground-truth range is not available pre-reconstruction but defines a scale-controlled retrospective endpoint.
    context=pd.read_csv(P2/'context_controls/per_case.csv')
    norm=context[(context.variant.eq('raw'))&~context.scale.astype(str).str.startswith('pair_')][['case','scale','target_model','range_normalized_error']].copy()
    norm['scale']=norm.scale.astype(int)
    x=x.merge(norm,on=['case','scale','target_model'],how='left')
    results=[]
    for ds,g in x.groupby('dataset'):
      split=sorted(g.case.unique()); halves={'derivation':split[:len(split)//2],'confirmation':split[len(split)//2:]}
      for part,cases in halves.items():
       q=g[g.case.isin(cases)]
       for feature in FEATURES:
        for endpoint in ('common_error','range_normalized_error'):
         if q[endpoint].notna().sum()==0: continue
         z=clustered_ci(q.dropna(subset=[endpoint]),endpoint,feature)
         results.append({'dataset':ds,'split':part,'cases':len(cases),'feature':feature,'endpoint':endpoint,**z})
    pd.DataFrame(results).to_csv(OUT/'prereconstruction_split_validation.csv',index=False)
    return results

def triangle_validation():
    x=pd.read_csv(OUT/'multicontext_triangle_per_case.csv'); rows=[]; rng=np.random.default_rng(20260901)
    for ds,g in x.groupby('dataset'):
      counts=g.true_worst.value_counts(); majority=int(counts.idxmax()); majority_acc=float((g.true_worst==majority).mean())
      obs=float(g.correct.mean()); cases=np.array(sorted(g.case.unique())); per={c:g[g.case.eq(c)] for c in cases}; diffs=[]
      # Equal rows per case (three architectures): bootstrap sufficient case means.
      case_values=np.array([[float(q.correct.mean()),float((q.true_worst==majority).mean())] for _,q in g.groupby('case')])
      draws=rng.integers(0,len(cases),size=(10000,len(cases)))
      sampled=case_values[draws]
      diffs=(sampled[:,:,0].mean(axis=1)-sampled[:,:,1].mean(axis=1)).tolist()
      rows.append({'dataset':ds,'n':len(g),'majority_factor':majority,'majority_accuracy':majority_acc,
                   'triangle_accuracy':obs,'improvement':obs-majority_acc,
                   'cluster_bootstrap_95ci':[float(np.quantile(diffs,.025)),float(np.quantile(diffs,.975))],
                   'true_worst_counts':{str(k):int(v) for k,v in counts.items()}})
    return rows

def pair_data():
    fast=pd.read_csv(P2/'context_controls/per_case.csv'); fast=fast[(fast.variant.eq('raw'))&fast.scale.astype(str).str.startswith('pair_')]
    fast=fast[['case','target_model','scale','score']].rename(columns={'scale':'pair','score':'d'}); fast.pair=fast.pair.str.replace('pair_','').str.replace('_','-'); fast['dataset']='fastmri'
    ning=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/cross_scale_physical_pair_scores.csv')
    ning=ning[(ning.dataset.eq('ningxia'))&ning.target_model.isin(['i3net','hat','swinir'])][['case','target_model','scale_a','scale_b','consistency']]
    ning['pair']=ning.scale_a.astype(str)+'-'+ning.scale_b.astype(str); ning=ning.rename(columns={'consistency':'d'})[['case','target_model','pair','d']]; ning['dataset']='ningxia'
    labels=pd.read_csv(OUT/'error_balanced_panel.csv')
    wide=labels.pivot_table(index=['dataset','case','target_model'],columns='scale',values='common_error').reset_index()
    e=pd.concat([fast,ning],ignore_index=True).merge(wide,on=['dataset','case','target_model'])
    return e

def diversity_analysis():
    x=pair_data(); rows=[]
    for (ds,pair,m),g in x.groupby(['dataset','pair','target_model']):
      a,b=map(int,pair.split('-')); avg=.5*(g[a]+g[b]); diversity=1-rank_metrics(g[a],g[b]); quality=rank_metrics(g.d,avg)
      rows.append({'dataset':ds,'pair':pair,'target_model':m,'n':len(g),'error_rank_diversity':diversity,
                   'error_rank_correlation':1-diversity,'witness_quality_rho':quality,
                   'mean_relative_error_gap':float(np.mean(np.abs(g[a]-g[b])/np.maximum(avg,1e-12)))})
    r=pd.DataFrame(rows); r.to_csv(OUT/'intervention_diversity_profiles.csv',index=False)
    by=[]
    for ds,g in r.groupby('dataset'):
      by.append({'dataset':ds,'profiles':len(g),'rho_diversity_vs_quality':rank_metrics(g.error_rank_diversity,g.witness_quality_rho),
                 'rho_error_gap_vs_quality':rank_metrics(g.mean_relative_error_gap,g.witness_quality_rho)})
    return {'profiles':rows,'association':by}

def main():
    result={'input_signal_validation':input_validation(),'triangle_attribution':triangle_validation(),'intervention_diversity':diversity_analysis()}
    (OUT/'diversity_validation_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
