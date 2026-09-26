from pathlib import Path
import shutil
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1];PAPER=P.parent;OUT=P/'outputs';FIG=P/'figures';FIG.mkdir(exist_ok=True)
CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER';TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED'
ORDER=['linear','cubic','acvtt','ressrdiff','arssr','cycleinr','resunet','gan_2p5d','swinir','saint','i3net','hat','smamba_unet']
LABEL=dict(zip(ORDER,['Linear','Cubic','ACVTT','Res-SRDiff','ArSSR','CycleINR-style','ResUNet','Pix2Pix-GAN','SwinIR','SAINT-style','I3Net','HAT','SMamba-UNet']))
a=pd.read_csv(OUT/'baseline_all_verified.csv');b=pd.read_csv(OUT/'training_budget_paired.csv');dep=pd.read_csv(OUT/'all13_error_dependence_summary.csv').set_index('dataset')
def original(p):return (P/'original_snapshot'/p.relative_to(PAPER)).read_text(encoding='utf-8')
def write(p,t):p.write_text(t,encoding='utf-8')
def sub(t,old,new):
    assert old in t,old[:60]
    return t.replace(old,new)

table=r'''\begin{table*}[t]
\caption{All 13 master-table baselines at $\times4$, independently recovered from original metrics. PSNR/SSIM are higher-is-better; MAE is lower-is-better. Full-plane evaluation excludes acquired planes. IXI/fastMRI average examinations; NingXia averages eight patient folds. These values do not replace the masked common-support reliability endpoints.}
\label{tab:p15-master}\centering\small\setlength{\tabcolsep}{3.7pt}
\begin{tabular}{lrrrrrrrrr}\toprule
&\multicolumn{3}{c}{IXI (115)}&\multicolumn{3}{c}{fastMRI (24)}&\multicolumn{3}{c}{NingXia (8 folds)}\\
Method&PSNR&SSIM&MAE&PSNR&SSIM&MAE&PSNR&SSIM&MAE\\\midrule
'''
for model in ORDER:
    cells=[]
    for ds in ['IXI','fastMRI','NingXia']:
        r=a[(a.model==model)&(a.dataset==ds)&(a.scale==4)&(a.budget=='master')].iloc[0]
        cells += [f'{r.source_psnr:.2f}',f'{r.source_ssim:.3f}',f'{r.source_mae:.2f}']
    table+=LABEL[model]+' & '+' & '.join(cells)+r'\\'+'\n'
table+=r'''\bottomrule\end{tabular}
\par\smallskip\parbox{.98\textwidth}{\footnotesize Locally adapted implementations retain their recorded training budgets; the master uses extended HAT training on fastMRI. This is not an equal-compute leaderboard. Standard and longer-budget results are reported separately.}
\end{table*}
'''
for folder in [CV,TMI]:write(folder/'table_p15_master_x4.tex',table)

# All 20 pre-existing budget experiments, no selection by sign or significance.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(11,6.8),gridspec_kw={'width_ratios':[2.4,1]})
for i,row in b.iterrows():
    label=('NX' if row.dataset=='NingXia' else 'fastMRI')+' / '+LABEL[row.model]+f' x{row.scale} / '+row.budget.replace('epoch',' ep')
    color='#2166ac' if row.mae_gain_sim_low>0 else '#777777'
    axes[0].errorbar(row.mae_gain,i,xerr=[[row.mae_gain-row.mae_gain_sim_low],[row.mae_gain_sim_high-row.mae_gain]],fmt='o',color=color,ms=4,capsize=3)
