"""Deterministic manuscript revision from the protected Plan-12 snapshot."""
from pathlib import Path
import re

P13=Path(__file__).resolve().parents[1]; PAPER=P13.parent; SNAP=P13/'original_snapshot'
CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'; TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED'
def original(path): return (SNAP/path.relative_to(PAPER)).read_text(encoding='utf-8')
def replace(s,old,new):
    assert old in s,old[:100]
    return s.replace(old,new)

c=original(CV/'main.tex')
c=replace(c,'Phase-0 wrappers reproduce every stored fastMRI and IXI output exactly.',
 'Phase-0 wrappers reproduce all 24 fastMRI outputs per model and one frozen IXI examination per model exactly.')
c=replace(c,'Dense slices create retrospective anchors and evaluate errors but never enter a reliability score.',
 'Dense volumes supply retrospective anchors and targets. Input-only scores use acquired anchors; the five-architecture and candidate-bank output scores use target-derived evaluation masks and are not fully target-free pipelines.')
c=replace(c,'Finally, a rule-frozen retrospective audit holds the reconstruction model fixed between',
 'Finally, a rule-frozen retrospective audit matches model identity between')
c=replace(c,'The supported contribution is a bounded physical-dependence--error-geometry mechanism, not calibrated uncertainty, universal score superiority, or prospective acquisition benefit.',
 'Exploratory controls retain local gains under simultaneous inference but weaken ranking and benefit claims. The contribution is a bounded error-geometry mechanism, not calibrated uncertainty or prospective acquisition benefit.')
c=replace(c,'The retrospective benefit endpoint is common-support',
 'Matching model identity does not hold factor-specific learned weights fixed. The retrospective benefit endpoint is common-support')
c=replace(c,'This is evidence for a local mechanism, not causal mediation or a universal ranking theorem.',
 'The cancellation arrow is constrained by the energy identity; its correlation is not independent mechanistic validation. The empirical evidence is the controlled change in error geometry, not causal mediation.')
c=replace(c,'{fig_architecture_replication.pdf}','{p13_architecture_robustness.pdf}')
oldcap='Architecture-family replication. (a) Local observable gain is positive on fastMRI and IXI; hollow squares additionally balance the two reflection-equivalent IXI residue classes. Frozen cohort summaries use the mean on fastMRI and median on IXI and are not pooled. (b) Ranking improvement is positive for all five IXI models but remains imprecise or null for four fastMRI models.'
newcap=r'Architecture replication and multiplicity sensitivity. (a) Local gains retain positive five-model simultaneous 95\% intervals (10,000 examination bootstraps); fastMRI uses means and IXI medians. (b) Thick bars are historical pointwise intervals; thin bars are simultaneous intervals with within-case median ranking. Simultaneous ranking intervals exclude zero for three IXI models and none on fastMRI. Cohorts are not pooled.'
c=replace(c,oldcap,newcap)
c=replace(c,'Local error geometry replicates more uniformly than examination ordering.',
 'An exploratory 10,000-bootstrap reanalysis keeps local gains positive for every model under all four within-/between-case mean/median combinations. Five-model simultaneous ranking intervals are positive for only HAT, SwinIR, and SAINT on IXI and none on fastMRI. Local geometry is more robust than ordering.')
c=replace(c,'Holding the reconstruction model fixed removes the previous estimator-switch ambiguity.',
 'Matching model labels removes a cross-architecture switch, but factor-specific checkpoints can differ.')
c=replace(c,'The practical claim is therefore limited to inexpensive retrospective prioritization for most evaluated models. It is not a randomized acquisition effect or a universal guarantee.',
 r'Controlling current $\times4$ MAE reduces Anchor-CV median partial $\rho$ to .203/.291; all 26 clustered intervals cross zero. A recovered 115-case IXI I3Net same-architecture analysis gives $\rho=.843$ [.768,.894], versus .845 [.771,.896] for adjacent MAE. Acquired-range normalization reverses these raw-benefit rankings to $-.238/- .236$. Thus benefit ranking depends on scale and current difficulty, not only acquisition value.')
