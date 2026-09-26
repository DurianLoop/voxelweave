"""P6-E05: test each association in the registered mechanism chain."""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs'

def rho(x,y):
    x=np.asarray(x,float);y=np.asarray(y,float);ok=np.isfinite(x)&np.isfinite(y)
    return float(stats.spearmanr(x[ok],y[ok]).statistic) if ok.sum()>5 and np.std(x[ok])>0 and np.std(y[ok])>0 else np.nan

def partial_rho(x,y,c,case):
    x=np.asarray(x,float);y=np.asarray(y,float);c=np.asarray(c,float);case=np.asarray(case)
    ok=np.isfinite(x)&np.isfinite(y)&np.all(np.isfinite(c),axis=1)
    if ok.sum()<10:return np.nan
    x=stats.rankdata(x[ok]);y=stats.rankdata(y[ok]);c=c[ok];case=case[ok]
    c=np.column_stack([stats.rankdata(c[:,j]) for j in range(c.shape[1])])
    # Absorb examination fixed effects by within-examination demeaning.
    codes=pd.factorize(case)[0]
    for k in np.unique(codes):
        take=codes==k;x[take]-=x[take].mean();y[take]-=y[take].mean();c[take]-=c[take].mean(axis=0)
    z=np.column_stack([np.ones(len(x)),c])
    ex=x-z@np.linalg.lstsq(z,x,rcond=None)[0];ey=y-z@np.linalg.lstsq(z,y,rcond=None)[0]
    return float(np.corrcoef(ex,ey)[0,1])

def controls(g,cols):return g[cols].to_numpy(float)

def arrows(g):
    # Self-comparison has exactly zero disagreement and carries no ranking information.
    g=g[g.context!='(-2, 2)'].copy()
    g['normalized_disagreement']=g.disagreement_mae/(g.paired_error_mae+1e-8)
    geom=['overlap_count','span','asymmetry']
    arrow1=partial_rho(g.neural_influence_cosine,g.error_cosine,controls(g,geom),g.case)
    arrow2=partial_rho(g.error_cosine,g.normalized_disagreement,controls(g,geom+['neural_influence_cosine']),g.case)
    arrow4a=partial_rho(g.neural_influence_cosine,g.observable_fraction,controls(g,geom),g.case)
    context=[]
    for ctx,q in g.groupby('context'):
        context.append({'context':ctx,'median_influence':q.neural_influence_cosine.median(),
                        'median_alignment':q.error_cosine.median(),
                        'ranking_rho':rho(q.disagreement_mae,q.paired_error_mae)})
    c=pd.DataFrame(context)
    arrow3=rho(c.median_alignment,c.ranking_rho)
    arrow4b=rho(c.median_influence,c.ranking_rho)
    return {'arrow1_influence_to_alignment_partial_rho':arrow1,
            'arrow2_alignment_to_normalized_disagreement_partial_rho':arrow2,
            'arrow3_alignment_to_context_ranking_rho':arrow3,
            'arrow4a_influence_to_observable_fraction_partial_rho':arrow4a,
            'arrow4b_influence_to_context_ranking_rho':arrow4b},c

x=pd.read_csv(OUT/'plan6_neural_shared_influence_confirm3_per_case_config.csv')
rng=np.random.default_rng(20260813);rows=[];context_frames=[]
for (ds,model),g in x.groupby(['dataset','model']):
    point,c=arrows(g);c.insert(0,'model',model);c.insert(0,'dataset',ds);context_frames.append(c)
    clusters=g.patient_cluster.unique();by={k:g[g.patient_cluster==k] for k in clusters};boot={k:[] for k in point}
    for _ in range(2000):
        # Relabel duplicate sampled clusters so case fixed effects remain well-posed.
        chunks=[]
        for j,k in enumerate(rng.choice(clusters,len(clusters),replace=True)):
            q=by[k].copy();q['case']=q.case.astype(str)+f'_b{j}';chunks.append(q)
        b,_=arrows(pd.concat(chunks,ignore_index=True))
        for k,v in b.items():boot[k].append(v)
    for k,v in point.items():
        a=np.asarray(boot[k],float)
        rows.append({'dataset':ds,'model':model,'arrow':k,'estimate':v,
                     'cluster_ci_low':float(np.nanquantile(a,.025)),
                     'cluster_ci_high':float(np.nanquantile(a,.975)),
                     'expected_sign':-1 if ('arrow2_' in k or 'arrow3_' in k or 'arrow4' in k) else 1})

result=pd.DataFrame(rows);contexts=pd.concat(context_frames,ignore_index=True)
result.to_csv(OUT/'plan6_mechanism_chain_summary.csv',index=False)
contexts.to_csv(OUT/'plan6_mechanism_chain_context_ranking.csv',index=False)
primary=result[result.arrow.isin(['arrow1_influence_to_alignment_partial_rho','arrow2_alignment_to_normalized_disagreement_partial_rho','arrow4a_influence_to_observable_fraction_partial_rho'])]
sign_ok=np.sign(primary.estimate)==primary.expected_sign
ci_ok=np.where(primary.expected_sign>0,primary.cluster_ci_low>0,primary.cluster_ci_high<0)
payload={'experiment':'P6-E05','status':'COMPLETE','inference_unit':'examination/patient-cluster bootstrap',
         'causal_wording':'prohibited; these are registered association arrows',
         'primary_all_expected_direction':bool(sign_ok.all()),'primary_all_ci_exclude_zero':bool(ci_ok.all()),
         'arrow3_and_arrow4b_note':'Context-level ranking uses eight non-self comparator contexts per dataset/model and is descriptive because the context count is small.',
         'summary_csv':'plan6_mechanism_chain_summary.csv','context_csv':'plan6_mechanism_chain_context_ranking.csv'}
(OUT/'plan6_mechanism_chain.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(result.to_string(index=False));print(json.dumps(payload,indent=2))
