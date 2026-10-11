# CVPR Upgrade Publication Readiness Report

Decision date: 2026-08-13.

## Verdict

**CVPR RESEARCH THRESHOLD MET; ANONYMIZED MANUSCRIPT GENERATED.**

Updated score after C5-E011--E014: novelty `4/5`, importance `4/5`, mechanistic depth `5/5`, experimental rigor `4/5`, reviewer resilience `4/5`.

Per Plan5, `PAPER/main.tex` and `PAPER/main.pdf` are now generated using the latest available official CVPR 2026 author kit. No CVPR 2027 kit was available on the audit date; the format must be rechecked once the target-year instructions appear.

Final build: six total pages (main content through page 5, references on pages 5--6), 307,306 bytes, plus a separately compilable one-page supplement. The final log has no overfull box, undefined citation/reference, or LaTeX error; every page was visually audited.

## Threshold-changing evidence

- C5-E011 introduces acquired-anchor cross-validation: every withheld pseudo-target is an actually acquired x4 anchor. It uses no dense target, no additional phase grid, no learned model, and no stride-8 inference.
- It ranks x4 error at `rho=0.937/0.955/0.955` on fastMRI/IXI/NingXia and predicts available densification benefit at `0.799/0.615`.
- C5-E012/E013 implement five exact overlap levels with fixed target, measurement count, absolute distance multiset, estimator, mask, and preprocessing. The preserved 0-to-1 exception falsifies an overlap-count-only law.
- C5-E014 derives shared coefficient influence. It explains error alignment and observability more strongly than raw overlap count in all three cohorts, with every clustered comparison interval above zero.

## What changed beyond the frozen TMI paper

- Added IXI-T2 test-115 (115 examinations, HAT and SwinIR) to the controlled overlap and method evidence.
- Quantified the complete error-energy/covariance chain, including a negative fastMRI reversal-control result.
- Completed the prespecified stable-wrong endpoint: clean maximal overlap increased high-error/low-disagreement prevalence by `0.209–0.282`, with all patient-cluster intervals above zero.
- Replaced the ordering-confounded maximum-overlap comparison with a clean same-anchor horizontal-equivariance control. Zero overlap retained higher ranking in all three cohorts with cluster intervals above zero.
- Derived an acquired-anchor bipartition estimator that needs no additional phase grid and never uses dense target in its score.
- Confirmed the estimator across two neural architectures and an analytical linear family.
- Evaluated all prespecified 10/20/30/50% retrospective densification budgets against random, oracle, PC, TTA, committee, adjacent-anchor difficulty, maximal-shared, and the original phase-grid score.
- Rejected a frozen two-component risk model when its confirmation gate failed.

## Evidence ledger

| Question | Result | Trace |
|---|---|---|
| Does clean maximal sharing reduce error observability? | yes in fastMRI, NingXia, IXI; zero-minus-max rho CIs all above zero | C5-E003, `outputs/clean_max_overlap*_summary.json` |
| Does the covariance chain hold? | yes in NingXia/IXI reversal comparisons; not all arrows in fastMRI | C5-E002, `outputs/overlap_covariance*_summary.json` |
| Is a strict multi-level matched ladder possible? | no with two bracketing anchors under all fixed constraints | `OVERLAP_LADDER_FEASIBILITY.md` |
| Can existing anchors yield a target-free score? | yes; neural and linear bipartition rank x4 error in three cohorts | C5-E007/E008 outputs |
| Does it predict densification benefit? | yes in fastMRI/NingXia association; IXI `NOT RUN` | C5-E007/E008 |
| Does it improve budget allocation? | versus random: fastMRI all budgets; NingXia 20/30/50%; not universally best | C5-E009 |
| Does two-component fusion improve reliability? | no, frozen confirmation gate failed | C5-E006 |

## Remaining boundaries after reaching 4/5 reviewer resilience

1. The exact ladder is not strictly monotone at 0-to-1 overlap; the paper claims shared influence rather than an integer-count law.
2. Anchor cross-validation is an examination-level triage method; fastMRI within-case plane localization is negative.
3. The allocation strategy is not uniformly best in NingXia and the 10% patient-cluster CI crosses zero.
4. IXI has no frozen x2 benefit endpoint, so its allocation consequence remains `NOT RUN`.
5. No prospective acquisition, clinical reader study, or externally locked benefit cohort exists.

## Required next evidence before paper generation

- Train or validate an interpolation model explicitly for bipartition/stride-8 contexts, with a locked test cohort.
- Obtain a third-cohort x2 endpoint or prospective acquisition simulation with genuinely available measurements.
- Demonstrate a consistent advantage over the strongest simple baseline, not merely random allocation.
- If feasible with new acquisition geometry, construct more than two overlap levels without changing target, distances, count, order, or preprocessing.

These items require new training/data/compute beyond the frozen assets. They are not silently marked complete.
