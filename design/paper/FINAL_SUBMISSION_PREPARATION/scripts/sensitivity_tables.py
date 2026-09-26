from pathlib import Path
import pandas as pd,numpy as np
P=Path(__file__).resolve().parents[1];CV=P/'revised_manuscript'
s=pd.read_csv(P/'CROSS_ARCH_SUPPORT_SENSITIVITY.csv');g=pd.read_csv(P/'CROSS_ARCH_GEOMETRY_SENSITIVITY.csv');f=pd.read_csv(P/'CROSS_ARCH_FAMILY_ROBUSTNESS.csv')
text=r'''\section{Post-hoc Submission Sensitivities}
\label{sec:submission-sensitivity}
The accepted primary evidence and its raw arrays were hashed before these analyses. These are post-hoc sensitivities, not prespecified primary tests. All original targets and frozen predictions are retained; no network is rerun, no new mask threshold is searched and no new score is formed. Each examination has equal weight after target averaging. We use 5,000 common examination-bootstrap draws for all 20 ordered pairs within each cohort. Simultaneous intervals apply separately to each cohort/support/geometry endpoint, not jointly to the entire sensitivity collection. Model pairs share examinations and architectures, and are not independent replications.

\subsection{Support contracts}
The original target 1\%-foreground mask, the existing union of the nearest two acquired phase-0 foreground masks, and all common finite image pixels are the only contracts. Each acquired anchor is thresholded at 1\% of its own maximum absolute intensity. Support is identical for all pairs and both conditions at the same target; the acquired mask never accesses the target. Shared $O$, disjoint $O$, their difference and pixel counts for every pair are retained in the accompanying numerical files. The target remains necessary for retrospective error evaluation under every contract.

All 20 effects and all 20 simultaneous intervals per cohort remain positive under each support. The maximum pair-effect rank movement is one on fastMRI and zero on IXI; minimum Spearman agreement with the original pair ordering is .997. This rules against dependence on the tested target-derived support, not against all conceivable support effects or against shared measurement/geometry confounding.
'''
def value(r):
 if pd.isna(r.delta_O):return 'NA'
 return f'{100*r.delta_O:.2f} [{100*r.simultaneous_low:.2f},{100*r.simultaneous_high:.2f}]'
def table(df,ds,analyses,labels,caption,label):
 q=df[(df.dataset==ds)&(df.pair!='equal_weight_family')];pairs=sorted(q.pair.unique());lines=[]
 for pair in pairs:
  cols=[value(q[(q.pair==pair)&(q.analysis==a)].iloc[0]) for a in analyses]
  lines.append(pair.replace('__',r'$\to$').replace('cycleinr','CycleINR').replace('swinir','SwinIR').replace('saint','SAINT').replace('i3net','I3Net').replace('hat','HAT')+' & '+' & '.join(cols)+r' \\')
 return r'\begin{table*}[t]\centering\scriptsize'+'\n'+r'\caption{'+caption+r'}\label{'+label+r'}\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{tabular}{l'+'r'*len(analyses)+r'}\toprule'+'\n'+'Ordered pair & '+' & '.join(labels)+r'\\\midrule'+'\n'+'\n'.join(lines)+r'\bottomrule\end{tabular}\end{table*}'+'\n'
for ds in ['fastmri','ixi']:text+=table(s,ds,['target_1pct','acquired_union','full_common_valid'],['Target mask','Acquired union','Full image'],ds+r': all 20 post-hoc support contrasts. $\Delta O$ [simultaneous 95\% CI], percentage points.','tab:support-'+ds)
text+=r'''\subsection{Residue, mirror and nearest-distance checks}
Targets are divided by their physical index modulo four. Within each examination we average each residue class, then weight residues 1 and 3 equally. The mirror difference is the residue-1 effect minus the residue-3 effect, analogous to the historical reflection-class analysis but retaining this experiment's mean estimand. It is not a new reflected-image prediction or an identity-only counterfactual. Nearest-distance matching requires actual bracketing distances $\{1,3\}$ in both phases. All originally selected targets satisfy this gate, so the matched balanced estimate equals the residue-balanced estimate.

The balanced local conclusion survives in both cohorts, as does each residue separately. However, mirror intervals exclude zero for eight fastMRI pairs (two positive, six negative) and six IXI pairs (two positive, four negative). These are retained orientation warnings; the remaining intervals do not prove equivalence. The stricter complete four-anchor contract requires two actual acquired anchors on each side in both phases and both residues within an examination. All IXI selected targets meet it. For fastMRI only target $z=7$ meets the complete-context requirement, leaving no residue-1 target: every such balanced pair estimate is NA. Boundary anchors are never duplicated or synthesized.
'''
for ds in ['fastmri','ixi']:text+=table(g,ds,['residue_1','residue_3','residue_balanced','mirror_residue1_minus_residue3'],['Residue 1','Residue 3','Balanced','Mirror difference'],ds+r': all ordered-pair geometry contrasts, percentage points, with simultaneous 95\% intervals per column. Mirror difference is an orientation diagnostic, not an observability-gain endpoint.','tab:geometry-'+ds)
text+=r'''\subsection{Joint family robustness}
The complete matrices remain primary. The following descriptive summaries resample whole examinations jointly across all pair columns; they do not resample pairs as independent units. Pair-family mean/median is recomputed inside each bootstrap sample. Excluding one architecture removes every pair involving it in either direction, leaving twelve. All family intervals remain positive, including after removing each individual architecture. These results test dominance within the observed model family, not generalization to arbitrary architectures.
\begin{table*}[t]\centering\scriptsize
\caption{Joint examination-bootstrap family summaries (pp). Intervals are descriptive percentile 95\% intervals, not simultaneous across exclusions.}
\label{tab:family-robustness}\setlength{\tabcolsep}{4pt}
\begin{tabular}{llrrr}\toprule Cohort & Excluded architecture & Pairs & Mean [CI] & Median [CI]\\\midrule
'''
for (ds,excluded),q in f.groupby(['dataset','excluded_architecture'],sort=False):
 a=q[q.statistic=='mean'].iloc[0];b=q[q.statistic=='median'].iloc[0];text+=f'{ds} & {excluded} & {a.pairs} & {100*a.delta_O:.2f} [{100*a.low:.2f},{100*a.high:.2f}] & {100*b.delta_O:.2f} [{100*b.low:.2f},{100*b.high:.2f}] '+r'\\'+'\n'
text+=r'\bottomrule\end{tabular}\end{table*}'
(CV/'submission_sensitivity.tex').write_text(text,encoding='utf-8')
print('Full 20-pair support/geometry tables and dependent family summaries written')
