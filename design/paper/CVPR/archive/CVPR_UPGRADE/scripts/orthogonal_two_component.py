"""C5-E006: frozen, mechanism-derived two-component risk model."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats,optimize

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];OUT=UP/'outputs';OUT.mkdir(exist_ok=True)
def rho(a,b):return float(stats.spearmanr(a,b).statistic)
def naurc(y,s):
 o=np.argsort(s);risk=np.cumsum(np.asarray(y)[o])/np.arange(1,len(y)+1);a=risk.mean();oracle=(np.cumsum(np.sort(y))/np.arange(1,len(y)+1)).mean();rev=(np.cumsum(np.sort(y)[::-1])/np.arange(1,len(y)+1)).mean();return float((a-oracle)/(rev-oracle))
def rankify(x):
 for c in ('score','input_adj_rmse','error'):x[c+'_rank']=x.groupby(['dataset','model'])[c].rank(pct=True)
 return x
def load():
 f=pd.read_csv(PAPER/'plan4_outputs'/'disjoint_anchor_per_case.csv').rename(columns={'target_model':'model'});f['dataset']='fastmri'
 n=pd.read_csv(PAPER/'plan4_outputs'/'ningxia_disjoint_per_case.csv').rename(columns={'target_model':'model'});n['dataset']='ningxia'
 # IXI score and error: median plane disagreement/mean error from completed C5-E002 zero-overlap rows.
 q=pd.read_csv(OUT/'overlap_covariance_ixi_per_plane.csv');q=q[q.overlap.eq(0)].groupby(['case_id','model'],as_index=False).agg(score=('disagreement_mae','median'),error=('mae','median')).rename(columns={'case_id':'case'});q['dataset']='ixi'
 base=pd.concat([f[['dataset','case','model','score','error']],n[['dataset','case','model','score','error']],q],ignore_index=True)
 ixi_feat=pd.read_csv(PAPER/'plan3_outputs'/'ixi_prereconstruction_features.csv');ixi_feat['dataset']='ixi'
 feat=pd.concat([pd.read_csv(PAPER/'plan3_outputs'/'prereconstruction_features.csv').query('scale==4'),ixi_feat],ignore_index=True)
 feat=feat[['dataset','case','input_adj_rmse']].drop_duplicates();return rankify(base.merge(feat,on=['dataset','case']))
def metrics(g,score):
 rows=[]
 for m,q in g.groupby('model'):rows.append({'model':m,'rho':rho(q.error,q[score]),'nAURC':naurc(q.error,q[score])})
 return {'mean_rho':float(np.mean([r['rho'] for r in rows])),'mean_nAURC':float(np.mean([r['nAURC'] for r in rows])),'per_model':rows}
def main():
 x=load();dev_cases=sorted(x[x.dataset.eq('fastmri')].case.unique())[:12];x['split']=np.where(x.dataset.ne('fastmri'),'transfer',np.where(x.case.isin(dev_cases),'development','confirmation'))
 d=x[(x.dataset.eq('fastmri'))&x.split.eq('development')]
 A=np.column_stack([np.ones(len(d)),d.score_rank]);alpha=np.linalg.lstsq(A,d.input_adj_rmse_rank,rcond=None)[0]
 dres=d.input_adj_rmse_rank-(alpha[0]+alpha[1]*d.score_rank);X=np.column_stack([np.ones(len(d)),d.score_rank,dres]);coef=optimize.nnls(X,d.error_rank)[0]
 x['input_orthogonal']=x.input_adj_rmse_rank-(alpha[0]+alpha[1]*x.score_rank);x['two_component']=coef[0]+coef[1]*x.score_rank+coef[2]*x.input_orthogonal
 x.to_csv(OUT/'orthogonal_two_component_per_case.csv',index=False)
 results=[]
 for (ds,split),g in x.groupby(['dataset','split']):
  results.append({'dataset':ds,'split':split,'cases':g.case.nunique(),'disjoint':metrics(g,'score_rank'),'two_component':metrics(g,'two_component')})
 conf=[r for r in results if r['dataset']=='fastmri' and r['split']=='confirmation'][0];gate=conf['two_component']['mean_rho']>conf['disjoint']['mean_rho'] and conf['two_component']['mean_nAURC']<conf['disjoint']['mean_nAURC']
 payload={'experiment':'C5-E006','status':'EXPLORATORY METHOD DERIVATION','residualization_intercept_slope':alpha.tolist(),'nonnegative_coefficients':coef.tolist(),'primary_gate_passed':bool(gate),'results':results,
  'decision':'KEEP as method candidate' if gate else 'REJECT as CVPR method candidate; retain negative result'}
 (OUT/'orthogonal_two_component_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