c=c.replace('$-.238/- .236$','$-.238/-.236$')
c=replace(c,'The reviewer-memory message is simple: \\emph{disagreement is only as informative as the independence of the information generating the compared predictions}.',
 'The central finding is that physical measurement dependence changes which paired-error components survive in disagreement.')
c=replace(c,'The same-model $\\times2$ consequence is a post-reconstruction retrospective audit on dense acquisitions; IXI lacks the corresponding broad same-model matrix, and scanner time, motion, and clinical cost are absent.',
 'Densification remains retrospective and compares factor-specific checkpoints. IXI adds one same-architecture pair, not a broad matrix. Scanner time, motion, and clinical cost are absent; target-derived output masks require separate deployment validation.')
# Tighten repetitive interpretive prose to keep the technical 8-page envelope.
c=replace(c,'Plane dependence is not a failed invariance theorem because the final claim is local: influence belongs to a target--context--input configuration. It would contradict a claim of one intrinsic global model coefficient; we make no such claim.',
 'Influence is local to a target--context--input configuration, not an intrinsic global model coefficient.')
c=replace(c,'This prevents both an underpowered nonreplication from erasing the primary effect and selective omission from overstating universality.','')
c=replace(c,'Training-free posterior approximation also addresses uncertainty in computational inverse problems \\cite{zhang2024trainingfree}.',
 'Training-free posterior approximation addresses inverse problems \\cite{zhang2024trainingfree}, while conformal quantile regression estimates MRI error intervals \\cite{giannakopoulos2026pixelwise}.')
(CV/'main.tex').write_text(c,encoding='utf-8')

s=original(CV/'supplement.tex')
s=replace(s,'The five phase-0 wrappers reproduce the stored benchmark volumes with zero maximum absolute error.',
 'Each of the five phase-0 wrappers reproduces one frozen IXI examination (IXI012) with zero maximum absolute error; this is a wrapper gate, not a 115-case reproduction audit.')
s=replace(s,'Dense target slices are used only for retrospective evaluation and never in Anchor-CV, adjacent-anchor, disagreement, or influence scores.',
 r'Missing target values are not subtracted in a disagreement score, but its evaluation support can be target-derived. Plan 9/11 and the recovered bank use a ground-truth 1\% mask. Anchor-CV uses held-out acquired anchors (including their masks); adjacent MAE uses masks from acquired pairs. These information regimes must not be conflated.')
s=s.replace('single dataset-grouped table','cohort-specific tables').replace('in a single dataset-grouped table','in cohort-specific tables')
s=replace(s,'in a single dataset-grouped table','in cohort-specific tables') if 'in a single dataset-grouped table' in s else s
s=replace(s,'Every clean and reflection-balanced gain interval is positive, and every model has a positive effect in all 115 examinations.',
 'Every historical pointwise clean and reflection-balanced gain interval is positive, and every model has a positive effect in all 115 examinations.')
for name in ['PLAN9_ARCH_GENERALIZATION','PLAN10_ACCEPTANCE_ITERATION','PLAN11_CLAIM_STRENGTHENING','PLAN12_STRICT_REVIEW_ITERATION']:
    s=s.replace('\\path{'+name+'/', '\\path{ARCHIVE/PLANS/'+name+'/')
s=replace(s,'\\section{Material Negative and Boundary Results}',r'\input{p13_additional_analysis.tex}'+'\n\n'+r'\section{Material Negative and Boundary Results}')
(CV/'supplement.tex').write_text(s,encoding='utf-8')

t=original(TMI/'main.tex')
t=replace(t,'All phase-0 wrappers reproduce their reference predictions exactly.',
 'Phase-0 reproduction is exact on all 24 fastMRI examinations per model and one frozen IXI examination per model.')
