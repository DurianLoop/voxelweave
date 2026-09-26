from pathlib import Path
import json,shutil,re
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';S=P.parent/'FINAL_SUBMISSION_PREPARATION';CV=P/'revised_manuscript';ORIG=P/'original_snapshot/manuscript'
LABEL={'linear':'Linear','cubic':'Cubic','acvtt':'ACVTT','ressrdiff':'Res-SRDiff','arssr':'ArSSR','resunet':'ResUNet','gan_2p5d':'Pix2Pix-GAN','smamba_unet':'SMamba-UNet','hat':'HAT','swinir':'SwinIR','saint':'SAINT-style','i3net':'I3Net','cycleinr':'CycleINR-style'}
def write(name,text):(CV/name).write_text(text,encoding='utf-8')
def main():
 d=pd.read_csv(P/'FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.csv');e=pd.read_csv(P/'MODEL_EVIDENCE_ELIGIBILITY.csv');breadth=pd.read_csv(P/'EXPANDED_PHENOMENON_BREADTH.csv');cov=pd.read_csv(P/'outputs/saint_covariance_summary.csv')
 assert len(d)==10 and len(e)==13 and len(breadth)==48
 t=(ORIG/'main.tex').read_text(encoding='utf-8')
 replacements={
 'Acquired-only HAT/SwinIR probes support influence beyond anchor count on both cohorts; a fixed-context perturbation test supports the conditional local covariance trend.':'Acquired-only HAT, SwinIR and SAINT-style probes pass their frozen numerical gates and support influence beyond anchor count on both cohorts; fixed-context perturbations support the conditional local covariance trend. The stricter probe contract excludes incompatible regular-grid interfaces.',
 'Our contributions are: (1) an executable same-target audit with explicit information contracts and separate evidence fields; (2) a physical-anchor response analysis linked to a conditional covariance model; and (3) cross-architecture interventions, acquired-only influence tests and local neural validation that separate observability from ranking.':'Our contributions are: (1) a same-target audit of local observability loss across diverse frozen estimators; (2) finite-response influence linked to a conditional covariance model where its numerical probe is valid; and (3) an explicit evidence hierarchy in which incompatible interfaces, historical stability failures and null results define the empirical boundary rather than disappear from the model count.',
 'HAT/SwinIR use the historical per-stratum .85 rank-stability criterion; the separate new-architecture gate is .90.':'HAT/SwinIR retain their per-stratum .85 rank-stability criterion; SAINT-style uses the separate frozen new-architecture .90 gate.',
 r'\paragraph{Three final analyses.}':r'\paragraph{Primary analyses and bounded coverage closure.}',
 'No new scalar score or threshold search follows these analyses.':'The bounded closure repeats (2) for SAINT-style and, conditional on numerical stability, (3). I3Net/CycleINR cannot consume the exact two-anchor variable-spacing probe without changing their frozen four-anchor contract. They retain NA for acquired-only influence, separately from historical stability failures. No score or threshold is searched.',
 'Original pooled-plane controls and historical five-model inference remain separately labeled.':'Original pooled-plane controls and historical five-model inference remain separately labeled. Their families are unchanged: new SAINT influence intervals cover both cohorts per endpoint, and its covariance intervals cover four amplitudes. These extension families do not claim joint coverage across the old and new studies.',
 'All twelve amplitude/sign rank checks exceed .85 (minimum .880). The original aggregate six-stratum gate is NA because NingXia was not rerun under this contract. Historical results are not relabeled acquired-only: their non-self advantages remain positive, but NingXia\'s fixed-count result is null/mixed, SAINT\'s beyond-count interval crosses zero, and I3Net/CycleINR fail their separate .90 stability gate. Numerical stability, association and information access are distinct requirements.':'The original twelve HAT/SwinIR checks exceed .85 (minimum .880). SAINT-style passes all three .90 checks per cohort (minimum .951 fastMRI, .996 IXI); its beyond-count advantages are .033 and .133, with positive simultaneous intervals. Fixed-count associations are .380 and .417. Historical target-informed SAINT beyond-count results remain null, and historical I3Net/CycleINR stability failures remain in the supplement; neither is relabeled acquired-only. The original six-stratum aggregate gate remains NA without NingXia. Numerical PASS, beyond-count support and information access are distinct requirements.',
 'The acquired-only neural result covers two models and two brain cohorts; it does not erase the historical knee and new-architecture failures.':'Acquired-only neural influence now covers three compatible models on two brain cohorts, including a non-transformer. This does not erase historical knee/architecture failures or establish validity for the incompatible regular-grid models.',
 'The acquired-only mechanism evidence is scoped to HAT/SwinIR on the two brain cohorts, and the fixed-context covariance trend has substantial individual nonlinear failures.':'The acquired-only mechanism evidence is scoped to HAT, SwinIR and SAINT-style on the two brain cohorts. The fixed-context covariance evidence includes SAINT-style on IXI while retaining substantial individual HAT/SwinIR nonlinear failures.'}
 for a,b in replacements.items():assert a in t,a;t=t.replace(a,b)
 anchor=r'\section{Results}'
 t=t.replace(anchor,r'''\paragraph{Model-evidence accounting.}
The bank contains 13 reconstruction implementations and 111 recorded configurations. Table~\ref{tab:coverage} separates reconstruction, phase intervention, acquired-only influence and covariance evidence. The additional eight baseline phase tests are secondary architecture-breadth sensitivities with an exact-repeat shared control, whose zero disagreement is constructed. They establish interface and phase-response coverage, not eight independent validations of the shared-error mechanism. The five-architecture cross-model matrix remains primary.
\input{architecture_coverage_table.tex}

'''+anchor)
 a='(a) Absolute alignment-correlation advantage over count on the non-self grid. (b) Partial influence--alignment correlation at exactly one shared anchor, adjusting geometry and examination. Points pool planes/contexts; 95\\% intervals resample examinations and are simultaneous across both models separately per cohort/endpoint. Targets enter only error-alignment evaluation. (c) Signed coupled-minus-independent disagreement-energy change and the fixed $\\epsilon_0=.0025$ local prediction, both models and all four amplitudes.'
 b='(a) Absolute alignment-correlation advantage over count. (b) Exactly-one-anchor partial correlation adjusting geometry and examination. HAT/SwinIR intervals retain the original two-model family per cohort/endpoint; the new SAINT family covers both cohorts per endpoint. Targets enter only error evaluation. (c) Signed coupled-minus-independent disagreement-energy change and the fixed $\\epsilon_0=.0025$ prediction for all three models and four amplitudes.'
 assert a in t;t=t.replace(a,b)
 marker='All eight model/amplitude mean effects are negative with simultaneous intervals below zero.'
 t=t.replace(marker,'In the original HAT/SwinIR family, all eight model/amplitude mean effects are negative with simultaneous intervals below zero.')
 marker='The experiment supports a conditional local sensitivity explanation, not the proposition\'s unobserved opposing-sensitivity branch or a claim that phase changes preserve bias/Jacobians.'
 t=t.replace(marker,marker+' The same frozen validation on SAINT-style adds four negative mean intervals; median relative errors are 0.008--1.069\\%, with a 3.199\\% maximum. This non-transformer replication broadens the observed local trend without removing the original 126.4\\% boundary or creating an opposing-sensitivity example.')
 t=t.replace('All 13 baseline models, 111 configurations and training-budget comparisons remain in the supplement, with adverse results intact.','All 13 baseline models, 111 configurations and training-budget comparisons remain in the supplement, with adverse results intact. Technical compatibility of a further five compatible interfaces is reported as available but not run; it is not counted as acquired-only validation.')
 t=t.replace('Aggregate trends agree and median individual relative errors are','Aggregate trends agree; original HAT/SwinIR median individual relative errors are')
 write('main.tex',t)
 # Compact 13-row coverage table; checkmarks refer to evidence in the named design.
 rows=[]
 for r in e.itertuples():
  m=r.model;core=m in {'hat','swinir','saint','i3net','cycleinr'}
  same=r'$\checkmark$' if core else r'$\checkmark_s$'
  cross=r'$\checkmark$' if core else '--'
  probe=r'$\checkmark$' if m in {'hat','swinir','saint'} else (r'$\times$' if r.level_C=='INELIGIBLE' else r'--$_a$')
  if m=='saint':probe=r'$\checkmark\,[\circ_h]$'
  stability=r'$\checkmark$' if m in {'hat','swinir','saint'} else (r'NA [$\times_h$]' if m in {'i3net','cycleinr'} else '--')
  covariance=r'$\checkmark$' if m in {'hat','swinir','saint'} else '--'
  role='Phenomenon + local influence' if m in {'hat','swinir','saint'} else ('Phenomenon; probe ineligible' if core else 'Secondary phase sensitivity')
  rows.append(f'{LABEL[m]} & '+r'$\checkmark$'+f' & {same} & {cross} & {probe} & {stability} & {covariance} & {role} '+r'\\')
 write('architecture_coverage_table.tex',r'''\begin{table*}[t]\centering\scriptsize
\caption{Model--evidence coverage. $\checkmark$: supported within the named design; $\circ$: evaluated but null/inconclusive; $\times$: numerical or interface eligibility failed; --: not run/not applicable. Subscript $s$: secondary exact-output-repeat control, so shared $O=0$ is constructed, not independent mechanism evidence. Subscript $a$: technically available pair interface, influence not run. $\times_h$: historical target-informed stability failure; current acquired-only stability is NA. SAINT's new acquired-only result is supported while its historical beyond-count result is $\circ$ (supplement). Native reconstruction metrics remain in the supplement.}
\label{tab:coverage}\setlength{\tabcolsep}{3pt}
\begin{tabular}{lcccccll}\toprule
Model & Recon. & Same-model & Cross-arch. & Acq. influence & Stability & Covariance & Role in claims\\\midrule
'''+ '\n'.join(rows)+r'\bottomrule\end{tabular}\end{table*}')
 # Acquired table includes every core architecture and actual NA fields.
 rows=[]
 for r in d.itertuples():
  fmt=lambda ep: f'{getattr(r,ep+"_estimate"):.3f} [{getattr(r,ep+"_simultaneous_low"):.3f},{getattr(r,ep+"_simultaneous_high"):.3f}]' if r.technical_eligibility=='ELIGIBLE' else 'NA (interface)'
  st=f'{r.rank_stability_min:.3f} / {r.stability}' if r.technical_eligibility=='ELIGIBLE' else 'NA'
  rows.append(f'{"fastMRI" if r.dataset=="fastmri" else "IXI"} & {LABEL[r.model]} & {fmt("beyond_count")} & {fmt("fixed_count")} & {st} '+r'\\')
 write('final_acquired_table.tex',r'''\begin{table*}[t]\centering\scriptsize
\caption{All five core architectures under the exact acquired-only contract. HAT/SwinIR retain their original two-model simultaneous 95\% intervals per cohort/endpoint and .85 numerical gate. SAINT retains the .90 gate, with new simultaneous intervals across both cohorts per endpoint. I3Net/CycleINR cannot consume the frozen pair-context grid; NA is not zero and does not import historical failed-probe values. Numerical PASS alone does not establish beyond-count support.}
\label{tab:neural}\setlength{\tabcolsep}{4pt}
\begin{tabular}{llrrl}\toprule Cohort & Model & $|\rho_I|-|\rho_{count}|$ [CI] & Fixed-count partial $\rho$ [CI] & Minimum stability / status\\\midrule
'''+ '\n'.join(rows)+r'\bottomrule\end{tabular}\end{table*}')
 # Preserve report-card designs; append all core probe rows without borrowing fields.
 old=pd.read_csv(S/'MIRA_MAIN_REPORT_CARD.csv');cards=old[~old.design.str.startswith('acquired-only')].copy();probes=[]
 for r in d.itertuples():probes.append(dict(design='acquired-only '+r.model,cohort=r.dataset,beyond_count=r.beyond_count_estimate,fixed_count=r.fixed_count_estimate,stability=r.stability,information=r.information_contract,eligibility=r.influence_claim,**{k:getattr(r,k) for k in ['threshold','technical_eligibility','beyond_count_simultaneous_low','beyond_count_simultaneous_high','fixed_count_simultaneous_low','fixed_count_simultaneous_high','inference_family']}))
 cards=pd.concat([cards,pd.DataFrame(probes)],ignore_index=True);cards['stability']=cards['stability'].fillna('NA');cards.to_csv(P/'UPDATED_MIRA_REPORT_CARD.csv',index=False,na_rep='NA')
 text=(ORIG/'mira_report_card_table.tex').read_text(encoding='utf-8')
 start=text.index('Probe/HAT');end=text.index('Covariance',start);new=[]
 for r in d.itertuples():
  b=f'{r.beyond_count_estimate:.3f}' if r.technical_eligibility=='ELIGIBLE' else 'NA';f=f'{r.fixed_count_estimate:.3f}' if r.technical_eligibility=='ELIGIBLE' else 'NA'
  role='Scoped influence' if r.influence_claim=='SUPPORTED' else 'Interface ineligible'
  stability=r.stability if pd.notna(r.stability) else 'NA'
  new.append(f'Probe/{LABEL[r.model]} & {"fastMRI" if r.dataset=="fastmri" else "IXI"} & NA & NA & {b} & {f} & {stability} & A & {role} '+r'\\')
 text=text[:start]+'\n'.join(new)+'\n'+text[end:];write('mira_report_card_table.tex',text)
 sup=(ORIG/'supplement.tex').read_text(encoding='utf-8');sup=sup.replace(r'\input{final_supp_4.tex}',r'\input{final_supp_4.tex}'+'\n'+r'\clearpage\input{architecture_coverage_supp.tex}');write('supplement.tex',sup)
 build_supp(d,e,breadth,cov)
 make_figure(d,cov)
 from polish_layout import polish
 polish()
 print('Manuscript, coverage table, cards and figure updated')