axes[0].set_yticks(range(len(b)),[('NX' if r.dataset=='NingXia' else 'fastMRI')+' / '+LABEL[r.model]+f' x{r.scale} / '+r.budget.replace('epoch',' ep') for r in b.itertuples()]);axes[0].invert_yaxis()
axes[0].set_xscale('symlog',linthresh=3);axes[0].axvline(0,c='#999',ls='--',lw=.8);axes[0].set_xlabel('MAE reduction: master minus longer budget\nSymmetric-log axis; simultaneous 95% intervals over 20 comparisons')
axes[0].set_title('(a) Every recorded budget extension',loc='left',fontweight='bold')
nx=a[(a.dataset=='NingXia')&(a.model=='ressrdiff')&(a.scale==2)].set_index('budget').loc[['master','60epoch','90epoch']]
axes[1].plot([30,60,90],nx.source_mae,'o-',color='#a63603',label='Res-SRDiff')
for ep,v in zip([30,60,90],nx.source_mae):axes[1].annotate(f'{v:.1f}',(ep,v),xytext=(0,9),textcoords='offset points',ha='center')
axes[1].axhline(78.5349,c='#555',ls='--',label='Linear (master)');axes[1].axhline(70.0441,c='#2166ac',ls=':',label='HAT x2 (master)')
axes[1].set_xticks([30,60,90]);axes[1].set_ylim(40,495);axes[1].set_xlabel('Recorded epoch budget');axes[1].set_ylabel('Full-plane MAE; equal patient-fold mean');axes[1].legend(frameon=False,loc='upper right',bbox_to_anchor=(1,0.69),fontsize=8)
axes[1].set_title('(b) Diffusion failure is budget-sensitive',loc='left',fontweight='bold',fontsize=9)
fig.tight_layout();fig.savefig(FIG/'p15_training_budget.pdf',bbox_inches='tight');fig.savefig(FIG/'p15_training_budget.png',dpi=170,bbox_inches='tight');plt.close(fig)
for folder in [CV,TMI]:shutil.copy2(FIG/'p15_training_budget.pdf',folder/'figures/p15_training_budget.pdf')

supp=r'''\section{Complete Baseline Ledger and Training-Budget Sensitivity}
The experiment master table contains 13 reconstruction baselines. We recover all 39 three-cohort $\times4$ rows, all 52 fastMRI/NingXia $\times2/\times6$ rows, and all 20 recorded longer-budget rows: 111 configurations and 555 metric values. Original metric summaries agree to their reported four-decimal precision. Two overwritten SAINT summaries at fastMRI $\times2/\times6$ are recovered from all 48 preserved output volumes. No run is retrained for this audit.

The native evaluator measures every nonacquired plane on the whole image, averages planes within an examination, and then averages examinations. NingXia first averages series within a held-out patient fold, then averages all eight folds. PSNR uses each target plane's range; SSIM is the full-plane implementation. These are reference-based evaluation metrics, not deployable QA scores. Each configuration has matching case identities and generated-plane counts across its models; this count audit does not independently certify all historical preprocessing. The old masked common-support tables and this native-metric ledger remain distinct contracts. Automatic threshold-mask Dice/HD95 columns are not interpreted as anatomical segmentation.

All model names denote the local implementations, including generic SR models adapted to 2.5-D conditioning, inherited GAN, and local SAINT/CycleINR variants. The recorded master profiles include different training budgets and early stopping; no equal-compute claim is made. PAST-Net's fastMRI development trajectory remains development evidence rather than a new independent three-cohort baseline result.

\paragraph{What the full bank adds.}
Using all 13 native-metric baselines gives 78 model pairs per cohort. Median case-error rank correlations are .997 on IXI, .899 on fastMRI, and 1.000 on eight NingXia patient folds. These descriptive estimates show shared difficulty across the full bank while retaining the lower fastMRI association than in the masked analysis. They do not imply independent model pairs or extend the five-model intervention to 13 models.

\paragraph{Budget protocol and negative boundaries.}
For every recorded 60/90-epoch experiment, compare its matched standard-profile cases; use 10,000 paired bootstrap draws (seed 20260910), examinations for fastMRI and patient folds for NingXia. The primary MAE intervals simultaneously cover all 20 comparisons using the bootstrap maximum standardized deviation. All five metric changes remain in the numerical record. Fifteen MAE intervals favor longer training; five cross zero. Runs are separate training experiments, not a controlled single-checkpoint continuation, and standard values are never replaced by their best budget.

NingXia Res-SRDiff $\times2$ MAE changes from 440.61 at 30 epochs to 140.45 at 60 and 118.25 at 90, still above Linear's 78.53. A short-budget failure therefore cannot establish an intrinsic diffusion-family failure. Conversely, CycleINR $\times2$ barely changes (.000006 MAE reduction), and five simultaneous intervals remain inconclusive. The source note that fastMRI ACVTT $\times6$ worsened at 60 epochs is contradicted by its numbers: PSNR improves 19.8309 to 20.0269, and MAE 72.4367 to 70.9050; all five metric directions improve. The original note is preserved and this correction is explicit.
'''
def fulltable(ds,scale,budget='master'):
    g=a[(a.dataset==ds)&(a.scale==scale)&(a.budget==budget)].set_index('model')
    s='\\begin{table*}[t]\\centering\\small\n'+f'\\caption{{{ds} $\\times{scale}$: complete native metrics, recorded {budget} profile.}}\n'
    s+=r'\begin{tabular}{lrrrrr}\toprule Method&PSNR&SSIM&MAE&MSE&NCC\\\midrule'+'\n'
    for model in ORDER:
        if model not in g.index:continue
        r=g.loc[model];s+=LABEL[model]+' & '+' & '.join(f'{r["source_"+m]:.4f}' for m in ['psnr','ssim','mae','mse','ncc'])+r'\\'+'\n'
    return s+r'\bottomrule\end{tabular}\end{table*}'+'\n'
