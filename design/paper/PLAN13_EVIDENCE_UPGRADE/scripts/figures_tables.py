from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

P13=Path(__file__).resolve().parents[1]; PAPER=P13.parent; OUT=P13/'outputs'; FIG=P13/'figures'; FIG.mkdir(exist_ok=True)
CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'; TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED'
MODELS=['hat','swinir','i3net','saint','cycleinr']; LABELS=['HAT','SwinIR','I3Net','SAINT-style','CycleINR-style']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
colors={'fastmri':'#2166AC','ixi':'#B35806'}
a=pd.read_csv(OUT/'architecture_sensitivity.csv')
hist_f=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs/p9_architecture_forest.csv').set_index('model')
hist_i=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_ixi_clean_model_summary_full.csv').set_index('model')
fig,axs=plt.subplots(1,2,figsize=(10.3,3.35),gridspec_kw={'width_ratios':[1,1.2]})
for ds,offset in [('fastmri',-.15),('ixi',.15)]:
    sel=a[a.dataset.eq(ds)&a.within_case.eq('mean' if ds=='fastmri' else 'median')&a.across_cases.eq('mean' if ds=='fastmri' else 'median')].set_index('model').loc[MODELS]
    y=np.arange(5)+offset
    axs[0].errorbar(100*sel.gain,y,xerr=100*np.array([sel.gain-sel.simultaneous_low,sel.simultaneous_high-sel.gain]),fmt='o',ms=4,capsize=3,color=colors[ds],label='fastMRI (24)' if ds=='fastmri' else 'IXI (115)')
    rank=a[a.dataset.eq(ds)&a.within_case.eq('median')&a.across_cases.eq('median')].set_index('model').loc[MODELS]
    h=hist_f.loc[MODELS] if ds=='fastmri' else hist_i.loc[MODELS]
    lo=h['ranking_ci_low' if ds=='fastmri' else 'ranking_delta_ci_low'].to_numpy()
    hi=h['ranking_ci_high' if ds=='fastmri' else 'ranking_delta_ci_high'].to_numpy()
    axs[1].hlines(y,rank.ranking_sim_low,rank.ranking_sim_high,color=colors[ds],lw=1,alpha=.8)
    axs[1].hlines(y,lo,hi,color=colors[ds],lw=4,alpha=.65)
    axs[1].scatter(rank.ranking_delta,y,s=17,color=colors[ds],zorder=3)
for ax in axs:
    ax.axvline(0,color='#777777',lw=.8,ls='--'); ax.set_yticks(range(5),LABELS); ax.invert_yaxis(); ax.grid(axis='x',alpha=.15)
axs[0].set_title('(a) Local observable gain',loc='left',fontweight='bold'); axs[0].set_xlabel('Disjoint minus shared (percentage points)')
axs[1].set_title('(b) Ranking: uncertainty across five models',loc='left',fontweight='bold'); axs[1].set_xlabel('Disjoint minus shared Spearman correlation')
fig.legend(handles=[Line2D([0],[0],color=colors['fastmri'],marker='o',lw=1,label='fastMRI (24)'),Line2D([0],[0],color=colors['ixi'],marker='o',lw=1,label='IXI (115)'),Line2D([0],[0],color='#555555',lw=4,label='Ranking: historical pointwise 95%'),Line2D([0],[0],color='#555555',lw=1,label='Exploratory simultaneous 95%')],loc='lower center',bbox_to_anchor=(.5,-.055),ncol=4,frameon=False,fontsize=7.5)
fig.tight_layout(rect=[0,.04,1,1]); fig.savefig(FIG/'p13_architecture_robustness.pdf',bbox_inches='tight'); fig.savefig(FIG/'p13_architecture_robustness.png',dpi=180,bbox_inches='tight'); plt.close(fig)