def build_supp(d,e,breadth,cov):
 lines=[r'\section{Bounded Architecture-Coverage Closure}',r'\label{sec:architecture-closure}',
 'This retrospective closure preserves the five-architecture primary matrix and all earlier negative results. The 13-model reconstruction bank is audited for four distinct contracts: native reconstruction, physical phase intervention, acquired-only finite response, and fixed-context covariance. Technical eligibility was determined from frozen wrappers, not observed accuracy. No model, data cohort, score, threshold or perturbation formula was added.',
 r'\subsection{Interface eligibility and full-bank accounting}',
 'All 13 implementations have traced native reconstruction evidence. The eight non-core phase experiments use the recorded master x4 weights on the same 24 fastMRI and 115 IXI examinations and the same five target indices. They preserve acquired-phase normalization and IXI input staging. Fresh predictions are retained as floating-point arrays; this is not a claim of reproducing historical output-file quantization or stochastic benchmark scores. Existing core weights remain fixed even where the later reconstruction master table uses a different training profile.',
 'I3Net requires four low-resolution slices at its checkpoint stride; CycleINR has a frozen four-anchor regular-grid probe. Neither can consume the exact new two-anchor grid without changing the context contract. Cubic falls back to linear with only two inputs. Pix2Pix-GAN fixes three x4 output channels and cannot represent all required variable-gap target fractions. ArSSR accepts variable-depth volumes and stride, but an exact acquired-only pair adapter remains unvalidated. Res-SRDiff draws additional Gaussian sampler noise not specified by the finite-response protocol. Linear, ACVTT, ArSSR, ResUNet and SMamba-UNet have compatible interfaces but are not given new influence experiments in this bounded task. Thus three models have evaluated acquired-only influence; five additional interfaces are available but not run, and five are ineligible under this exact contract.',
 r'\subsection{All-core acquired-only report card}',r'Table~\ref{tab:neural} retains every core architecture and each unavailable field.',
 'SAINT uses its unchanged six channels: two acquired images, relative target position, physical target z/(source depth-1), and fixed in-plane coordinate maps. Input pools, mask, Q1 offset, Q99--Q1 range, target selection, four Rademacher seeds, amplitudes and sign reversal are exactly those of the final acquired-only protocol. FP32/no AMP/no TF32 and native clipping are retained. Response arrays are hash-bound before the separate target files are read. All 417 target responses and 13,344 non-self context/amplitude observations are retained.',
 'HAT/SwinIR numerical thresholds and original inference families remain unchanged. SAINT requires all three alternative-versus-primary rank correlations to exceed .90 separately per cohort. Its extension intervals are simultaneous over both cohorts per endpoint, using the original 5,000 examination draws and respective seeds; they are not substituted into the original HAT/SwinIR families. Historical target-informed SAINT null results and I3Net/CycleINR failures remain in the negative-results section. Changing information formation and precision can change results, so the new positive result does not invalidate the historical null.',
 r'\begin{table*}[t]\centering\small\caption{New acquired-only SAINT stability. All three checks are required; threshold .90 unchanged.}\begin{tabular}{lrrrl}\toprule Cohort & $+.005$ & $+.02$ & $-.01$ & Status\\\midrule']
 for r in d[d.model=='saint'].itertuples():lines.append(f'{r.dataset} & {r.stability_half:.6f} & {r.stability_double:.6f} & {r.stability_negative:.6f} & {r.stability} '+r'\\')
 lines+=[r'\bottomrule\end{tabular}\end{table*}',r'\subsection{Secondary signs: every amplitude and endpoint}',
 'The following secondary correlations are descriptive. They do not add corrected hypothesis families or replace the primary alignment endpoint. Fixed-count values control span, asymmetry and examination as in the primary analysis.',
 r'\begin{table*}[t]\centering\scriptsize\caption{SAINT secondary signs under acquired-only formation. BC denotes absolute-correlation advantage over count; FC denotes fixed-count partial association.}\begin{tabular}{llrrrrrrr}\toprule Cohort & Endpoint & BC .01 & FC .01 & BC .005 & FC .005 & BC .02 & FC .02 & BC/FC $-.01$\\\midrule']
 signs=pd.read_csv(P/'outputs/saint_secondary_signs.csv')
 for (ds,ep),g in signs.groupby(['dataset','endpoint']):
  q=g.set_index('epsilon');v=[]
  for eps in [.01,.005,.02]:v.extend([f'{q.loc[eps,"beyond_count"]:.3f}',f'{q.loc[eps,"fixed_count"]:.3f}'])
  v.append(f'{q.loc[-.01,"beyond_count"]:.3f}/{q.loc[-.01,"fixed_count"]:.3f}');lines.append(' & '.join([ds,ep.replace('_',' '),*v])+r'\\')
 lines +=[r'\bottomrule\end{tabular}\end{table*}',r'\subsection{Fixed-context covariance replication}',
 'SAINT passed the IXI numerical gate and uses the same physical pair interface, so it receives all twelve original hash-selected cases, central targets, four one-anchor contexts, four amplitudes, eight balanced fields and Cartesian independent construction. Selection does not depend on a positive beyond-count result. A separate four-amplitude simultaneous family preserves the earlier eight HAT/SwinIR contrasts. No target is read for this validation. The fixed .0025 odd-response approximation is distinguished from same-amplitude covariance identity closure.',
 r'\begin{table*}[t]\centering\scriptsize\caption{All new SAINT fixed-context validation amplitudes (12 examinations, 48 case/context observations each). Relative error divides by absolute fixed-local prediction.}\begin{tabular}{rrrrrr}\toprule $\epsilon$ & Observed $\Delta\mathbb ED^2$ [sim. CI] & Fixed local prediction & Median rel. error & Maximum rel. error & Identity residual\\\midrule']
 for r in cov.itertuples():lines.append(f'{r.epsilon:.4f} & {r.observed_delta_mean:.3f} [{r.simultaneous_low:.3f},{r.simultaneous_high:.3f}] & {r.linear_prediction_mean:.3f} & {100*r.median_relative_error:.3f}\\% & {100*r.max_relative_error:.3f}\\% & {r.maximum_closure_error:.2e} '+r'\\')
 prop=pd.read_csv(P/'outputs/saint_covariance_observations.csv');counts=prop[prop.epsilon==.0025].reference_sensitivity_class.value_counts().to_dict()
 lines +=[r'\bottomrule\end{tabular}\end{table*}',f'Among the 48 new case/context examples, {counts.get("aligned",0)} are aligned, {counts.get("near_orthogonal",0)} near-orthogonal and {counts.get("opposing",0)} opposing. All are retained. The original HAT/SwinIR maximum relative error of 126.4\\% remains material; the new architecture does not establish a uniform neural approximation bound.',
 r'\subsection{All eight non-core phase sensitivities}',
 'The shared companion is an exact repeat of the same frozen phase-0 output. Its zero disagreement and zero observable fraction are constructed. Positive disjoint-minus-shared O therefore demonstrates phase-response sensitivity, not an independently controlled shared-error mechanism or a cross-architecture result. This deliberately limited secondary design must not be described as thirteen baselines validating MIRA influence. No expanded cross-model matrix replaces the original five-model primary.',
 'Res-SRDiff conditions the unchanged stochastic sampler on one exogenously fixed RNG seed (20260914) in both phase passes. The full sampler random-draw order is preserved, including draws for unused output planes. Skipping only their neural evaluations was verified against full inference with identical outputs and final RNG states on both phases of the first registered case in each cohort. ArSSR retains full-volume feature encoding and physical target support; the initial selected-output optimization failed a 0.0001 native-unit equality check because of floating-point coordinate arithmetic. The correction restores the wrapper\'s stepwise float32 coordinate arithmetic without changing the tolerance, weights or observations; the initial diagnostic failure is retained.',
 'All three support rules are reported: target-derived 1-percent foreground, union of the nearest bracketing phase-0 acquired foregrounds, and common finite full-image pixels. Targets are identical across masks and conditions. Five-target means precede examination means; 5,000 paired examination draws yield simultaneous intervals over all eight non-core models separately per cohort/support. These are post-hoc architecture-breadth sensitivities.']
 for ds,g in breadth.groupby('dataset'):
  lines +=[r'\begin{table*}[t]\centering\scriptsize',f'\\caption{{{ds}: complete secondary phase sensitivities, $\\Delta O$ [simultaneous 95\\% CI] in pp. Shared $O=0$ is constructed.}}',r'\begin{tabular}{lrrr}\toprule Model & Target support & Acquired union & Full common valid\\\midrule']
  for m,h in g.groupby('model'):
   q=h.set_index('support');vals=[]
   for support in ['target_1pct','acquired_union','full_common_valid']:
    r=q.loc[support];vals.append(f'{100*r.delta_O:.3f} [{100*r.simultaneous_low:.3f},{100*r.simultaneous_high:.3f}]' if r.status=='ELIGIBLE' else 'NA (technical)')
   lines.append(' & '.join([LABEL[m],*vals])+r'\\')
  lines.append(r'\bottomrule\end{tabular}\end{table*}')
 lines +=[r'\subsection{Claim boundaries and author documentation}',
 'Claims A (local observability under changed evidence) and B (architectural diversity is insufficient) continue to rely primarily on the five-model intervention and its support/geometry sensitivities. The eight self-control extensions clarify interface breadth, not eight independent causal confirmations. Claim C gains a numerically eligible non-transformer on both brain cohorts; Claim D gains that implementation on the fixed IXI design. Neither claim extends to all reconstruction baselines. Existing null ranking, knee, scoring, orientation and stability results remain unchanged. NingXia ethics, consent, de-identification and use permissions, and precise fastMRI release authorization remain NEEDS HUMAN CONFIRMATION.',
 r'\paragraph{Reproduction.} The closure protocol, model-evidence matrix, raw-response bindings, exact commands and claim map accompany the local package in \path{ARCHITECTURE_COVERAGE_CLOSURE/}. New array-derived checks are separate from the previous complete reproduction; no historical CSV is relabeled as a new neural response.']
 write('architecture_coverage_supp.tex','\n\n'.join(lines))

