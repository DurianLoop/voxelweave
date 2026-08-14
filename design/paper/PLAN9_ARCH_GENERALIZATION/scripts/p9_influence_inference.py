"""Clustered and fixed-count inference for Plan-9 new-architecture influence."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();P9=HERE.parents[1];OUT=P9/'outputs';RNG=np.random.default_rng(20260814)
ENDPOINTS=['error_cosine','shared_fraction','observable_fraction','disagreement_mae']

def rho(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float);ok=np.isfinite(a)&np.isfinite(b)
 return float(stats.spearmanr(a[ok],b[ok]).statistic) if ok.sum()>=8 and np.std(a[ok])>0 and np.std(b[ok])>0 else np.nan

def within_partial(g,y):
 x=stats.rankdata(g.influence_primary.to_numpy(float));o=stats.rankdata(g[y].to_numpy(float));
 c=np.column_stack([stats.rankdata(g.span),stats.rankdata(g.asymmetry)]).astype(float);ids=pd.factorize(g.case)[0]
 for k in np.unique(ids):
  q=ids==k;x[q]-=x[q].mean();o[q]-=o[q].mean();c[q]-=c[q].mean(axis=0)
 z=np.column_stack([np.ones(len(x)),c]);ex=x-z@np.linalg.lstsq(z,x,rcond=None)[0];ey=o-z@np.linalg.lstsq(z,o,rcond=None)[0]
 return float(np.corrcoef(ex,ey)[0,1]) if np.std(ex)>0 and np.std(ey)>0 else np.nan

def boot(g,y,fn,n=1000):
 cases=g.case.unique();by={c:g[g.case==c] for c in cases};vals=[]
 for _ in range(n):
  chunks=[]
  for j,c in enumerate(RNG.choice(cases,len(cases),replace=True)):
   q=by[c].copy();q['case']=q.case.astype(str)+f'_b{j}';chunks.append(q)
  vals.append(fn(pd.concat(chunks,ignore_index=True),y))
 a=np.asarray(vals,float);return float(np.nanquantile(a,.025)),float(np.nanquantile(a,.975))

def main():
 stability=pd.concat([pd.read_csv(OUT/f'p9_influence_{m}_stability.csv') for m in ['saint','i3net','cycleinr']])
 eligible={m:bool(g['pass'].all()) for m,g in stability.groupby('model')};rows=[]
 for model in ['saint','i3net','cycleinr']:
  x=pd.read_csv(OUT/f'p9_influence_{model}_per_case_config.csv');x=x[x.context!=x.reference_context]
  for design,g in [('broad',x),('fixed_nonzero',x[x.overlap_count>0])]:
   for ep in ENDPOINTS:
    fn=(lambda q,y:within_partial(q,y)) if design=='fixed_nonzero' else (lambda q,y:rho(q.influence_primary,q[y]))
    est=fn(g,ep);lo,hi=boot(g,ep,fn)
    rows.append({'model':model,'claim_eligible':eligible[model],'design':design,'endpoint':ep,'estimate':est,'ci_low':lo,'ci_high':hi,
                 'cases':g.case.nunique(),'configurations':len(g),'controls':'case FE + span + asymmetry' if design=='fixed_nonzero' else 'clustered marginal'})
 out=pd.DataFrame(rows);out.to_csv(OUT/'p9_influence_clustered_inference.csv',index=False)
 verdict={'claim_eligible_models':[m for m,v in eligible.items() if v],
          'saint_fixed_nonzero_expected_directions':bool(((out[(out.model=='saint')&(out.design=='fixed_nonzero')].set_index('endpoint').estimate*np.array([1,1,-1,-1]))>0).all()),
          'note':'I3Net and CycleINR estimates are retained as exploratory but excluded from influence claims after stability failure.'}
 (OUT/'p9_influence_clustered_verdict.json').write_text(json.dumps(verdict,indent=2),encoding='utf-8')
 print(out.to_string(index=False));print(json.dumps(verdict,indent=2))
if __name__=='__main__':main()
