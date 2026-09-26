"""Generate Plan 14 revisions from the protected Plan 13 manuscripts."""
from pathlib import Path
import json,re
import pandas as pd
P14=Path(__file__).resolve().parents[1]; PAPER=P14.parent; OUT=P14/'outputs'
CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'; TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED'
def original(p): return (P14/'original_snapshot'/p.relative_to(PAPER)).read_text(encoding='utf-8')
def replace(t,a,b):
    if a not in t: raise ValueError('Missing revision anchor: '+a[:100])
    return t.replace(a,b)
def write(p,t): p.write_text(t,encoding='utf-8')
e=pd.read_csv(OUT/'topcow_effects.csv'); a=e[e['mask'].eq('acquired')].set_index('pair')
r=pd.read_csv(OUT/'topcow_rankings.csv'); r=r[r['mask'].eq('acquired')].set_index(['pair','endpoint'])
m=json.loads((OUT/'topcow_analysis_manifest.json').read_text())
values={'@PLANES@':str(m['unique_target_planes'])}
for pair in ['LC','CL']:
    for key,col in [('GAIN','gain'),('LO','simultaneous_low'),('HI','simultaneous_high')]: values[f'@{key}_{pair}@']=f'{100*a.loc[pair,col]:.1f}'
    for endpoint,name in [('error','ALL'),('vessel_error','VESSEL')]: values[f'@RANK_{pair}_{name}@']=f'{r.loc[(pair,endpoint),"delta_rho"]:.3f}'
def fill(t):
    for k,v in values.items(): t=t.replace(k,v)
    return t

t=original(CV/'main.tex')
t=replace(t,'the five-architecture and candidate-bank output scores use target-derived evaluation masks and are not fully target-free pipelines.','the five-architecture intervention uses target-derived masks, while bank scores use target-model prediction masks. These supports are evaluated separately.')
t=replace(t,'Bank disagreement is unavailable for analytical interpolators outside the frozen candidate bank.','Bank scores were precomputed for neural targets only; analytical interpolators remain candidate members.')
t=replace(t,'but all evaluated data remain MRI T2 and the five-architecture intervention has no knee replication.','but the five-architecture intervention remains limited to brain T2 and has no knee replication. External MRA extends only the analytical test.')
t=replace(t,'Finally, a rule-frozen retrospective audit matches model identity between $\\times4$ and $\\times2$: Anchor-CV has positive within-model association with benefit for 13/13 fastMRI models and 12/13 NingXia models, with the degraded Res-SRDiff exception retained.','A 125-case external MR angiography experiment tests acquired-only score support with fixed analytical estimators. Retrospective benefit audits retain a degraded-model exception and expose sensitivity to score--endpoint scale agreement.')
t=replace(t,'Dense volumes supply retrospective anchors and targets.','Dense volumes supply retrospective anchors and targets. A DICOM audit verifies physical slice order for all 24 fastMRI test cases; their legacy affine alone does not preserve patient orientation.')
t=replace(t,'Thus benefit ranking depends on scale and current difficulty, not only acquisition value.',r'Normalizing both score and benefit instead yields $.539/.551$ on IXI. Thus benefit ranking depends on its unit convention and current difficulty, not only acquisition value.')
external=r'''\paragraph{External acquired-support check.}
We apply fixed linear (L) and four-point Lagrange cubic (C) estimators to 125 TopCoW MRA cases with vascular annotations~\cite{yang2026topcow}, covering @PLANES@ common missing planes. L$_0$--C$_0$ versus L$_0$--C$_2$, and C$_0$--L$_0$ versus C$_0$--L$_2$, keep the estimator pairing fixed while changing anchor identity. Both residues are averaged equally within cases. The score mask uses only phase-0 acquired anchors; labels define evaluation endpoints only. Observable gains are @GAIN_LC@ [@LO_LC@,@HI_LC@] and @GAIN_CL@ [@LO_CL@,@HI_CL@] points under two-pair simultaneous intervals. This is an analytical external check, not a neural MRA replication. Fixed phase-0 error and annotated-vessel ranking are separately reported in the supplement.

'''
t=replace(t,'\\FloatBarrier\n\n\\flushbottom',fill(external)+'\\FloatBarrier\n\n\\flushbottom')
t=replace(t,'No result establishes diagnostic safety.','A train/validation patient overlap affects historical checkpoint-selection provenance, although test patients are disjoint. No result establishes diagnostic safety.')
# The cohort hierarchy repeats the explicit sample-size and scope statements above.
start=t.index('\\paragraph{Evidence hierarchy.}'); end=t.index('\\section{Conclusion}',start)
t=t[:start]+t[end:]
write(CV/'main.tex',t)

