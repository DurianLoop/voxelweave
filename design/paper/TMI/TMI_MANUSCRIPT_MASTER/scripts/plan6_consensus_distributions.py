"""P6-E02: full consensus-error distributions and stable-wrong failure."""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();MASTER=HERE.parents[1];PAPER=HERE.parents[3];CV= PAPER/'CVPR'/'CVPR_UPGRADE'/'outputs';OUT=MASTER/'experiments';FIG=MASTER/'figures'
OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)

def partial_spearman(x,y,control,case):
    x=stats.rankdata(np.asarray(x,float));y=stats.rankdata(np.asarray(y,float));c=stats.rankdata(np.asarray(control,float));case=np.asarray(case)
    for k in np.unique(case):
        q=case==k;x[q]-=x[q].mean();y[q]-=y[q].mean();c[q]-=c[q].mean()
    z=np.column_stack([np.ones(len(x)),c]);ex=x-z@np.linalg.lstsq(z,x,rcond=None)[0];ey=y-z@np.linalg.lstsq(z,y,rcond=None)[0]
    return float(np.corrcoef(ex,ey)[0,1])

x=pd.concat([pd.read_csv(CV/'overlap_covariance_per_plane.csv'),pd.read_csv(CV/'overlap_covariance_ixi_per_plane.csv')],ignore_index=True)
x['total_squared_error']=x.mean_mse;x['shared_consensus_component']=x.shared_mse;x['context_sensitive_component']=x.diversity_mse
x['normalized_disagreement']=x.disagreement_mae/(np.sqrt(x.mean_mse)+1e-8)
summ=[];assoc=[];stable=[];rng=np.random.default_rng(20260813)
metrics=['total_squared_error','shared_consensus_component','context_sensitive_component','shared_fraction','observable_fraction','error_cosine','disagreement_mae']
for keys,g in x.groupby(['dataset','model','condition']):
    rec=dict(zip(['dataset','model','condition'],keys));rec.update({'planes':len(g),'cases':g.case_id.nunique(),'patient_clusters':g.patient_cluster.nunique()})
    for m in metrics:
        rec[f'{m}_q05']=g[m].quantile(.05);rec[f'{m}_q25']=g[m].quantile(.25);rec[f'{m}_median']=g[m].median();rec[f'{m}_q75']=g[m].quantile(.75);rec[f'{m}_q95']=g[m].quantile(.95)
    summ.append(rec)
    assoc.append({**dict(zip(['dataset','model','condition'],keys)),'partial_rho_shared_fraction_vs_normalized_disagreement_given_total_error_and_case':partial_spearman(g.shared_fraction,g.normalized_disagreement,np.log1p(g.mean_mse),g.case_id),
                  'partial_rho_shared_fraction_vs_disagreement_given_total_error_and_case':partial_spearman(g.shared_fraction,g.disagreement_mae,np.log1p(g.mean_mse),g.case_id)})

# Pooled within dataset/model thresholds permit a fair condition comparison.
for (ds,model),g in x.groupby(['dataset','model']):
    err_cut=g.mae.quantile(.75);dis_cut=g.disagreement_mae.quantile(.25);g=g.copy();g['stable_wrong']=(g.mae>=err_cut)&(g.disagreement_mae<=dis_cut)
    point=g.groupby('condition').stable_wrong.mean();delta=float(point.get('max_shared_reversal',np.nan)-point.get('disjoint_phase',np.nan))
    clusters=g.patient_cluster.unique();by={k:g[g.patient_cluster==k] for k in clusters};boots=[]
    for _ in range(2000):
        b=pd.concat([by[k] for k in rng.choice(clusters,len(clusters),replace=True)],ignore_index=True);p=b.groupby('condition').stable_wrong.mean();boots.append(p.get('max_shared_reversal',np.nan)-p.get('disjoint_phase',np.nan))
    stable.append({'dataset':ds,'model':model,'error_q75':err_cut,'disagreement_q25':dis_cut,'disjoint_prevalence':point.get('disjoint_phase',np.nan),'max_shared_prevalence':point.get('max_shared_reversal',np.nan),'paired_prevalence_delta':delta,'cluster_ci_low':float(np.nanquantile(boots,.025)),'cluster_ci_high':float(np.nanquantile(boots,.975))})

pd.DataFrame(summ).to_csv(OUT/'p6_e02_consensus_distribution_summary.csv',index=False)
pd.DataFrame(assoc).to_csv(OUT/'p6_e02_consensus_failure_associations.csv',index=False)
pd.DataFrame(stable).to_csv(OUT/'p6_e02_stable_wrong_prevalence.csv',index=False)
x.to_csv(OUT/'p6_e02_consensus_per_plane.csv',index=False)

names={'fastmri':'fastMRI','ixi':'IXI','ningxia':'NingXia'};colors={'disjoint_phase':'#2b6cb0','max_shared_reversal':'#d65f45'}
fig,axs=plt.subplots(2,3,figsize=(11.5,6.2))
for col,ds in enumerate(['fastmri','ixi','ningxia']):
    q=x[x.dataset==ds]
    groups=[q[q.condition==c].shared_fraction for c in colors]
    bp=axs[0,col].boxplot(groups,positions=[0,1],widths=.58,showfliers=False,patch_artist=True)
    for box,c in zip(bp['boxes'],colors.values()):box.set_facecolor(c);box.set_alpha(.75)
    axs[0,col].set_title(names[ds]);axs[0,col].set_xticks([0,1],['Disjoint','Max shared']);axs[0,col].set_ylabel('Shared error fraction' if col==0 else '')
    for cond,c in colors.items():
        v=np.sort(q[q.condition==cond].normalized_disagreement);axs[1,col].plot(v,np.linspace(0,1,len(v),endpoint=True),color=c,label='Disjoint' if cond=='disjoint_phase' else 'Max shared')
    axs[1,col].set_xlabel('Disagreement / RMSE');axs[1,col].set_ylabel('Empirical CDF' if col==0 else '');axs[1,col].grid(alpha=.2)
axs[1,0].legend(frameon=False,fontsize=8);fig.suptitle('Measurement sharing increases consensus error and suppresses observable disagreement',fontsize=11);fig.tight_layout();fig.savefig(FIG/'p6_e02_consensus_distributions.pdf',bbox_inches='tight');fig.savefig(FIG/'p6_e02_consensus_distributions.png',dpi=300,bbox_inches='tight');plt.close(fig)

payload={'experiment':'P6-E02','status':'COMPLETE','coverage':['fastmri','ixi','ningxia'],'models':['hat','swinir'],'ningxia_independent_units':'8 patient clusters (22 series)',
         'stable_wrong_definition':'pooled-within-dataset/model top-quartile plane MAE and bottom-quartile disagreement; thresholds applied identically to both overlap conditions',
         'outputs':['p6_e02_consensus_per_plane.csv','p6_e02_consensus_distribution_summary.csv','p6_e02_consensus_failure_associations.csv','p6_e02_stable_wrong_prevalence.csv'],'figure':'../figures/p6_e02_consensus_distributions.pdf'}
(OUT/'p6_e02_consensus_distributions.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(pd.DataFrame(assoc).to_string(index=False));print(pd.DataFrame(stable).to_string(index=False));print(json.dumps(payload,indent=2))