b=pd.read_csv(OUT/'benefit_coupling.csv'); q=b[b.score.eq('anchor_cv')]; mods=sorted(q.model.unique())
fig,axs=plt.subplots(1,3,figsize=(12.2,4.05),gridspec_kw={'width_ratios':[1,1,1.1]})
for ax,ds,title in zip(axs[:2],['fastmri','ningxia'],['(a) fastMRI: 24 examinations','(b) NingXia: 8 patient clusters']):
    g=q[q.dataset.eq(ds)].set_index('model').loc[mods]
    y=np.arange(len(g)); ax.hlines(y,g.raw_rho,g.partial_rho_given_x4,color='#BBBBBB',lw=1)
    ax.scatter(g.raw_rho,y,c='#2166AC',s=15,label='Raw association',zorder=3)
    ax.errorbar(g.partial_rho_given_x4,y,xerr=np.array([g.partial_rho_given_x4-g.partial_ci_low,g.partial_ci_high-g.partial_rho_given_x4]),fmt='s',ms=3,color='#B35806',lw=.8,label='Conditional on current error')
    ax.set_yticks(y,[m.replace('ressrdiff','Res-SRDiff').replace('smamba_unet','SMamba') for m in mods]); ax.invert_yaxis(); ax.set_xlim(-1,1); ax.axvline(0,color='#777',ls='--',lw=.8); ax.set_title(title,fontsize=10,loc='left',fontweight='bold'); ax.set_xlabel('Anchor-CV / densification benefit correlation')
fig.legend(*axs[0].get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.32,-.025),ncol=2,fontsize=8,frameon=False)
g=pd.read_csv(OUT/'ixi_i3net_benefit_budgets.csv')
for score,c,style,label in [('anchor_cv','#2166AC','-','Anchor-CV, raw'),('adjacent_mae','#B35806','-','Adjacent MAE, raw'),('anchor_cv_acquired_normalized','#2166AC','--','Anchor-CV, normalized'),('adjacent_mae_acquired_normalized','#B35806','--','Adjacent MAE, normalized')]:
    z=g[g.score.eq(score)]; axs[2].plot(z.budget*100,z.oracle_normalized_gain,style,color=c,marker='o',ms=3,label=label)
axs[2].axhline(0,color='#777777',lw=.8); axs[2].set_ylim(-.4,1); axs[2].set_title('(c) IXI I3Net: scale sensitivity',loc='left',fontweight='bold',fontsize=10); axs[2].set_xlabel('Selected examinations (%)'); axs[2].set_ylabel('Gain above random / oracle gain'); axs[2].legend(frameon=False,fontsize=7.5,loc='center right'); axs[2].grid(alpha=.15)
fig.tight_layout(rect=[0,.07,1,1]); fig.savefig(FIG/'p13_benefit_boundaries.pdf',bbox_inches='tight'); fig.savefig(FIG/'p13_benefit_boundaries.png',dpi=180,bbox_inches='tight'); plt.close(fig)
for dest in [CV/'figures',TMI/'figures']:
    for src in FIG.glob('*.pdf'): shutil.copy2(src,dest/src.name)

# Replace the inherited universal-sounding headline with a scoped mechanism diagram.
from matplotlib.patches import FancyBboxPatch
fig,ax=plt.subplots(figsize=(10,2.0)); ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.text(.5,.93,'A controlled route to error cancellation',ha='center',va='center',fontsize=12,fontweight='bold')
boxes=[('Physical anchor reuse','Intervened measurement context'),('Similar local responses','Measured finite-response alignment'),('Aligned target errors','Retrospective error geometry'),('Small disagreement','Common error can remain hidden')]
for j,(title,sub) in enumerate(boxes):
    x=.015+j*.25
    ax.add_patch(FancyBboxPatch((x,.36),.22,.4,boxstyle='round,pad=0.008',facecolor=['#EAF2F8','#F4EDF7','#FFF3DF','#EAF4E8'][j],edgecolor='#5B6670',lw=.8))
    ax.text(x+.11,.60,title,ha='center',fontsize=9,fontweight='bold')
    ax.text(x+.11,.45,sub,ha='center',fontsize=6.8)
    if j<3: ax.annotate('',xy=(x+.245,.56),xytext=(x+.222,.56),arrowprops={'arrowstyle':'->','color':'#5B6670'})