abstract=r'''Deterministic magnetic resonance slice interpolation can produce agreeing predictions with substantial shared error. We examine how physical measurement dependence affects this blind spot in 24 fastMRI brain examinations, 115 IXI brain examinations, and 22 NingXia knee series from eight patients. Target-preserving comparisons distinguish historical order-reversal controls from clean in-plane sharing controls. Five neural architectures on both brain cohorts show positive disjoint-minus-shared observable-error gains, ranging from 8.0 to 30.2 percentage points. Exploratory simultaneous intervals retain these local gains, while examination-ranking improvement is less robust. Multi-endpoint analysis retains weak structural-error ranking, intensity-scale sensitivity, and rare stable-wrong events. Shared-energy and normalized-disagreement associations are structurally coupled and are treated as descriptive decompositions. In retrospective densification audits, matching model labels does not hold factor-specific weights fixed. Anchor cross-validation has positive raw benefit association in most recovered models, but all 26 fastMRI and NingXia intervals cross zero after conditioning on current error. An additional common-support I3Net analysis covers 115 IXI examinations: raw anchor cross-validation and adjacent-anchor scores correlate with benefit at 0.843 and 0.845, whereas acquired-range normalization reverses both raw-benefit rankings. Output-score evaluations also use target-derived masks in several experiments. The evidence supports a bounded measurement-dependence mechanism and technical quality-assurance study, with explicit information-availability constraints; it does not establish calibrated uncertainty, diagnostic safety, or prospective acquisition utility.'''
t=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _: '\\begin{abstract}\n'+abstract+'\n\\end{abstract}',t,flags=re.S)
t=replace(t,'These methods learn or sample predictive distributions.',
 'Recent conformal quantile regression estimates pixelwise MRI error intervals \\cite{giannakopoulos2026pixelwise}. These methods learn, calibrate, or sample predictive distributions.')
t=replace(t,'For paired predictions $a,b$, the primary score was mean $|a-b|$ on a fixed foreground mask. Dense targets entered only retrospective acquisition synthesis and evaluation.',
 r'For paired predictions $a,b$, the score is mean $|a-b|$ on the declared foreground mask. Plan 9/11 and candidate-bank scores use a target-derived 1\% mask: the score support therefore accesses the dense reference. The clean legacy flip analysis uses a phase-0 prediction mask. Acquired-anchor scores use only observed slices. These are retrospective evaluations, not uniformly target-free pipelines.')
t=replace(t,'Normalized disagreement divides paired RMSE by total-error scale, making the conditional analysis sensitive to allocation of fixed error energy rather than simply its magnitude.',
 r'''The stored normalized statistic is $D_1=\mathrm{MAE}(a-b)/\sqrt{T}$, not RMSE disagreement. It obeys
\begin{equation}
D_1=2\kappa\sqrt{1-q},\qquad
\kappa=\frac{\mathrm{MAE}(a-b)}{\mathrm{RMSE}(a-b)}\in[0,1].
\label{eq:coupling}
\end{equation}
For nonzero disagreement, $\kappa$ describes residual shape. Thus the normalized-disagreement/shared-fraction association is structurally coupled and cannot independently validate the mechanism.''')
t=replace(t,'Thus suppression was not merely caused by low-error images having small output differences. Equation~\\ref{eq:decomp} closed to numerical precision.',
 'These are descriptive associations constrained by Eq.~\\ref{eq:coupling}, not independent tests of error cancellation. The stored MAE normalization factorizes to numerical precision after retaining the residual-shape term.')
t=replace(t,'In all 12 strata, more shared error energy predicts less observable disagreement conditional on total error and examination.',
 'The distributions describe error allocation; normalized disagreement and shared fraction are structurally coupled by Eq.~\\ref{eq:coupling}.')
t=replace(t,'For the retrospective densification audit, benefit is common-support',
 'The exploratory sensitivity analysis uses 10,000 paired cluster bootstrap replicates and five-model simultaneous intervals from the bootstrap maximum absolute standardized deviation. A same-label densification comparison can use different factor-specific checkpoints. Benefit is common-support')
