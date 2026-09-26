"""Held-out tests of acquired-anchor curvature and sampling-spacing laws."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent; OUT=HERE/'plan4_outputs'

def rho(a,b):
    return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')

def design(x, kind):
    cols=[np.ones(len(x))]
    # Architecture offsets; i3net is reference.
    cols += [(x.target_model.eq(m)).astype(float).to_numpy() for m in ('hat','swinir')]
    if kind in ('spacing','change','curvature','full'):
        cols.append(np.log(np.maximum(x.spacing_mm.to_numpy(),1e-8)))
    if kind in ('change','full'):
        cols.append(np.log(np.maximum(x.anchor_change.to_numpy(),1e-8)))
    if kind in ('curvature','full'):
        cols.append(np.log(np.maximum(x.curvature_spacing_term.to_numpy(),1e-8)))
    return np.column_stack(cols)

def fit_predict(train,test,kind):
    y=np.log(np.maximum(train.normalized_error.to_numpy(),1e-8)); beta=np.linalg.lstsq(design(train,kind),y,rcond=None)[0]
    return np.exp(design(test,kind)@beta),beta

def scores(y,p):
    y=np.asarray(y);p=np.asarray(p);return {'rho':rho(y,p),'mae':float(np.mean(np.abs(y-p))),
        'r2':float(1-np.sum((y-p)**2)/np.sum((y-y.mean())**2))}

def main():
    x=pd.read_csv(OUT/'curvature_spacing_per_plane.csv')
    fm=x[x.dataset.eq('fastmri')].copy(); cases=sorted(fm.case.unique()); dev=set(cases[::2]); train=fm[fm.case.isin(dev)];confirm=fm[~fm.case.isin(dev)]
    nx=x[x.dataset.eq('ningxia')].copy()
    rows=[];betas={}
    for kind in ('architecture','spacing','change','curvature','full'):
        for label,test in [('fastmri_confirmation',confirm),('ningxia_oof',nx)]:
            # Cross-cohort transfer is tested at the common x4 factor to prevent a support mismatch.
            tr=train if label.startswith('fastmri') else train[train.factor.eq(4)]
            pred,beta=fit_predict(tr,test,kind);betas[f'{kind}_{label}']=beta.tolist()
            rows.append({'model':kind,'test':label,'n':len(test),**scores(test.normalized_error,pred)})
    # Architecture-free, no-fit rank predictions and oracle ceiling.
    for label,g in [('fastmri_all',fm),('fastmri_confirmation',confirm),('ningxia_oof',nx)]:
        for feature in ('spacing_mm','anchor_change','input_curvature','curvature_spacing_term','oracle_linear_residual'):
            rows.append({'model':'no_fit_'+feature,'test':label,'n':len(g),'rho':rho(g.normalized_error,g[feature]),'mae':None,'r2':None})
    # Does high input curvature predict a steeper factor penalty within the same case/model?
    piv=fm.groupby(['case','target_model','factor'],as_index=False).agg(error=('normalized_error','median'),curvature=('input_curvature','median'))
    lo=piv[piv.factor.eq(2)].rename(columns={'error':'e2','curvature':'c2'});hi=piv[piv.factor.eq(6)].rename(columns={'error':'e6','curvature':'c6'})
    q=lo[['case','target_model','e2','c2']].merge(hi[['case','target_model','e6','c6']],on=['case','target_model']);q['penalty']=q.e6-q.e2;q['curvature']=.5*(q.c2+q.c6)
    interaction={'units':len(q),'rho_curvature_vs_x6_minus_x2_penalty':rho(q.curvature,q.penalty)}
    # Case-cluster bootstrap for theory term versus the strongest simple input baseline.
    bootstrap={};rng=np.random.default_rng(20260813)
    for label,g in [('fastmri_confirmation',confirm),('ningxia_oof',nx)]:
        cases0=np.array(sorted(g.case.unique())); by={c:g[g.case.eq(c)] for c in cases0};delta=[]
        for _ in range(5000):
            b=pd.concat([by[c] for c in rng.choice(cases0,len(cases0),replace=True)],ignore_index=True)
            delta.append(rho(b.normalized_error,b.curvature_spacing_term)-rho(b.normalized_error,b.anchor_change))
        bootstrap[label]={'delta_rho_theory_minus_anchor_change':float(rho(g.normalized_error,g.curvature_spacing_term)-rho(g.normalized_error,g.anchor_change)),
                          'case_cluster_95ci':[float(np.nanquantile(delta,.025)),float(np.nanquantile(delta,.975))]}
    pd.DataFrame(rows).to_csv(OUT/'curvature_spacing_model_comparison.csv',index=False)
    result={'split':{'development_cases':sorted(dev),'confirmation_cases':sorted(set(cases)-dev)},'models':rows,'coefficients':betas,'factor_interaction':interaction,'bootstrap':bootstrap,
            'interpretation_rule':'The theory-motivated model is supported only if curvature improves held-out prediction beyond spacing and anchor-change baselines.'}
    (OUT/'curvature_spacing_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(pd.DataFrame(rows).to_string(index=False));print(interaction)

if __name__=='__main__':main()
