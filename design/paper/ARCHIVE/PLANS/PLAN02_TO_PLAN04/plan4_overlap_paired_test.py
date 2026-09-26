"""Paired same-target comparison: disjoint phase grids vs ordinary x4-x6 contexts."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;P3=HERE/'plan3_outputs';P4=HERE/'plan4_outputs'
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def anchor_count(z,a=4,b=6):
 la=(z//a)*a;ra=la+a;lb=(z//b)*b;rb=lb+b;return int(la==lb)+int(ra==rb)
def main():
 frames=[]
 for ds,dp in [('fastmri',P4/'disjoint_anchor_per_plane.csv'),('ningxia',P4/'ningxia_disjoint_per_plane.csv')]:
  d=pd.read_csv(dp).rename(columns={'disjoint_inconsistency':'disjoint_score'})
  o=pd.read_csv(P3/'spectral_spatial_per_plane.csv');o=o[(o.dataset.eq(ds))&o.pair.eq('4-6')&o.target_model.isin(['hat','swinir'])].rename(columns={'za':'z','raw_inc':'overlap_score','raw_error':'overlap_endpoint'})
  q=d.merge(o[['case','target_model','z','overlap_score','overlap_endpoint']],on=['case','target_model','z'])
  q['dataset']=ds;q['shared_anchor_count']=[anchor_count(int(z)) for z in q.z];frames.append(q)
 x=pd.concat(frames,ignore_index=True);x.to_csv(P4/'overlap_paired_planes.csv',index=False)
 rows=[];rng=np.random.default_rng(20260920)
 for (ds,shared),g in x.groupby(['dataset','shared_anchor_count']):
  # Use phase-0 error, common to both scores. Within model ranks remove score units.
  g=g.copy();g['d_rank']=g.groupby('target_model').disjoint_score.rank(pct=True);g['o_rank']=g.groupby('target_model').overlap_score.rank(pct=True)
  rd=rho(g.d_rank,g.phase0_error);ro=rho(g.o_rank,g.phase0_error);cases=np.array(sorted(g.case.unique()));by={c:g[g.case.eq(c)] for c in cases};diff=[]
  for _ in range(5000):
   b=pd.concat([by[c] for c in rng.choice(cases,len(cases),replace=True)],ignore_index=True);diff.append(rho(b.d_rank,b.phase0_error)-rho(b.o_rank,b.phase0_error))
  # Define blind spots using the same endpoint and within model/overlap stratum ranks.
  g['e_pct']=g.groupby('target_model').phase0_error.rank(pct=True);g['o_pct']=g.groupby('target_model').overlap_score.rank(pct=True);g['d_pct']=g.groupby('target_model').disjoint_score.rank(pct=True)
  blind=(g.e_pct>=.75)&(g.o_pct<=.25)
  rows.append({'dataset':ds,'shared_anchor_count':int(shared),'planes':len(g),'cases':len(cases),'disjoint_rho':rd,'overlap_rho':ro,'delta_rho':rd-ro,
   'case_cluster_95ci':[float(np.nanquantile(diff,.025)),float(np.nanquantile(diff,.975))],'overlap_blind_spots':int(blind.sum()),
   'disjoint_recovers_top_quartile':int((g.loc[blind,'d_pct']>=.75).sum()),'recovery_rate':float((g.loc[blind,'d_pct']>=.75).mean()) if blind.any() else None})
 result={'rows':rows};pd.DataFrame(rows).to_csv(P4/'overlap_paired_summary.csv',index=False);(P4/'overlap_paired_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