def make_figure(d,cov):
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
 fig,ax=plt.subplots(1,3,figsize=(7.1,2.45),gridspec_kw={'width_ratios':[1,1,1.4],'wspace':.35})
 q=d[d.technical_eligibility=='ELIGIBLE'].set_index(['dataset','model']);order=[(ds,m) for ds in ['ixi','fastmri'] for m in ['hat','swinir','saint']]
 colors={'hat':'#236c98','swinir':'#b86516','saint':'#37825c'}
 for j,ep in enumerate(['beyond_count','fixed_count']):
  for i,key in enumerate(order):
   r=q.loc[key];v=r[ep+'_estimate'];ax[j].errorbar(v,5-i,xerr=[[v-r[ep+'_simultaneous_low']],[r[ep+'_simultaneous_high']-v]],fmt='o',color=colors[key[1]],capsize=2,ms=3.5)
  ax[j].set_yticks(range(6),[('IXI' if ds=='ixi' else 'fastMRI')+'/'+LABEL[m].replace('-style','') for ds,m in reversed(order)] if j==0 else ['']*6)
  ax[j].axvline(0,color='.6',ls='--',lw=.6);ax[j].grid(axis='x',color='.93');ax[j].set_ylim(-.6,5.6)
  ax[j].set_xlabel(r'$|\rho_I|-|\rho_{count}|$' if j==0 else 'Partial correlation');ax[j].set_title('(a) Beyond count' if j==0 else '(b) Fixed count',fontsize=8,weight='bold')
 prop=pd.concat([pd.read_csv(B/'outputs/proposition_summary.csv'),cov],ignore_index=True)
 for m,col in colors.items():
  g=prop[prop.model==m].sort_values('epsilon');ax[2].plot(100*g.epsilon,g.observed_delta_mean,'o-',color=col,ms=3,lw=1,label=LABEL[m].replace('-style',''));ax[2].plot(100*g.epsilon,g.linear_prediction_mean,'--',color=col,lw=1)
 ax[2].axhline(0,color='.7',lw=.5);ax[2].set_xticks([.25,.5,1,2]);ax[2].set_xlabel('Perturbation amplitude (%)');ax[2].set_ylabel(r'$\Delta\,\mathbb{E}D^2$ (native intensity$^2$)',labelpad=1);ax[2].set_title('(c) Fixed-context validation',fontsize=8,weight='bold');ax[2].legend(fontsize=6,frameon=False,loc='lower left',bbox_to_anchor=(0,.10));ax[2].text(.03,.02,'solid: observed; dashed: local',transform=ax[2].transAxes,fontsize=5.8)
 fig.subplots_adjust(left=.155,right=.995,bottom=.20,top=.87);out=P/'figures';out.mkdir(exist_ok=True)
 for ext in ['pdf','png']:fig.savefig(out/f'final_fig3_acquired_influence.{ext}',dpi=220,bbox_inches='tight',pad_inches=.03)
 plt.close(fig);shutil.copy2(out/'final_fig3_acquired_influence.pdf',CV/'final_fig3_acquired_influence.pdf')
if __name__=='__main__':main()
