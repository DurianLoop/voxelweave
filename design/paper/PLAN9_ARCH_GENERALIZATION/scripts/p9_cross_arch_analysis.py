"""Plan-9 benchmark, cross-architecture failures, diversity, factor and influence synthesis."""
from __future__ import annotations
import itertools
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve(); P9=HERE.parents[1]; PAPER=P9.parent; ROOT=PAPER.parents[1]; OUT=P9/'outputs'
MODELS=['hat','swinir','i3net','saint','cycleinr']
FAMILY={'hat':'transformer','swinir':'transformer','i3net':'medical_inter_intra','saint':'spatial_attention','cycleinr':'implicit_coordinate'}

def rho(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float);ok=np.isfinite(a)&np.isfinite(b)
 return float(stats.spearmanr(a[ok],b[ok]).statistic) if ok.sum()>=5 and np.std(a[ok])>0 and np.std(b[ok])>0 else np.nan

def pair_type(a,b):
 fa,fb=FAMILY[a],FAMILY[b]
 if fa==fb:return fa+'--'+fb
 return '--'.join(sorted([fa,fb]))

def benchmark():
 src=pd.read_csv(ROOT/'design/rasinet/corrected_reconstruction_fidelity.csv')
 src=src.rename(columns={'scale':'factor','model':'method','n':'n_cases'})
 src['rmse']=np.sqrt(src.mse)
 cols=['dataset','factor','method','n_cases','mae','rmse','psnr','ssim','ncc']
 src[cols].sort_values(['dataset','factor','method']).to_csv(OUT/'p9_reconstruction_benchmark.csv',index=False)
 focus=src[src.method.isin(['linear','cubic']+MODELS)].copy()
 focus[cols].sort_values(['dataset','factor','method']).to_csv(OUT/'p9_reconstruction_benchmark_compact.csv',index=False)
 return src

def factor_arch(src):
 rows=[]
 for (ds,m),g in src.groupby(['dataset','method']):
  g=g.sort_values('factor'); d=dict(zip(g.factor,g.mae))
  if 2 in d and 6 in d:
   rows.append({'dataset':ds,'model':m,'family':FAMILY.get(m,'other'),'mae_x2':d[2],'mae_x4':d.get(4,np.nan),'mae_x6':d[6],
                'x6_minus_x2':d[6]-d[2],'x6_over_x2':d[6]/d[2]})
 pd.DataFrame(rows).to_csv(OUT/'p9_factor_architecture_interaction.csv',index=False)

def error_correlations():
 x=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/common_fidelity_per_case_development.csv')
 x=x[x.model.isin(MODELS)]
 rows=[]
 consensus=[]
 for (ds,scale),g in x.groupby(['dataset','scale']):
  p=g.pivot(index='case',columns='model',values='mae')
  have=[m for m in MODELS if m in p]
  for a,b in itertools.combinations(have,2):
   q=p[[a,b]].dropna(); topa=set(q.index[q[a]>=q[a].quantile(.75)]);topb=set(q.index[q[b]>=q[b].quantile(.75)])
   rows.append({'dataset':ds,'factor':scale,'model_a':a,'model_b':b,'family_pair':pair_type(a,b),'cases':len(q),
                'error_rank_rho':rho(q[a],q[b]),'top_quartile_jaccard':len(topa&topb)/max(len(topa|topb),1),
                'top_quartile_intersection':len(topa&topb)})
  if len(have)>=3:
   ranks=p[have].rank(pct=True); consensus.append({'dataset':ds,'factor':scale,'cases':len(p),'models':len(have),
       'cases_top_quartile_all_models':int((ranks>=.75).all(axis=1).sum()),
       'cases_top_quartile_at_least_4':int(((ranks>=.75).sum(axis=1)>=min(4,len(have))).sum()),
       'median_pair_rho':float(np.nanmedian([rho(p[a],p[b]) for a,b in itertools.combinations(have,2)]))})
 pairs=pd.DataFrame(rows);pairs.to_csv(OUT/'p9_cross_arch_error_rank_correlations.csv',index=False)
 pairs.groupby(['dataset','factor','family_pair'],as_index=False).agg(pair_count=('error_rank_rho','size'),median_error_rank_rho=('error_rank_rho','median'),median_top_quartile_jaccard=('top_quartile_jaccard','median')).to_csv(OUT/'p9_error_correlation_pair_types.csv',index=False)
 pd.DataFrame(consensus).to_csv(OUT/'p9_consensus_error_intersection.csv',index=False)

def output_paths():
 return {
  'hat':ROOT/'baseline/fastmri_brain_hat_2p5d/runs/full/model_outputs',
  'swinir':ROOT/'baseline/fastmri_brain_swinir_2p5d/runs/full/model_outputs',
  'i3net':ROOT/'baseline/fastmri_brain_i3net/runs/full/model_outputs',
  'saint':ROOT/'baseline/fastmri_brain_t2_saint_expanded/runs/full/saint_outputs',
  'cycleinr':ROOT/'baseline/fastmri_brain_cycleinr/runs/full/model_outputs'}

