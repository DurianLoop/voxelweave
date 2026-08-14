"""P6-E07B: frozen IXI x4->x2 consequence and IXI+fastMRI budget confirmation."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1];OUT=UP/'outputs';RUN=ROOT/'baseline'/'ixi_i3net'/'runs'/'full_test115_x2_fast';RNG=np.random.default_rng(20260813);BUDGETS=(.1,.2,.3,.5)
def rho(a,b):return float(stats.spearmanr(a,b).statistic)
def selected(v,score,b):
 k=max(1,int(np.ceil(len(v)*b)));return float(np.mean(np.asarray(v)[np.argsort(np.asarray(score))[::-1][:k]]))
def make_rows(g,ds):
 rows=[];clusters=g.patient_cluster.unique();groups=[g.index[g.patient_cluster.eq(c)].to_numpy() for c in clusters]
 methods={'Anchor-CV':'anchor_cv','Adjacent MAE':'adjacent_mae','Output PC':'pc_score'}
 for b in BUDGETS:
  random=float(g.benefit.mean());oracle=selected(g.benefit,g.benefit,b)
  for name,col in methods.items():
   point=selected(g.benefit,g[col],b);boots=[]
   for _ in range(2000):
    ix=np.concatenate([groups[j] for j in RNG.integers(0,len(groups),len(groups))]);q=g.iloc[ix];boots.append(selected(q.benefit,q[col],b)-q.benefit.mean())
   rows.append({'dataset':ds,'budget':b,'method':name,'selected_benefit':point,'random_expected':random,'gain_above_random':point-random,'oracle_benefit':oracle,'oracle_normalized_gain':(point-random)/(oracle-random) if oracle>random else np.nan,'cluster_ci_low':float(np.quantile(boots,.025)),'cluster_ci_high':float(np.quantile(boots,.975))})
 return rows

def main():
 metrics=RUN/'metrics'/'per_case_metrics.csv'
 if not metrics.exists():raise FileNotFoundError(f'Frozen IXI x2 metrics not ready: {metrics}')
 q=pd.read_csv(metrics);q=q[q.method=='i3net'][['case','mae']].rename(columns={'mae':'x2_error'})
 if q.case.nunique()!=115:raise RuntimeError(f'Expected 115 IXI x2 cases, found {q.case.nunique()}')
 acv=pd.read_csv(OUT/'plan6_anchor_cv_explanation_per_case.csv');acv=acv.groupby(['dataset','case','patient_cluster'],as_index=False).agg(anchor_cv=('anchor_cv','first'),adjacent_mae=('adjacent_mae','first'),x4_error=('x4_error','mean'))
 pc=pd.read_csv(OUT/'orthogonal_two_component_per_case.csv').groupby(['dataset','case'],as_index=False).pc_score.mean() if False else None
 op=pd.read_csv(OUT/'orthogonal_two_component_per_case.csv').groupby(['dataset','case'],as_index=False).agg(pc_score=('score','mean'))
 ixi=acv[acv.dataset=='ixi'].merge(op,on=['dataset','case']).merge(q,on='case');ixi['benefit']=ixi.x4_error-ixi.x2_error;ixi.to_csv(OUT/'plan6_ixi_x2_consequence_per_case.csv',index=False)
 # Existing fastMRI definition-matched benefit, used only with IXI as the permitted two-cohort pair.
 f=acv[acv.dataset=='fastmri'].merge(op,on=['dataset','case']);benef=pd.read_csv(PAPER/'plan4_outputs'/'adaptive_acquisition_per_case.csv').rename(columns={'target_model':'model'}).groupby('case',as_index=False).benefit_x4_to_x2.mean();f=f.merge(benef,on='case').rename(columns={'benefit_x4_to_x2':'benefit'})
 corr=[]
 for ds,g in [('fastmri',f),('ixi',ixi)]:
  for name,col in [('Anchor-CV','anchor_cv'),('Adjacent MAE','adjacent_mae'),('Output PC','pc_score')]:corr.append({'dataset':ds,'method':name,'cases':len(g),'spearman_vs_benefit':rho(g[col],g.benefit),'kendall_vs_benefit':float(stats.kendalltau(g[col],g.benefit).statistic)})
 budgets=pd.DataFrame(make_rows(f.reset_index(drop=True),'fastmri')+make_rows(ixi.reset_index(drop=True),'ixi'));pd.DataFrame(corr).to_csv(OUT/'plan6_ixi_x2_consequence_correlations.csv',index=False);budgets.to_csv(OUT/'plan6_ixi_x2_consequence_budgets.csv',index=False)
 payload={'experiment':'P6-E07B','status':'COMPLETE','coverage':['ixi','fastmri'],'coverage_rule':'permitted two-dataset pair','frozen_protocol':'../../IXI_X2_FROZEN_EVALUATION.md','ixi_cases':115,'ixi_x2_checkpoint_sha256':'8C87AC897EBFD7C166CB99F4A7B8922BFC4552BE79C242ABB39194C3DA21C3B8','benefit_definition':'x4 mean HAT/SwinIR examination MAE minus frozen I3Net x2 examination MAE','retrospective_only':True,'outputs':['plan6_ixi_x2_consequence_per_case.csv','plan6_ixi_x2_consequence_correlations.csv','plan6_ixi_x2_consequence_budgets.csv']}
 (OUT/'plan6_ixi_x2_consequence.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(pd.DataFrame(corr).to_string(index=False));print(budgets.to_string(index=False));print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
