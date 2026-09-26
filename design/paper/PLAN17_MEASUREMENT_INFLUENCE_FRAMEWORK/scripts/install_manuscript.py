from common import *
import re,shutil
CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'
SNAP=P/'original_snapshot'/CV.relative_to(ROOT)
def write(p,s):p.write_text(s,encoding='utf-8')
def old_table(label):
 t=(SNAP/'main.tex').read_text(encoding='utf-8');i=t.index('\\label{'+label+'}');a=t.rfind('\\begin{table*}',0,i);b=t.index('\\end{table*}',i)+len('\\end{table*}')
 return t[a:b]
t=old_table('tab:controlled')
t=re.sub(r'\\caption\{.*?\}\n\\label',r'\\caption{Original clean shared/disjoint comparison. Ranking against fixed phase-0 error pools plane/model observations; intervals resample examinations/patients. Stable-wrong thresholds are test-relative, fixed from the disjoint condition.}\n\\label',t,count=1)
write(CV/'p17_control_table.tex',t)
ns=pd.read_csv(OUT/'nonself_influence_summary.csv');fx=pd.read_csv(PAPER/'CVPR/archive/CVPR_UPGRADE/outputs/plan6_fixed_overlap_ladder.csv').query("endpoint=='error_cosine'").set_index(['dataset','model'])
lines=[r'\begin{table*}[t]\centering\small',r'\caption{Non-self broad grid and fixed-count influence. Broad-grid advantage uses six-stratum simultaneous 95\% intervals; fixed-count estimates retain historical pointwise clustered 95\% intervals. Both analyses preserve every cohort/model.}\label{tab:neural}',r'\begin{tabular}{llrrrr}\toprule',r'Cohort & Model & $\rho_{count}$ & $\rho_I$ & Non-self advantage [CI] & Fixed-one partial $\rho$ [CI]\\\midrule']
for r in ns.itertuples():
 q=fx.loc[(r.dataset,r.model)];lines.append(f'{r.dataset} & {r.model.upper()} & {r.rho_count:.3f} & {r.rho_influence:.3f} & {r.advantage:.3f} [{r.simultaneous_low:.3f},{r.simultaneous_high:.3f}] & {q.partial_rho_neural_influence:.3f} [{q.cluster_ci_low:.3f},{q.cluster_ci_high:.3f}]'+r'\\')
lines.append(r'\bottomrule\end{tabular}\end{table*}');write(CV/'p17_influence_table.tex','\n'.join(lines))
shutil.copy2(P/'main_revised.tex',CV/'main.tex');shutil.copy2(P/'p17_additional_material.tex',CV/'p17_additional_material.tex')

# Apply provenance terminology corrections to preserved supporting sources, while
# retaining every numeric table and previous negative analysis.
source_names=['supplement.tex','p13_additional_analysis.tex','p14_additional_analysis.tex','p15_baseline_supplement.tex']
for name in source_names:
 t=(SNAP/name).read_text(encoding='utf-8')
 t=t.replace('prospectively frozen','documented').replace('prespecified','documented').replace('rule-frozen','fixed-rule retrospective')
 t=t.replace('Independent IXI Five-Architecture Replication','Distinct-Cohort IXI Five-Architecture Replication')
 t=t.replace('all 115 held-out IXI examinations','all 115 historically reused IXI reconstruction-test examinations')
 t=t.replace('Definitions and Frozen Protocol','Definitions and Documented Protocol')
 t=t.replace('The architecture hypothesis and falsification conditions were frozen before new P0 results.','The architecture hypothesis and falsification conditions are recorded in local documents; their pre-outcome timing is not independently established.')
 t=t.replace('was rejected before cohort inference because it changed physical geometry and exposed direction non-equivariance','was rejected after its one-case outcome exposed order non-equivariance; documents report that this preceded full-cohort inference')
 t=t.replace('The response-cosine statistic averages identical-field response cosines across shared anchors and seeds.','The influence numerator sums identical-field response inner products over shared anchors and seeds, while its denominator uses the geometric mean of all-anchor response energies on the two sides, including unshared anchors.')
 t=t.replace('The following table unifies the reconstruction context for fastMRI, IXI, and NingXia. It deliberately preserves the recovered audit\'s missing cells: fastMRI and out-of-fold NingXia have broad $\\times2/\\times4/\\times6$ coverage, while IXI has a complete auditable recovery only at $\\times4$ for fewer methods. The table is not used to select a winner and does not identify any method as ours.', 'The following historical table preserves masked/common-support recovery, including its missing cells. Those missing cells do not mean the native baseline runs are absent: the complete native 13-model, three-cohort comparison and all 111 configurations are retained elsewhere in this supplement. The two supports are not interchangeable and no method is labeled ours.')
 t=t.replace('clean causal contrast','cleaner dependence contrast')
 if name=='supplement.tex':
  pos=t.index('\\section{Scope and Evidence Contract}');t=t[:pos]+'\\input{p17_additional_material.tex}\n\n'+t[pos:]
 write(CV/name,t)

