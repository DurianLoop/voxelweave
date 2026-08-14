"""P6-E07A: frozen three-cohort x4 risk-coverage confirmation."""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';FIG=UP/'PAPER'/'figures';FIG.mkdir(parents=True,exist_ok=True)
acv=pd.read_csv(OUT/'plan6_anchor_cv_explanation_per_case.csv')
pc=pd.read_csv(OUT/'orthogonal_two_component_per_case.csv').rename(columns={'score':'pc_disagreement'})
x=acv.merge(pc[['dataset','case','model','pc_disagreement']],on=['dataset','case','model'])
METHODS={'Anchor-CV':'anchor_cv','Adjacent MAE':'adjacent_mae','Output PC':'pc_disagreement'}
COVERAGES=(.10,.20,.30,.50,.70,.90,1.0);rng=np.random.default_rng(20260813)

def risk(y,s,c):
    k=max(1,int(np.ceil(len(y)*c)));return float(np.mean(np.asarray(y)[np.argsort(np.asarray(s))[:k]]))

rows=[]
for (ds,model),g in x.groupby(['dataset','model']):
    g=g.reset_index(drop=True);clusters=g.patient_cluster.unique();groups=[g.index[g.patient_cluster.eq(k)].to_numpy() for k in clusters]
    for method,col in METHODS.items():
        yy=g.x4_error.to_numpy(float);ss=g[col].to_numpy(float)
        for cov in COVERAGES:
            point=risk(g.x4_error,g[col],cov);boots=[]
            for _ in range(2000):
                ix=np.concatenate([groups[j] for j in rng.integers(0,len(groups),len(groups))]);boots.append(risk(yy[ix],ss[ix],cov))
            oracle=risk(g.x4_error,g.x4_error,cov);random=float(g.x4_error.mean())
            rows.append({'dataset':ds,'model':model,'method':method,'coverage':cov,'retained_risk':point,'oracle_risk':oracle,'random_risk':random,
                         'excess_over_oracle':point-oracle,'improvement_over_random':random-point,'cluster_ci_low':float(np.quantile(boots,.025)),'cluster_ci_high':float(np.quantile(boots,.975))})
r=pd.DataFrame(rows);r.to_csv(OUT/'plan6_frozen_risk_coverage.csv',index=False)

# Exact all-prefix curves and normalized AURC per stratum.
curve=[];summ=[]
for (ds,model),g in x.groupby(['dataset','model']):
    y=g.x4_error.to_numpy(float);oracle=np.cumsum(np.sort(y))/np.arange(1,len(y)+1);reverse=np.cumsum(np.sort(y)[::-1])/np.arange(1,len(y)+1)
    for method,col in METHODS.items():
        o=np.argsort(g[col].to_numpy(float));rr=np.cumsum(y[o])/np.arange(1,len(y)+1);naurc=float((rr.mean()-oracle.mean())/(reverse.mean()-oracle.mean()))
        summ.append({'dataset':ds,'model':model,'method':method,'nAURC':naurc})
        for k,v in enumerate(rr,1):curve.append({'dataset':ds,'model':model,'method':method,'coverage':k/len(y),'retained_risk':v})
pd.DataFrame(curve).to_csv(OUT/'plan6_frozen_risk_coverage_full_curve.csv',index=False);pd.DataFrame(summ).to_csv(OUT/'plan6_frozen_risk_coverage_summary.csv',index=False)

colors={'Anchor-CV':'#1f5fa8','Adjacent MAE':'#d05b3e','Output PC':'#629f53'};fig,axs=plt.subplots(2,3,figsize=(10.8,6.0),sharex=True)
for col,ds in enumerate(['fastmri','ixi','ningxia']):
    for row,model in enumerate(['hat','swinir']):
        q=pd.DataFrame(curve);q=q[(q.dataset==ds)&(q.model==model)]
        for method,c in colors.items():
            z=q[q.method==method];axs[row,col].plot(z.coverage,z.retained_risk,label=method,color=c,lw=1.6)
        axs[row,col].grid(alpha=.2);axs[row,col].set_title(f"{ds} · {model.upper()}",fontsize=9);axs[row,col].set_xlabel('Retained coverage');axs[row,col].set_ylabel('Retained x4 MAE' if col==0 else '')
axs[0,0].legend(frameon=False,fontsize=7);fig.suptitle('Frozen examination triage: full risk–coverage curves',fontsize=11);fig.tight_layout();fig.savefig(FIG/'plan6_frozen_risk_coverage.pdf',bbox_inches='tight');fig.savefig(FIG/'plan6_frozen_risk_coverage.png',dpi=300,bbox_inches='tight');plt.close(fig)

s=pd.DataFrame(summ);payload={'experiment':'P6-E07A','status':'FROZEN REANALYSIS COMPLETE; NOT INDEPENDENT EXTERNAL CONFIRMATION','coverage':['fastmri','ixi','ningxia'],'models':['hat','swinir'],
 'frozen_score':'ANCHOR_CV_V1','selection_rule':'retain lowest score','primary':'nAURC and complete curve; lower is better',
 'anchor_cv_best_naurc_all_strata':bool((s[s.method=='Anchor-CV'].set_index(['dataset','model']).nAURC < s[s.method=='Output PC'].set_index(['dataset','model']).nAURC).all()),
 'ixix2_status':'not computed: completed definition-matched IXI x2 outputs unavailable; no fastMRI+NingXia-only Plan6 confirmation',
 'outputs':['plan6_frozen_risk_coverage.csv','plan6_frozen_risk_coverage_full_curve.csv','plan6_frozen_risk_coverage_summary.csv'],'figure':'../PAPER/figures/plan6_frozen_risk_coverage.pdf'}
(OUT/'plan6_frozen_risk_coverage.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(s.to_string(index=False));print(json.dumps(payload,indent=2))
