"""CONFIRMATORY independent IXI x4 replication of frozen pre-reconstruction features."""
from __future__ import annotations
import json,sys
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'plan3_outputs'
sys.path.insert(0,str(ROOT/'design'))
from rasinet.optimization_protocol import profile_sources,case_names,sparse_path
from rasinet.icassp_statistics import ranking_metrics
from plan3_prereconstruction_triangle import sparse_features

def rho(a,b): return float(stats.spearmanr(a,b).statistic)
def main():
 src=profile_sources('ixi',4)['i3net']; cases=case_names(src,None); rows=[]
 for i,case in enumerate(cases):
  img=nib.load(str(sparse_path(src,None,case))); rows.append({'case':case,'scale':4,**sparse_features(img.get_fdata(dtype=np.float32),img.affine)})
  if (i+1)%25==0: print('IXI features',i+1,flush=True)
 feat=pd.DataFrame(rows); feat.to_csv(OUT/'ixi_prereconstruction_features.csv',index=False)
 labels=pd.read_csv(ROOT/'design/rasinet/outputs/nested_optimization/common_errors_per_case_development.csv')
 labels=labels[labels.dataset.eq('ixi')]; x=labels.merge(feat,on=['case','scale']); x.to_csv(OUT/'ixi_prereconstruction_panel.csv',index=False)
 features=['input_adj_rmse','input_dynamic_range','input_adj_mae','input_gradient','input_highfreq_fraction']
 result=[]; rng=np.random.default_rng(20260904); cs=np.array(sorted(x.case.unique())); by={c:x[x.case.eq(c)] for c in cs}
 for feature in features:
  obs=np.mean([rho(g.common_error,g[feature]) for _,g in x.groupby('target_model')]); vals=[]
  for _ in range(2000):
   b=pd.concat([by[c] for c in rng.choice(cs,len(cs),replace=True)],ignore_index=True)
   vals.append(np.mean([rho(g.common_error,g[feature]) for _,g in b.groupby('target_model')]))
  per={m:rho(g.common_error,g[feature]) for m,g in x.groupby('target_model')}
  result.append({'feature':feature,'cases':len(cs),'models':len(per),'mean_model_rho':float(obs),'cluster_bootstrap_95ci':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))],'per_model_rho':per})
 # Architecture-invariant latent difficulty on IXI.
 piv=x.pivot(index='case',columns='target_model',values='common_error'); corr=piv.corr(method='spearman'); corr.to_csv(OUT/'ixi_model_error_correlations.csv')
 payload={'feature_results':result,'median_pairwise_model_error_rho':float(corr.where(np.triu(np.ones(corr.shape),1).astype(bool)).stack().median())}
 (OUT/'ixi_prereconstruction_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8'); print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
