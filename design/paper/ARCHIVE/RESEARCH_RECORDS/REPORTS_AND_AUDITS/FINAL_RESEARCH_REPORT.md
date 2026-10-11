# Final Research Report — Plan 2 (Historical Milestone)

## Outcome

> Superseded as a project-status document by `PLAN3_RESEARCH_REPORT.md`. This file preserves the Plan-2 branch milestone; it is not a terminal project decision.

The Plan-2 branch reached a deliberately scoped scientific claim. The defensible contribution was not merely “PC improves nAURC,” but a mechanism with a proved direction, replicated empirical utility, and demonstrated failure boundary.

> In deterministic T2 brain slice interpolation, disagreement of the same reconstructor on world-coordinate-identical planes under different sampling factors is a reproducible, ground-truth-free, one-sided error witness across pixel, plane, and examination granularity. Large separation implies that at least one context output is wrong beyond a corresponding tolerance, but agreement cannot certify correctness. Empirical usefulness requires context-induced error diversity and intensity comparability.

This statement is supported in two retrospective cohorts and three reconstruction architectures. It is not a calibrated uncertainty, clinical-safety, or universal generalization claim.

## 1. Frozen method and governance

`PC-v1-FROZEN` was specified before Plan-2 confirmation in `FROZEN_METHOD.md`: identical NIfTI world planes are matched across interpolation factors 2, 4, and 6; absolute output separation is measured on common support and aggregated without target-derived selection. Method, support, aggregation, factors, orientation, endpoint, and prohibited rescue changes are fixed.

Experiments are labeled confirmatory or exploratory in `EXPERIMENTS.md`. The first 8 lexicographically ordered fastMRI cases were used only to derive the localization protocol; the remaining 16 were held out. The fixed protocol was then replicated on all 22 NingXia out-of-fold cases.

## 2. Formal principle

For an unknown target plane `y`, two context reconstructions `f_a` and `f_b`, and any metric `d` satisfying the triangle inequality,

`d(f_a, f_b) <= d(f_a, y) + d(f_b, y)`.

Therefore,

`max(d(f_a,y), d(f_b,y)) >= d(f_a,f_b)/2`.

Large context separation is thus a valid one-sided witness that at least one output is inaccurate. The reverse statement is false: both outputs may share a large stable error and agree closely. This distinction is the central scientific result.

## 3. Multi-granularity confirmation and replication

| Dataset / split | Cases | Matched planes | Median pixel Spearman | Slice Spearman | Case-pair Spearman | Top-10% error enrichment |
|---|---:|---:|---:|---:|---:|---:|
| fastMRI held-out confirmation | 16 | 960 | 0.693 [0.649, 0.743] | 0.799 [0.659, 0.867] | 0.915 [0.805, 0.942] | 2.49x [2.32, 2.72] |
| NingXia OOF replication | 22 | 1,464 | 0.489 [0.477, 0.500] | 0.727 [0.618, 0.810] | 0.883 [0.775, 0.937] | 2.06x [2.00, 2.15] |

Intervals use 5,000 examination-clustered bootstrap replicates. The cross-dataset result is stronger than a single aggregate leaderboard improvement: local inconsistency identifies error-rich pixels, planes, and examination/model/factor-pair units under a protocol fixed before confirmation.

## 4. Corrected examination-level statistics

The examination is the independent sampling unit. Replacing the earlier profile-aligned interval with examination-clustered inference changed the conclusion.

| Dataset | Cases | Profiles favoring PC | Delta nAURC vs committee | Clustered 95% CI | Rank-permutation p | LOO direction |
|---|---:|---:|---:|---:|---:|---:|
| fastMRI | 24 | 9/9 | -0.0698 | [-0.1597, -0.0183] | 0.005 | 24/24 |
| NingXia | 22 | 6/9 | -0.0256 | [-0.0957, 0.0092] | 0.164 | 22/22 |

The earlier NingXia confidence interval excluding zero is superseded. Its direction is not driven by one case, but comparative superiority is heterogeneous and statistically uncertain. Full risk-coverage curves agree: PC is better at 20/24 fastMRI coverage points with one crossing, and 14/22 NingXia points with three crossings.

## 5. Falsification: common-mode and consistent-but-wrong errors