for ds in ['IXI','fastMRI','NingXia']:supp+=fulltable(ds,4)
for ds in ['fastMRI','NingXia']:
    for scale in [2,6]:supp+=fulltable(ds,scale)
supp+=r'''\begin{table*}[t]\centering\small
\caption{All recorded extended-budget results. Native five-metric values are kept separately from the master-profile ranking.}
\begin{tabular}{llrrrrrrr}\toprule Cohort&Method&Factor&Epochs&PSNR&SSIM&MAE&MSE&NCC\\\midrule
'''
for r in a[a.budget!='master'].itertuples():
    supp+=('NX' if r.dataset=='NingXia' else r.dataset)+' & '+LABEL[r.model]+f' & {r.scale} & '+r.budget.replace('epoch','')+' & '+' & '.join(f'{getattr(r,"source_"+m):.4f}' for m in ['psnr','ssim','mae','mse','ncc'])+r'\\'+'\n'
supp+=r'''\bottomrule\end{tabular}\end{table*}
\begin{figure*}[t]\centering\includegraphics[width=\textwidth]{p15_training_budget.pdf}
\caption{All 20 recorded budget extensions. Positive reductions favor longer training; the symmetric-log axis keeps the large diffusion changes and small effects visible. Intervals simultaneously cover the 20 primary MAE contrasts. Five cross zero. Budget sensitivity does not validate a new QA score or erase the original short-budget failure.}
\end{figure*}
\clearpage
'''
for folder in [CV,TMI]:write(folder/'p15_baseline_supplement.tex',supp)
standalone=r'''\documentclass[10pt,twocolumn]{article}
\usepackage[a4paper,margin=0.7in]{geometry}
\usepackage{graphicx,booktabs,amsmath}
\graphicspath{{figures/}}
\title{Complete Baseline Evidence: Supplement to MRI Interpolation Quality Assessment}
\author{}\date{}
\begin{document}\maketitle
\input{p15_baseline_supplement.tex}
\end{document}
'''
write(TMI/'baseline_supplement.tex',standalone)

