"""Build a reviewable manuscript copy; originals are installed only after checks."""
from common import *
import re,shutil
OLD=P/'original_snapshot/design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER'
NEW=P/'revised_manuscript';NEW.mkdir(exist_ok=True)

def replace(text,old,new):
    assert old in text,old[:100]
    return text.replace(old,new,1)

def main():
    # Do not overwrite original files or assets while preparing the revision.
    for source in OLD.iterdir():
        if source.is_file() and source.suffix in ['.tex','.bib','.sty','.bst','.pdf','.png','.cls']:shutil.copy2(source,NEW/source.name)
    shutil.copytree(OLD/'figures',NEW/'figures',dirs_exist_ok=True)
    t=(OLD/'main.tex').read_text(encoding='utf-8')
    abstract=r'''Prediction agreement can hide error when shared measurements drive similar reconstruction responses. We introduce the Measurement-Influence Reliability Audit (MIRA), combining same-target measurement interventions, error-energy decomposition, and local response analysis with frozen estimators. The decomposition is elementary; the empirical question is whether changing physical evidence dependence exposes common error beyond same-network test-time augmentation. Across all 20 ordered pairs of five architecture implementations, disjoint companion evidence increases observable error by 6.2--16.0 percentage points on fastMRI and 13.1--28.5 on IXI, with simultaneous intervals above zero. Acquired-only HAT/SwinIR probes contain information beyond anchor count on both brain cohorts, including an exactly-one-anchor test. A fixed-context neural perturbation experiment supports the covariance model's local trend while retaining nonlinear approximation failures. Examination ranking is less consistent: fixed-reference gains pass simultaneous inference for 16 of 20 IXI pairs and no fastMRI pair. MIRA returns separate evidence and eligibility fields, not a calibrated correctness score. These retrospective results show why architectural diversity and prediction agreement alone cannot certify reliability under shared influential measurements.'''
    t=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',t,flags=re.S)
    t=replace(t,'p17_qualitative_teaser.pdf','final_fig1_physical_anchors.pdf')
    oldcap=t[t.index(r'\caption{Agreement hides'):t.index(r'\label{fig:teaser}')]
    t=replace(t,oldcap,r'''\caption{Shared measurements can conceal aligned error. A fixed median-effect fastMRI example uses frozen SwinIR weights. Physical anchor strips identify reused and distinct measurements; the target and prediction A are identical across rows. Shared inputs give small disagreement despite substantial error. Disjoint inputs expose more of that error. All error and disagreement maps share one scale. The supplement gives the fixed selection rule, precision check and a seeded random example.}
''')
    t=replace(t,'We retain the original failures and one additional limited scoring test rather than make successful deployment a prerequisite for a coherent mechanism paper.','We distinguish evidence for a conditional mechanism from evidence for useful error ranking, and retain the failures of attempted scalar scores.')
    t=replace(t,'Our contributions are: (1) a same-target measurement audit usable with frozen estimators and explicit information-access contracts; (2) a local covariance explanation and an implementation-matched influence measure for common-error blindness; and (3) replication and falsification across cohorts and architecture lineages, separating robust local observability effects from weaker case-ranking consequences. The study is a retrospective synthesis of iteratively developed experiments. Its provenance audit does not establish that every historical choice preceded outcome inspection.',r'''Our contributions are: (1) an executable same-target audit with explicit information contracts and separate evidence fields; (2) a physical-anchor response analysis linked to a conditional covariance model; and (3) cross-architecture interventions, acquired-only influence tests and local neural validation that separate observability from ranking. The project is retrospective. The final three analyses were frozen before their inference, but use cohorts that already informed earlier development.''')
    start=t.index(r'\section{Related Work}');end=t.index(r'\section{Our Measurement-Influence Framework}')
    related=r'''\section{Related Work}
\paragraph{Diversity, covariance and uncertainty.}
The interaction between ensemble error and diversity is established by ambiguity decompositions, negative-correlation learning and diversity measures~\cite{krogh1994ensembles,liu1999negative,kuncheva2003measures,brown2005diversity,ortega2022diversity}. Random-subspace methods and gradient-diversity training already diversify inputs or sensitivities~\cite{ho1998random,kariyappa2019diversity}. We do not claim a new error identity or that diversity first becomes meaningful through MIRA. Our distinction is a controlled physical-measurement intervention with frozen, possibly different estimators, a response audit and explicit failure boundaries.

\paragraph{MRI uncertainty and practical reliability.}
Deep ensembles, dropout, TTA and posterior reconstruction characterize predictive variation~\cite{lakshminarayanan2017ensembles,gal2016dropout,wang2019aleatoric,edupuganti2021uncertainty,narnhofer2022bayesian,luo2023diffusion}. Hu \etal distinguish random and systematic MRI error~\cite{hu2021predict}; common-error blindness is not new. Unlike a posterior sampler, MIRA tests how measurement identity and local responses affect the interpretation of deterministic agreement. Error/OOD detection and selective prediction evaluate actionable ranking or abstention~\cite{hendrycks2017baseline,geifman2017selective}. Our local energy result does not establish those downstream properties, and the scoring failures remain relevant.

\paragraph{Consistency and interpolation.}
Acquired-data consistency~\cite{lustig2010spirit} differs from agreement between two missing-slice estimates. We audit HAT/SwinIR and frozen I3Net, SAINT-style and CycleINR-style implementations~\cite{song2024i3net,peng2020saint,fang2024cycleinr}, without proposing an interpolator. Complementary acquisitions and held-out acquired-slice checks are established~\cite{greenspan2002interslice,nicastro2022shift,horvath2017highorder}. The question here is when agreement hides error, not whether complementary slices or interpolation holdouts are new.

'''
    t=t[:start]+related+t[end:]
    t=replace(t,'Let $F$ be a frozen reconstruction estimator and $c_a,c_b$ two contexts for target location $z$.','Let $F_a,F_b$ be frozen reconstruction estimators (possibly identical) and $c_a,c_b$ two contexts for target location $z$.')
    t=replace(t,'The framework takes $F$, target location $z$, two target-preserving contexts, and a registry of physical anchor identities.','The framework takes frozen $F_a,F_b$, target location $z$, two target-preserving contexts, and a registry of physical anchor identities.')
    t=replace(t,'The intervention holds the target and estimator fixed while varying anchor identity;','The intervention holds the target and estimator identities fixed while varying anchor identity;')
    insert='Nearest-anchor distances can be matched as the multiset $\\{1,3\\}$ up to reflection, but full signed geometry and context normalization may still differ.'
    t=replace(t,insert,insert+' The cross-architecture experiment instead compares $A_0/B_0$ with the identical $A_0/B_2$, without a flip or other TTA. This directly tests whether the phenomenon extends beyond same-network equivariance.')
    old=r"\textbf{Output:} an audit of agreement's limitations in this measurement regime; no per-case correctness certificate.\par"
    t=replace(t,old,r'''\textbf{Output report card:} (i) local observability gap; (ii) named examination-ranking gap; (iii) beyond-count advantage; (iv) fixed-count association; (v) stability PASS/FAIL/NA; (vi) information contract; (vii) claim eligibility. Unmeasured fields remain NA; no combined scalar.\par''')
    t=t.replace(r'\textbf{Input:} frozen $F$;',r'\textbf{Input:} frozen $F_a,F_b$;')
    start=t.index('Historical probes use four centered Rademacher fields');end=t.index(r'\subsection{Reliability interpretation',start)
    t=t[:start]+r'''We use four centered Rademacher fields, primary amplitude .01 and alternatives .005/.02/$-.01$. Clipping is part of the finite response. The new acquired-only experiment fixes its mask and Q99--Q1 scale from acquired slices before responses, then accesses targets only for evaluation. FP32 without AMP/TF32 is fixed in its protocol. Historical full-examination scales and target-derived masks remain a different contract. HAT/SwinIR use the historical per-stratum .85 rank-stability criterion; the separate new-architecture gate is .90. Passing a numerical gate does not establish global Jacobian accuracy.

'''+t[end:]
    start=t.index(r'\section{Experimental Design and Provenance}');end=t.index(r'\section{Results}',start)
    t=t[:start]+r'''\section{Experimental Design and Provenance}
\paragraph{Cohorts and frozen implementations.}
We use 24 fastMRI brain T2 examinations~\cite{knoll2020fastmri}, 115 IXI brain T2 examinations~\cite{ixi_dataset}, and 22 NingXia knee T2 series from eight patients. Existing dataset-specific training splits or patient-group out-of-fold models supply the weights. HAT/SwinIR cover all three cohorts; I3Net, adapted SAINT-style and internal CycleINR-style add three brain-cohort lineages. These are frozen local implementations, not claims of exact official reproductions. All 695 legacy phase-0 case/model wrapper outputs were reproduced exactly. New SAINT predictions use physical $z/(\mathrm{source\ depth}-1)$ coordinates in both phases, with legacy coordinates reproduced separately.

\paragraph{Three final analyses.}
(1) All 20 ordered cross-architecture pairs per brain cohort use five missing planes per examination and one identical target-derived 1\% mask. The fixed reference $A_0$ is unchanged. (2) Acquired-only influence uses both HAT/SwinIR, three depth-selected targets, reference $(-2,+2)$ and eight non-self contexts from offsets $\{\pm1,\pm2,\pm3\}$. Four contexts share exactly one anchor. A six-plane acquired pool defines a common scale; the nearest acquired foreground union defines support. (3) Twelve hash-selected IXI examinations test coupled versus independent perturbations at fixed nominal contexts, both models and all four one-anchor comparators. The supplement gives complete geometry, precision and noise settings. No new scalar score or threshold search follows these analyses.

\paragraph{Statistical units and study status.}
Examinations are independent units; NingXia resamples patients with all subordinate observations. New cross-architecture points average five planes within each examination, then average examinations. Ranking correlates examination means. New influence points pool planes/contexts, with examination bootstrap and fixed-count geometry/examination adjustment. Simultaneous 95\% intervals use 5,000 paired examination draws and maximum standardized deviation: 20 ordered pairs per cohort/endpoint, two models per influence cohort/endpoint, or eight model/amplitude contrasts. Original pooled-plane controls and historical five-model inference remain separately labeled.

The final protocol, inputs, masks, checkpoints and case/pair registries were frozen before new inference. This is a frozen retrospective iteration, not preregistration or an untouched holdout. Earlier outcomes informed the project; some historical controls and endpoints evolved. Local IDs show one fastMRI training/validation patient overlap but no test overlap, disjoint IXI IDs and patient-group NingXia folds. Selection uncertainty across the research history is outside the reported bootstrap intervals. Full provenance and negative results are in the supplement.

'''+t[end:]
    start=t.index(r'\subsection{Mechanism: influence');end=t.index(r'\section{Discussion and Limitations}')
    results=r'''\subsection{Mechanism: acquired-only influence beyond count}
Overlap count is not a monotone dose: the analytical ladder reverses from zero to one shared anchor in every original cohort. The new acquired-only probe asks whether continuous response influence retains information when neither its scale nor support accesses the missing target. On IXI, beyond-count alignment advantages are .098/.093 for HAT/SwinIR; on fastMRI they are .103/.093. Every two-model simultaneous interval is positive (Fig.~\ref{fig:influence}, Table~\ref{tab:neural}). At exactly one shared anchor, partial associations adjusting span, asymmetry and examination are .270/.265 on IXI and .474/.365 on fastMRI, again with positive simultaneous intervals.

\begin{figure*}[t]
\centering\includegraphics[width=.98\textwidth]{final_fig3_acquired_influence.pdf}
\caption{Influence formed with acquired-only masks and scales. (a) Absolute alignment-correlation advantage over count on the non-self grid. (b) Partial influence--alignment correlation at exactly one shared anchor, adjusting geometry and examination. Points pool planes/contexts; 95\% intervals resample examinations and are simultaneous across both models separately per cohort/endpoint. Targets enter only error-alignment evaluation.}
\label{fig:influence}
\end{figure*}
\input{final_acquired_table.tex}

All twelve amplitude/sign rank checks exceed .85 (minimum .880). The original aggregate six-stratum gate is NA because NingXia was not rerun under this contract. Historical results are not relabeled acquired-only: their non-self advantages remain positive, but NingXia's fixed-count result is null/mixed, SAINT's beyond-count interval crosses zero, and I3Net/CycleINR fail their separate .90 stability gate. Numerical stability, association and information access are distinct requirements.

\subsection{Cross-architecture sharing beyond TTA}
All 20 ordered pairs on each brain cohort show a positive local observable gain with simultaneous intervals above zero: 6.2--16.0 percentage points on fastMRI and 13.1--28.5 on IXI (Fig.~\ref{fig:arch}). Error alignment decreases and disagreement increases in every pair. The result therefore extends beyond same-network flip equivariance. It does not establish a pure effect of identity with every nuisance fixed: companion geometry, accuracy, normalization and nonlinear response may also change.

\begin{figure*}[t]
\centering\includegraphics[width=.98\textwidth]{final_fig4_cross_architecture.pdf}
\caption{All cross-architecture measurement interventions, without TTA. Row A retains its phase-0 prediction; column B changes from phase 0 to phase 2 at the same target. Cells show mean observable-fraction gains in percentage points. Stars indicate simultaneous 95\% intervals excluding zero across all 20 ordered pairs per cohort. Diagonals are outside this cross-architecture design. The target-derived mask is identical across pairs and conditions.}
\label{fig:arch}
\end{figure*}

The examination-ranking boundary is substantial. Fixed-reference A-error ranking has 16 positive simultaneous intervals on IXI and four crossing zero (all with I3Net as companion); all 20 fastMRI intervals cross zero, including one negative point estimate. Condition-specific paired-error ranking has 20 positive intervals on IXI and none on fastMRI. Those endpoints are not interchangeable. The historical same-model five-architecture local effects and weaker ranking results remain in the supplement, together with the earlier analytical two-member ensemble contrast. Architecture diversity alone does not eliminate measurement dependence, and improved local observability does not imply universal ranking improvement.

\subsection{A fixed-context neural test of the local model}
At fixed nominal inputs, coupled perturbations reuse eight balanced fields on the common anchor; independent perturbations use their full $8\times8$ Cartesian product. Empirical marginals are identical. The matched finite-response covariance closes $\Delta\mathbb E D^2=-2\kappa$ numerically, which is an algebraic check. The substantive approximation test instead freezes the odd response at $\epsilon_0=.0025$ and predicts effects at .0025/.005/.01/.02 by $\epsilon^2$ scaling.

All eight model/amplitude mean effects are negative with simultaneous intervals below zero. Median relative approximation errors range from 1.9\% to 10.6\%; the worst individual error is 126.4\%, so the local trend is not a uniform approximation guarantee. Of 96 model/case/context combinations, 86 have aligned and 10 near-orthogonal reference sensitivities; none is opposing. All are retained. The experiment supports a conditional local sensitivity explanation, not the proposition's unobserved opposing-sensitivity branch or a claim that phase changes preserve bias/Jacobians.

\paragraph{Actionable scoring remains unresolved.}
The single acquired-only guard has no positive internal-evaluation cases and only two per pair on IXI; every IXI guard-minus-baseline simultaneous AP interval crosses zero. Its full negative evaluation and the earlier context-selection, jackknife and residualization failures remain in the supplement; no further score is searched.

'''
    t=t[:start]+results+t[end:]
    t=replace(t,'fig2_controlled_intervention.pdf','final_fig2_original_control.pdf')
    t=replace(t,'Left: pooled-plane disagreement ranking against fixed phase-0 error, with examination/patient-clustered pointwise 95\\% intervals.','Left: pooled-plane disagreement ranking against a fixed endpoint: phase-0 error on fastMRI/NingXia, disjoint-pair mean error on IXI. Intervals are examination/patient-clustered pointwise 95\\%.')
    t=replace(t,'The five-architecture case-ranking test is reported separately below.','The new cross-architecture examination-ranking test is reported separately below.')
    start=t.index(r'\section{Discussion and Limitations}');end=t.index(r'\clearpage',start)
    t=t[:start]+r'''\section{Discussion and Limitations}
MIRA separates replicated local observability loss, conditional influence/ranking support, and unestablished actionable reliability. Cross-architecture interventions address a TTA-only explanation; acquired-only probes address target-derived influence formation; fixed-context perturbations test a local approximation separately from its algebraic identity. None identifies arbitrary common bias without targets. The report card retains these levels separately, with NA for measurements absent from a design.

The principal limitations remain retrospective cohort reuse, incomplete historical selection chronology, residual phase-geometry/preprocessing changes, adapted implementations and limited independent patient counts. The acquired-only neural result covers two models and two brain cohorts; it does not erase the historical knee and new-architecture failures. No authenticated untouched cohort was available for the optional final confirmation. Sampling intervals do not account for the full history of analysis selection. Local perturbations are not a validated clinical noise model.

All 13 baseline models, 111 configurations and training-budget comparisons remain in the supplement, with adverse results intact. They establish breadth of reconstruction evidence, not a new reconstruction method. Current-error adjustment weakens retrospective densification associations, Res-SRDiff retains an adverse boundary, and no clinical, prospective acquisition or non-MRI benefit is established.

\section{Conclusion}
Shared influential measurements can make even different frozen architectures agree on errors. A same-target intervention, acquired-only response audit and conditional local model make this failure measurable. The strongest result is local error observability; examination ranking and useful target-free scoring require separate evidence.

'''+t[end:]
    t=t.replace('kuncheva2003measures','kuncheva2003diversity').replace('ho1998random','ho1998subspace').replace('wang2019aleatoric','wang2019tta')
    (NEW/'main.tex').write_text(t,encoding='utf-8')
    c=(OLD/'p17_control_table.tex').read_text(encoding='utf-8')
    c=c.replace('fixed phase-0 error','a fixed endpoint (phase-0 MAE on fastMRI/NingXia; disjoint-pair mean MAE on IXI)')
    (NEW/'p17_control_table.tex').write_text(c,encoding='utf-8')
    (NEW/'references.bib').write_text((OLD/'references.bib').read_text(encoding='utf-8')+'\n'+(P/'added_references.bib').read_text(encoding='utf-8'),encoding='utf-8')
    df=pd.read_csv(OUT/'array_reproduced/acquired_only_summary.csv').set_index(['dataset','model','endpoint']);st=pd.read_csv(P/'acquired_only_stability.csv');lines=[]
    for ds in ['ixi','fastmri']:
        for model in ['hat','swinir']:
            a=df.loc[(ds,model,'beyond_count')];b=df.loc[(ds,model,'fixed_count')];v=st[(st.dataset==ds)&(st.model==model)].rank_stability.min()
            lines.append(f"{'IXI' if ds=='ixi' else 'fastMRI'} & {'HAT' if model=='hat' else 'SwinIR'} & {a.estimate:.3f} [{a.simultaneous_low:.3f},{a.simultaneous_high:.3f}] & {b.estimate:.3f} [{b.simultaneous_low:.3f},{b.simultaneous_high:.3f}] & {v:.3f} / PASS \\\\")
    table=r'''\begin{table*}[t]
\centering\small
\caption{Acquired-only neural influence. Beyond-count and fixed-one-anchor estimates have simultaneous 95\% intervals across both models, separately by cohort/endpoint. Stability is the minimum of three amplitude/sign correlations; the historical per-stratum threshold is .85.}
\label{tab:neural}
\setlength{\tabcolsep}{5pt}
\begin{tabular}{llrrr}\toprule
Cohort & Model & $|\rho_I|-|\rho_{count}|$ [CI] & Fixed-count partial $\rho$ [CI] & Minimum stability / status\\\midrule
'''+ '\n'.join(lines)+r'''
\bottomrule\end{tabular}
\end{table*}
'''
    (NEW/'final_acquired_table.tex').write_text(table,encoding='utf-8')
    for source in (P/'figures').glob('final_*.pdf'):shutil.copy2(source,NEW/source.name)
    print('Reviewable main draft prepared',len(t.split()),'whitespace words',flush=True)
if __name__=='__main__':main()
