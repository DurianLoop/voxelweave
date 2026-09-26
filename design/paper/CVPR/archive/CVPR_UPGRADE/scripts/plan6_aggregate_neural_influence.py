"""Aggregate P6-E04 three-cohort confirmation outputs and render a forest plot."""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';FIG=UP/'PAPER'/'figures';FIG.mkdir(parents=True,exist_ok=True)
DATASETS=('fastmri','ixi','ningxia')
ENDPOINTS=('error_cosine','shared_fraction','observable_fraction','disagreement_mae')

frames=[];records=[]
for ds in DATASETS:
    stem=f'plan6_neural_shared_influence_confirm3_{ds}'
    frames.append(pd.read_csv(OUT/f'{stem}_per_case_config.csv'))
    payload=json.loads((OUT/f'{stem}_summary.json').read_text(encoding='utf-8'))
    for row in payload['rows']:
        ci=row['cluster_95ci_abs_rho_advantage']
        for a in row['associations']:
            records.append({
                'dataset':row['dataset'],'model':row['model'],'cases':row['cases'],
                'planes':row['planes'],'clusters':row['clusters'],'endpoint':a['endpoint'],
                'rho_overlap':a['rho_overlap'],'rho_neural_influence':a['rho_neural_influence'],
                'rho_common_response_mass':a['rho_common_response_mass'],
                'abs_rho_advantage':abs(a['rho_neural_influence'])-abs(a['rho_overlap']),
                'advantage_ci_low':ci[a['endpoint']][0],'advantage_ci_high':ci[a['endpoint']][1],
                'partial_rho_overlap_given_distance_and_case':a['partial_rho_overlap_given_distance_and_case'],
                'partial_rho_influence_given_geometry_and_case':a['partial_rho_influence_given_geometry_and_case'],
            })

raw=pd.concat(frames,ignore_index=True)
tidy=pd.DataFrame(records)
raw.to_csv(OUT/'plan6_neural_shared_influence_confirm3_per_case_config.csv',index=False)
tidy.to_csv(OUT/'plan6_neural_shared_influence_confirm3_summary.csv',index=False)

labels={'fastmri':'fastMRI','ixi':'IXI','ningxia':'NingXia','hat':'HAT','swinir':'SwinIR'}
ep_labels={'error_cosine':'Error cosine','shared_fraction':'Shared fraction','observable_fraction':'Observable fraction','disagreement_mae':'Disagreement MAE'}
fig,axs=plt.subplots(1,4,figsize=(13.0,3.8),sharex=True)
for ax,ep in zip(axs,ENDPOINTS):
    q=tidy[tidy.endpoint==ep].reset_index(drop=True)
    y=np.arange(len(q))[::-1]
    color=['#2463a8' if m=='hat' else '#d05a39' for m in q.model]
    for i,r in q.iterrows():
        ax.errorbar(r.abs_rho_advantage,y[i],xerr=[[r.abs_rho_advantage-r.advantage_ci_low],[r.advantage_ci_high-r.abs_rho_advantage]],fmt='o',color=color[i],capsize=2.5,lw=1.2,ms=4.5)
    ax.axvline(0,color='0.35',lw=.8,ls='--');ax.grid(axis='x',alpha=.2)
    ax.set_title(ep_labels[ep],fontsize=10);ax.set_xlabel(r'$|\rho_{influence}|-|\rho_{overlap}|$',fontsize=9)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{labels[d]} · {labels[m]}" for d,m in zip(q.dataset,q.model)] if ax is axs[0] else [])
for ax in axs:ax.tick_params(labelsize=8)
fig.suptitle('Neural shared influence improves association beyond anchor-overlap count',fontsize=11,y=1.02)
fig.tight_layout();fig.savefig(FIG/'plan6_neural_influence_forest.pdf',bbox_inches='tight');fig.savefig(FIG/'plan6_neural_influence_forest.png',dpi=300,bbox_inches='tight');plt.close(fig)

primary=tidy[tidy.endpoint.isin(ENDPOINTS[:3])]
payload={
    'experiment':'P6-E04','status':'THREE-COHORT THREE-PLANE CONFIRMATION COMPLETE',
    'coverage':{'fastmri_cases':24,'ixi_cases':115,'ningxia_series':22,'ningxia_patient_clusters':8,'models':['hat','swinir'],'planes_per_case':3},
    'primary_all_positive_advantage':bool((primary.abs_rho_advantage>0).all()),
    'primary_all_cluster_ci_exclude_zero':bool((primary.advantage_ci_low>0).all()),
    'supporting_disagreement_all_positive_advantage':bool((tidy[tidy.endpoint=='disagreement_mae'].abs_rho_advantage>0).all()),
    'supporting_disagreement_all_cluster_ci_exclude_zero':bool((tidy[tidy.endpoint=='disagreement_mae'].advantage_ci_low>0).all()),
    'summary_csv':'plan6_neural_shared_influence_confirm3_summary.csv',
    'raw_csv':'plan6_neural_shared_influence_confirm3_per_case_config.csv',
    'figure':'../PAPER/figures/plan6_neural_influence_forest.pdf',
}
(OUT/'plan6_neural_shared_influence_confirm3.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(tidy.to_string(index=False));print(json.dumps(payload,indent=2))