Controlled blur directly rejects the hypothesis that PC detects general shared reconstruction failure. At blur severity 1.5, shared uniform smoothing increased MAE by 3.69 while cross-model disagreement fell by 12.79 and PC fell by 7.89. Factor-dependent and target-only smoothing showed the same direction. Both observables can become more confident-looking as stable error grows.

Natural data expose the same logical boundary. NingXia contains 14 planes simultaneously in the lowest PC quartile and highest error quartile; 12 are x4-x6 first generated planes. This concentration suggests a boundary-context failure, but does not establish its cause. Low PC must never be interpreted as a correctness certificate.

## 6. Geometry audit

All 1,518 audited case/model/factor-pair records have equal in-plane shape and orientation, zero spacing/FOV/slice-step/affine discrepancies at recorded precision, at least six matched planes, and maximum matched-plane distance 0 mm. A geometry mismatch explanation is rejected for the evaluated artifacts.

## 7. Intensity and endpoint confounding

Raw PC is extremely predictive of raw MAE (nAURC 0.019, Spearman 0.965), but raw dynamic range correlates with both PC (`rho=0.851`) and raw error (`rho=0.643`). Independent per-factor normalization destroys the signal, showing that representation choice is part of the method rather than innocuous preprocessing.

Using one pooled per-case range preserves a structural component: normalized PC versus normalized error has `rho=0.593`; its nAURC is 0.114 versus 0.266 for the frozen normalized committee. The exploratory comparative delta is -0.152, but its examination-clustered interval [-0.278, 0.017] includes zero. This `PC-v2` variant is promising, not confirmed.

## 8. Alternative explanations and baselines

- Every raw factor pair is informative; nAURC ranges 0.0178–0.0234, with no monotonic improvement as factor distance grows. The effect is not carried by a single pair and does not support a simple “larger context distance is better” story.
- The initial fastMRI x4 SwinIR comparison was inconclusive. Plan 3 supersedes it with 18 matched profiles: PC beats flip-TTA throughout, with clustered `p=0.0035` fastMRI and `p=0.0015` NingXia. This supports physical context over flips, not universal perturbation superiority.
- Adaptive committee selection, target attribution, and unnecessary hybrid complexity remain rejected by the earlier evidence chain.

## 9. Novelty position

Consistency-based uncertainty, ensembles, TTA, learned error prediction, probabilistic MRI reconstruction, and selective prediction are established. The defensible distinction is their combination here: a physical target-preserving acquisition-context intervention on identical world planes; an explicit one-sided mathematical interpretation; held-out and cross-cohort localization; and controlled plus natural demonstrations of what consistency cannot see. The work must not claim invention of consistency uncertainty generally. See `LITERATURE.md` and `NOVELTY_AUDIT.md`.

## 10. Reproducibility and traceability

- Frozen specification: `FROZEN_METHOD.md`
- Hypotheses and experiment registry: `HYPOTHESES.md`, `EXPERIMENTS.md`
- Evidence graph: `CLAIM_EVIDENCE_MATRIX.md`
- Statistics and influence: `STATISTICAL_VALIDITY.md`, `CASE_INFLUENCE_ANALYSIS.md`
- Mechanism and formalization: `MECHANISM_REPORT.md`, `THEORY.md`
- Falsification: `FALSIFICATION_REPORT.md`
- Machine-readable outputs: `plan2_outputs/`
- Analysis programs: `plan2_*.py`

The independent audit records 21/21 checks passing; the canonical RASINet test suite records 64/64 passing. Plan-2 scripts and reports remain entirely under `D:\MRI\design\paper`; original research artifacts were read only.

## 11. Remaining blockers and prohibited claims

Unavailable inputs prevent further decisive in-repository progress: no untouched external anatomy/site with aligned multi-factor predictions, no reader/downstream labels, and no multi-target multi-architecture TTA outputs. Consequently, the following remain unsupported: accuracy certification from low PC, calibrated uncertainty, clinical benefit, external anatomy/site generalization, universal superiority over committee/TTA, and identification of which output is wrong.

## 12. Final decision

Stop optimizing the score. The mechanism is now better understood than the original leaderboard framing: context separation is useful precisely when the intervention diversifies errors, and necessarily blind when errors remain shared. Future evidence should test the frozen principle on genuinely new data and meaningful downstream endpoints; it should not tune again on the present cohorts.
