from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
P14=Path(__file__).resolve().parents[1]; OUT=P14/'outputs'; FIG=P14/'figures'; FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,name):
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight'); fig.savefig(FIG/(name+'.png'),dpi=180,bbox_inches='tight'); plt.close(fig)

scale=pd.read_csv(OUT/'ixi_scale_contract_correlations.csv')
fig,axes=plt.subplots(1,2,figsize=(8.2,3.2))
for ax,score,title in zip(axes,['anchor_cv','adjacent_mae'],['Anchor-CV','Adjacent-anchor MAE']):
    g=scale[scale.score.eq(score)].set_index(['score_unit','endpoint_unit'])
    a=np.array([[g.loc[(s,e),'rho'] for e in ['raw','normalized']] for s in ['raw','normalized']])
    ax.imshow(a,cmap='RdBu',vmin=-1,vmax=1)
    for i,s in enumerate(['raw','normalized']):
        for j,e in enumerate(['raw','normalized']):
            r=g.loc[(s,e)]; ax.text(j,i,f'{r.rho:.3f}\n[{r.ci_low:.3f}, {r.ci_high:.3f}]',ha='center',va='center',color='white' if abs(r.rho)>.6 else '#161616',fontsize=10)
    ax.set_xticks([0,1],['Raw benefit','Normalized benefit']); ax.set_yticks([0,1],['Raw score','Normalized score']); ax.set_title(title,fontweight='bold')
fig.suptitle('IXI I3Net: score and endpoint units define the ranking task',fontsize=11,fontweight='bold');fig.tight_layout();save(fig,'p14_scale_contract')

e=pd.read_csv(OUT/'topcow_effects.csv'); r=pd.read_csv(OUT/'topcow_rankings.csv')
fig,axes=plt.subplots(1,2,figsize=(9.8,3.0),gridspec_kw={'width_ratios':[1,1.35]})
colors={'acquired':'#2166AC','full':'#666666','gt':'#B35806'}
for j,mask in enumerate(['acquired','full','gt']):
    g=e[e['mask'].eq(mask)].set_index('pair').loc[['LC','CL']]; y=np.arange(2)+(j-1)*.16
    axes[0].errorbar(g.gain*100,y,xerr=np.stack([(g.gain-g.simultaneous_low)*100,(g.simultaneous_high-g.gain)*100]),fmt='o',ms=4,capsize=3,color=colors[mask],label={'acquired':'Acquired anchors','full':'All pixels','gt':'GT mask (sensitivity)'}[mask])
axes[0].set_yticks([0,1],['Linear target / Cubic partner','Cubic target / Linear partner']);axes[0].invert_yaxis();axes[0].set_xlabel('Observable gain (percentage points)');axes[0].set_title('(a) Local effect across score supports',loc='left',fontsize=10,fontweight='bold')
g=r[r['mask'].eq('acquired')]
for j,endpoint in enumerate(['error','vessel_error']):
    z=g[g.endpoint.eq(endpoint)].set_index('pair').loc[['LC','CL']]; y=np.arange(2)+(j-.5)*.2
    axes[1].errorbar(z.delta_rho,y,xerr=np.stack([z.delta_rho-z.delta_ci_low,z.delta_ci_high-z.delta_rho]),fmt='s' if j else 'o',ms=4,capsize=3,color=['#2166AC','#A33742'][j],label=['Acquired-support MAE','Annotated-vessel MAE'][j])
axes[1].set_yticks([0,1],['Linear target','Cubic target']);axes[1].invert_yaxis();axes[1].set_xlabel('Disjoint minus shared error-ranking correlation');axes[1].set_title('(b) Ranking against a fixed target-model error',loc='left',fontsize=10,fontweight='bold')
for ax in axes: ax.axvline(0,color='#777777',lw=.8,ls='--');ax.grid(axis='x',alpha=.15)
axes[0].legend(loc='lower left',bbox_to_anchor=(0,-.6),frameon=False,ncol=3,fontsize=7.5)
axes[1].legend(loc='lower left',bbox_to_anchor=(0,-.6),frameon=False,ncol=2,fontsize=7.5)
fig.tight_layout();save(fig,'p14_topcow_external')

