from pathlib import Path
import re,json
P=Path(__file__).resolve().parents[1];CV=P/'revised_manuscript';OLD=P/'original_snapshot/manuscript'
text=(OLD/'main.tex').read_text(encoding='utf-8')
text=text.replace('Shared Measurement Influence in MRI Slice Interpolation','Auditing Shared Measurement Dependence in MRI Slice Interpolation',1)
abstract=r'''Agreement can hide reconstruction error when predictors reuse the same physical evidence. We introduce the Measurement-Influence Reliability Audit (MIRA): same-target measurement-identity interventions with frozen estimators, paired-error decomposition, and local response analysis. Across all 20 ordered pairs of five architecture implementations on NYU fastMRI brain T2 and IXI, disjoint companion measurements increase local error observability with simultaneous intervals above zero. Acquired-only HAT/SwinIR probes support influence beyond anchor count on both cohorts; a fixed-context perturbation test supports the conditional local covariance trend. Support and residue-balancing sensitivities preserve the local finding, while orientation effects remain. Examination ranking is cohort dependent, and the data have been reused retrospectively. MIRA audits when agreement loses observability; it does not provide a calibrated correctness score.'''
text=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',text,flags=re.S)
text=text.replace(r'\cite{song2024i3net,peng2020saint,fang2024cycleinr}',r'\cite{chen2023hat,liang2021swinir,song2024i3net,peng2020saint,fang2024cycleinr}')
text=text.replace(r'24 fastMRI brain T2 examinations~\cite{knoll2020fastmri}',r'24 locally catalogued NYU fastMRI brain T2 examinations~\cite{knoll2020fastmri,muckley2021brain,fastmri_portal}')
text=text.replace('I3Net, adapted SAINT-style and internal CycleINR-style','locally configured I3Net, adapted SAINT-style and internal CycleINR-style')
text=text.replace('Full provenance and negative results are in the supplement.','Full provenance, unresolved release/ethics documentation and negative results are in the supplement. The present support and geometry checks are post-hoc sensitivities, separately frozen before calculation; they do not change the primary protocol.')
start=text.index('Figure~\\ref{fig:control} and Table~\\ref{tab:controlled}')
end=text.index('\n\\input{p17_control_table.tex}',start)
text=text[:start]+r'''Figure~\ref{fig:control} and Table~\ref{tab:controlled} re-express the original two-architecture clean comparison using one local estimand: the fraction of paired-error energy visible in disagreement. Shared and disjoint conditions use identical paired targets and the original prediction-derived support. Examinations/patients and models receive equal weight; series are first averaged within NingXia patients. Shared $O$ is small in every cohort, while disjoint evidence exposes more error. Historical pooled-plane ranking and stable-wrong prevalence remain in the supplement, with their original endpoints and aggregation. This descriptive re-expression does not create a new confirmatory experiment.
'''+text[end:]
text=text.replace(r'\input{p17_control_table.tex}',r'\input{local_control_table.tex}')
oldcaption='Controlled sharing and error observability. Left: pooled-plane disagreement ranking against a fixed endpoint: phase-0 error on fastMRI/NingXia, disjoint-pair mean error on IXI. Intervals are examination/patient-clustered pointwise 95\\%. Right: mean shared and observable paired-error fractions in clean shared HAT/SwinIR controls. Fractions describe error geometry; they are not independent evidence for the algebraic identity.'
newcaption=r'Local error observability in the original clean same-model experiment. (a) Shared/disjoint observable fractions, with pointwise 95\% patient/examination-bootstrap intervals. (b) Common versus observable energy under sharing, using the same observations and aggregation. Target planes, models and subordinate series are averaged before the independent unit. The energy decomposition is descriptive, not independent evidence for its own algebraic identity.'
assert oldcaption in text;text=text.replace(oldcaption,newcaption)
text=text.replace('Targets enter only error-alignment evaluation.}',r'Targets enter only error-alignment evaluation. (c) Signed coupled-minus-independent disagreement-energy change and the fixed $\epsilon_0=.0025$ local prediction, both models and all four amplitudes. Aggregate trends agree and median individual relative errors are 1.9--10.6\%, but the worst individual error is 126.4\%: there is no uniform Jacobian guarantee. Complete individual scatter is retained in the supplement.}')
needle='The examination-ranking boundary is substantial.'
sens=r'''\paragraph{Post-hoc support and geometry checks.}
The same predictions retain all 20 positive simultaneous local intervals per cohort under acquired-anchor foreground union and full-image support; pair-effect ordering changes by at most one rank. Residue-1 and residue-3 estimates, their equal-weight average, and nearest-distance matching also retain all 20 positive intervals. However, mirror differences exclude zero for 8 fastMRI and 6 IXI pairs. The stricter four-neighbor, two-residue contract is feasible on IXI and NA on shallow fastMRI volumes. Thus balancing preserves the phenomenon but does not remove orientation/context effects. Joint examination bootstrap preserves pair dependence; leave-one-architecture-out family summaries stay positive. Complete post-hoc matrices and family intervals are in the supplement; the 20 pairs are not independent replications.

'''
text=text.replace(needle,sens+needle)
text=text.replace('The substantive approximation test instead freezes','The substantive approximation test (Fig.~\\ref{fig:influence}c) instead freezes')
text=text.replace(r'\section{Discussion and Limitations}',r'\input{mira_report_card_table.tex}'+'\n\n'+r'\section{Discussion and Limitations}')
text=text.replace('The report card retains these levels separately, with NA for measurements absent from a design.','Table~\\ref{tab:mira-card} shows actual report cards with NA for measurements absent from each design.')
start=text.index('\\section{Conclusion}')
end=text.index('\\clearpage',start)
text=text[:start]+r'''\section{Conclusion}
Architectural diversity and evidence diversity are different axes. In these MRI interpolation experiments, different frozen architectures can inherit aligned error when they reuse the same measurements. Changing companion evidence reveals more of that error, including after support and residue-balancing checks, while residual orientation effects prevent a pure identity-only causal interpretation. Agreement among different networks therefore should not be treated as independent reliability evidence merely because their architectures differ.

MIRA makes this distinction testable through physical-anchor interventions, explicit information contracts and separate observability, influence and ranking fields. The acquired-only mechanism evidence is scoped to HAT/SwinIR on the two brain cohorts, and the fixed-context covariance trend has substantial individual nonlinear failures. Neither establishes universal ranking or calibrated uncertainty. MIRA measures when agreement loses observability, not whether an individual reconstruction is correct.

'''+text[end:]
(CV/'main.tex').write_text(text,encoding='utf-8')
# Clean reader-facing project names without changing numerical content.
mapping={'Plan 9/11': 'The historical architecture studies','Plan 9/11\'s':'The historical architecture studies\'','Plan-9':'historical architecture-family','Plan 9':'historical architecture-family','Plan-11':'IXI architecture','Plan 11':'IXI architecture','Plan-14':'external MRA','Plan 14':'external MRA','Plan-13':'robustness and inference','Plan 13':'robustness and inference','Plan-8':'earlier stable-wrong','Plan-7':'perturbation-stability'}
for i in range(1,7):
 s=(OLD/f'final_supp_{i}.tex').read_text(encoding='utf-8')
 for a,b in mapping.items():s=s.replace(a,b)
 s=s.replace('The The historical architecture studies','The historical architecture studies').replace('the historical architecture-family Architecture-Family Protocol','Historical Architecture-Family Protocol').replace('historical architecture-family Architecture-Family Protocol','Historical Architecture-Family Protocol')
 s=re.sub(r'\\path\{[^}]+\}',lambda m:'the final reproducibility and evidence map',s)
 (CV/f'final_supp_{i}.tex').write_text(s,encoding='utf-8')