t=replace(t,'A score can rank current error without identifying cases that benefit from denser sampling. We therefore evaluated stored $\\times4\\rightarrow\\times2$ improvement as a separate consequence while holding the reconstruction model fixed.',
 'A score can rank current error without identifying incremental benefit. We evaluate stored $\\times4\\rightarrow\\times2$ improvement with matched model labels and common target support; this does not fix factor-specific learned weights.')
t=replace(t,'This result supports examination-level retrospective prioritization for most evaluated models, not prospective policy or a unique score. Dense source acquisitions, model outputs, and potential benefit were already available, and no scanner randomized sampling density. The older IXI analysis compared HAT/SwinIR $\\times4$ with I3Net $\\times2$ and is retained only as cross-estimator sensitivity evidence, not as the same-model treatment estimand.',
 r'''Since benefit contains current $\times4$ error, we also condition on its rank. Anchor-CV median partial correlation falls from .851/.727 to .203/.291 on fastMRI/NingXia; all 26 model--cohort intervals cross zero. This weakens a claim of incremental benefit information beyond current difficulty.

We additionally recover a same-architecture I3Net pair on all 115 IXI examinations. Different $\times2/\times4$ checkpoint hashes are recorded. Re-evaluation uses 7,334 common odd planes, identical target-derived masks and physical affines; case means are computed before examination bootstrap. Mean MAE falls from 33.65 to 25.62, with positive benefit in 115/115 cases. Linear interpolation on the same support gives 57.36 and 39.21. Raw Anchor-CV and adjacent MAE correlate with benefit at .843 [.768,.894] and .845 [.771,.896]; conditional correlations are .216 [.007,.430] and .227 [.020,.437]. These are pointwise exploratory intervals.

Normalization by the acquired-anchor robust range reverses the raw-benefit correlations to $-.238$ [$-.404,-.058$] and $-.236$ [$-.397,-.060$]. At 50\% selection, normalized Anchor-CV is below random by .920 MAE units (95\% CI $[-1.635,-.149]$). This is a scale-sensitive ranking failure against a raw-scale endpoint, not a claim that normalization is always harmful. The third cohort adds one architecture, not a broad matrix or fixed-weight acquisition experiment.''')
t=replace(t,'{fig_architecture_replication.pdf}','{p13_architecture_robustness.pdf}')
t=replace(t,oldcap,newcap)
t=replace(t,'This is an architecture-specific rare phenotype, not a common prevalence estimate.',
 'This remains rare. Exploratory five-model simultaneous ranking intervals exclude zero for IXI HAT/SwinIR/SAINT only, and for no fastMRI model. In contrast, all local-gain simultaneous intervals remain positive under four mean/median aggregation choices.')
t=replace(t,'full $\\times2$ coverage','broad $\\times2$ coverage') if 'full $\\times2$ coverage' in t else t
t=replace(t,'The same-model densification audit is exploratory, lacks broad IXI $\\times2$ coverage, and is not an acquisition intervention.',
 'The densification audit is exploratory; IXI has only one recovered same-architecture pair, and factor-specific weights differ. Target-derived output masks require an acquired-only support validation before deployment.')
# Remove duplicated interpretation, not unique outcomes.
for start,end in [
 ('The resources deliberately differ in volume depth and intensity distribution.','\\subsection{Physical Matching and Scores}'),
 ('Figure~\\ref{fig:intensity} visualizes the scale boundary.','\\begin{figure}[t]'),
 ('Table~\\ref{tab:factors} gives the factor summaries.','\\begin{table}[t]'),
 ('\\subsection{Cohort Heterogeneity}','\\subsection{Comparator Semantics and Cost}'),
 ('\\subsection{Clinical Interpretation and Validation}','\\subsection{Limitations}'),
 ('\\begin{table*}[t]\n\\caption{Claim boundary summary}','\\subsection{Ethics and Data Availability}')]:
    assert start in t and end in t,start
    i=t.index(start); j=t.index(end,i); t=t[:i]+t[j:]
