"""EXPLORATORY mechanism-derived anchor-change witness for PC blind spots."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent; OUT=HERE/'plan3_outputs'

def rho(a,b): return float(stats.spearmanr(a,b).statistic)
def enrichment(y,s,q=.9): return float(np.mean(y[s>=np.quantile(s,q)])/np.mean(y))
def main():
 x=pd.read_csv(OUT/'anchor_curvature_per_plane.csv')
 keys=['dataset','target_model','pair']
 for col in ('raw_inc','anchor_change','raw_error'):
  x[col+'_pct']=x.groupby(keys)[col].rank(pct=True)
 # Logical OR via max rank follows directly from complementary failure mechanisms.
 x['union_rank']=x[['raw_inc_pct','anchor_change_pct']].max(axis=1)
 x['mean_rank']=x[['raw_inc_pct','anchor_change_pct']].mean(axis=1)
 rows=[]; rng=np.random.default_rng(20260903)
 for ds,g in x.groupby('dataset'):
  cases=np.array(sorted(g.case.unique())); by={c:g[g.case.eq(c)] for c in cases}
  for score in ('raw_inc','anchor_change','union_rank','mean_rank'):
   obs={'rho':rho(g[score],g.raw_error),'top10_enrichment':enrichment(g.raw_error,g[score])}
   boot=[]
   for _ in range(2000):
    b=pd.concat([by[c] for c in rng.choice(cases,len(cases),replace=True)],ignore_index=True)
    boot.append([rho(b[score],b.raw_error),enrichment(b.raw_error,b[score])])
   boot=np.asarray(boot)
   rows.append({'dataset':ds,'score':score,**obs,'rho_ci':[float(np.quantile(boot[:,0],.025)),float(np.quantile(boot[:,0],.975))],
    'enrichment_ci':[float(np.quantile(boot[:,1],.025)),float(np.quantile(boot[:,1],.975))]})
 blind=x[(x.raw_error_pct>=.75)&(x.raw_inc_pct<=.25)]
 coverage=[]
 for ds,g in blind.groupby('dataset'):
  coverage.append({'dataset':ds,'blind_spots':len(g),'anchor_top_quartile_recall':float((g.anchor_change_pct>=.75).mean()),
   'anchor_median_percentile':float(g.anchor_change_pct.median()),'union_top_quartile_recall':float((g.union_rank>=.75).mean())})
 x.to_csv(OUT/'anchor_witness_per_plane.csv',index=False); pd.DataFrame(rows).to_csv(OUT/'anchor_witness_metrics.csv',index=False)
 result={'metrics':rows,'blind_spot_coverage':coverage}; (OUT/'anchor_witness_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
