"""P6-E04B: within-one-shared-anchor neural influence ladder."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();OUT=HERE.parents[1]/'outputs'
def partial(x,y,c,case):
 x=stats.rankdata(np.asarray(x,float));y=stats.rankdata(np.asarray(y,float));c=np.column_stack([stats.rankdata(np.asarray(c)[:,j]) for j in range(np.asarray(c).shape[1])]);case=np.asarray(case)
 for k in np.unique(case):
  q=case==k;x[q]-=x[q].mean();y[q]-=y[q].mean();c[q]-=c[q].mean(axis=0)
 z=np.column_stack([np.ones(len(x)),c]);ex=x-z@np.linalg.lstsq(z,x,rcond=None)[0];ey=y-z@np.linalg.lstsq(z,y,rcond=None)[0]
 return float(np.corrcoef(ex,ey)[0,1])
x=pd.read_csv(OUT/'plan6_neural_shared_influence_confirm3_per_case_config.csv');x=x[x.overlap_count==1].copy();endpoints=['error_cosine','shared_fraction','observable_fraction','disagreement_mae'];rows=[];rng=np.random.default_rng(20260813)
for (ds,model),g in x.groupby(['dataset','model']):
 clusters=g.patient_cluster.unique();by={k:g[g.patient_cluster==k] for k in clusters}
 for ep in endpoints:
  point=partial(g.neural_influence_cosine,g[ep],g[['span','asymmetry']],g.case);boots=[]
  for _ in range(2000):
   chunks=[]
   for j,k in enumerate(rng.choice(clusters,len(clusters),replace=True)):
    q=by[k].copy();q['case']=q.case.astype(str)+f'_b{j}';chunks.append(q)
   b=pd.concat(chunks,ignore_index=True);boots.append(partial(b.neural_influence_cosine,b[ep],b[['span','asymmetry']],b.case))
  rows.append({'dataset':ds,'model':model,'endpoint':ep,'cases':g.case.nunique(),'planes':g[['case','z']].drop_duplicates().shape[0],'contexts':g.context.nunique(),'partial_rho_neural_influence':point,'cluster_ci_low':float(np.nanquantile(boots,.025)),'cluster_ci_high':float(np.nanquantile(boots,.975))})
r=pd.DataFrame(rows);r.to_csv(OUT/'plan6_fixed_overlap_ladder.csv',index=False)
primary=r[r.endpoint.isin(endpoints[:3])];payload={'experiment':'P6-E04B','status':'COMPLETE','constraint':'overlap_count=1 exactly; four comparator contexts; target/model/input count fixed; span/asymmetry and case controlled','coverage':['fastmri','ixi','ningxia'],'primary_expected_direction_all':bool(((primary.partial_rho_neural_influence*np.where(primary.endpoint=='observable_fraction',-1,1))>0).all()),'summary_csv':'plan6_fixed_overlap_ladder.csv','geometry_note':'With two physical anchors and a fixed target, changing overlap while holding the complete anchor-distance set fixed is combinatorially impossible; this fixed-count continuous-influence test is the identifiable alternative.'}
(OUT/'plan6_fixed_overlap_ladder.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(r.to_string(index=False));print(json.dumps(payload,indent=2))