# Replace verbose benchmark framing; all unfavorable models remain in the table.
i=t.index('Table~\\ref{tab:arch-benchmark} places'); j=t.index('\\input{table_full_reconstruction_benchmark.tex}',i)
t=t[:i]+r'''Table~\ref{tab:arch-benchmark} retains every recovered model and factor, including degraded runs and unavailable cells. Its all-generated-plane support differs from the new IXI common-odd-plane analysis; the two estimates must not be interchanged. The table uses masked MAE to document estimator context. Complete PSNR, SSIM, and NCC values remain in the numerical record.

'''+t[j:]
t=replace(t,'The exact ethics and release record remains an author dependency. Public-data terms must be cited from the releases actually used, and internal NingXia approval/waiver language must identify the institution and decision. Until those fields are filled, the manuscript is scientifically compiled but not submission-ready.','')
# AI disclosure is factual, and does not pretend author verification already occurred.
t=replace(t,'\\section{Conclusion}',r'''\section*{Acknowledgment}
OpenAI Codex assisted with revision of the abstract and Sections II--VI, exploratory statistical scripts, and the architecture robustness figure. The source data are pre-existing; author verification of the generated material and the final disclosure is required before submission.

\section{Conclusion}''')
(TMI/'main.tex').write_text(t,encoding='utf-8')

newbib=r'''@article{giannakopoulos2026pixelwise,
 author={Giannakopoulos, Ilias I. and Gautham Muthukumar, Lokesh B. and Lui, Yvonne W. and Lattanzi, Riccardo},
 title={Pixel-Wise Uncertainty Quantification of Accelerated MRI Reconstruction},
 journal={Magnetic Resonance in Medicine}, year={2026}, doi={10.1002/mrm.70526}, note={Early view}
}
'''
for dest in [CV,TMI]:
    bib=original(dest/'references.bib')
    if dest==TMI:
        bib=re.sub(r'@article\{vandervelde2026prostate,.*?\n\}',lambda _:r'''@article{vandervelde2026prostate,
 author={van Lohuizen, Quintin and Fransen, Stefan J. and Huisman, Henkjan and Wolterink, Jelmer M. and Kwee, Thomas C. and Yakar, Derya and Simonis, Frank F. J.},
 title={Aleatoric Uncertainty in Accelerated Prostate MRI Reconstruction: Echo-Train Dropout Versus Gaussian Noise Monte Carlo Sampling},
 journal={Magnetic Resonance Materials in Physics, Biology and Medicine},
 year={2026}, doi={10.1007/s10334-026-01369-0}, note={Online ahead of print}
}''',bib,flags=re.S)
    bib=bib+'\n'+newbib
    if dest==TMI:
        def author_limit(match):
            names=match.group(1).split(' and ')
            return 'author={'+(names[0]+' and others' if len(names)>6 else match.group(1))+'},'
        bib=re.sub(r'author=\{(.*?)\},',author_limit,bib,flags=re.S)
    (dest/'references.bib').write_text(bib,encoding='utf-8')
# Final consistency: make the negative benefit findings visible in the conclusions.
for dest in [CV,TMI]:
    path=dest/'main.tex'
    text=path.read_text(encoding='utf-8')
    if dest==CV:
        text=replace(text,'A same-model audit supports retrospective prioritization for most evaluated models while retaining a degraded-model exception. Operational value still requires prospective validation for the acquisition and endpoint.','Raw same-model benefit associations are positive for most models, but current-error adjustment and acquired-range normalization expose important limits. Operational value still requires prospective validation for the acquisition and endpoint.')
    else:
        text=replace(text,'with RMSE-normalized disagreement after controlling total error and examination','with MAE disagreement normalized by paired-error RMS after controlling total error and examination')
        text=replace(text,'Ranking remains cohort dependent, different architectures continue to fail on many of the same examinations, and same-model retrospective benefit prediction retains a degraded-model exception.','Ranking remains cohort dependent, architectures share difficult examinations, and retrospective benefit prediction is limited by current-error coupling, intensity scale, and a degraded-model exception.')
    path.write_text(text,encoding='utf-8')
print('Revised CVPR, supplement and TMI from protected originals')