s=original(CV/'supplement.tex')
s=replace(s,'Plan 9/11 and the recovered bank use a ground-truth 1\\% mask.','Plan 9/11 use a ground-truth 1\\% mask; the recovered bank uses the target model\'s prediction mask, not ground truth.')
s=replace(s,'The rule-frozen consequence audit instead holds the reconstruction model fixed.','The rule-frozen consequence audit instead matches model identity while allowing factor-specific weights.')
s=replace(s,'analytical interpolators are not registry-declared candidate-bank members.','the precomputation includes neural targets only; Linear/Cubic are candidate members but not target rows.')
s=replace(s,'\\end{document}','\\input{p14_additional_analysis.tex}\n\\end{document}')
write(CV/'supplement.tex',s)
s=original(CV/'p13_additional_analysis.tex')
s=replace(s,'The Plan 9/11 output-score mask and candidate-bank support use dense targets; they are retrospective scores under privileged support.','The Plan 9/11 output-score mask uses dense targets. The bank instead uses target-model prediction support; its field name does not denote ground truth.')
write(CV/'p13_additional_analysis.tex',s)

t=original(TMI/'main.tex')
t=replace(t,'Measurement Dependence Governs Disagreement-Based Reliability in Deterministic MRI Slice Interpolation','Disagreement-Based Quality Assessment of MRI Slice Interpolation: Measurement Dependence and Anatomical Error')
t=replace(t,'Plan 9/11 and candidate-bank scores use a target-derived 1\\% mask: the score support therefore accesses the dense reference.','Plan 9/11 scores use a target-derived 1\\% mask. Candidate-bank scores instead use a target-model prediction mask; raw-output recomputation verifies this distinction.')
t=replace(t,'its denominator excludes analytical interpolators that are not declared bank members.','its denominator reflects neural-only target precomputation, although Linear/Cubic are bank members.')
t=replace(t,'Generated planes were matched using NIfTI affine-derived physical origins.','Generated planes were matched within the recorded grids. A new DICOM audit verifies pixel order and physical positions for all 24 fastMRI test cases; the legacy diagonal affine does not preserve patient orientation.')
t=replace(t,'The third cohort adds one architecture, not a broad matrix or fixed-weight acquisition experiment.',r'''Normalizing both score and benefit by the same acquired range gives correlations .539 [.356,.698] and .551 [.372,.704]; raw scores against normalized benefit instead give $-.375/-.373$. The four contracts preserve both positive and negative results: a shared denominator can itself induce association, so this is a unit-sensitivity diagnostic, not a new calibrated score.

Independent source reconstruction also distinguishes prediction-only bank support from GT support. Across all 11 neural targets, acquired-input masks yield median raw benefit correlations .863/.723 on fastMRI/NingXia, compared with .835/.710 for prediction masks and .805/.519 for bank unions. Current-error-adjusted medians remain $-.058/.425$ for acquired masks. Changing support does not remove the current-difficulty limitation.''')
external=r'''\subsection{External MRA and Anatomical Error}
All 125 locally available TopCoW MRA cases have paired vascular annotations~\cite{yang2026topcow}. We use the public challenge training images as a new external evaluation cohort, with no estimator fitting. Fixed linear (L) and four-point Lagrange cubic (C) interpolation use complete native-resolution contexts on phase-0/phase-2 $\times4$ grids. All @PLANES@ eligible odd planes enter; residues 1 and 3 receive equal case weight. The score mask is the union of the two nearest phase-0 acquired-anchor masks. Vessel labels are used only to evaluate error, never to select inputs or target planes.

\begin{figure*}[t]
\centering\includegraphics[width=.98\textwidth]{p14_anatomical_transfer.pdf}
\caption{Anatomical specificity with fixed analytical estimators. (a) TopCoW acquired-support scores rank general and vessel-region errors differently (pointwise intervals). (b) Bright-anchor weighting improves vessel-error ranking on TopCoW and transfers in disjoint contexts to CAS2023; intervals are simultaneous across two pairings within each cohort/context. TopCoW motivated the rule; CAS2023 received it without retuning. General-error ranking deteriorates under this weighting.}
\label{fig:topcow}
\end{figure*}

Keeping the estimator pair fixed, L$_0$--C$_2$ minus L$_0$--C$_0$ increases observable fraction by @GAIN_LC@ [@LO_LC@,@HI_LC@] points; C$_0$--L$_2$ minus C$_0$--L$_0$ gives @GAIN_CL@ [@LO_CL@,@HI_CL@]. Ranking changes against fixed linear/cubic error are @RANK_LC_ALL@/@RANK_CL_ALL@, and against vessel-region error @RANK_LC_VESSEL@/@RANK_CL_VESSEL@ (Fig.~\ref{fig:topcow}). These endpoints test distinct consequences. The paired $\times4\!\rightarrow\!\times2$ control uses the same interpolation rules, eliminating factor-specific learned weights; all case-level general and vessel benefits, including negative values, are retained in the numerical record. Region-restricted intensity error is an anatomical endpoint, not segmentation or diagnostic accuracy.

'''
t=replace(t,'\\subsection{Failure Granularity}',fill(external)+'\\subsection{Failure Granularity}')
t=t.replace('These endpoints test distinct consequences.', 'Vessel-risk coverage also worsens: disjoint-minus-shared normalized excess risk area is .00140 [.00028,.03211] for L and .00135 [.00026,.03120] for C. These endpoints test distinct consequences.')
t=replace(t,'\\subsection{Failure Granularity}',r'''\paragraph{Fixed anatomical weighting and transfer.}
After observing TopCoW's endpoint mismatch, we fix a label-free rule: retain the brightest 5\% of each acquired anchor's 1\%-foreground, then unite the nearest two anchor masks. The same TopCoW cases are exploratory development evidence. Disjoint vessel-error correlations rise from .488/.471 to .705/.693 for L/C, with changes .217 [.100,.334] and .222 [.110,.334] under two-pair simultaneous intervals.

We transfer the unchanged rule to all 100 paired CAS2023 angiograms~\cite{cas2023} (6,412 eligible planes), without fitting, label-based plane selection, or threshold search. Disjoint vessel-error correlations improve from .880/.877 to .953/.947: changes .073 [.017,.130] and .070 [.014,.126]. Shared-context changes .010/$ .005$ have simultaneous intervals crossing zero. This anatomical improvement has a cost: general-error correlations fall by .085/.084 on CAS2023 and .250/.235 on TopCoW in disjoint contexts. CAS2023 vessel-risk coverage changes favor bright weighting, but both pointwise intervals cross zero. Thus rank transfer does not establish screening utility. Labels define intensity-error endpoints, not diagnostic outcomes; CAS header provenance does not certify physical slice spacing.

\subsection{Failure Granularity}''')
t=replace(t,'The analytical factor experiment changes target availability and distance together.','The analytical factor experiment changes target availability and distance together. MRA broadens contrast and anatomical evaluation only for fixed analytical estimators; neural conclusions remain T2-specific.')
t=replace(t,'NingXia has only eight independent patients.','NingXia has only eight independent patients. One legacy fastMRI patient overlaps train/validation, but none overlaps test; historical checkpoint-selection bias is not quantified.')
t=replace(t,'OpenAI Codex assisted with revision of the abstract and Sections II--VI, exploratory statistical scripts, and the architecture robustness figure.','OpenAI Codex assisted with the abstract, Sections II--VI, statistical and external-MRA scripts, and the robustness/MRA figures.')
# Keep abstract under 250 words while foregrounding the new anatomical evidence.
begin=t.index('\\begin{abstract}')+len('\\begin{abstract}');end=t.index('\\end{abstract}',begin)
t=t[:begin]+fill(r'''
Agreement between deterministic MRI interpolators can hide substantial shared error. We study measurement dependence in 24 fastMRI brain examinations, 115 IXI brain examinations, and 22 NingXia knee series from eight patients, with additional analytical experiments on 125 TopCoW and 100 CAS2023 annotated angiograms. Five neural architectures on both brain cohorts retain positive disjoint-minus-shared observable gains under exploratory simultaneous inference, while examination ranking is less robust. Raw-output reconstruction distinguishes prediction-derived bank masks from ground-truth support. In retrospective densification audits, all 26 fastMRI/NingXia Anchor-CV intervals cross zero after conditioning on current error. On IXI, normalizing both scores and benefit preserves positive association, whereas normalizing only one reverses ranking. Fixed linear/cubic estimators on TopCoW give local observable gains of @GAIN_LC@ and @GAIN_CL@ percentage points, but general-error ranking does not imply vessel-error ranking. A bright-anchor weighting rule motivated on TopCoW transfers without retuning to CAS2023: disjoint vessel-error correlations improve by .073 [.017,.130] and .070 [.014,.126] under two-pair simultaneous intervals. General-error ranking deteriorates, and vessel-risk coverage intervals cross zero. Shared-energy decompositions are algebraically coupled rather than independent mechanism tests. The results support anatomically specified quality assessment with explicit measurement, support, and scale contracts, without establishing calibrated uncertainty, diagnostic safety, or prospective acquisition utility.
''')+t[end:]
# Remove a table that repeats the complete counts/correlations in adjacent prose.
table_start=t.index('\\begin{table}[t]',t.index('Independent source reconstruction'))
table_end=t.index('\\end{table}',table_start)+len('\\end{table}')
assert '\\label{tab:benefit}' in t[table_start:table_end]
t=t[:table_start]+t[table_end:]
start=t.index('Several boundaries change the practical recommendation.')
end=t.index('The literature boundary is also precise.',start)
t=t[:start]+r'''Local exposure, examination ranking, and screening utility require separate validation. The MRA transfer makes this distinction actionable: a fixed acquired-bright score improves vessel-error ranking while losing general-error ranking, with uncertain risk-coverage benefit. A quality score should therefore specify its anatomical endpoint before evaluation.

'''+t[end:]
start=t.index('Every Plan6 experiment writes');end=t.index('\\subsection{Ethics and Data Availability}',start)
t=t[:start]+r'''Per-plane and case-level records, source hashes, protocol amendments, and plotting scripts retain the historical and new analyses separately. TopCoW (125 cases) motivated a fixed rule subsequently evaluated on CAS2023 (100 cases); this chronology is explicit. The journal emphasizes anatomical QA and does not claim the conference paper's finite-response statistic as a new method. Shared cohorts and architecture experiments remain overlapping evidence.

'''+t[end:]
t=t.replace('All phase grids are retrospective simulations from dense T2 volumes;','All phase grids are retrospective simulations from dense MRI volumes;')
t=t.replace('Our contributions are: (i)', 'Our contributions include an acquired-only anatomical score with fixed-rule external MRA transfer, alongside: (i)')
# Declare the wide operating-regime table early enough to precede references.
start=t.index('\\begin{table*}[t]',t.index('\\subsection{Comparator Semantics and Cost}'))
end=t.index('\\end{table*}',start)+len('\\end{table*}')
regime=t[start:end];t=t[:start]+t[end:]
t=t.replace('\\subsection{Failure Granularity}',regime+'\n\n\\subsection{Failure Granularity}')
write(TMI/'main.tex',t)