s=(CV/'final_supp_4.tex').read_text(encoding='utf-8');s=s.replace(r'\subsection{Controlled Dependence Results}',r'''\subsection{Controlled Dependence Results}
The original pooled-plane ranking and stable-wrong summaries are retained here without changing their endpoints, thresholds or weights. They differ from the uniform local-error estimand used by the revised main Figure 2 and Table 1.
\begin{figure*}[t]\centering\includegraphics[width=.97\textwidth]{historical_ranking_prevalence.pdf}
\caption{Retained historical pooled-plane disagreement ranking and stable-wrong prevalence. Ranking uses fixed phase-0 MAE on fastMRI/NingXia and disjoint-pair MAE on IXI. Intervals resample examination/patient clusters; prevalence uses the original test-relative thresholds. Neither is an examination-level point correlation or calibrated event rate.}
\end{figure*}
\input{historical_control_table.tex}
''');(CV/'final_supp_4.tex').write_text(s,encoding='utf-8')
s=(OLD/'p17_control_table.tex').read_text(encoding='utf-8').replace('tab:controlled','tab:historical-controlled');(CV/'historical_control_table.tex').write_text(s,encoding='utf-8')
sup=(OLD/'supplement.tex').read_text(encoding='utf-8').replace(r'\input{final_supp_5.tex}',r'\input{submission_sensitivity.tex}'+'\n\\clearpage\n'+r'\input{final_supp_5.tex}')
(CV/'supplement.tex').write_text(sup,encoding='utf-8')
s=(CV/'final_supp_1.tex').read_text(encoding='utf-8')+r'''
\subsection{Data Attribution and Unresolved Author Documentation}
The brain T2 collection is locally catalogued as NYU fastMRI and converted from local DICOM series to NIfTI. The conversion manifest and physical-position/pixel-order checks trace the analyzed files, but do not authenticate an official download release or accession. We retain the fastMRI initiative citation required by its data portal, and add the brain challenge publication for brain-dataset context; we do not claim that our local split is the official challenge split. The author must confirm the precise release, access agreement and image-publication permission before submission. NYU fastMRI investigators supplied the attributed resource, without participating in this analysis or manuscript; this attribution is conditional on confirmation of local provenance.

IXI is attributed to the Biomedical Image Analysis Group at Imperial College London. Its public T2 NIfTI collection is described on the Brain Development website and distributed under CC BY-SA 3.0. Our local training/validation/test partition is separate from the source collection. No unsupported dataset publication year is assigned.

NingXia denotes a locally retained knee T2 collection with eight patient groups and 22 analyzed series. Acquisition institution, data custodian, release/allowed-use agreement, de-identification process, IRB approval or exemption, and consent or consent-waiver status are not established by the repository documents reviewed. Local patient-group splitting establishes analysis clustering, not ethics authorization or de-identification. \textbf{Author confirmation required before submission:} supply those records and the verified statement here; no approval number, consent waiver or permission is inferred. Direct identifiers found in raw directory naming are not reproduced in the manuscript or review package, and de-identification of the research extract cannot presently be certified.

TopCoW and CAS remain public-challenge training-collection analyses with locally available labels, not hidden-test evaluations. Dataset citations and the remaining local permission/release checks are listed in the final evidence map. No new subject data were acquired for this submission patch.
''';(CV/'final_supp_1.tex').write_text(s,encoding='utf-8')
s=(OLD/'final_supp_7.tex').read_text(encoding='utf-8')+r'''
\subsection{Submission Patch Evidence Map}
The separately frozen post-hoc patch is in \path{FINAL_SUBMISSION_PREPARATION/}. Its \path{FINAL_SUBMISSION_PATCH_PROTOCOL.md}, \path{ARRAY_FREEZE_MANIFEST.json} and \path{freeze.json} bind the accepted manuscript and all array inputs before calculation. \path{CROSS_ARCH_SUPPORT_SENSITIVITY.csv}, \path{CROSS_ARCH_GEOMETRY_SENSITIVITY.csv} and \path{CROSS_ARCH_FAMILY_ROBUSTNESS.csv} contain every pair and unavailable geometry contract. The frozen acquired-union rule comes from \path{PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/PROTOCOL.md}; reflection-class comparison follows \path{ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/scripts/p11_matched_geometry_identity.py}, with the new study's mean aggregation explicitly retained.

The patch's \path{reproduce_main.py --complete} reconstructs observations from preserved arrays into its own output directory. \path{REPRODUCTION_CHECK.md}, \path{UPDATED_CLAIM_EVIDENCE_MATRIX.md} and \path{DATA_ETHICS_CITATION_AUDIT.md} separate numerical checks, interpretation limits, and unresolved author documentation. Legacy file names are retained only for traceability; reader-facing sections use scientific descriptions. Existing \path{PLAN13_EVIDENCE_UPGRADE/}, \path{PLAN14_SCIENTIFIC_STRENGTHENING/} and \path{PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/} retain the complete historical provenance and adverse results.
''';(CV/'final_supp_7.tex').write_text(s,encoding='utf-8')
bib=(OLD/'references.bib').read_text(encoding='utf-8').replace('title={{IXI} Dataset},year={2014}','title={{IXI} Dataset}').replace('Accessed 2026-08-13','Accessed 2026-09-12')
bib+=r'''
@inproceedings{chen2023hat,author={Chen, Xiangyu and Wang, Xintao and Zhou, Jiantao and Qiao, Yu and Dong, Chao},title={Activating More Pixels in Image Super-Resolution Transformer},booktitle={CVPR},year={2023},pages={22367--22377}}
@inproceedings{liang2021swinir,author={Liang, Jingyun and Cao, Jiezhang and Sun, Guolei and Zhang, Kai and Van Gool, Luc and Timofte, Radu},title={{SwinIR}: Image Restoration Using Swin Transformer},booktitle={ICCV Workshops},year={2021},pages={1833--1844}}
@article{muckley2021brain,author={Muckley, Matthew J. and Riemenschneider, Bruno and Radmanesh, Alireza and others},title={Results of the 2020 {fastMRI} Challenge for Machine Learning {MR} Image Reconstruction},journal={IEEE Transactions on Medical Imaging},year={2021},doi={10.1109/TMI.2021.3075856}}
@misc{fastmri_portal,author={{NYU Langone Health}},title={{fastMRI} Dataset: Brain Collection and Data Sharing Agreement},url={https://fastmri.med.nyu.edu/},note={Accessed 2026-09-12}}
'''
(CV/'references.bib').write_text(bib,encoding='utf-8')
print('Main and supplement edited from immutable accepted snapshot')