scores=pd.read_csv(OUT/'score_evaluation.csv');names={'guard':'Guard','disagreement_norm':'Disagreement','anchor_cv_norm':'Anchor-CV','adjacent_mae_norm':'Adjacent MAE','adjacent_rmse_norm':'Adjacent RMSE','acquired_range':'Acquired range','spacing':'Header spacing'}
def fmt(x):return 'NA' if pd.isna(x) else f'{x:.3f}'
lines=[r'\begin{table*}[t]\centering\small',r'\caption{All candidates and comparators in the new guard audit. HS: HAT/SwinIR; IC: I3Net/CycleINR. Internal fastMRI evaluation has zero positives, so AP is undefined. IXI has two positives per pair; its AP point estimates do not establish superiority. $\rho$ ranks normalized paired error.}',r'\begin{tabular}{llrrrr}\toprule',r'Cohort & Score & HS AP & IC AP & HS $\rho$ & IC $\rho$\\\midrule']
for ds in ['fastmri','ixi']:
 for score in names:
  g=scores[(scores.dataset==ds)&(scores.score==score)].set_index('pair');h=g.loc['hat_swinir'];i=g.loc['i3net_cycleinr']
  lines.append(f'{ds} & {names[score]} & {fmt(h.auprc)} & {fmt(i.auprc)} & {fmt(h.error_rho)} & {fmt(i.error_rho)}'+r'\\')
lines += [r'\bottomrule\end{tabular}\end{table*}'];write(CV/'p17_score_table.tex','\n'.join(lines))
df=pd.read_csv(OUT/'practical_proxy_summary.csv').fillna('')
lines=[r'\begin{table*}[t]\centering\small',r'\caption{IXI two-member analytical ensemble, 115 examinations. Contrasts are disjoint minus shared, with simultaneous intervals over the two directions for each displayed endpoint. ``Fixed'' uses the unchanged reference predictor; ``paired'' uses both predictions.}',r'\begin{tabular}{llrr}\toprule',r'Proxy / metric & Error endpoint & L$_0$ reference [95\% CI] & C$_0$ reference [95\% CI]\\\midrule']
for metric,ep in [('local_observable_gain',''),('disagreement_ranking_delta','mae_a'),('disagreement_ranking_delta','error'),('variance_ranking_delta','mae_a'),('variance_ranking_delta','error')]:
 g=df[(df.metric==metric)&(df.endpoint==ep)].set_index('pair');cells=[]
 for pair in ['LC','CL']:
  r=g.loc[pair];cells.append(f'{r.point:.4f} [{r.simultaneous_low:.4f},{r.simultaneous_high:.4f}]')
 name={'local_observable_gain':'Observable gain','disagreement_ranking_delta':'MAE disagreement','variance_ranking_delta':'Population variance'}[metric];endpoint={'':'---','mae_a':'Fixed','error':'Paired'}[ep]
 lines.append(name+' & '+endpoint+' & '+' & '.join(cells)+r'\\')
lines += [r'\bottomrule\end{tabular}\end{table*}'];write(CV/'p17_proxy_table.tex','\n'.join(lines))

t=(PAPER/'PLAN16_RESEARCH_DIAGRAMS/scripts/build.py').read_text(encoding='utf-8');t=t.replace("{'cvpr','tmi'}","{'cvpr','supplement'}")
write(P/'scripts/build.py',t)
print('CVPR main, supplement and generated tables installed; TMI untouched.')