def prediction_error_diversity():
 cases=[q.strip() for q in (ROOT/'dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407/test_cases.txt').read_text(encoding='utf-8').splitlines() if q.strip()]
 paths=output_paths();rows=[];zs=[1,2,3,5,6,7,9,10,11]
 for case in cases:
  fn=case if case.endswith('.nii.gz') else case+'.nii.gz'; gt=nib.load(str(ROOT/'dataset/fastMRI_brain_T2/processed/nifti'/fn)).get_fdata(dtype=np.float32)[:,:,:13]
  pred={m:nib.load(str(p/f'diff_{fn}')).get_fdata(dtype=np.float32) for m,p in paths.items()}
  for a,b in itertools.combinations(MODELS,2):
   ea=[];eb=[];pa=[];pb=[]
   for z in zs:
    y=gt[:,:,z];mask=np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6)
    ea.append((pred[a][:,:,z]-y)[mask]);eb.append((pred[b][:,:,z]-y)[mask]);pa.append(pred[a][:,:,z][mask]);pb.append(pred[b][:,:,z][mask])
   ea=np.concatenate(ea).astype(float);eb=np.concatenate(eb).astype(float);pa=np.concatenate(pa);pb=np.concatenate(pb)
   n1=ea@ea;n2=eb@eb;tot=.5*(n1+n2);obs=np.sum(((ea-eb)/2)**2)
   rows.append({'case':case,'model_a':a,'model_b':b,'family_pair':pair_type(a,b),'prediction_diversity_mae':float(np.mean(np.abs(pa-pb))),
                'error_cosine':float(ea@eb/np.sqrt(n1*n2)),'observable_fraction':float(obs/tot),'paired_error_mae':float(.5*(np.mean(np.abs(ea))+np.mean(np.abs(eb))))})
 x=pd.DataFrame(rows);x.to_csv(OUT/'p9_cross_arch_prediction_error_diversity_per_case.csv',index=False)
 sums=[]
 for typ,g in x.groupby('family_pair'):
  sums.append({'family_pair':typ,'model_pairs':g[['model_a','model_b']].drop_duplicates().shape[0],'cases':g.case.nunique(),
   'median_prediction_diversity_mae':g.prediction_diversity_mae.median(),'median_error_cosine':g.error_cosine.median(),
   'median_observable_fraction':g.observable_fraction.median(),'rho_diversity_observable':rho(g.prediction_diversity_mae,g.observable_fraction),
   'rho_diversity_error_cosine':rho(g.prediction_diversity_mae,g.error_cosine)})
 pd.DataFrame(sums).to_csv(OUT/'p9_cross_arch_prediction_error_diversity_summary.csv',index=False)

def stable_wrong_overlap():
 a=pd.read_csv(OUT/'p9_disjoint_shared_per_plane.csv');b=pd.read_csv(OUT/'p9_disjoint_shared_per_plane_transformer_reference.csv');x=pd.concat([a,b],ignore_index=True)
 x=x[x.condition=='shared']; rows=[]
 for a,b in itertools.combinations(MODELS,2):
  qa=x[x.model==a].set_index(['case','target_z']).stable_wrong.astype(bool);qb=x[x.model==b].set_index(['case','target_z']).stable_wrong.astype(bool);idx=qa.index.intersection(qb.index)
  aa=set(idx[qa.loc[idx].to_numpy()]);bb=set(idx[qb.loc[idx].to_numpy()])
  rows.append({'model_a':a,'model_b':b,'stable_wrong_a':len(aa),'stable_wrong_b':len(bb),'intersection':len(aa&bb),'jaccard':len(aa&bb)/max(len(aa|bb),1)})
 pd.DataFrame(rows).to_csv(OUT/'p9_stable_wrong_cross_model_overlap.csv',index=False)

def influence_synthesis():
 frames=[];st=[]
 for m in ['saint','i3net','cycleinr']:
  frames.append(pd.read_csv(OUT/f'p9_influence_{m}_summary.csv'));st.append(pd.read_csv(OUT/f'p9_influence_{m}_stability.csv'))
 pd.concat(frames,ignore_index=True).to_csv(OUT/'p9_new_arch_influence_summary.csv',index=False)
 pd.concat(st,ignore_index=True).to_csv(OUT/'p9_new_arch_influence_stability.csv',index=False)
 stable_models=[m for m,g in pd.concat(st).groupby('model') if g['pass'].all()]
 payload={'stable_new_models':stable_models,'phenomenon_only_due_to_stability_failure':sorted(set(['saint','i3net','cycleinr'])-set(stable_models)),
          'interpretation':'Influence evidence is claim-eligible only for models passing every preregistered stability gate.'}
 (OUT/'p9_influence_verdict.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')

def main():
 OUT.mkdir(parents=True,exist_ok=True);src=benchmark();factor_arch(src);error_correlations();prediction_error_diversity();stable_wrong_overlap();influence_synthesis()
 print('Plan-9 cross-architecture analyses complete')
if __name__=='__main__':main()
