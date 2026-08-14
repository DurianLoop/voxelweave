"""Case-clustered uncertainty for balanced-panel orthogonal variance fractions."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from plan3_boundary_variance import orthogonal_variance
HERE=Path(__file__).resolve().parent;OUT=HERE/'plan3_outputs'
def main():
 x=pd.read_csv(OUT/'error_balanced_panel.csv');rng=np.random.default_rng(20260909);rows=[]
 for ds,g in x.groupby('dataset'):
  point=orthogonal_variance(g);cases=np.array(sorted(g.case.unique()));by={c:g[g.case.eq(c)] for c in cases};vals={k:[] for k in point}
  for _ in range(5000):
   parts=[]
   for i,c in enumerate(rng.choice(cases,len(cases),replace=True)):
    q=by[c].copy();q['case']=f'draw{i}';parts.append(q)
   z=orthogonal_variance(pd.concat(parts,ignore_index=True))
   for k,v in z.items():vals[k].append(v)
  for k,v in point.items():rows.append({'dataset':ds,'component':k,'fraction':v,'case_cluster_95ci_low':float(np.quantile(vals[k],.025)),'case_cluster_95ci_high':float(np.quantile(vals[k],.975))})
 pd.DataFrame(rows).to_csv(OUT/'variance_fraction_clustered_ci.csv',index=False);(OUT/'variance_fraction_clustered_ci.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