bib=r'''
@article{yang2026topcow,
author={Yang, Kaiyuan and others},
title={The {TopCoW} Challenge---Topology-Aware Circle of Willis Segmentation for {CT} and {MR} Angiography},
journal={NEJM AI},year={2026},volume={3},number={8},doi={10.1056/AIdbp2500994}
}
@misc{cas2023,
author={{Society for Magnetic Resonance Angiography}},
title={Cerebral Artery Segmentation Challenge ({CAS2023})},year={2023},
howpublished={\url{https://society4mra.org/index.php/2023/06/14/cerebral-artery-segmentation-challenge-cas2023/}}
}
'''
for d in [CV,TMI]: write(d/'references.bib',original(d/'references.bib')+bib)

supp=r'''\section{External Support, Scale, and Anatomical Checks}
These Plan 14 experiments are exploratory. The external MRA protocol was written before outcome calculation; it uses a different cohort from the historical brain T2 studies. All native images and labels remain unchanged. Complete cases, protocol versions, 250 source hashes, all mask choices and fixed-estimator benefit results are retained in \path{PLAN14_SCIENTIFIC_STRENGTHENING/}.

\paragraph{Correcting bank-score provenance.}
The archived \texttt{target\_0.01} field denotes the target model's prediction mask, not ground truth. We independently recompute 84 mask/target/partner combinations from original predictions on the lexicographically first case in each cohort; maximum difference is $1.42\times10^{-14}$. Linear/Cubic are candidate members; the smaller denominator comes from neural-only target precomputation. Plan 9/11's intervention masks remain ground-truth-derived. Across all 506 eligible model--case rows, acquired-input masks give median benefit correlations .863/.723, prediction masks .835/.710, and bank unions .805/.519 on fastMRI/NingXia. Acquired-mask partial medians given current error are $-.058/.425$. No mask is chosen based on these outcomes.

\begin{figure*}[t]
\centering\includegraphics[width=.98\textwidth]{p14_bank_mask_sensitivity.pdf}
\caption{All 11 neural target models under three score-support contracts. Points are raw benefit correlations, not confidence limits. Linear/Cubic remain candidate members; neither was precomputed as a target model. All model-specific bootstrap intervals and paired mask differences are retained in the numerical record.}
\end{figure*}

\paragraph{Crossing score and endpoint units.}
For the 115 recovered IXI I3Net pairs, use the same acquired-anchor 1st--99th percentile range $r$ to form all four contracts: $(s,b)$, $(s/r,b)$, $(s,b/r)$, and $(s/r,b/r)$. Anchor-CV correlations are .843, $-.238$, $-.375$, and .539; adjacent MAE gives .845, $-.236$, $-.373$, and .551. Bootstrap count is 10,000 and seed 20260909. At 50\% selection, matched normalized Anchor-CV exceeds random by .000655 normalized MAE units [.000151,.001537], while the same score against raw benefit remains below random. Shared scaling can induce correlation, so unit consistency is not a causal or calibration guarantee.

\begin{figure*}[t]
\centering\includegraphics[width=.92\textwidth]{p14_scale_contract.pdf}
\caption{Score--endpoint unit contracts on IXI. Each cell gives Spearman correlation and an exploratory pointwise 95\% examination-bootstrap interval. Both favorable diagonal cells and adverse off-diagonal cells are reported.}
\end{figure*}

\paragraph{External MRA protocol.}
We use all 125 locally available annotated TopCoW MRA cases (public challenge training data, no fitting in this experiment), with @PLANES@ eligible odd planes. L is linear interpolation; C is four-point Lagrange interpolation with no output clipping. For each phase, all four cubic anchors must lie inside the image; neither boundary duplication nor label-based plane selection is allowed. L$_0$--C$_0$ and C$_0$--L$_0$ are shared controls; their disjoint partners are C$_2$ and L$_2$. The input-support mask is the union of the two nearest acquired phase-0 anchor masks, each thresholded at 1\% of that anchor's maximum absolute intensity. The full-image and target-derived-mask alternatives are sensitivity contracts, not pooled replicas. Within each case, means are first taken within target residues 1 and 3, then the two residue means are equally weighted. Cases are the bootstrap units; 10,000 common draws are used. Local-gain simultaneous intervals use the maximum standardized deviation across the two estimator pairings within each mask. Other intervals are exploratory pointwise.

Vessel labels define region-restricted intensity error only. Empty-vessel planes are recorded as undefined, not zero; every case retains its actual vessel-plane denominator. The ranking endpoint is the fixed phase-0 target estimator's error, so it does not change between the shared and disjoint scores. The $\times2/\times4$ benefit comparison uses identical estimator rules and common odd planes. Raw and acquired-range-normalized endpoints/scores, both estimators, and fixed 20\%/50\% budgets are all retained.

\begin{figure*}[t]
\centering\includegraphics[width=\textwidth]{p14_topcow_external.pdf}
\caption{External MRA local geometry and anatomical ranking. The analytical experiment broadens contrast and endpoint coverage, but does not replicate the five neural models on MRA. Local error exposure is distinct from useful global or vessel-error ordering.}
\end{figure*}

\paragraph{Legacy split and geometry audit.}
The old fastMRI split contains one patient in both train and validation, but test patients overlap neither. Historical checkpoint-selection bias cannot be quantified from the existing outputs. For all 24 paper test cases, original DICOM headers and first/middle/last pixel planes confirm ordering, parallel directions, and monotone physical positions. The stored diagonal NIfTI affine does not retain patient orientation, so agreement of inherited affine matrices alone is insufficient evidence. Source documents in other projects are used for traceability, without importing their developed-model performance as independent evidence.
'''
supp+=r'''
\paragraph{Anatomical weighting: development and fixed-rule transfer.}
After the TopCoW baseline analysis, we fix a bright-anchor mask at the 95th percentile within each acquired anchor's 1\%-foreground and unite the nearest two masks. The threshold is never searched. TopCoW reuses the development cohort; CAS2023 receives this rule unchanged on all 100 image/label pairs and 6,412 eligible planes. Image and label shapes/affines match. No file hashes match TopCoW, which does not prove person-level nonoverlap without linked identifiers. Unknown CAS header provenance precludes a physical-spacing claim. Cases, residue balancing, estimator rules, and bootstrap count/seed match the preceding protocol.

\begin{table*}[t]\centering\small
\caption{Bright-anchor minus general-support vessel-error ranking. Intervals are simultaneous across L/C within each cohort/context. TopCoW is exploratory rule development; CAS2023 is fixed-rule transfer. General-error changes are retained to expose the tradeoff.}
\begin{tabular}{llrrrr}\toprule
Cohort & Context/target & Baseline $\rho$ & Bright $\rho$ & $\Delta\rho$ [95\% CI] & General $\Delta\rho$\\\midrule
'''
for dataset,filename in [('TopCoW','bright_anchor_rankings.csv'),('CAS2023','cas_transfer_rankings.csv')]:
    data=pd.read_csv(OUT/filename)
    for condition in ['shared','disjoint']:
        for pair,target in [('LC','L'),('CL','C')]:
            row=data[(data.pair==pair)&(data.condition==condition)&(data.endpoint=='vessel_error')].iloc[0]
            general=data[(data.pair==pair)&(data.condition==condition)&(data.endpoint=='error')].iloc[0]
            supp+=f'{dataset} & {condition}/{target} & {row.baseline_rho:.3f} & {row.bright_rho:.3f} & {row.delta_rho:.3f} [{row.simultaneous_low:.3f},{row.simultaneous_high:.3f}] & {general.delta_rho:.3f}'+r'\\'+'\n'
