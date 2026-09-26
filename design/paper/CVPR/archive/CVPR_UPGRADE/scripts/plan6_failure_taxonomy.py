"""P6-E09: frozen Anchor-CV/output-disagreement failure taxonomy and MRI panels."""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs';FIG=UP/'PAPER'/'figures';FIG.mkdir(parents=True,exist_ok=True)
acv=pd.read_csv(OUT/'plan6_anchor_cv_explanation_per_case.csv')
pc=pd.read_csv(OUT/'orthogonal_two_component_per_case.csv').rename(columns={'score':'pc_score','error':'pc_error'})
x=acv.merge(pc[['dataset','case','model','pc_score']],on=['dataset','case','model'])
for c in ['anchor_cv','pc_score','x4_error']:
    x[c+'_rank']=x.groupby(['dataset','model'])[c].rank(pct=True)
x['anchor_abs_rank_error']=(x.anchor_cv_rank-x.x4_error_rank).abs();x['pc_abs_rank_error']=(x.pc_score_rank-x.x4_error_rank).abs()
x['taxonomy']='concordant_midrange'
x.loc[(x.anchor_cv_rank>=.75)&(x.x4_error_rank<=.25),'taxonomy']='anchor_false_positive'
x.loc[(x.anchor_cv_rank<=.25)&(x.x4_error_rank>=.75),'taxonomy']='anchor_false_negative'
x.loc[(x.pc_abs_rank_error+.20<x.anchor_abs_rank_error),'taxonomy']='pc_more_accurate'
x.loc[(x.anchor_abs_rank_error+.20<x.pc_abs_rank_error),'taxonomy']='anchor_more_accurate'

features=['adjacent_mae','adjacent_gradient_mae','adjacent_lowfreq_mae','adjacent_highfreq_mae','first_difference_variability','robust_intensity_range','spacing_mm','local_rho']
summary=x.groupby(['dataset','model','taxonomy'],as_index=False).agg(n=('case','size'),anchor_error=('anchor_abs_rank_error','median'),pc_error=('pc_abs_rank_error','median'),**{f:(f,'median') for f in features})
summary.to_csv(OUT/'plan6_failure_taxonomy_summary.csv',index=False);x.to_csv(OUT/'plan6_failure_taxonomy_per_case.csv',index=False)

# Select two discordant exemplars per dataset from HAT, favoring the largest rank-margin.
x['anchor_advantage']=x.pc_abs_rank_error-x.anchor_abs_rank_error
chosen=[]
for ds,g in x[x.model=='hat'].groupby('dataset'):
    chosen.append(g.loc[g.anchor_advantage.idxmax()])
    chosen.append(g.loc[g.anchor_advantage.idxmin()])
chosen=pd.DataFrame(chosen).drop_duplicates(['dataset','case'])
manifest=pd.read_csv(UP/'DATA_MANIFEST.csv');manifest=manifest[(manifest.factor==4)&(manifest.architecture=='hat')][['dataset','case_id','ground_truth_file','source_file']].rename(columns={'case_id':'case'})
chosen=chosen.merge(manifest,on=['dataset','case'],how='left');chosen.to_csv(OUT/'plan6_failure_taxonomy_exemplars.csv',index=False)

fig,axs=plt.subplots(len(chosen),3,figsize=(7.4,2.0*len(chosen)))
for row,(_,r) in enumerate(chosen.iterrows()):
    gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);pred=nib.load(r.source_file).get_fdata(dtype=np.float32)
    candidates=[z for z in range(1,min(gt.shape[2],pred.shape[2])-1) if z%4!=0]
    scores=[]
    for z in candidates:
        y=gt[:,:,z];p=pred[:,:,z];mask=np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6);scores.append(np.abs(y-p)[mask].mean() if mask.any() else -1)
    z=candidates[int(np.argmax(scores))];y=gt[:,:,z];p=pred[:,:,z];e=np.abs(y-p);v0,v1=np.percentile(y[np.isfinite(y)],[1,99]);emax=np.percentile(e[np.isfinite(e)],99)
    axs[row,0].imshow(np.rot90(y),cmap='gray',vmin=v0,vmax=v1);axs[row,1].imshow(np.rot90(p),cmap='gray',vmin=v0,vmax=v1);axs[row,2].imshow(np.rot90(e),cmap='magma',vmin=0,vmax=emax)
    axs[row,0].set_ylabel(f"{r.dataset}\nACV err {r.anchor_abs_rank_error:.2f}\nPC err {r.pc_abs_rank_error:.2f}",fontsize=7)
    for ax in axs[row]:ax.set_xticks([]);ax.set_yticks([])
for ax,t in zip(axs[0],['Ground truth','HAT x4 reconstruction','Absolute error']):ax.set_title(t,fontsize=9)
fig.suptitle('Frozen case-level scores are complementary but neither localizes the failure',fontsize=10,y=.995);fig.tight_layout();fig.savefig(FIG/'plan6_failure_exemplars.pdf',bbox_inches='tight');fig.savefig(FIG/'plan6_failure_exemplars.png',dpi=300,bbox_inches='tight');plt.close(fig)

counts=x.groupby(['dataset','taxonomy']).size().unstack(fill_value=0).to_dict(orient='index')
payload={'experiment':'P6-E09','status':'COMPLETE','coverage':['fastmri','ixi','ningxia'],'models':['hat','swinir'],
 'rank_failure_rule':'within-dataset/model; score rank differs from x4 error rank; complementary winner requires >=0.20 absolute-rank-error margin',
 'counts':counts,'caution':'categories characterize case-level ranking discordance, not diagnostic or prospective acquisition failures',
 'outputs':['plan6_failure_taxonomy_per_case.csv','plan6_failure_taxonomy_summary.csv','plan6_failure_taxonomy_exemplars.csv'],'figure':'../PAPER/figures/plan6_failure_exemplars.pdf'}
(OUT/'plan6_failure_taxonomy.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(summary.to_string(index=False));print(json.dumps(payload,indent=2))
