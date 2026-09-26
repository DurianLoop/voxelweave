from common import *
import re
OLD=P/'original_snapshot/design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER';NEW=P/'revised_manuscript'

def chunks(text):
    matches=list(re.finditer(r'\\section\{([^}]+)\}',text))
    return [(m.group(1),text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)]) for i,m in enumerate(matches)]
def nested(text):return text.replace(r'\subsection{',r'\subsubsection{').replace(r'\section{',r'\subsection{')
def write_tex(name,t):(NEW/name).write_text(t,encoding='utf-8')
def ci(r):return f'{r.delta:.3f} [{r.simultaneous_low:.3f},{r.simultaneous_high:.3f}]'

def main():
    text=(OLD/'supplement.tex').read_text(encoding='utf-8');body=text.split(r'\maketitle',1)[1].split(r'\end{document}',1)[0]
    for name in ['p17_additional_material.tex','p13_additional_analysis.tex','p14_additional_analysis.tex','p15_baseline_supplement.tex']:
        body=body.replace(r'\input{'+name+'}',(OLD/name).read_text(encoding='utf-8'))
    body=body.replace(r'\clearpage','')
    # Correct semantics, not historical numeric outcomes.
    body=body.replace('The research ledger inventories 1,623 paper source files, 832 CSV files, 64 workspace split files, 1,336 available checkpoint candidates, and 655 training configurations. Candidate availability does not establish checkpoint usage:','The machine-readable research ledger records source, split, checkpoint and training-configuration provenance. Candidate availability does not establish checkpoint usage:')
    body=body.replace('against fixed phase-0 error while resampling','against a fixed endpoint (phase-0 MAE for fastMRI/NingXia; disjoint-pair mean MAE for IXI) while resampling')
    body=body.replace('Main Figure 3 and Table 2 now use this non-self result; their fixed-one-overlap estimates are unchanged.','The preserved historical non-self figure and table below use this result; the final main Figure 3 and Table 2 instead report the new acquired-only experiment. Historical fixed-one-overlap estimates are unchanged.')
    body=body.replace('complete target-free neural mechanism validation, and non-MRI generalization','universal target-free neural mechanism validation, and non-MRI generalization')
    body=body.replace(r'\path{RUN_COMMANDS_ZH.md}',r'\path{REPRODUCIBILITY.md}')
    body=body.replace('The horizontal-flip clean control preserves anchor identities, target, distances, count, $z$ order, mask, and preprocessing and is therefore the primary intervention.','The horizontal-flip clean control preserves anchor identities, target, distances, count, $z$ order, mask, and preprocessing and is the cleaner historical TTA intervention. The final cross-architecture primary experiment uses no TTA.')
    body=body.replace('Each of the five phase-0 wrappers reproduces one frozen IXI examination (IXI012) with zero maximum absolute error; this is a wrapper gate, not a 115-case reproduction audit.','The historical gate checked one IXI examination per wrapper. The final array audit additionally reproduces all 115 examinations per model with zero maximum absolute difference under the legacy mapping; new SAINT physical coordinates remain a separately declared correction.')
    body=body.replace('The resulting plane table contains exactly 5,750 rows (five models, 115 examinations, five targets, two conditions), with no duplicate keys or non-finite metric values.','All five models, examinations, five targets and both conditions remain, without duplicate keys or non-finite metric values.')
    groups=[[],[],[],[],[],[],[]];mapping={
      'Provenance, Implementation Correction, and Claim Levels':0,'Scope and Evidence Contract':0,
      'Framework Diagram and Full Covariance Derivation':1,
      'Definitions and Documented Protocol':2,'Plan-9 Architecture-Family Protocol':2,'Objective Qualitative Selection and Precision Check':2,
      'One Acquired-Only Guard: Full Negative Evaluation':4,'Material Negative and Boundary Results':4,'New-Architecture Influence Stability and Boundary':4,
      'External Support, Scale, and Anatomical Checks':5,'Reproducibility and Evidence Map':6}
    for title,chunk in chunks(body):
        if title=='Plan-9 Architecture-Family Protocol':chunk=chunk.replace(r'\input{table_full_reconstruction_benchmark.tex}','')
        groups[mapping.get(title,3)].append(nested(chunk))
    groups[3].append(r'\subsection{Preserved common-support reconstruction benchmark}'+'\n'+r'\input{table_full_reconstruction_benchmark.tex}'+'\n')
    groups[0].insert(0,r'''\subsection{Frozen final iteration and information boundaries}
Exactly three new scientific analyses were permitted: all ordered cross-architecture phase contrasts, acquired-only neural influence, and a fixed-context perturbation test of Proposition 1. Original papers and inputs were preserved before new inference. This is a frozen retrospective iteration on reused cohorts, not preregistration. The optional unused-cohort branch is skipped because no authenticated untouched cohort was established. Administrative submission metadata are outside this scientific iteration.

The SAINT coordinate amendment was recorded after interface inspection but before any new inference: both new phases use physical $z/(\mathrm{source\ depth}-1)$. Legacy coordinates are preserved for reproduction. New FP32 finite-response probes also differ from historical mixed precision. These are explicit implementation contracts, not favorable-result substitutions. Raw arrays and the initial/amended protocol hashes are retained.

''')
    groups[2].insert(0,r'''\subsection{Complete final-analysis protocols}
Cross-architecture sharing compares $A_0/B_0$ and identical $A_0/B_2$ for every ordered $A\ne B$ among HAT, SwinIR, I3Net, SAINT-style and CycleINR-style. No TTA is used. fastMRI targets are $\{3,5,7,9,11\}$; IXI uses the unchanged deterministic residue-balanced geometry. Both conditions use the same target-derived 1\% support. Five-plane means form examination observations. Primary $\Delta O$ and secondary alignment/disagreement differences average examinations. Fixed-reference and condition-specific paired-error rankings correlate examination means separately. The two cohorts are not pooled.

The acquired-only probe selects three rounded interior quartiles of $[3,\mathrm{depth}-4]$, with geometry-only deduplication. Its six acquired offsets are $\{-3,-2,-1,+1,+2,+3\}$; the target is absent. A common Q1 offset and Q99--Q1 range use finite nonzero acquired intensities; normalized values are clipped to $[0,1]$. The mask is the union of the nearest acquired planes' 1\% foregrounds. Both mask and normalizer are fixed before perturbations and shared across contexts. The common normalizer itself is shared preprocessing. Empty or invalid inputs would remain excluded with reasons; no case was removed by outcome.

Reference $(-2,+2)$ is compared with $(-2,+1),(-2,+3),(-1,+2),(-3,+2),(-1,+1),(-1,+3),(-3,+1),(-3,+3)$. The self-pair is absent. Four centered Rademacher fields use seeds 6101--6104 on the $256\times256$ input grid. Primary amplitude is .01; .005/.02/$-.01$ are all retained. FP32 without AMP/TF32, input/output clipping and resizing are fixed. Responses and hashes are saved before separate targets are accessed. Error outcomes use the same acquired support. Broad points pool contexts/planes; fixed-count rank residuals adjust span/asymmetry and examination. Examination resampling retains subordinate observations and reranks repeated observations. Weighted computations match direct bootstrap expansion.

Each HAT/SwinIR stratum passes only if all three alternative-versus-primary rank correlations reach the existing .85 threshold; .70 remains the historical catastrophic floor. The original six-stratum aggregate gate is NA without an acquired-only NingXia replication. The .90 threshold belongs to a separate historical new-architecture protocol and is not substituted here.

For the perturbation experiment, sort IXI IDs by SHA-256 of \texttt{MIRA-final-proposition:} plus ID and take the first twelve; use the depth-only central target, both models and all four exactly-one-anchor contexts. Perturb only the common anchor, holding other inputs, masks and scales fixed. Four fields and their negatives define eight equal-weight samples. Coupled outputs pair equal field indices; independent outputs average the entire Cartesian product, giving exactly equal empirical marginals. All amplitudes .0025/.005/.01/.02 remain. The odd response at .0025 supplies a fixed linear prediction scaled by squared amplitude. Relative error divides by the magnitude of that prediction. Reference response cosine $\ge.1$, $\le-.1$ and intermediate values label aligned, opposing and near-orthogonal examples descriptively, without eligibility selection.

All final intervals use 5,000 paired examination draws. Seeds are 18001/18002 for cross-architecture fastMRI/IXI; 18003/18004 for acquired-only IXI/fastMRI; 18005 for perturbation validation. Maximum standardized bootstrap deviation yields simultaneous intervals over 20 ordered pairs per cohort/endpoint, two models per acquired-only cohort/endpoint, or two models times four amplitudes. Pointwise intervals and finite-draw counts remain in the CSVs. These families do not correct the full retrospective search history.

''')
    groups[3].insert(0,r'''\subsection{Complete final primary results}
Tables below retain every ordered pair and every registered endpoint. Shared/disjoint ranking points use examination means and fixed A-error or condition-specific paired error as explicitly labeled. No null or negative pair is dropped. The acquired-only tables retain all four strata, and the fixed-context table retains every amplitude. Case/context-level values, including all individual approximation failures, are in the corresponding CSVs.
\input{final_cross_tables.tex}
\input{final_acquired_table.tex}
\input{final_stability_table.tex}
\input{final_proposition_table.tex}

\subsection{Interpreting local neural validation}
The maximum matched-covariance closure residual is $5.60\times10^{-12}$, which checks an identity. The independent substantive comparison uses the fixed .0025 odd-response approximation at every amplitude. Median relative error is 1.9--10.6\%, but the maximum is 126.4\% and the maximum absolute discrepancy is 112.14 native squared-intensity units. There are 86 aligned and ten near-orthogonal fixed model/case/context examples, and no opposing example. All 384 amplitude-specific observations remain. The near-orthogonal examples still have positive covariance; no neural opposing-sign validation is claimed. No post-result amplitude threshold defines success.

\begin{figure*}[t]\centering\includegraphics[width=.98\textwidth]{final_proposition_validation.pdf}
\caption{Fixed-context neural covariance experiment. (a) Mean observed coupled-minus-independent disagreement compared with the single .0025 odd-response prediction scaled by squared amplitude. (b) All individual relative approximation errors, including the 126.4\% boundary. The exact same-amplitude covariance closure is a separate identity check.}\label{fig:final-proposition}\end{figure*}

\subsection{Preserved historical headline figures}
These figures retain the original information contracts and estimands. They are not replaced numerically by the new acquired-only or cross-architecture results.
\begin{figure*}[t]\centering\includegraphics[width=.98\textwidth]{p17_influence_beyond_count.pdf}
\caption{Historical target-informed non-self influence advantage with six-stratum simultaneous intervals, alongside the fixed-count test with historical pointwise intervals. The NingXia null/mixed result remains.}\end{figure*}
\input{p17_influence_table.tex}
\begin{figure*}[t]\centering\includegraphics[width=.98\textwidth]{p13_architecture_robustness.pdf}
\caption{Historical same-model TTA replication: local effects versus examination ranking. Local fastMRI points use means and IXI medians; ranking uses within-examination medians. Five-model simultaneous intervals preserve the weak/null ranking results. Legacy SAINT coordinates are retained in this historical figure.}\end{figure*}

''')
    groups[4].insert(0,r'''\subsection{Final-analysis boundaries}
Every fastMRI fixed-reference ranking interval crosses zero; SAINT-to-I3Net has a negative point estimate. Four IXI fixed-reference intervals cross zero, all with I3Net as companion. The more favorable condition-specific paired-error endpoint is separately labeled and cannot replace fixed-reference inference. Near-orthogonal but no opposing neural sensitivities occur in the fixed-context sample, and individual approximation errors can exceed 100\%. Acquired-only brain influence does not repair the old NingXia null/mixed result or establish a cross-architecture finite-response claim. The final score-search branch is closed.

''')
    groups[5].insert(0,r'''\subsection{No new untouched-cohort confirmation}
No locally authenticated unused cohort was available under the optional final branch. Existing TopCoW/CAS analyses below remain analytical studies on public challenge training collections with the documented outcome-informed history, not newly untouched external neural confirmation.

''')
    groups[6].insert(0,r'''\subsection{Executable reproduction and report cards}
Run \texttt{python reproduce\_main.py} in the final-iteration directory. It reads saved target, prediction and finite-response arrays; independently reconstructs the historical and new observation tables and clustered statistics; asserts displayed main-paper numbers; and recreates figures and report cards. Historical summaries are assertion targets, never numerical inputs. Array hashes, per-column differences, reported/recomputed headline values and tolerances are in \path{REPRODUCTION_CHECK.md}. Full instructions and environment details are in \path{REPRODUCIBILITY.md}. No GPU or new network inference is needed for this reproduction path.

The MIRA CSV supplies separate local gap, named ranking gap, beyond-count advantage, fixed-count association, stability, information contract and claim eligibility. A design without a corresponding experiment has NA, not a borrowed value. Cross-architecture phase rows do not inherit within-model acquired-only influence; probe rows do not inherit phase-ranking effects. Eligibility means evidence for the named claim under that contract, not correctness probability. File inventories and all immutable source/array bindings stay in the machine-readable audit rather than substitute for scientific evidence in the paper.

''')
    titles=['Provenance and Study Status','Theory and Framework','Protocols and Eligibility','Complete Primary and Supporting Results','Negative Results and Boundaries','External Evidence and Its Limits','Reproducibility and Evidence Map']
    pre=text.split(r'\maketitle',1)[0]+r'\maketitle'+'\n'+r'\raggedbottom'+'\n'
    pre+=r'''This supplement is organized by provenance, theory, protocols, complete results, negative results, external scope and reproduction. Historical results remain unchanged unless an explicitly documented semantic or numerical correction is stated.\par
'''
    for i,(title,content) in enumerate(zip(titles,groups),1):
        name=f'final_supp_{i}.tex';part=r'\section{'+title+'}\n'+''.join(content)
        part=part.replace('$(-2,+1),(-2,+3),(-1,+2),(-3,+2),(-1,+1),(-1,+3),(-3,+1),(-3,+3)$','$(-2,+1)$, $(-2,+3)$, $(-1,+2)$, $(-3,+2)$, $(-1,+1)$, $(-1,+3)$, $(-3,+1)$, $(-3,+3)$')
        write_tex(name,part)
        if i>=4:pre+=r'\clearpage'+'\n'
        pre+=r'\input{'+name+'}\n'
    write_tex('supplement.tex',pre+r'\end{document}'+'\n')
    # Full 20-pair table for every endpoint, separately in each cohort.
    df=pd.read_csv(P/'cross_arch_shared_disjoint_intervals.csv');lines=[]
    labels={'observable_gap':'observable fraction','alignment_gap':'error alignment','disagreement_gap':'disagreement MAE','fixed_reference_ranking':'fixed-reference examination ranking','paired_error_ranking':'condition-specific paired-error examination ranking'}
    for ds in ['fastmri','ixi']:
        for ep,label in labels.items():
            lines += [r'\begin{table*}[t]\centering\small',r'\caption{'+('fastMRI' if ds=='fastmri' else 'IXI')+': '+label+r'. All ordered pairs; simultaneous family size 20.}',r'\begin{tabular}{llrrr}\toprule Reference A & Companion B & Shared & Disjoint & Disjoint minus shared [simultaneous 95\% CI]\\\midrule']
            for r in df[(df.dataset==ds)&(df.endpoint==ep)].itertuples():lines.append(f'{r.a.upper()} & {r.b.upper()} & {r.shared:.3f} & {r.disjoint:.3f} & {ci(r)} \\\\')
            lines += [r'\bottomrule\end{tabular}\end{table*}']
    write_tex('final_cross_tables.tex','\n'.join(lines)+'\n')
    st=pd.read_csv(P/'acquired_only_stability.csv');lines=[r'\begin{table*}[t]\centering\small\caption{All acquired-only amplitude/sign stability checks against +.01. The per-stratum threshold is .85; the original six-stratum aggregate gate is NA.}\begin{tabular}{llrrl}\toprule Cohort & Model & Alternative amplitude & Rank stability & Status\\\midrule']
    for r in st.itertuples():lines.append(f'{r.dataset} & {r.model.upper()} & {r.epsilon:g} & {r.rank_stability:.4f} & {r.status} \\\\')
    lines.append(r'\bottomrule\end{tabular}\end{table*}');write_tex('final_stability_table.tex','\n'.join(lines))
    pr=pd.read_csv(OUT/'proposition_summary.csv');lines=[r'\begin{table*}[t]\centering\small\caption{Every fixed-context neural amplitude. Effects are in native squared-intensity units; intervals are simultaneous over eight model/amplitude contrasts. Relative approximation error uses the fixed .0025 prediction as denominator.}\begin{tabular}{llrrr}\toprule Model & Amplitude & Observed mean [95\% CI] & Fixed-linear mean & Median relative error\\\midrule']
    for r in pr.itertuples():lines.append(f'{r.model.upper()} & {r.epsilon:g} & {r.observed_delta_mean:.3f} [{r.simultaneous_low:.3f},{r.simultaneous_high:.3f}] & {r.linear_prediction_mean:.3f} & {100*r.median_relative_error:.2f}\\% \\\\')
    lines.append(r'\bottomrule\end{tabular}\end{table*}');write_tex('final_proposition_table.tex','\n'.join(lines))
    print('Seven-part supplement prepared; historical sections retained',sum(map(len,groups)),flush=True)
if __name__=='__main__':main()
