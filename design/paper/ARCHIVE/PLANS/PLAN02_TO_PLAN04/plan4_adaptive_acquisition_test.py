"""Does the x4 anchor-disjoint witness identify who benefits from denser x2 sampling?"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent;P3=HERE/'plan3_outputs';P4=HERE/'plan4_outputs'
def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')

def main():
    d=pd.concat([pd.read_csv(P4/'disjoint_anchor_per_case.csv').assign(dataset='fastmri'),pd.read_csv(P4/'ningxia_disjoint_per_case.csv').assign(dataset='ningxia')],ignore_index=True)
    e=pd.read_csv(P3/'error_balanced_panel.csv');e=e[e.target_model.isin(['hat','swinir'])]
    wide=e.pivot_table(index=['dataset','case','target_model'],columns='scale',values='common_error').reset_index().rename(columns={2:'error_x2',4:'error_x4',6:'error_x6'})
    x=d.merge(wide,on=['dataset','case','target_model']);x['benefit_x4_to_x2']=x.error_x4-x.error_x2;x['benefit_x6_to_x4']=x.error_x6-x.error_x4
    x.to_csv(P4/'adaptive_acquisition_per_case.csv',index=False);rows=[];rng=np.random.default_rng(20260813)
    for ds,g in x.groupby('dataset'):
        rd=rho(g.score,g.benefit_x4_to_x2);re=rho(g.score,g.error_x4);cases=np.array(sorted(g.case.unique()));by={c:g[g.case.eq(c)] for c in cases};boot=[]
        for _ in range(5000):
            b=pd.concat([by[c] for c in rng.choice(cases,len(cases),replace=True)],ignore_index=True);boot.append(rho(b.score,b.benefit_x4_to_x2))
        # Budgeted policy: densify top quartile score versus oracle and random expected gain.
        k=max(1,int(np.ceil(.25*len(g))));chosen=g.nlargest(k,'score').benefit_x4_to_x2.mean();oracle=g.nlargest(k,'benefit_x4_to_x2').benefit_x4_to_x2.mean();random=g.benefit_x4_to_x2.mean()
        rows.append({'dataset':ds,'units':len(g),'cases':len(cases),'rho_score_vs_x4_to_x2_benefit':rd,'case_cluster_95ci':[float(np.nanquantile(boot,.025)),float(np.nanquantile(boot,.975))],
                     'rho_score_vs_x4_error':re,'top_quartile_policy_gain':float(chosen),'random_policy_gain':float(random),'oracle_policy_gain':float(oracle),
                     'fraction_oracle_gain_above_random':float((chosen-random)/(oracle-random)) if oracle!=random else None})
    result={'question':'Can a zero-shared-anchor x4 witness prioritize examinations for denser x2 acquisition?','rows':rows}
    (P4/'adaptive_acquisition_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
