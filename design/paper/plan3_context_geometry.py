"""MECHANISTIC continuous context-geometry analysis of matched output planes."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent; OUT=HERE/'plan3_outputs'

def rho(a,b): return float(stats.spearmanr(a,b).statistic) if len(a)>2 and np.std(a)>0 and np.std(b)>0 else float('nan')

def decorate(x):
 vals=[]
 for r in x.itertuples():
  a,b=map(int,r.pair.split('-')); z=int(r.za)
  la=(z//a)*a; ra=la+a; lb=(z//b)*b; rb=lb+b
  vals.append({'phase_a':(z-la)/a,'phase_b':(z-lb)/b,'phase_gap':abs((z-la)/a-(z-lb)/b),
   'shared_left':la==lb,'shared_right':ra==rb,'shared_anchor_count':int(la==lb)+int(ra==rb),
   'nearest_anchor_distance_a':min(z-la,ra-z),'nearest_anchor_distance_b':min(z-lb,rb-z),
   'min_nearest_anchor_distance':min(z-la,ra-z,z-lb,rb-z)})
 return pd.concat([x.reset_index(drop=True),pd.DataFrame(vals)],axis=1)

def main():
 x=pd.read_csv(OUT/'spectral_spatial_per_plane.csv'); x=decorate(x)
 x['error_pct']=x.groupby(['dataset','target_model','pair']).raw_error.rank(pct=True); x['inc_pct']=x.groupby(['dataset','target_model','pair']).raw_inc.rank(pct=True); x['stable_wrong']=(x.error_pct>=.75)&(x.inc_pct<=.25)
 x.to_csv(OUT/'context_geometry_per_plane.csv',index=False)
 rows=[]
 for (ds,pair),g in x.groupby(['dataset','pair']):
  for feature in ('phase_gap','shared_anchor_count','min_nearest_anchor_distance','relative_position'):
   rows.append({'dataset':ds,'pair':pair,'feature':feature,'rho_error':rho(g[feature],g.raw_error),'rho_inconsistency':rho(g[feature],g.raw_inc)})
  for anchor,q in g.groupby('shared_anchor_count'):
   rows.append({'dataset':ds,'pair':pair,'feature':f'shared_anchor={anchor}','n':len(q),'mean_error':float(q.raw_error.mean()),'mean_inconsistency':float(q.raw_inc.mean()),'stable_wrong_rate':float(q.stable_wrong.mean())})
 pd.DataFrame(rows).to_csv(OUT/'context_geometry_summary.csv',index=False)
 result={'rows':len(x),'stable_wrong_by_dataset':x.groupby('dataset').stable_wrong.sum().astype(int).to_dict(),
  'x4_x6_first':x[(x.pair.eq('4-6'))&x.ordinal.eq(1)].groupby('dataset').agg(n=('raw_error','size'),mean_error=('raw_error','mean'),mean_inc=('raw_inc','mean'),stable_wrong_rate=('stable_wrong','mean'),phase_gap=('phase_gap','first'),shared_left=('shared_left','first')).reset_index().to_dict('records')}
 (OUT/'context_geometry_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()
