"""Joint case-clustered PC versus flip-TTA comparison across 18 profiles."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;OUT=HERE/'plan3_outputs';P2=HERE/'plan2_outputs'
from rasinet.icassp_statistics import ranking_metrics

def load():
 fs=[]
 for ds in ('fastmri','ningxia'):
  for s in (2,4,6):
   for m in ('i3net','hat','swinir'):
    if ds=='ningxia':p=OUT/f'ningxia_{m}_x{s}_tta.csv'
    elif s!=4:p=OUT/f'{m}_x{s}_tta_per_case.csv'
    elif m=='swinir':
     q=pd.read_csv(P2/'fastmri_x4_swinir_comparator_per_case.csv').rename(columns={'physical_consistency':'pc'});q['target_model']=m;q['scale']=s;q['dataset']=ds;fs.append(q[['dataset','case','target_model','scale','common_error','tta','pc']]);continue
    else:p=OUT/f'{m}_tta_per_case.csv'
    q=pd.read_csv(p);q['dataset']=ds;q['target_model']=m;q['scale']=s;fs.append(q[['dataset','case','target_model','scale','common_error','tta','pc']])
 return pd.concat(fs,ignore_index=True)
def metrics(g,col):return ranking_metrics(g.common_error,g[col])['normalized_aurc']
def main():
 x=load()
 for c in ('tta','pc'):x[c+'_rank']=x.groupby(['dataset','scale','target_model'])[c].rank()
 per=[]
 for keys,g in x.groupby(['dataset','scale','target_model']):per.append({'dataset':keys[0],'scale':keys[1],'target_model':keys[2],'tta_nAURC':metrics(g,'tta_rank'),'pc_nAURC':metrics(g,'pc_rank'),'delta':metrics(g,'pc_rank')-metrics(g,'tta_rank')})
 per=pd.DataFrame(per);per.to_csv(OUT/'tta_all_profiles.csv',index=False)
 # Pre-compute each case-swap assignment's profile delta; same case mask applied to all profiles in a cohort.
 rng=np.random.default_rng(20260908); tests=[]
 for label,g in list(x.groupby('dataset'))+[('pooled',x)]:
  datasets=sorted(g.dataset.unique()); obs=float(per[per.dataset.isin(datasets)].delta.mean()); null=[]
  for _ in range(2000):
   z=g.copy()
   for ds,q in z.groupby('dataset'):
    cs=np.array(sorted(q.case.unique())); swap=set(cs[rng.random(len(cs))<.5]); mask=(z.dataset.eq(ds)&z.case.isin(swap));a=z.loc[mask,'tta_rank'].copy();z.loc[mask,'tta_rank']=z.loc[mask,'pc_rank'].values;z.loc[mask,'pc_rank']=a.values
   deltas=[metrics(q,'pc_rank')-metrics(q,'tta_rank') for _,q in z.groupby(['dataset','scale','target_model'])];null.append(np.mean(deltas))
  tests.append({'scope':label,'profiles':int(per.dataset.isin(datasets).sum()),'mean_delta_pc_minus_tta_nAURC':obs,'profiles_pc_better':int((per[per.dataset.isin(datasets)].delta<0).sum()),'case_clustered_swap_p':float((1+np.sum(np.abs(null)>=abs(obs)))/2001),'permutations':2000})
 result={'tests':tests,'per_profile':per.to_dict('records')};x.to_csv(OUT/'tta_all_per_case.csv',index=False);(OUT/'tta_all_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