t=original(TMI/'main.tex');start=t.index('\\subsection{Broad Reconstruction Context}');end=t.index('\\subsection{Generalization Across Interpolation Paradigms}',start)
replacement=r'''\subsection{Complete Baseline Comparison and Budget Sensitivity}
Table~\ref{tab:p15-master} restores all 13 methods on all three $\times4$ cohorts: classical, CNN, GAN, Transformer, INR, Mamba, ACVTT, and diffusion-refinement baselines. We independently reproduce every original PSNR/SSIM/MAE/MSE/NCC entry. I3Net leads all five metrics on IXI/fastMRI, whereas SwinIR leads four on NingXia and HAT leads NCC. The complete supplement retains 111 configurations: 39 at $\times4$, 52 at $\times2/\times6$, and 20 longer-budget results. Native full-plane metrics and eight-fold NingXia averaging differ from the masked common-support QA contract and are never interchanged.

\input{table_p15_master_x4.tex}

All 13 models give median case-error rank correlations .997/.899/1.000 on IXI/fastMRI/NingXia (78 pairs each; descriptive). The historical masked seven-stratum audit remains separate: median correlations .938--.991, including a low NingXia diffusion tail. Full-bank evidence therefore supports shared difficulty but not uniformly independent errors.

Crucially, training budget changes the failure interpretation. Across all 20 recorded extensions, 15 paired MAE intervals favor longer training under simultaneous inference; five cross zero. NingXia Res-SRDiff $\times2$ MAE improves 440.61$\rightarrow$140.45$\rightarrow$118.25 at 30/60/90 epochs, still worse than Linear (78.53). The corresponding 60/90-epoch reductions are 300.16 [153.17,447.14] and 322.36 [166.01,478.71]. These separate runs diagnose convergence sensitivity; they do not replace the standard-budget failure or establish an intrinsic diffusion limitation. Profiles retain unequal recorded budgets, including extended fastMRI HAT training. Complete five-metric, multi-scale, and budget tables accompany the baseline supplement.

'''
t=t[:start]+replacement+t[end:]
t=t.replace('Five neural architectures on both brain cohorts retain positive', 'A complete 13-baseline, three-cohort benchmark contextualizes the study. Five neural architectures on both brain cohorts retain positive')
write(TMI/'main.tex',t)
t=original(CV/'main.tex')
old='The supplement reports the recovered reconstruction-fidelity matrix in a single dataset-grouped table for fastMRI, IXI, and NingXia across the available $\\times2/\\times4/\\times6$ factors. It is included to document estimator context and coverage gaps, not to turn the mechanism study into a reconstruction leaderboard.'
new=r'''Table~\ref{tab:p15-master} integrates all 13 master-table baselines on all three $\times4$ cohorts; the supplement retains all five metrics over 111 configurations, including 52 multi-scale and 20 extended-budget rows. Native full-plane metrics remain distinct from masked QA endpoints. Across all 13 models, median case-error rank correlation is .997/.899/1.000 on IXI/fastMRI/NingXia (78 pairs each). Budget matters: NingXia Res-SRDiff $\times2$ MAE falls from 440.61 to 140.45/118.25 at 60/90 epochs, yet remains above Linear's 78.53. Fifteen of 20 MAE budget comparisons favor longer training under simultaneous inference; five are inconclusive. Thus the short-budget negative run does not establish an intrinsic family failure.

\input{table_p15_master_x4.tex}'''
t=sub(t,old,new)
# Let discussion text fill space below outstanding wide result floats.
t=sub(t,'\\FloatBarrier\n\n\\flushbottom','\\flushbottom')
write(CV/'main.tex',t)
s=original(CV/'supplement.tex');s=sub(s,'\\end{document}','\\clearpage\n\\input{p15_baseline_supplement.tex}\n\\end{document}');write(CV/'supplement.tex',s)
for name in ['build.py','render.py']:
    src=(PAPER/'PLAN14_SCIENTIFIC_STRENGTHENING/scripts'/name).read_text(encoding='utf-8')
    if name=='build.py':src=src.replace("JOBS=[", "JOBS=[('tmi_baselines',PAPER/'TMI/TMI_ARCH_GENERALIZED','baseline_supplement',False),")
    else:src=src.replace("jobs={", "jobs={'tmi_baselines':PAPER/'TMI/TMI_ARCH_GENERALIZED/baseline_supplement.pdf',")
    write(P/'scripts'/name,src)
print('All baseline tables and manuscripts revised; 20 budget contrasts plotted.')
