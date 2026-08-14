# Mechanism and Confounder Report

## Mechanistic question

Does target-preserving sampling-context disagreement reveal an error mode missed by cross-model disagreement, and what must it fail to detect?

## Controlled common-mode blur experiment

Status: EXPLORATORY. Eight fastMRI cases were selected lexicographically without inspecting outcomes. Three targets, three factors, and three degradation modes were evaluated.

At maximum severity:

| Perturbation | MAE change | Cross-model score change | PC score change |
|---|---:|---:|---:|
| Shared uniform blur | +3.69 | -12.79 | -7.89 |
| Shared factor-dependent blur | +3.14 | -12.98 | -2.46 |
| Target-only factor-dependent blur | +3.14 | -2.52 | -2.46 |

Gaussian smoothing makes outputs closer while moving them farther from ground truth. Both disagreement paradigms therefore become less alarming as error rises. PC does not generally solve common-mode blindness; it detects only errors that produce context-dependent output separation.

## Intensity and endpoint confounder

On all 24 fastMRI cases:

- raw PC vs raw MAE: mean nAURC 0.019, Spearman 0.965;
- raw PC vs range-normalized error: nAURC 0.240, Spearman 0.742;
- pooled-range-normalized PC vs normalized error: nAURC 0.113, Spearman 0.828;
- frozen committee vs normalized error: nAURC 0.266, Spearman 0.759.

Inferred dynamic range correlates with raw error at rho=0.643 and raw PC at rho=0.851. Thus part of raw PC performance comes from measuring error and disagreement in the same absolute intensity units. A nontrivial normalized association remains, but the exploratory normalized PC advantage has clustered delta nAURC -0.152 with interval [-0.278, 0.017], which includes zero.

Independent per-factor percentile normalization destroys the signal because it removes genuine cross-factor scale relationships as well as nuisance variation. A shared per-case scale is scientifically preferable, but it is PC-v2-EXPLORATORY, not a rescue modification to PC-v1.

## Generic perturbation comparator

For fastMRI x4 SwinIR under a unified common-support error endpoint:

| Score | nAURC | Spearman |
|---|---:|---:|
| Frozen committee | 0.0850 | 0.906 |
| TTA variance | 0.0339 | 0.940 |
| PC-v1 | 0.0113 | 0.982 |

The initial single SwinIR profile was inconclusive (`p=0.170`). Plan 3 expanded the comparison to 18 profiles: PC wins all of them, with examination-clustered `p=0.0035` on fastMRI and `p=0.0015` on NingXia. Sampling context is therefore more informative than four-view flip-TTA in this scope, but is not proven universally superior to every perturbation family.

## Factor-pair structure

On fastMRI, raw pair-level mean nAURC is 0.0178 for x2-x4, 0.0234 for x2-x6, and 0.0189 for x4-x6. More distant factors are not monotonically more informative. The signal is not driven by a single pair, and simple context distance does not explain it.

## Localization and natural granularity

The fixed map `abs(f_s1 - f_s2)` was evaluated without visual selection.

| Cohort/split | Cases | Planes | Median pixel rho (clustered 95% CI) | Slice rho | Case-pair rho | Top-10% error enrichment |
|---|---:|---:|---:|---:|---:|---:|
| fastMRI derivation | 8 | 480 | 0.677 | 0.631 | 0.802 | 2.41x |
| fastMRI held-out | 16 | 960 | 0.693 [0.649, 0.743] | 0.799 [0.659, 0.867] | 0.915 [0.805, 0.942] | 2.49x [2.32, 2.72] |
| NingXia OOF replication | 22 | 1,464 | 0.489 [0.477, 0.500] | 0.727 [0.618, 0.810] | 0.883 [0.775, 0.937] | 2.06x [2.00, 2.15] |

The phenomenon is strongest after aggregation but remains quantitatively meaningful at pixel and plane level.

## Consistent-but-wrong regime

NingXia contains 14 planes in the bottom PC quartile but top error quartile. Twelve are x4-x6 comparisons at the first generated plane (`z=1`), across six examinations. These boundary planes have limited surrounding context and define a real failure regime: two contexts can make the same edge mistake.

## Mechanistic conclusion

PC is a one-sided instability witness. Large disagreement certifies that at least one context-specific reconstruction differs materially from truth under a metric, but small disagreement does not certify accuracy. Its empirical value depends on the context intervention eliciting diverse errors and on meaningful intensity comparability.