bank=pd.read_csv(OUT/'bank_mask_correlations.csv')
fig,axes=plt.subplots(1,2,figsize=(9.5,3.5)); models=sorted(bank.model.unique())
for ax,ds,title in zip(axes,['fastmri','ningxia'],['fastMRI (24 examinations)','NingXia (8 patient clusters)']):
    for j,mask in enumerate(['target_0.01','input_derived','bank_union']):
        g=bank[bank.dataset.eq(ds)&bank['mask'].eq(mask)].set_index('model').loc[models]
        ax.scatter(g.rho,np.arange(11)+(j-1)*.2,s=16,color=['#666666','#2166AC','#B35806'][j],label=['Target-model prediction mask','Acquired-input mask','Prediction-bank union'][j])
    ax.set_yticks(range(11),models);ax.invert_yaxis();ax.axvline(0,color='#777',lw=.8);ax.set_xlim(-.35,1);ax.set_xlabel('Bank score / raw benefit Spearman correlation');ax.set_title(title,fontweight='bold')
fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.5,-.045),ncol=3,frameon=False,fontsize=8)
fig.tight_layout();save(fig,'p14_bank_mask_sensitivity')

if (OUT/'cas_transfer_rankings.csv').exists():
    bright=pd.read_csv(OUT/'bright_anchor_rankings.csv'); cas=pd.read_csv(OUT/'cas_transfer_rankings.csv')
    fig,axes=plt.subplots(1,2,figsize=(10.4,3.05),gridspec_kw={'width_ratios':[1,1.1]})
    base=r[r['mask'].eq('acquired')]
    for j,endpoint in enumerate(['error','vessel_error']):
        z=base[base.endpoint.eq(endpoint)].set_index('pair').loc[['LC','CL']];y=np.arange(2)+(j-.5)*.2
        axes[0].errorbar(z.delta_rho,y,xerr=np.stack([z.delta_rho-z.delta_ci_low,z.delta_ci_high-z.delta_rho]),fmt='o',ms=4,capsize=3,color=['#2166AC','#A33742'][j],label=['General error','Vessel error'][j])
    axes[0].set_yticks([0,1],['Linear target','Cubic target']);axes[0].set_xlabel('Disjoint minus shared ranking correlation');axes[0].set_title('(a) TopCoW: local exposure is insufficient',loc='left',fontweight='bold',fontsize=10)
    keys=[('shared','LC'),('shared','CL'),('disjoint','LC'),('disjoint','CL')]
    for j,(data,color,label) in enumerate([(bright,'#2166AC','TopCoW: exploratory'),(cas,'#B35806','CAS2023: fixed-rule transfer')]):
        z=data[data.endpoint.eq('vessel_error')].set_index(['condition','pair']).loc[keys];y=np.arange(4)+(j-.5)*.2
        axes[1].errorbar(z.delta_rho,y,xerr=np.stack([z.delta_rho-z.simultaneous_low,z.simultaneous_high-z.delta_rho]),fmt='s' if j else 'o',ms=4,capsize=3,color=color,label=label)
    axes[1].set_yticks(range(4),['Shared / Linear','Shared / Cubic','Disjoint / Linear','Disjoint / Cubic']);axes[1].set_xlabel('Bright minus general support: vessel ranking');axes[1].set_title('(b) Frozen acquired-bright support transfer',loc='left',fontweight='bold',fontsize=10)
    for ax in axes:
        ax.invert_yaxis();ax.axvline(0,color='#777777',lw=.8,ls='--');ax.grid(axis='x',alpha=.15)
        ax.legend(frameon=False,loc='lower center',bbox_to_anchor=(.5,-.45),ncol=2,fontsize=7.5)
    fig.tight_layout();save(fig,'p14_anatomical_transfer')

for destination in [P14.parent/'CVPR/CVPR_ARCH_GENERALIZED/PAPER/figures',P14.parent/'TMI/TMI_ARCH_GENERALIZED/figures']:
    for p in FIG.glob('*.pdf'): shutil.copy2(p,destination/p.name)
print('Built three Plan 14 vector figures')