ax.text(.5,.15,r'$f_a-f_b=e_a-e_b$: a shared error component cancels; the intervention tests when errors align.',ha='center',fontsize=9)
fig.tight_layout(pad=.2); fig.savefig(FIG/'p13_mechanism.pdf',bbox_inches='tight'); fig.savefig(FIG/'p13_mechanism.png',dpi=180,bbox_inches='tight'); plt.close(fig)
shutil.copy2(FIG/'p13_mechanism.pdf',CV/'figures/fig1_mechanism.pdf')

# Compact full-model MAE matrix retains every model/factor and unfavorable run.
data=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs/p9_three_cohort_reconstruction_benchmark.csv')
methods=data.method.drop_duplicates().tolist()
lines=[r'\begin{table*}[t]',r'\caption{Recovered reconstruction context: mean masked MAE on each factor\textquotesingle s common generated-plane support. All methods and adverse outcomes are retained. Cohort intensity scales differ; values are not pooled. The later IXI I3Net common-odd-plane analysis has a different support and is reported separately.}',r'\label{tab:arch-benchmark}\centering',r'\small',r'\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{lrrrrrrrrr}',r'\toprule',r'&\multicolumn{3}{c}{fastMRI (24)}&\multicolumn{3}{c}{IXI (115)}&\multicolumn{3}{c}{NingXia (22 series / 8 patients)}\\',r'Method&$\times2$&$\times4$&$\times6$&$\times2$&$\times4$&$\times6$&$\times2$&$\times4$&$\times6$\\',r'\midrule']
for method in methods:
    vals=[]
    for ds in ['fastmri','ixi','ningxia']:
        for f in [2,4,6]:
            v=data.loc[data.method.eq(method)&data.factor.eq(f),ds+'_mae'].iloc[0]
            vals.append('---' if pd.isna(v) else f'{v:.2f}')
    label=method+'-style' if method in ['SAINT','CycleINR'] else method
    lines.append(label+' & '+' & '.join(vals)+r' \\')
lines.extend([r'\bottomrule',r'\end{tabular}',r'\par\smallskip\parbox{\textwidth}{\footnotesize ``---'' denotes unavailable or non-auditable cells, not zero. Full PSNR/SSIM/NCC and MAE values remain in the machine-readable reconstruction record. This table describes estimator context and does not establish a reconstruction contribution.}',r'\end{table*}'])
tex='\n'.join(lines).replace(r"factor\textquotesingle s","factor's")+'\n'
(TMI/'table_full_reconstruction_benchmark.tex').write_text(tex,encoding='utf-8')
# CVPR supplement keeps complete metrics, now split into legible per-cohort tables.
lines=[]
for ds,title in [('fastmri','fastMRI'),('ixi','IXI'),('ningxia','NingXia')]:
    lines.extend([r'\begin{table*}[t]',r'\caption{'+title+r' recovered reconstruction context. Four metrics at every available factor; ``---'' denotes unavailable audited cells.}',r'\label{tab:arch-benchmark'+('' if ds=='fastmri' else '-'+ds)+r'}\centering\scriptsize',r'\setlength{\tabcolsep}{3pt}',r'\begin{tabular}{lrrrrrrrrrrrr}',r'\toprule',r'&\multicolumn{4}{c}{$\times2$}&\multicolumn{4}{c}{$\times4$}&\multicolumn{4}{c}{$\times6$}\\',r'Method&MAE&PSNR&SSIM&NCC&MAE&PSNR&SSIM&NCC&MAE&PSNR&SSIM&NCC\\',r'\midrule'])
    for method in methods:
        vals=[]
        for f in [2,4,6]:
            row=data[data.method.eq(method)&data.factor.eq(f)].iloc[0]
            for metric in ['mae','psnr','ssim','ncc']:
                v=row[ds+'_'+metric]; vals.append('---' if pd.isna(v) else (f'{v:.2f}' if metric in ['mae','psnr'] else f'{v:.4f}'))
        lines.append(method+' & '+' & '.join(vals)+r' \\')
    lines.extend([r'\bottomrule',r'\end{tabular}',r'\end{table*}'])
(CV/'table_full_reconstruction_benchmark.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Figures and reconstruction tables built')
