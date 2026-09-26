from common import *

def put(name,text): (P/name).write_text(text,encoding='utf-8')
def table(df):
    def fmt(x):
        if isinstance(x,(float,np.floating)):return f'{x:.6g}'
        return str(x)
    return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(x) for x in row)+' |' for row in df.itertuples(index=False,name=None))+'\n'

def main():
    c=pd.read_csv(P/'cross_arch_shared_disjoint_intervals.csv');a=pd.read_csv(OUT/'acquired_only_summary.csv');st=pd.read_csv(P/'acquired_only_stability.csv');p=pd.read_csv(P/'proposition1_neural_validation.csv');ps=pd.read_csv(OUT/'proposition_summary.csv')
    put('CROSS_ARCH_INTERPRETATION.md','''# Cross-architecture shared-evidence intervention

This is one of three frozen final-iteration analyses, on historically reused cohorts. All 20 ordered pairs of five frozen architecture implementations were evaluated separately on fastMRI (24 examinations) and IXI (115). The reference A(phase 0) is identical in the shared A0/B0 and disjoint A0/B2 conditions. There is no TTA in this experiment. Every target and common evaluation mask is identical across conditions. The mask is target-derived; this contrast is not acquired-only.

The primary endpoint averages five plane-level observable-fraction differences within an examination and then averages examinations. All 40 local intervals exclude zero under simultaneous 20-pair inference separately in each cohort: fastMRI gains 6.236–16.022 percentage points and IXI gains 13.113–28.531. Disagreement increases and alignment decreases in all pairs with their endpoint-specific simultaneous intervals excluding zero. These are related geometric endpoints, not three independent discoveries.

The ranking boundary remains material. All 20 fastMRI fixed-reference ranking intervals cross zero, including SAINT→I3Net with a negative point estimate (−.002609). IXI has 16 positive simultaneous fixed-reference ranking intervals and four crossing zero: HAT→I3Net, SwinIR→I3Net, SAINT→I3Net, CycleINR→I3Net. Condition-specific paired-error ranking is a different endpoint: 0/20 fastMRI and 20/20 IXI intervals exclude zero positively. Changing the error endpoint changes the conclusion; paired error is not silently substituted for fixed A-error.

This answers the objection that the original effect is only failure of same-network flip equivariance. It does not isolate acquisition identity from every nuisance: signed geometry, phase-specific normalization, companion accuracy and nonlinear response may change. Different models still share datasets/training objectives; these are ordered contrasts, not 40 independent replications. Five lineages do not establish all neural ensembles.

SAINT uses the physical target coordinate z/(source_depth−1) in both new phases. The correction and separate legacy reproduction were bound before new inference. All 695 legacy phase-0 wrapper outputs match the stored outputs exactly. That verification applies to legacy mapping; it does not imply corrected SAINT phase-0 equals its legacy prediction.

No pairs were excluded for result direction, no new significance threshold was selected, and no new score was fitted. The complete 200 endpoint rows, pointwise/simultaneous intervals, bootstrap seeds and raw arrays remain available.

## All primary and ranking contrasts

'''+table(c[c.endpoint.isin(['observable_gap','fixed_reference_ranking','paired_error_ranking'])][['dataset','pair','endpoint','delta','simultaneous_low','simultaneous_high']]))
    put('ACQUIRED_ONLY_INFLUENCE_REPORT.md','''# Acquired-only neural influence

IXI is the primary cohort; fastMRI follows exactly the same acquired-only contract. All eligible cases and all three depth-selected targets remain. The six-plane acquired pool excludes the missing target. A common Q1 offset/Q99−Q1 scale and the union of the two nearest acquired foreground masks are frozen before responses. The pool-wide normalizer is itself shared preprocessing; this is explicitly disclosed. Finite responses are saved and hashed before separate target arrays are read for evaluation. All-anchor response energy remains in the influence denominator. The eight comparator contexts exclude the reference self-pair.

All four model/cohort strata show positive beyond-count advantages and positive exactly-one-anchor partial associations with simultaneous two-model intervals. The partial test adjusts ranked span/asymmetry and examination; it is an association conditional on those controls, not causal mediation. Points pool contexts/planes, while the bootstrap unit is examination. The target remains necessary for the error-alignment outcome; “acquired-only” describes influence formation, not target-free measurement of unknown error.

All twelve amplitude/sign checks exceed the historical HAT/SwinIR per-stratum threshold .85; minimum .880314. No gate was weakened in response to outcomes. The distinct new-architecture .90 gate is not the HAT/SwinIR rule. The original aggregate six-stratum gate is NA because no NingXia acquired-only replication was registered. FP32 without AMP/TF32 was fixed in advance; new and old estimates differ in preprocessing and precision, so their difference is not attributed solely to mask correction.

The positive brain results strengthen a previously missing information-access link. They do not repair historical target-derived probes, NingXia's null/mixed fixed-count result, SAINT's non-significant beyond-count result, I3Net/CycleINR instability, or the lack of useful universal scoring. Those observations remain intact.

## Associations (simultaneous across two models per cohort/endpoint)

'''+table(a[['dataset','model','endpoint','estimate','simultaneous_low','simultaneous_high','examinations','observations']])+'\n## Every stability check\n\n'+table(st[['dataset','model','epsilon','rank_stability','threshold','status']]))
    cats=p.drop_duplicates(['model','case','context']).reference_sensitivity_class.value_counts()
    put('PROPOSITION1_VALIDATION.md','''# Neural local validation of Proposition 1

Twelve IXI examinations were selected by the frozen hash order, not effect size. Both models, all four exactly-one-anchor contexts and all four amplitudes remain. Acquired-only preprocessing is fixed. Coupled noise uses eight identical field indices, while the independent condition uses the complete 8×8 Cartesian product. The empirical marginals are exactly equal; no noisy unmatched Monte Carlo comparator is used. Targets are not read in this experiment.

There are TWO distinct statements. First, computing centered finite-response covariance at the same amplitude gives ΔE||A−B||² = −2κ up to numerical precision (maximum absolute residual '''+f'{p.closure_abs_error.max():.6g}'+'''). This is an algebraic closure check, not scientific validation of a Jacobian model. Second, a single odd-response linearization fixed at ε0=.0025 predicts all amplitudes by ε² scaling. That prediction is compared to independently computed coupled-versus-independent disagreement from actual perturbed neural outputs. No amplitude is chosen after results.

All eight model/amplitude mean observed effects are negative with simultaneous eight-contrast intervals below zero. Median relative approximation errors range from 1.9% to 10.6%, but the worst individual relative error is '''+f'{100*p.approx_relative_error.max():.1f}%'+''' and the largest absolute error is '''+f'{p.approx_abs_error.max():.3f}'+''' native intensity-squared units. Thus the approximation has a useful local average trend and material individual nonlinear boundaries. Relative error divides by |linear prediction|, not by observed effect.

The 96 fixed model/case/context combinations contain '''+str(int(cats.get('aligned',0)))+' aligned and '+str(int(cats.get('near_orthogonal',0)))+''' near-orthogonal reference sensitivities, and zero opposing examples. The near-orthogonal examples still have positive response covariance and retain negative observed effects. The neural experiment therefore does not validate the opposing-sensitivity sign reversal; the analytical counterexample remains separate. Lack of such examples is reported, not repaired by searching another subset.

The experiment perturbs fixed nominal contexts. It does not prove that a phase change preserves bias/Jacobians, that sharing creates deterministic common bias, or that every realized error cosine increases. No empirical global remainder bound or clinical noise model is claimed.

## All amplitude summaries

'''+table(ps)+'\n## Largest individual approximation errors (all rows in CSV)\n\n'+table(p.sort_values('approx_relative_error',ascending=False).head(12)[['model','case','context','epsilon','observed_delta','linear_prediction','approx_relative_error','reference_sensitivity_class']]))
    put('UPDATED_CLAIM_EVIDENCE_MATRIX.md','''# Final claim–evidence matrix

| Claim | Evidence / independent unit | Information and inference | Final scope |
|---|---|---|---|
| Same-model clean sharing hides common error | Historical three-cohort HAT/SwinIR controls; examination/patient | Prediction mask; pooled-plane points and clustered pointwise intervals; IXI fixed endpoint is disjoint-pair MAE | Retained; neither examination ranking nor all-model 97–99.8% claim |
| Effect extends beyond same-network TTA | New E1 all 20 ordered pairs/cohort; examination | GT support; mean within/between; simultaneous family 20 per endpoint/cohort | Strengthened: all 40 local positive intervals; no universal ranking |
| Disjoint improves fixed-reference examination ranking | New E1 | Same A prediction/error both conditions | 16/20 IXI, 0/20 fastMRI simultaneous positive; four IXI intervals cross zero |
| Influence contains information beyond count without target-derived formation | New E2 HAT/SwinIR, IXI primary and fastMRI; examination | Acquired-only support/scale/responses; target only outcome; simultaneous family 2 | Strengthened within four brain strata; no acquired-only NingXia or cross-architecture probe |
| Fixed-count influence association | E2 pooled planes/contexts; examination bootstrap and fixed effects | Exactly one shared anchor, adjust span/asymmetry | Positive brain strata; historical NingXia remains null/mixed |
| Finite-response probe stability | E2 .005/.02/−.01 against .01 | Historical HAT/SwinIR per-stratum .85 rule | All 12 pass; original six-stratum aggregate gate NA |
| Conditional covariance proposition | Algebra, linear counterexamples, E3 neural fixed-context perturbations | Equal empirical marginals; identity separated from ε0-frozen prediction | Local support; worst relative error 126.4%, no neural opposing examples |
| MIRA usable output | 54 design-specific report cards, explicit schema and scripts | Seven separate fields; NA never borrowed across contracts | Audit output, no arbitrary scalar or correctness certificate |
| Five-architecture same-model replication | Historical P9/P11 arrays; examination | GT support and historical coordinate mapping | Retained separately from new corrected SAINT mapping |
| Universal scalar reliability improvement | Guard/context selection/jackknife/residualization attempts | Historical reused cohorts and degenerate labels retained | Not established; no new score search |
| Reconstruction quality breadth | All 13 models, 111 configurations, 20 budget contrasts | Native/master vs common-support protocols separate | Context and boundaries; no invented architecture or “ours” label |
| Untouched external confirmation | No authenticated unused local cohort | Optional branch skipped | Absent; previous TopCoW/CAS are reused analytical evidence |
| Prospective/clinical/non-MRI benefit | None | Not measured | Remove/avoid |
| 80% acceptance probability | No calibrated acceptance model | No defensible numerical estimate | Not promised |

The final protocol was frozen before this iteration's inference but the project and cohorts were already outcome-informed. Simultaneous intervals address the declared within-iteration families, not full-history analysis selection. The source manifest and reproduction report retain chronology and numerical corrections.
''')
    print('Scientific interpretation reports written',flush=True)
if __name__=='__main__':main()