supp+=r'''\bottomrule\end{tabular}\end{table*}
Before bright weighting, changing shared to disjoint contexts worsens TopCoW vessel-risk coverage: normalized excess risk area increases by .00140 [.00028,.03211] for L and .00135 [.00026,.03120] for C. Full-image score support also yields a negative vessel-ranking change for L, $-.0490$ [$-.1016,-.0003$]. These qualified negative sensitivity results remain part of the evidence.
On TopCoW, all four vessel-risk coverage changes favor bright weighting and all four general-error rankings deteriorate. On CAS2023, the disjoint vessel-risk coverage changes are $-.01047$ [$-.02389,.00034$] and $-.01074$ [$-.02482,.00089$]; shared changes also cross zero. Negative changes in normalized excess risk area favor the new score. Both contexts lose general-error ranking on CAS2023. This is a target-specific ranking transfer with unresolved screening benefit, not a universal score improvement. The full numerical record includes all endpoints and contexts, including nonsignificant and adverse results.
'''
start=supp.index('\\begin{table*}[t]');end=supp.index('\\end{table*}',start)+len('\\end{table*}')
transfer_table=supp[start:end];supp=supp[:start]+supp[end:]
anchor='\\begin{figure*}[t]\n\\centering\\includegraphics[width=\\textwidth]{p14_topcow_external.pdf}'
supp=replace(supp,anchor,transfer_table+'\n\n'+anchor)
write(CV/'p14_additional_analysis.tex',fill(supp))
print('Plan 14 manuscripts regenerated; TMI abstract words:',len(t[t.index('\\begin{abstract}'):t.index('\\end{abstract}')].split()))
